/**
 * Step 3: Applicant Information - Enter personal/company details.
 */

import { Controller, type UseFormReturn, type Control, type FieldErrors, type UseFormRegister } from 'react-hook-form';
import type { ApplicationFormData } from '../../../types/application';
import { Input, Select, Textarea } from '../../ui';
import { TITLES } from '../../../lib/constants';

interface ApplicantInfoStepProps {
  form: UseFormReturn<ApplicationFormData>;
}

interface IndividualFormProps {
  prefix?: string;
  label?: string;
  control: Control<ApplicationFormData>;
  register: UseFormRegister<ApplicationFormData>;
  errors: FieldErrors<ApplicationFormData>;
}

interface CorporateFormProps {
  register: UseFormRegister<ApplicationFormData>;
  errors: FieldErrors<ApplicationFormData>;
}

// Individual or Joint applicant form - moved outside to avoid recreation on each render
function IndividualForm({ prefix = '', label = '', control, register, errors }: IndividualFormProps) {
  const p = prefix ? `${prefix}_` : '';
  const getFieldName = (field: string) => `${p}${field}` as keyof ApplicationFormData;

  return (
    <div className="space-y-4">
      {label && (
        <h3 className="text-lg font-semibold text-primary-500 border-b border-dark-border pb-2">
          {label}
        </h3>
      )}

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        {/* Title */}
        <Controller
          name={getFieldName('title')}
          control={control}
          render={({ field }) => (
            <Select
              label="Title"
              placeholder="Select"
              options={TITLES}
              required
              {...field}
              value={field.value as string || ''}
              error={(errors as Record<string, {message?: string}>)[getFieldName('title')]?.message}
            />
          )}
        />

        {/* Full Name */}
        <div className="md:col-span-3">
          <Input
            label="Full Name (as it appears on official documents)"
            placeholder="Enter full name"
            required
            {...register(getFieldName('full_name'))}
            error={(errors as Record<string, {message?: string}>)[getFieldName('full_name')]?.message}
          />
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Date of Birth */}
        <Input
          type="date"
          label="Date of Birth"
          required
          {...register(getFieldName('date_of_birth'))}
          error={(errors as Record<string, {message?: string}>)[getFieldName('date_of_birth')]?.message}
        />

        {/* Phone Number */}
        <Input
          label="Phone Number"
          placeholder="e.g., 08012345678"
          required
          {...register(getFieldName('phone_number'))}
          error={(errors as Record<string, {message?: string}>)[getFieldName('phone_number')]?.message}
          hint="Nigerian format: 080XXXXXXXX"
        />
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Email */}
        <Input
          type="email"
          label="Email Address"
          placeholder="email@example.com"
          required
          {...register(getFieldName('email'))}
          error={(errors as Record<string, {message?: string}>)[getFieldName('email')]?.message}
        />

        {/* Occupation */}
        <Input
          label="Occupation"
          placeholder="Enter occupation"
          {...register(getFieldName('occupation'))}
          error={(errors as Record<string, {message?: string}>)[getFieldName('occupation')]?.message}
        />
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Passport/ID Number */}
        <Input
          label="Passport/ID Number"
          placeholder="Enter passport or ID number"
          {...register(getFieldName('passport_no'))}
          error={(errors as Record<string, {message?: string}>)[getFieldName('passport_no')]?.message}
        />

        {/* Next of Kin */}
        <Input
          label="Next of Kin"
          placeholder="Enter next of kin name"
          required
          {...register(getFieldName('next_of_kin'))}
          error={(errors as Record<string, {message?: string}>)[getFieldName('next_of_kin')]?.message}
        />
      </div>

      {/* Only show for primary applicant */}
      {!prefix && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {/* Mother's Maiden Name */}
          <Input
            label="Mother's Maiden Name"
            placeholder="Enter mother's maiden name"
            {...register('mothers_maiden_name')}
            error={errors.mothers_maiden_name?.message}
          />

          {/* CSCS Number */}
          <Input
            label="CSCS Number"
            placeholder="Enter CSCS number (if available)"
            {...register('cscs_number')}
            error={errors.cscs_number?.message}
          />
        </div>
      )}

      {/* CHN Number (only for primary) */}
      {!prefix && (
        <Input
          label="CHN Number"
          placeholder="Enter CHN number (if available)"
          {...register('chn_number')}
          error={errors.chn_number?.message}
        />
      )}

      {/* Address */}
      <Textarea
        label="Residential Address"
        placeholder="Enter full residential address"
        required
        {...register(getFieldName('address'))}
        error={(errors as Record<string, {message?: string}>)[getFieldName('address')]?.message}
      />
    </div>
  );
}

// Corporate applicant form - moved outside to avoid recreation on each render
function CorporateForm({ register, errors }: CorporateFormProps) {
  return (
    <div className="space-y-4">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Company Name */}
        <Input
          label="Company Name"
          placeholder="Enter company name"
          required
          {...register('company_name')}
          error={errors.company_name?.message}
        />

        {/* RC Number */}
        <Input
          label="RC Number"
          placeholder="Enter RC registration number"
          required
          {...register('rc_number')}
          error={errors.rc_number?.message}
        />
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Business Type */}
        <Input
          label="Type of Business"
          placeholder="e.g., Manufacturing, Trading"
          required
          {...register('business_type')}
          error={errors.business_type?.message}
        />

        {/* Contact Person */}
        <Input
          label="Contact Person"
          placeholder="Enter contact person name"
          required
          {...register('contact_person')}
          error={errors.contact_person?.message}
        />
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Phone Number */}
        <Input
          label="Phone Number"
          placeholder="e.g., 08012345678"
          required
          {...register('corp_phone_number')}
          error={errors.corp_phone_number?.message}
          hint="Nigerian format: 080XXXXXXXX"
        />

        {/* Email */}
        <Input
          type="email"
          label="Email Address"
          placeholder="company@example.com"
          required
          {...register('corp_email')}
          error={errors.corp_email?.message}
        />
      </div>

      {/* Passport/ID Number */}
      <Input
        label="Contact Person Passport/ID Number"
        placeholder="Enter passport or ID number"
        {...register('corp_passport_no')}
        error={errors.corp_passport_no?.message}
      />
    </div>
  );
}

export function ApplicantInfoStep({ form }: ApplicantInfoStepProps) {
  const {
    register,
    control,
    watch,
    formState: { errors },
  } = form;

  const applicantType = watch('applicant_type');

  return (
    <div className="space-y-6">
      <div className="text-center mb-8">
        <h2 className="text-2xl font-semibold text-dark-text mb-2">
          {applicantType === 'Corporate' ? 'Company Information' : 'Applicant Information'}
        </h2>
        <p className="text-dark-text-secondary">
          {applicantType === 'Corporate'
            ? 'Enter the company details for the subscription.'
            : applicantType === 'Joint'
            ? 'Enter details for both applicants.'
            : 'Enter your personal details as they appear on official documents.'}
        </p>
      </div>

      {applicantType === 'Corporate' ? (
        <CorporateForm register={register} errors={errors} />
      ) : applicantType === 'Joint' ? (
        <>
          <IndividualForm label="Primary Applicant" control={control} register={register} errors={errors} />
          <IndividualForm prefix="joint" label="Joint Applicant" control={control} register={register} errors={errors} />
        </>
      ) : (
        <IndividualForm control={control} register={register} errors={errors} />
      )}
    </div>
  );
}
