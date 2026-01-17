/**
 * Step 5: Classification - Select residency status and investor category.
 */

import { Controller, type UseFormReturn } from 'react-hook-form';
import type { ApplicationFormData } from '../../../types/application';
import { RadioGroup, CheckboxGroup } from '../../ui';
import { INVESTOR_CATEGORIES } from '../../../lib/constants';

interface ClassificationStepProps {
  form: UseFormReturn<ApplicationFormData>;
}

export function ClassificationStep({ form }: ClassificationStepProps) {
  const {
    control,
    formState: { errors },
  } = form;

  return (
    <div className="space-y-8">
      <div className="text-center mb-8">
        <h2 className="text-2xl font-semibold text-dark-text mb-2">
          Investor Classification
        </h2>
        <p className="text-dark-text-secondary">
          Indicate your residency status and select your investor category.
        </p>
      </div>

      {/* Residency Status */}
      <div className="card">
        <h3 className="text-lg font-semibold text-dark-text mb-4">
          Residency Status
        </h3>
        <Controller
          name="is_resident"
          control={control}
          render={({ field }) => (
            <RadioGroup
              name="is_resident"
              value={field.value === true ? 'true' : field.value === false ? 'false' : undefined}
              onChange={(val) => field.onChange(val === 'true')}
              required
              orientation="horizontal"
              options={[
                {
                  value: 'true',
                  label: 'Resident',
                  description: 'Currently residing in Nigeria',
                },
                {
                  value: 'false',
                  label: 'Non-Resident',
                  description: 'Living outside Nigeria',
                },
              ]}
              error={errors.is_resident?.message}
            />
          )}
        />
      </div>

      {/* Investor Category */}
      <div className="card">
        <h3 className="text-lg font-semibold text-dark-text mb-4">
          Investor Category
        </h3>
        <p className="text-sm text-dark-text-secondary mb-4">
          Select all categories that apply to you.
        </p>
        <Controller
          name="investor_category"
          control={control}
          render={({ field }) => (
            <CheckboxGroup
              options={INVESTOR_CATEGORIES.map((cat) => ({
                value: cat,
                label: cat,
              }))}
              value={field.value || []}
              onChange={field.onChange}
              required
              error={errors.investor_category?.message}
            />
          )}
        />
      </div>
    </div>
  );
}
