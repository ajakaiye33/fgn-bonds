# FGN Bond App - Bug Fixes and Recommendations Implementation Plan

## Summary of Issues Found During Playwright Testing

| Issue | Severity | Status |
|-------|----------|--------|
| 1. Wizard steps 2-7 showing raw HTML | **CRITICAL** | To Fix |
| 2. `KeyError: 'corp_phone'` | HIGH | **FIXED** |
| 3. Plotly not working in admin dashboard | MEDIUM | To Fix |

---

## Issue 1: Wizard CSS Rendering Bug (CRITICAL)

### Root Cause
CSS is being re-injected on every Streamlit rerun without session state caching. The `ProgressIndicator.render()` method in `src/components/progress.py` injects CSS every time it's called, causing:
- CSS accumulation in the DOM
- Selector conflicts between duplicate style blocks
- Browser CSS parser failures
- Raw HTML displayed instead of rendered components

### Files to Modify

1. **`src/components/progress.py`** - Primary fix
2. **`src/design_system/theme.py`** - Add caching
3. **`src/accessibility.py`** - Add caching
4. **`src/responsive.py`** - Add caching
5. **`src/error_handling.py`** - Add caching

### Implementation

#### Step 1: Fix `src/components/progress.py` (lines 52-161)

Add session state caching to prevent CSS re-injection:

```python
def render(self):
    """Render the progress indicator."""
    # Cache CSS to prevent re-injection on every rerun
    if '_wizard_progress_css_injected' not in st.session_state:
        st.markdown("""
        <style>
        .wizard-progress { ... }
        ...
        </style>
        """, unsafe_allow_html=True)
        st.session_state._wizard_progress_css_injected = True

    # Generate and render steps HTML (this can re-render)
    steps_html = self._generate_steps_html()
    st.markdown(steps_html, unsafe_allow_html=True)
```

#### Step 2: Fix `src/design_system/theme.py` (apply_theme function ~line 827)

```python
def apply_theme(theme: str = "dark") -> None:
    """Apply the specified theme to the Streamlit app."""
    cache_key = f'_theme_{theme}_css_applied'
    if cache_key not in st.session_state:
        css = get_theme_css(theme)
        st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)
        st.session_state[cache_key] = True
```

#### Step 3: Fix `src/accessibility.py` (setup_accessibility function)

```python
def setup_accessibility():
    """Set up accessibility features."""
    if '_accessibility_css_applied' not in st.session_state:
        inject_accessibility_css()
        st.session_state._accessibility_css_applied = True
```

#### Step 4: Fix `src/responsive.py` (setup_responsive function)

```python
def setup_responsive():
    """Set up responsive design."""
    if '_responsive_css_applied' not in st.session_state:
        inject_responsive_css()
        st.session_state._responsive_css_applied = True
```

#### Step 5: Fix `src/error_handling.py` (setup_error_handling function)

```python
def setup_error_handling():
    """Set up error handling UI."""
    if '_error_handling_css_applied' not in st.session_state:
        # inject CSS
        st.session_state._error_handling_css_applied = True
```

---

## Issue 2: Corporate Phone Field Mismatch (FIXED)

### Status: Already Fixed During Testing

**Location:** `src/form_handler.py` lines 251-252 and 347-348

**Change Applied:**
```python
# Before (broken):
["Phone Number:", data['corp_phone']],
["Email:", data['corp_email']]

# After (fixed):
["Phone Number:", data.get('corp_phone_number', data.get('corp_phone', ''))],
["Email:", data.get('corp_email', '')]
```

**No additional action needed.**

---

## Issue 3: Plotly Dependency

### Root Cause
- Plotly IS in `requirements.txt` (`plotly==5.18.0`)
- The import is conditional (inside function) so error only appears when that tab is accessed
- The try/except fallback still calls `st.plotly_chart()` which requires plotly

### Files to Modify

1. **`src/admin_app.py`** - Fix fallback logic
2. **Verify installation** - Ensure plotly is installed

### Implementation

#### Step 1: Verify plotly is installed

```bash
pip install plotly==5.18.0
```

#### Step 2: Fix fallback in `src/admin_app.py` (lines 257-279)

Improve the fallback to use Streamlit's native bar chart if plotly is unavailable:

```python
def render_value_analysis(df: pd.DataFrame):
    """Render value analysis tab with charts."""
    # ... existing code to prepare value_df ...

    try:
        import plotly.express as px
        fig = px.pie(
            value_df,
            values='Count',
            names='Range',
            hole=0.4,
            color_discrete_sequence=px.colors.sequential.Greens
        )
        fig.update_layout(showlegend=True, height=400)
        st.plotly_chart(fig, use_container_width=True)
    except ImportError:
        # True fallback using native Streamlit chart
        st.warning("Plotly not available. Showing basic chart.")
        st.bar_chart(value_df.set_index('Range')['Count'])
```

---

## Implementation Order

1. **Fix wizard CSS caching** (Issue 1) - Critical, breaks core functionality
   - `src/components/progress.py`
   - `src/design_system/theme.py`
   - `src/accessibility.py`
   - `src/responsive.py`
   - `src/error_handling.py`

2. **Fix plotly fallback** (Issue 3) - Medium priority
   - `src/admin_app.py`

3. **Verify corp_phone fix** (Issue 2) - Already done, verify working

---

## Verification Plan

### Test 1: Wizard Navigation
```bash
streamlit run src/streamlit_app.py
```
1. Navigate through all 7 wizard steps
2. Verify no raw HTML appears
3. Verify CSS styling persists across steps

### Test 2: Corporate Application
1. Select "Corporate" applicant type
2. Fill all corporate fields
3. Submit application
4. Verify PDF generates without errors

### Test 3: Admin Dashboard
```bash
streamlit run src/admin_app.py --server.port 8502
```
1. Login with admin/admin123
2. Navigate to "Value Analysis" tab
3. Verify pie/donut chart renders (or fallback bar chart)

### Test 4: Run Playwright Again
Re-run the comprehensive Playwright test to verify all issues are resolved.

---

## Files Summary

| File | Changes |
|------|---------|
| `src/components/progress.py` | Add CSS caching with session state |
| `src/design_system/theme.py` | Add CSS caching with session state |
| `src/accessibility.py` | Add CSS caching with session state |
| `src/responsive.py` | Add CSS caching with session state |
| `src/error_handling.py` | Add CSS caching with session state |
| `src/admin_app.py` | Fix plotly fallback to use native Streamlit chart |
| `src/form_handler.py` | Already fixed - verify |

---

## Estimated Impact

- **Wizard CSS fix**: Resolves critical user-facing bug, enables full wizard functionality
- **Plotly fix**: Improves admin dashboard reliability
- **Corp phone fix**: Enables corporate applications to work correctly

---

# Phase 2: Streamlit Native Features Optimization

## Overview

Based on analysis of [Streamlit's official documentation](https://docs.streamlit.io), the app is using extensive custom CSS injection when Streamlit provides native alternatives. This creates maintenance overhead and bugs like the wizard rendering issue.

## Recommended Native Feature Adoption

### 1. Replace Custom Theme CSS with Native Theming

**Current:** `src/design_system/theme.py` injects 800+ lines of CSS via `st.markdown(unsafe_allow_html=True)`

**Better:** Use Streamlit's native `.streamlit/config.toml` theming

**Implementation:**
Update `.streamlit/config.toml`:
```toml
[theme]
primaryColor = "#006400"  # DMO Green
backgroundColor = "#0E1117"  # Dark background
secondaryBackgroundColor = "#262730"
textColor = "#FAFAFA"
font = "sans serif"

[theme.light]
primaryColor = "#006400"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"
textColor = "#31333F"
```

**Files to modify:**
- `.streamlit/config.toml` - Add comprehensive theme config
- `src/design_system/theme.py` - Simplify to only inject minimal custom CSS for elements Streamlit doesn't style natively

**Benefit:** Eliminates ~800 lines of custom CSS, uses Streamlit's optimized theming engine

---

### 2. Replace Custom Progress Indicator with `st.progress`

**Current:** `src/components/progress.py` renders custom HTML/CSS wizard steps

**Better:** Use native [st.progress](https://docs.streamlit.io/develop/api-reference/status/st.progress) with text

**Implementation:**
```python
# Simple native progress bar with step text
def render_wizard_progress(current_step: int, total_steps: int, step_names: list):
    progress_value = current_step / total_steps
    step_text = f"**Step {current_step} of {total_steps}:** {step_names[current_step-1]}"
    st.progress(progress_value, text=step_text)
```

**Files to modify:**
- `src/components/progress.py` - Replace custom HTML with `st.progress`
- `src/components/wizard.py` - Update to use simplified progress

**Benefit:** No custom CSS needed, native styling, automatic dark/light theme support

---

### 3. Use `st.status` for Form Submission Feedback

**Current:** Custom success/error messages with manual styling

**Better:** Use native [st.status](https://docs.streamlit.io/develop/api-reference/status/st.status) container

**Implementation:**
```python
with st.status("Submitting application...", expanded=True) as status:
    st.write("Validating form data...")
    # validation logic
    st.write("Generating PDF...")
    # PDF generation
    st.write("Saving to database...")
    # database save
    status.update(label="Application submitted successfully!", state="complete")
```

**Files to modify:**
- `src/streamlit_app.py` - Update submission flow to use `st.status`
- `src/components/feedback.py` - Simplify or deprecate custom feedback components

**Benefit:** Native spinner, expandable details, automatic state icons

---

### 4. Leverage `st.form` More Effectively

**Current:** The app uses `st.form` but may not leverage all features

**Better:** Use [st.form](https://docs.streamlit.io/develop/api-reference/execution-flow/st.form) with:
- `clear_on_submit=True` for fresh form after submission
- `enter_to_submit=True` (default) for keyboard accessibility
- Proper `st.form_submit_button` placement

**Files to review:**
- `src/streamlit_app.py` - Audit form usage

---

### 5. Consider `st.Page` / `st.navigation` for Wizard

**Current:** Custom wizard with session state step tracking

**Alternative:** Use Streamlit's native [multipage app](https://docs.streamlit.io/develop/concepts/multipage-apps/overview) pattern

**Structure:**
```
src/
├── streamlit_app.py          # Entry point with st.navigation
├── pages/
│   ├── 1_bond_details.py
│   ├── 2_applicant_type.py
│   ├── 3_applicant_info.py
│   ├── 4_bank_details.py
│   ├── 5_classification.py
│   ├── 6_distribution_agent.py
│   └── 7_review_submit.py
```

**Note:** This is a larger refactor. The CSS caching fix (Phase 1) should be done first. This can be a future improvement.

---

## Implementation Priority

| Priority | Task | Effort | Impact |
|----------|------|--------|--------|
| 1 | Fix CSS caching (Phase 1 bugs) | Low | Critical |
| 2 | Replace theme CSS with config.toml | Medium | High |
| 3 | Replace progress indicator with st.progress | Low | Medium |
| 4 | Add st.status for submission feedback | Low | Medium |
| 5 | Audit st.form usage | Low | Low |
| 6 | Consider st.Page refactor (future) | High | Medium |

---

## Native Features Reference

| Feature | Streamlit Native | Current Custom |
|---------|-----------------|----------------|
| Theming | `.streamlit/config.toml` | `theme.py` (800+ lines CSS) |
| Progress | `st.progress(value, text)` | `progress.py` (160+ lines) |
| Status | `st.status(label, state)` | `feedback.py` (custom) |
| Forms | `st.form` with all options | Partial usage |
| Tabs | `st.tabs` | Already using ✓ |
| Multipage | `st.Page` / `st.navigation` | Custom wizard |

---

## Updated Files Summary (Full Plan)

### Phase 1: Bug Fixes (Critical)
| File | Changes |
|------|---------|
| `src/components/progress.py` | Add CSS caching |
| `src/design_system/theme.py` | Add CSS caching |
| `src/accessibility.py` | Add CSS caching |
| `src/responsive.py` | Add CSS caching |
| `src/error_handling.py` | Add CSS caching |
| `src/admin_app.py` | Fix plotly fallback |

### Phase 2: Native Feature Adoption (Improvement)
| File | Changes |
|------|---------|
| `.streamlit/config.toml` | Add comprehensive native theme |
| `src/design_system/theme.py` | Reduce to minimal custom CSS |
| `src/components/progress.py` | Replace with `st.progress` |
| `src/streamlit_app.py` | Add `st.status` for submission |
| `src/components/feedback.py` | Simplify using native components |

---

## Verification Plan (Updated)

### After Phase 1:
1. Wizard navigation works without raw HTML
2. Corporate applications submit successfully
3. Admin dashboard charts render

### After Phase 2:
1. Theme switches correctly between light/dark
2. Progress bar shows native Streamlit styling
3. Form submission shows expandable status
4. App feels more "native" Streamlit

### Final Test:
Re-run comprehensive Playwright tests to verify all functionality

---

## Sources

- [st.progress Documentation](https://docs.streamlit.io/develop/api-reference/status/st.progress)
- [st.status Documentation](https://docs.streamlit.io/develop/api-reference/status/st.status)
- [st.form Documentation](https://docs.streamlit.io/develop/api-reference/execution-flow/st.form)
- [Streamlit Theming Guide](https://docs.streamlit.io/develop/concepts/configuration/theming)
- [Multipage Apps Overview](https://docs.streamlit.io/develop/concepts/multipage-apps/overview)
- [2025 Release Notes](https://docs.streamlit.io/develop/quick-reference/release-notes/2025)
