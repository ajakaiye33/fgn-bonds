/**
 * Reusable select component with validation support.
 */

import { forwardRef, type SelectHTMLAttributes } from 'react';
import { cn } from '../../lib/utils';

export interface SelectOption {
  value: string;
  label: string;
}

export interface SelectProps extends SelectHTMLAttributes<HTMLSelectElement> {
  label?: string;
  error?: string;
  hint?: string;
  options: SelectOption[] | string[];
  placeholder?: string;
}

export const Select = forwardRef<HTMLSelectElement, SelectProps>(
  ({ className, label, error, hint, options, placeholder, id, ...props }, ref) => {
    const selectId = id || props.name;

    // Normalize options to SelectOption format
    const normalizedOptions: SelectOption[] = options.map((opt) =>
      typeof opt === 'string' ? { value: opt, label: opt } : opt
    );

    return (
      <div className="w-full">
        {label && (
          <label htmlFor={selectId} className="label">
            {label}
            {props.required && <span className="text-error ml-1">*</span>}
          </label>
        )}
        <select
          id={selectId}
          ref={ref}
          className={cn('select', error && 'input-error', className)}
          {...props}
        >
          {placeholder && (
            <option value="" disabled>
              {placeholder}
            </option>
          )}
          {normalizedOptions.map((option) => (
            <option key={option.value} value={option.value}>
              {option.label}
            </option>
          ))}
        </select>
        {hint && !error && (
          <p className="text-xs text-dark-text-secondary mt-1">{hint}</p>
        )}
        {error && <p className="error-message">{error}</p>}
      </div>
    );
  }
);

Select.displayName = 'Select';
