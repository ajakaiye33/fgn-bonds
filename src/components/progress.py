"""
Progress Indicator Component

Provides visual progress tracking for multi-step forms.
"""

import streamlit as st
from typing import List, Optional
from dataclasses import dataclass


@dataclass
class StepInfo:
    """Information about a wizard step"""
    number: int
    title: str
    icon: str
    is_complete: bool = False
    is_current: bool = False
    is_error: bool = False


class ProgressIndicator:
    """
    Renders a horizontal progress indicator for multi-step forms.
    """

    def __init__(self, steps: List[str], current_step: int, completed_steps: set = None):
        """
        Initialize the progress indicator.

        Args:
            steps: List of step titles
            current_step: Zero-indexed current step
            completed_steps: Set of completed step indices
        """
        self.steps = steps
        self.current_step = current_step
        self.completed_steps = completed_steps or set()
        self.total_steps = len(steps)

    @property
    def progress_percentage(self) -> float:
        """Calculate completion percentage"""
        if self.total_steps == 0:
            return 0
        return (len(self.completed_steps) / self.total_steps) * 100

    def render(self):
        """Render the progress indicator"""
        # CSS must be injected every render as Streamlit rebuilds the DOM on each rerun
        st.markdown("""
        <style>
        .wizard-progress {
            display: flex !important;
            justify-content: space-between !important;
            align-items: center !important;
            padding: 20px 0 !important;
            margin-bottom: 20px !important;
            position: relative !important;
            background: transparent !important;
        }
        .wizard-progress::before {
            content: '' !important;
            position: absolute !important;
            top: 50% !important;
            left: 5% !important;
            right: 5% !important;
            height: 3px !important;
            background: var(--color-border, #30363D) !important;
            transform: translateY(-50%) !important;
            z-index: 0 !important;
        }
        .wizard-step {
            display: flex !important;
            flex-direction: column !important;
            align-items: center !important;
            position: relative !important;
            z-index: 1 !important;
            flex: 1 !important;
        }
        .step-circle {
            width: 40px !important;
            height: 40px !important;
            border-radius: 50% !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            font-weight: 600 !important;
            font-size: 14px !important;
            margin-bottom: 8px !important;
            transition: all 0.3s ease !important;
        }
        .step-circle.pending {
            background: var(--color-surface, #161B22) !important;
            border: 2px solid var(--color-border, #30363D) !important;
            color: var(--color-text-secondary, #8B949E) !important;
        }
        .step-circle.current {
            background: var(--color-primary, #4CAF50) !important;
            border: 2px solid var(--color-primary, #4CAF50) !important;
            color: white !important;
            box-shadow: 0 0 0 4px rgba(76, 175, 80, 0.3) !important;
        }
        .step-circle.complete {
            background: var(--color-success, #2DA44E) !important;
            border: 2px solid var(--color-success, #2DA44E) !important;
            color: white !important;
        }
        .step-label {
            font-size: 12px !important;
            color: var(--color-text-secondary, #8B949E) !important;
            text-align: center !important;
            max-width: 100px !important;
        }
        .step-label.current {
            color: var(--color-primary, #4CAF50) !important;
            font-weight: 600 !important;
        }
        .step-label.complete {
            color: var(--color-success, #2DA44E) !important;
        }
        /* High contrast mode support */
        @media (prefers-contrast: high) {
            .step-circle {
                border-width: 3px !important;
            }
            .step-label {
                font-weight: 500 !important;
            }
        }
        @media (max-width: 768px) {
            .step-label {
                font-size: 10px !important;
                max-width: 60px !important;
            }
            .step-circle {
                width: 32px !important;
                height: 32px !important;
                font-size: 12px !important;
            }
        }
        </style>
        """, unsafe_allow_html=True)

        # Build the HTML for progress indicator (single line to avoid Streamlit escaping)
        steps_html = '<div class="wizard-progress">'

        for i, step_title in enumerate(self.steps):
            is_complete = i in self.completed_steps
            is_current = i == self.current_step

            circle_class = "complete" if is_complete else ("current" if is_current else "pending")
            label_class = "complete" if is_complete else ("current" if is_current else "")

            # Icon/number display
            if is_complete:
                icon = "&#10003;"  # Checkmark
            else:
                icon = str(i + 1)

            # Build HTML without extra whitespace to prevent Streamlit code block detection
            steps_html += f'<div class="wizard-step"><div class="step-circle {circle_class}">{icon}</div><div class="step-label {label_class}">{step_title}</div></div>'

        steps_html += '</div>'

        st.markdown(steps_html, unsafe_allow_html=True)

        # Also show a progress bar
        progress = self.progress_percentage
        st.progress(progress / 100, text=f"Step {self.current_step + 1} of {self.total_steps}")


def render_step_indicator(steps: List[str], current_step: int,
                          completed_steps: set = None) -> None:
    """
    Convenience function to render a step indicator.

    Args:
        steps: List of step titles
        current_step: Zero-indexed current step
        completed_steps: Set of completed step indices
    """
    indicator = ProgressIndicator(steps, current_step, completed_steps)
    indicator.render()


def render_native_progress(current_step: int, total_steps: int, step_names: List[str]) -> None:
    """
    Render a simple native Streamlit progress bar with step text.

    This is a lightweight alternative to the full wizard-style progress indicator.
    Uses only native Streamlit components, no custom CSS.

    Args:
        current_step: Current step number (1-indexed)
        total_steps: Total number of steps
        step_names: List of step names
    """
    progress_value = current_step / total_steps
    step_name = step_names[current_step - 1] if current_step <= len(step_names) else ""
    step_text = f"**Step {current_step} of {total_steps}:** {step_name}"
    st.progress(progress_value, text=step_text)
