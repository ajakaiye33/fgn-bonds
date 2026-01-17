/**
 * Currency input with Naira formatting.
 */

import { forwardRef, useState, type ChangeEvent } from 'react';
import { cn, formatCurrency } from '../../lib/utils';

export interface CurrencyInputProps {
  label?: string;
  error?: string;
  hint?: string;
  value?: number;
  onChange?: (value: number) => void;
  min?: number;
  max?: number;
  required?: boolean;
  name?: string;
  id?: string;
  className?: string;
  disabled?: boolean;
}

export const CurrencyInput = forwardRef<HTMLInputElement, CurrencyInputProps>(
  (
    {
      label,
      error,
      hint,
      value,
      onChange,
      min = 5000,
      max = 50000000,
      required,
      name,
      id,
      className,
      disabled,
    },
    ref
  ) => {
    const inputId = id || name;
    const [isFocused, setIsFocused] = useState(false);
    const [editingValue, setEditingValue] = useState('');

    // Compute display value: when focused show raw editing value, otherwise show formatted
    const displayValue = isFocused
      ? editingValue
      : value !== undefined
        ? formatCurrency(value)
        : '';

    const handleFocus = () => {
      setIsFocused(true);
      setEditingValue(value !== undefined ? value.toString() : '');
    };

    const handleBlur = () => {
      setIsFocused(false);
    };

    const handleChange = (e: ChangeEvent<HTMLInputElement>) => {
      const rawValue = e.target.value.replace(/[^0-9]/g, '');
      setEditingValue(rawValue);

      const numericValue = parseInt(rawValue, 10);
      if (!isNaN(numericValue)) {
        onChange?.(numericValue);
      } else {
        onChange?.(0);
      }
    };

    return (
      <div className="w-full">
        {label && (
          <label htmlFor={inputId} className="label">
            {label}
            {required && <span className="text-error ml-1">*</span>}
          </label>
        )}
        <div className="relative">
          <span className="absolute left-4 top-1/2 -translate-y-1/2 text-dark-text-secondary">
            ₦
          </span>
          <input
            ref={ref}
            type="text"
            inputMode="numeric"
            id={inputId}
            name={name}
            value={displayValue}
            onChange={handleChange}
            onFocus={handleFocus}
            onBlur={handleBlur}
            disabled={disabled}
            className={cn(
              'input pl-8 currency-input',
              error && 'input-error',
              className
            )}
          />
        </div>
        {hint && !error && (
          <p className="text-xs text-dark-text-secondary mt-1">
            {hint} (Min: {formatCurrency(min)}, Max: {formatCurrency(max)})
          </p>
        )}
        {error && <p className="error-message">{error}</p>}
      </div>
    );
  }
);

CurrencyInput.displayName = 'CurrencyInput';
