/**
 * Step 2: Applicant Type - Choose between Individual, Joint, or Corporate.
 */

import { Controller, type UseFormReturn } from 'react-hook-form';
import type { ApplicationFormData, ApplicantType } from '../../../types/application';
import { cn } from '../../../lib/utils';

interface ApplicantTypeStepProps {
  form: UseFormReturn<ApplicationFormData>;
}

const applicantTypes: {
  value: ApplicantType;
  title: string;
  description: string;
  icon: React.ReactNode;
}[] = [
  {
    value: 'Individual',
    title: 'Individual',
    description: 'Single person subscription with personal details',
    icon: (
      <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth={1.5}
          d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"
        />
      </svg>
    ),
  },
  {
    value: 'Joint',
    title: 'Joint',
    description: 'Two individuals subscribing together (e.g., spouses)',
    icon: (
      <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth={1.5}
          d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"
        />
      </svg>
    ),
  },
  {
    value: 'Corporate',
    title: 'Corporate',
    description: 'Company or organization subscription',
    icon: (
      <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth={1.5}
          d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"
        />
      </svg>
    ),
  },
];

export function ApplicantTypeStep({ form }: ApplicantTypeStepProps) {
  const {
    control,
    formState: { errors },
  } = form;

  return (
    <div className="space-y-6">
      <div className="text-center mb-8">
        <h2 className="text-2xl font-semibold text-dark-text mb-2">
          Select Applicant Type
        </h2>
        <p className="text-dark-text-secondary">
          Choose the type of subscription you want to make.
        </p>
      </div>

      <Controller
        name="applicant_type"
        control={control}
        render={({ field }) => (
          <div className="space-y-4">
            {applicantTypes.map((type) => (
              <button
                key={type.value}
                type="button"
                onClick={() => field.onChange(type.value)}
                className={cn(
                  'w-full p-6 rounded-xl border-2 transition-all duration-200',
                  'flex items-center gap-6 text-left',
                  field.value === type.value
                    ? 'border-primary-500 bg-primary-900/20'
                    : 'border-dark-border hover:border-primary-700 bg-dark-surface'
                )}
              >
                <div
                  className={cn(
                    'p-4 rounded-lg',
                    field.value === type.value
                      ? 'bg-primary-500 text-white'
                      : 'bg-dark-elevated text-dark-text-secondary'
                  )}
                >
                  {type.icon}
                </div>
                <div className="flex-1">
                  <h3
                    className={cn(
                      'text-lg font-semibold',
                      field.value === type.value
                        ? 'text-primary-500'
                        : 'text-dark-text'
                    )}
                  >
                    {type.title}
                  </h3>
                  <p className="text-sm text-dark-text-secondary mt-1">
                    {type.description}
                  </p>
                </div>
                <div
                  className={cn(
                    'w-6 h-6 rounded-full border-2 flex items-center justify-center',
                    field.value === type.value
                      ? 'border-primary-500 bg-primary-500'
                      : 'border-dark-border'
                  )}
                >
                  {field.value === type.value && (
                    <svg
                      className="w-4 h-4 text-white"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M5 13l4 4L19 7"
                      />
                    </svg>
                  )}
                </div>
              </button>
            ))}
            {errors.applicant_type && (
              <p className="error-message">{errors.applicant_type.message}</p>
            )}
          </div>
        )}
      />
    </div>
  );
}
