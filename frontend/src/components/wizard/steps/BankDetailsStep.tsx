/**
 * Step 4: Bank Details - Enter bank account information.
 */

import { Controller, type UseFormReturn, type Control, type FieldErrors, type UseFormRegister } from 'react-hook-form';
import type { ApplicationFormData } from '../../../types/application';
import { Input, Select } from '../../ui';
import { BANKS } from '../../../lib/constants';

interface BankDetailsStepProps {
  form: UseFormReturn<ApplicationFormData>;
}

interface BankFormProps {
  prefix?: string;
  label?: string;
  control: Control<ApplicationFormData>;
  register: UseFormRegister<ApplicationFormData>;
  errors: FieldErrors<ApplicationFormData>;
}

// Bank form section - moved outside to avoid recreation on each render
function BankForm({ prefix = '', label = '', control, register, errors }: BankFormProps) {
  const p = prefix ? `${prefix}_` : '';
  const getFieldName = (field: string) => `${p}${field}` as keyof ApplicationFormData;

  return (
    <div className="space-y-4">
      {label && (
        <h3 className="text-lg font-semibold text-primary-500 border-b border-dark-border pb-2">
          {label}
        </h3>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Bank Name */}
        <Controller
          name={getFieldName('bank_name')}
          control={control}
          render={({ field }) => (
            <Select
              label="Bank Name"
              placeholder="Select your bank"
              options={BANKS}
              required
              {...field}
              value={field.value as string || ''}
              error={(errors as Record<string, {message?: string}>)[getFieldName('bank_name')]?.message}
            />
          )}
        />

        {/* Bank Branch */}
        <Input
          label="Bank Branch"
          placeholder="Enter branch name"
          {...register(getFieldName('bank_branch'))}
          error={(errors as Record<string, {message?: string}>)[getFieldName('bank_branch')]?.message}
        />
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Account Number */}
        <Input
          label="Account Number"
          placeholder="Enter 10-digit account number"
          maxLength={10}
          required
          {...register(getFieldName('account_number'))}
          error={(errors as Record<string, {message?: string}>)[getFieldName('account_number')]?.message}
          hint="Must be exactly 10 digits"
        />

        {/* Sort Code */}
        <Input
          label="Sort Code"
          placeholder="Enter sort code"
          {...register(getFieldName('sort_code'))}
          error={(errors as Record<string, {message?: string}>)[getFieldName('sort_code')]?.message}
        />
      </div>

      {/* BVN */}
      <Input
        label="BVN (Bank Verification Number)"
        placeholder="Enter 11-digit BVN"
        maxLength={11}
        {...register(getFieldName('bvn'))}
        error={(errors as Record<string, {message?: string}>)[getFieldName('bvn')]?.message}
        hint="Must be exactly 11 digits"
      />
    </div>
  );
}

export function BankDetailsStep({ form }: BankDetailsStepProps) {
  const {
    register,
    control,
    watch,
    formState: { errors },
  } = form;

  const applicantType = watch('applicant_type');
  const isJoint = applicantType === 'Joint';

  return (
    <div className="space-y-6">
      <div className="text-center mb-8">
        <h2 className="text-2xl font-semibold text-dark-text mb-2">
          Bank Account Details
        </h2>
        <p className="text-dark-text-secondary">
          Enter the bank account details where bond interest payments will be credited.
        </p>
      </div>

      {/* Info box */}
      <div className="card bg-primary-900/10 border-primary-700">
        <div className="flex gap-3">
          <svg
            className="w-5 h-5 text-primary-500 flex-shrink-0 mt-0.5"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
            />
          </svg>
          <div>
            <p className="text-sm text-dark-text">
              <strong>Important:</strong> Ensure the account details are correct. All quarterly
              interest payments and principal at maturity will be credited to this account.
            </p>
          </div>
        </div>
      </div>

      {/* Primary Bank Details */}
      <BankForm
        label={isJoint ? "Primary Applicant's Bank Details" : undefined}
        control={control}
        register={register}
        errors={errors}
      />

      {/* Joint Applicant Bank Details */}
      {isJoint && (
        <BankForm
          prefix="joint"
          label="Joint Applicant's Bank Details"
          control={control}
          register={register}
          errors={errors}
        />
      )}
    </div>
  );
}
