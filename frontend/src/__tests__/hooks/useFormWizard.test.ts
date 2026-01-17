/**
 * Tests for useFormWizard hook.
 */

import { act, renderHook } from '@testing-library/react';
import { describe, expect, it, vi } from 'vitest';
import { useFormWizard } from '../../hooks/useFormWizard';

// Mock form object
const mockForm = {
  trigger: vi.fn(),
  getValues: vi.fn(),
  setValue: vi.fn(),
  watch: vi.fn(),
  formState: { errors: {} },
} as unknown as Parameters<typeof useFormWizard>[0];

describe('useFormWizard', () => {
  it('should initialize at step 0', () => {
    const { result } = renderHook(() => useFormWizard(mockForm));

    expect(result.current.currentStep).toBe(0);
    expect(result.current.isFirstStep).toBe(true);
    expect(result.current.isLastStep).toBe(false);
  });

  it('should return total steps', () => {
    const { result } = renderHook(() => useFormWizard(mockForm));

    expect(result.current.totalSteps).toBeGreaterThan(0);
  });

  it('should navigate to next step', async () => {
    const { result } = renderHook(() => useFormWizard(mockForm));

    await act(async () => {
      await result.current.nextStep();
    });

    expect(result.current.currentStep).toBe(1);
    expect(result.current.isFirstStep).toBe(false);
  });

  it('should navigate to previous step', async () => {
    const { result } = renderHook(() => useFormWizard(mockForm));

    // Go to step 1 first
    await act(async () => {
      await result.current.nextStep();
    });

    expect(result.current.currentStep).toBe(1);

    // Go back
    act(() => {
      result.current.prevStep();
    });

    expect(result.current.currentStep).toBe(0);
    expect(result.current.isFirstStep).toBe(true);
  });

  it('should not go below step 0', () => {
    const { result } = renderHook(() => useFormWizard(mockForm));

    act(() => {
      result.current.prevStep();
    });

    expect(result.current.currentStep).toBe(0);
  });

  it('should not exceed max steps', async () => {
    const { result } = renderHook(() => useFormWizard(mockForm));
    const maxSteps = result.current.totalSteps;

    // Try to go beyond max
    for (let i = 0; i < maxSteps + 5; i++) {
      await act(async () => {
        await result.current.nextStep();
      });
    }

    expect(result.current.currentStep).toBe(maxSteps - 1);
    expect(result.current.isLastStep).toBe(true);
  });

  it('should go to specific step', () => {
    const { result } = renderHook(() => useFormWizard(mockForm));

    act(() => {
      result.current.goToStep(3);
    });

    expect(result.current.currentStep).toBe(3);
  });

  it('should not go to negative step', () => {
    const { result } = renderHook(() => useFormWizard(mockForm));

    act(() => {
      result.current.goToStep(-1);
    });

    expect(result.current.currentStep).toBe(0);
  });

  it('should not go to step beyond total', () => {
    const { result } = renderHook(() => useFormWizard(mockForm));
    const maxSteps = result.current.totalSteps;

    act(() => {
      result.current.goToStep(maxSteps + 10);
    });

    // Should remain at initial step
    expect(result.current.currentStep).toBe(0);
  });

  it('should return step info', () => {
    const { result } = renderHook(() => useFormWizard(mockForm));

    expect(result.current.stepInfo).toBeDefined();
    expect(result.current.stepInfo.id).toBeDefined();
    expect(result.current.stepInfo.title).toBeDefined();
  });

  it('should call validation on next step if provided', async () => {
    const validateStep = vi.fn().mockResolvedValue(true);
    const { result } = renderHook(() => useFormWizard(mockForm, validateStep));

    await act(async () => {
      await result.current.nextStep();
    });

    expect(validateStep).toHaveBeenCalledWith(0);
    expect(result.current.currentStep).toBe(1);
  });

  it('should not proceed if validation fails', async () => {
    const validateStep = vi.fn().mockResolvedValue(false);
    const { result } = renderHook(() => useFormWizard(mockForm, validateStep));

    await act(async () => {
      await result.current.nextStep();
    });

    expect(validateStep).toHaveBeenCalledWith(0);
    expect(result.current.currentStep).toBe(0); // Should stay on current step
  });

  it('should manage canProceed state', () => {
    const { result } = renderHook(() => useFormWizard(mockForm));

    expect(result.current.canProceed).toBe(true);

    act(() => {
      result.current.setCanProceed(false);
    });

    expect(result.current.canProceed).toBe(false);
  });
});
