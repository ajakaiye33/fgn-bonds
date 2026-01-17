/**
 * Step 6: Distribution Agent - Enter agent details and optional witness.
 */

import { Controller, type UseFormReturn } from 'react-hook-form';
import type { ApplicationFormData } from '../../../types/application';
import { Input, Textarea, Checkbox } from '../../ui';

interface DistributionStepProps {
  form: UseFormReturn<ApplicationFormData>;
}

export function DistributionStep({ form }: DistributionStepProps) {
  const {
    register,
    control,
    watch,
    formState: { errors },
  } = form;

  const needsWitness = watch('needs_witness');

  return (
    <div className="space-y-6">
      <div className="text-center mb-8">
        <h2 className="text-2xl font-semibold text-dark-text mb-2">
          Distribution Agent
        </h2>
        <p className="text-dark-text-secondary">
          Enter the details of your distribution agent or stockbroker (optional).
        </p>
      </div>

      {/* Agent Details */}
      <div className="card">
        <h3 className="text-lg font-semibold text-dark-text mb-4">
          Stockbroker/Agent Information
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <Input
            label="Agent/Stockbroker Name"
            placeholder="Enter agent or stockbroker name"
            {...register('agent_name')}
            error={errors.agent_name?.message}
          />
          <Input
            label="Stockbroker Code"
            placeholder="Enter stockbroker code (if any)"
            {...register('stockbroker_code')}
            error={errors.stockbroker_code?.message}
          />
        </div>
        <p className="text-xs text-dark-text-secondary mt-2">
          If you don't have a stockbroker, you can leave these fields blank.
        </p>
      </div>

      {/* Witness Section */}
      <div className="card">
        <h3 className="text-lg font-semibold text-dark-text mb-4">
          Witness (Optional)
        </h3>
        <p className="text-sm text-dark-text-secondary mb-4">
          A witness may be required for certain subscription amounts. Check the box below
          if you need to add a witness.
        </p>

        <Controller
          name="needs_witness"
          control={control}
          render={({ field }) => (
            <Checkbox
              label="I need a witness for this subscription"
              checked={field.value}
              onChange={(e) => field.onChange(e.target.checked)}
            />
          )}
        />

        {needsWitness && (
          <div className="mt-6 space-y-4 border-t border-dark-border pt-6">
            <Input
              label="Witness Name"
              placeholder="Enter witness full name"
              required={needsWitness}
              {...register('witness_name')}
              error={errors.witness_name?.message}
            />

            <Textarea
              label="Witness Address"
              placeholder="Enter witness address"
              {...register('witness_address')}
              error={errors.witness_address?.message}
            />

            <Controller
              name="witness_acknowledged"
              control={control}
              render={({ field }) => (
                <Checkbox
                  label="I confirm that the witness has acknowledged this subscription"
                  checked={field.value}
                  onChange={(e) => field.onChange(e.target.checked)}
                  error={errors.witness_acknowledged?.message}
                />
              )}
            />
          </div>
        )}
      </div>
    </div>
  );
}
