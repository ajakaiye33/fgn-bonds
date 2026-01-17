/**
 * Step 1: Bond Details - Select tenor, month of offer, and bond value.
 */

import { Controller, type UseFormReturn } from 'react-hook-form';
import type { ApplicationFormData } from '../../../types/application';
import { RadioGroup, Select, CurrencyInput } from '../../ui';
import { formatMoneyInWords } from '../../../lib/utils';
import { MONTHS, TENORS, BOND_VALUE_MIN, BOND_VALUE_MAX } from '../../../lib/constants';

interface BondDetailsStepProps {
  form: UseFormReturn<ApplicationFormData>;
}

export function BondDetailsStep({ form }: BondDetailsStepProps) {
  const {
    control,
    watch,
    setValue,
    formState: { errors },
  } = form;

  const bondValue = watch('bond_value');

  // Update amount in words when bond value changes
  const handleBondValueChange = (value: number) => {
    setValue('bond_value', value);
    if (value > 0) {
      setValue('amount_in_words', formatMoneyInWords(value));
    } else {
      setValue('amount_in_words', '');
    }
  };

  return (
    <div className="space-y-6">
      <div className="text-center mb-8">
        <h2 className="text-2xl font-semibold text-dark-text mb-2">
          FGN Savings Bond Subscription
        </h2>
        <p className="text-dark-text-secondary">
          Select the bond tenor, month of offer, and enter the subscription amount.
        </p>
      </div>

      {/* Tenor Selection */}
      <Controller
        name="tenor"
        control={control}
        render={({ field }) => (
          <RadioGroup
            label="Bond Tenor"
            name="tenor"
            value={field.value}
            onChange={field.onChange}
            required
            size="lg"
            options={TENORS.map((tenor) => ({
              value: tenor,
              label: tenor,
              description:
                tenor === '2-Year'
                  ? 'Interest paid quarterly, matures in 2 years'
                  : 'Interest paid quarterly, matures in 3 years',
            }))}
            error={errors.tenor?.message}
          />
        )}
      />

      {/* Month of Offer */}
      <Controller
        name="month_of_offer"
        control={control}
        render={({ field }) => (
          <Select
            label="Month of Offer"
            placeholder="Select the month of offer"
            options={MONTHS}
            required
            {...field}
            error={errors.month_of_offer?.message}
          />
        )}
      />

      {/* Bond Value */}
      <Controller
        name="bond_value"
        control={control}
        render={({ field }) => (
          <CurrencyInput
            label="Bond Value (Subscription Amount)"
            value={field.value}
            onChange={handleBondValueChange}
            min={BOND_VALUE_MIN}
            max={BOND_VALUE_MAX}
            required
            hint="Enter the amount you wish to subscribe"
            error={errors.bond_value?.message}
          />
        )}
      />

      {/* Amount in Words */}
      {bondValue > 0 && (
        <div className="card bg-dark-elevated/50">
          <label className="label">Amount in Words</label>
          <p className="text-primary-500 font-medium">
            {formatMoneyInWords(bondValue)} Only
          </p>
        </div>
      )}
    </div>
  );
}
