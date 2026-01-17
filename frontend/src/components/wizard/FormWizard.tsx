/**
 * Main Form Wizard component that orchestrates the multi-step form.
 */

import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { useState } from 'react';
import type { ApplicationFormData } from '../../types/application';
import { applicationFormSchema } from '../../lib/validation';
import { formatMoneyInWords, getCurrentMonth } from '../../lib/utils';
import { publicApi } from '../../services/api';
import { useFormWizard } from '../../hooks/useFormWizard';
import { StepProgress } from './StepProgress';
import { Button } from '../ui';
import {
  BondDetailsStep,
  ApplicantTypeStep,
  ApplicantInfoStep,
  BankDetailsStep,
  ClassificationStep,
  DistributionStep,
  ReviewStep,
} from './steps';

interface FormWizardProps {
  onSuccess?: (applicationId: number) => void;
}

export function FormWizard({ onSuccess }: FormWizardProps) {
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState<string | null>(null);

  // Initialize form with default values
  const form = useForm<ApplicationFormData>({
    resolver: zodResolver(applicationFormSchema),
    defaultValues: {
      tenor: '2-Year',
      month_of_offer: getCurrentMonth(),
      bond_value: 5000,
      amount_in_words: formatMoneyInWords(5000),
      applicant_type: 'Individual',
      is_resident: true,
      investor_category: [],
      needs_witness: false,
      witness_acknowledged: false,
    },
    mode: 'onChange',
  });

  // Step-specific field validation
  const validateStep = async (step: number): Promise<boolean> => {
    let fieldsToValidate: (keyof ApplicationFormData)[] = [];

    switch (step) {
      case 0: // Bond Details
        fieldsToValidate = ['tenor', 'month_of_offer', 'bond_value'];
        break;
      case 1: // Applicant Type
        fieldsToValidate = ['applicant_type'];
        break;
      case 2: {
        // Applicant Info
        const applicantType = form.getValues('applicant_type');
        if (applicantType === 'Individual') {
          fieldsToValidate = [
            'title', 'full_name', 'date_of_birth', 'phone_number',
            'email', 'next_of_kin', 'address',
          ];
        } else if (applicantType === 'Joint') {
          fieldsToValidate = [
            'title', 'full_name', 'date_of_birth', 'phone_number',
            'email', 'next_of_kin', 'address',
            'joint_title', 'joint_full_name', 'joint_date_of_birth',
            'joint_phone_number', 'joint_email', 'joint_next_of_kin', 'joint_address',
          ];
        } else {
          fieldsToValidate = [
            'company_name', 'rc_number', 'business_type',
            'contact_person', 'corp_phone_number', 'corp_email',
          ];
        }
        break;
      }
      case 3: // Bank Details
        fieldsToValidate = ['bank_name', 'account_number'];
        if (form.getValues('applicant_type') === 'Joint') {
          fieldsToValidate.push('joint_bank_name', 'joint_account_number');
        }
        break;
      case 4: // Classification
        fieldsToValidate = ['is_resident', 'investor_category'];
        break;
      case 5: // Distribution
        // Optional fields, no required validation
        break;
      default:
        break;
    }

    if (fieldsToValidate.length === 0) return true;

    const result = await form.trigger(fieldsToValidate);
    return result;
  };

  const wizard = useFormWizard(form, validateStep);

  // Handle form submission
  const handleSubmit = async () => {
    setIsSubmitting(true);
    setSubmitError(null);

    try {
      const data = form.getValues();
      const response = await publicApi.submitApplication(data);
      onSuccess?.(response.id);
    } catch (error: unknown) {
      console.error('Submission error:', error);
      if (error && typeof error === 'object' && 'response' in error) {
        const axiosError = error as { response?: { data?: { detail?: string } } };
        setSubmitError(axiosError.response?.data?.detail || 'Failed to submit application. Please try again.');
      } else {
        setSubmitError('Failed to submit application. Please try again.');
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  // Render current step
  const renderStep = () => {
    switch (wizard.currentStep) {
      case 0:
        return <BondDetailsStep form={form} />;
      case 1:
        return <ApplicantTypeStep form={form} />;
      case 2:
        return <ApplicantInfoStep form={form} />;
      case 3:
        return <BankDetailsStep form={form} />;
      case 4:
        return <ClassificationStep form={form} />;
      case 5:
        return <DistributionStep form={form} />;
      case 6:
        return <ReviewStep form={form} />;
      default:
        return null;
    }
  };

  return (
    <div className="max-w-4xl mx-auto">
      {/* Progress indicator */}
      <StepProgress
        currentStep={wizard.currentStep}
        onStepClick={wizard.goToStep}
        allowNavigation={false}
      />

      {/* Form content */}
      <form onSubmit={(e) => e.preventDefault()}>
        <div className="mt-8 min-h-[400px]">{renderStep()}</div>

        {/* Error message */}
        {submitError && (
          <div className="mt-4 p-4 bg-error/10 border border-error rounded-lg">
            <p className="text-error text-sm">{submitError}</p>
          </div>
        )}

        {/* Navigation buttons */}
        <div className="wizard-nav mt-8">
          <Button
            type="button"
            variant="secondary"
            onClick={wizard.prevStep}
            disabled={wizard.isFirstStep}
          >
            Previous
          </Button>

          {wizard.isLastStep ? (
            <Button
              type="button"
              variant="primary"
              onClick={handleSubmit}
              isLoading={isSubmitting}
            >
              Submit Application
            </Button>
          ) : (
            <Button type="button" variant="primary" onClick={wizard.nextStep}>
              Next
            </Button>
          )}
        </div>
      </form>
    </div>
  );
}
