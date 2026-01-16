"""
Multi-Step Form Wizard

A wizard component for multi-step form flows with progress tracking.
"""

import streamlit as st
from typing import List, Dict, Callable, Optional, Any
from dataclasses import dataclass, field
from enum import Enum


class StepStatus(Enum):
    """Status of a wizard step"""
    PENDING = "pending"
    CURRENT = "current"
    COMPLETE = "complete"
    ERROR = "error"


@dataclass
class WizardStep:
    """Represents a single step in the wizard"""
    id: str
    title: str
    description: str = ""
    fields: List[str] = field(default_factory=list)
    validation_fn: Optional[Callable[[Dict], tuple]] = None
    render_fn: Optional[Callable[[], None]] = None

    def validate(self, data: Dict) -> tuple:
        """
        Validate this step's data.

        Returns:
            Tuple of (is_valid, list of error messages)
        """
        if self.validation_fn:
            return self.validation_fn(data)
        return True, []


class FormWizard:
    """
    Multi-step form wizard with progress tracking and navigation.
    """

    # Step definitions for FGN Bond form
    STEPS = [
        WizardStep(
            id="bond_details",
            title="Bond Details",
            description="Select your bond preferences",
            fields=["tenor", "month_of_offer", "bond_value", "amount_in_words"],
        ),
        WizardStep(
            id="applicant_type",
            title="Applicant Type",
            description="Select your applicant category",
            fields=["applicant_type"],
        ),
        WizardStep(
            id="applicant_info",
            title="Applicant Information",
            description="Enter your personal or company details",
            fields=["title", "full_name", "email", "phone_number", "occupation",
                    "passport_no", "next_of_kin", "address", "mothers_maiden_name",
                    "cscs_number", "chn_number", "date_of_birth"],
        ),
        WizardStep(
            id="bank_details",
            title="Bank Details",
            description="Enter your bank information for interest payments",
            fields=["bank_name", "bank_branch", "account_number", "sort_code", "bvn"],
        ),
        WizardStep(
            id="classification",
            title="Classification",
            description="Select your residency status and investor category",
            fields=["is_resident", "investor_category"],
        ),
        WizardStep(
            id="distribution",
            title="Distribution Agent",
            description="Enter distribution agent details",
            fields=["agent_name", "stockbroker_code"],
        ),
        WizardStep(
            id="review",
            title="Review & Submit",
            description="Review your application and submit",
            fields=[],
        ),
    ]

    def __init__(self):
        """Initialize the form wizard"""
        self._init_session_state()

    def _init_session_state(self):
        """Initialize wizard state in session"""
        if 'wizard_current_step' not in st.session_state:
            st.session_state.wizard_current_step = 0

        if 'wizard_completed_steps' not in st.session_state:
            st.session_state.wizard_completed_steps = set()

        if 'wizard_step_errors' not in st.session_state:
            st.session_state.wizard_step_errors = {}

    @property
    def current_step(self) -> int:
        """Get current step index"""
        return st.session_state.wizard_current_step

    @current_step.setter
    def current_step(self, value: int):
        """Set current step index"""
        st.session_state.wizard_current_step = max(0, min(value, len(self.STEPS) - 1))

    @property
    def completed_steps(self) -> set:
        """Get set of completed step indices"""
        return st.session_state.wizard_completed_steps

    @property
    def current_step_info(self) -> WizardStep:
        """Get current step information"""
        return self.STEPS[self.current_step]

    @property
    def is_first_step(self) -> bool:
        """Check if on first step"""
        return self.current_step == 0

    @property
    def is_last_step(self) -> bool:
        """Check if on last step"""
        return self.current_step == len(self.STEPS) - 1

    @property
    def progress_percentage(self) -> float:
        """Calculate completion percentage"""
        return (len(self.completed_steps) / len(self.STEPS)) * 100

    def get_step_titles(self) -> List[str]:
        """Get list of step titles"""
        return [step.title for step in self.STEPS]

    def go_to_step(self, step_index: int):
        """Navigate to a specific step"""
        if 0 <= step_index < len(self.STEPS):
            self.current_step = step_index
            st.rerun()

    def next_step(self, validate: bool = True) -> bool:
        """
        Move to the next step.

        Args:
            validate: Whether to validate current step before proceeding

        Returns:
            True if moved to next step, False if validation failed
        """
        if validate:
            # Get form data from session state
            data = self._collect_form_data()
            is_valid, errors = self.current_step_info.validate(data)

            if not is_valid:
                st.session_state.wizard_step_errors[self.current_step] = errors
                # Trigger rerun to display validation errors immediately
                st.rerun()

        # Mark current step as complete
        st.session_state.wizard_completed_steps.add(self.current_step)
        st.session_state.wizard_step_errors.pop(self.current_step, None)

        # Move to next step
        if not self.is_last_step:
            self.current_step += 1
            st.rerun()
            return True

        return True

    def prev_step(self):
        """Move to the previous step"""
        if not self.is_first_step:
            self.current_step -= 1
            st.rerun()

    def mark_complete(self, step_index: int):
        """Mark a step as complete"""
        st.session_state.wizard_completed_steps.add(step_index)

    def mark_incomplete(self, step_index: int):
        """Mark a step as incomplete"""
        st.session_state.wizard_completed_steps.discard(step_index)

    def reset(self):
        """Reset wizard to initial state"""
        st.session_state.wizard_current_step = 0
        st.session_state.wizard_completed_steps = set()
        st.session_state.wizard_step_errors = {}

    def _collect_form_data(self) -> Dict:
        """Collect all form data from session state"""
        data = {}
        for step in self.STEPS:
            for field in step.fields:
                if field in st.session_state:
                    data[field] = st.session_state[field]
        return data

    def render_progress(self):
        """Render the progress indicator"""
        from .progress import render_step_indicator
        render_step_indicator(
            steps=self.get_step_titles(),
            current_step=self.current_step,
            completed_steps=self.completed_steps
        )

    def render_navigation(self, on_submit: Callable = None):
        """
        Render navigation buttons.

        Args:
            on_submit: Callback function for final submission
        """
        col1, col2, col3 = st.columns([1, 2, 1])

        with col1:
            if not self.is_first_step:
                if st.button("Previous", use_container_width=True):
                    self.prev_step()

        with col3:
            if self.is_last_step:
                if st.button("Submit Application", type="primary", use_container_width=True):
                    if on_submit:
                        on_submit()
            else:
                if st.button("Next", type="primary", use_container_width=True):
                    self.next_step()

    def render_step_header(self):
        """Render current step header"""
        step = self.current_step_info
        st.header(step.title)
        if step.description:
            st.caption(step.description)

        # Show any errors for this step
        if self.current_step in st.session_state.wizard_step_errors:
            errors = st.session_state.wizard_step_errors[self.current_step]
            if errors:
                for error in errors:
                    st.error(error)

    def render(self, step_renderers: Dict[str, Callable], on_submit: Callable = None):
        """
        Render the complete wizard.

        Args:
            step_renderers: Dictionary mapping step IDs to render functions
            on_submit: Callback for final submission
        """
        # Render progress indicator
        self.render_progress()

        st.divider()

        # Render current step header
        self.render_step_header()

        # Render current step content
        step_id = self.current_step_info.id
        if step_id in step_renderers:
            step_renderers[step_id]()
        else:
            st.warning(f"No renderer defined for step: {step_id}")

        st.divider()

        # Render navigation
        self.render_navigation(on_submit)


def create_wizard() -> FormWizard:
    """Factory function to create and return a FormWizard instance"""
    return FormWizard()
