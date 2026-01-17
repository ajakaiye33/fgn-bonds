/**
 * Custom hook for managing form wizard state and navigation.
 */

import { useState, useCallback } from 'react';
import type { UseFormReturn } from 'react-hook-form';
import { WIZARD_STEPS } from '../types/application';
import type { ApplicationFormData } from '../types/application';

export interface UseFormWizardReturn {
  currentStep: number;
  totalSteps: number;
  isFirstStep: boolean;
  isLastStep: boolean;
  stepInfo: typeof WIZARD_STEPS[number];
  goToStep: (step: number) => void;
  nextStep: () => void;
  prevStep: () => void;
  canProceed: boolean;
  setCanProceed: (value: boolean) => void;
}

export function useFormWizard(
  _form: UseFormReturn<ApplicationFormData>,
  validateStep?: (step: number) => Promise<boolean>
): UseFormWizardReturn {
  const [currentStep, setCurrentStep] = useState(0);
  const [canProceed, setCanProceed] = useState(true);
  const totalSteps = WIZARD_STEPS.length;

  const isFirstStep = currentStep === 0;
  const isLastStep = currentStep === totalSteps - 1;
  const stepInfo = WIZARD_STEPS[currentStep];

  const goToStep = useCallback((step: number) => {
    if (step >= 0 && step < totalSteps) {
      setCurrentStep(step);
    }
  }, [totalSteps]);

  const nextStep = useCallback(async () => {
    if (currentStep < totalSteps - 1) {
      if (validateStep) {
        const isValid = await validateStep(currentStep);
        if (!isValid) return;
      }
      setCurrentStep((prev) => prev + 1);
    }
  }, [currentStep, totalSteps, validateStep]);

  const prevStep = useCallback(() => {
    if (currentStep > 0) {
      setCurrentStep((prev) => prev - 1);
    }
  }, [currentStep]);

  return {
    currentStep,
    totalSteps,
    isFirstStep,
    isLastStep,
    stepInfo,
    goToStep,
    nextStep,
    prevStep,
    canProceed,
    setCanProceed,
  };
}
