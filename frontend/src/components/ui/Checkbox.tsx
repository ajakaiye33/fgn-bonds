/**
 * Checkbox component with label.
 */

import { forwardRef, type InputHTMLAttributes } from 'react';
import { cn } from '../../lib/utils';

export interface CheckboxProps extends Omit<InputHTMLAttributes<HTMLInputElement>, 'type'> {
  label?: string;
  error?: string;
  description?: string;
}

export const Checkbox = forwardRef<HTMLInputElement, CheckboxProps>(
  ({ className, label, error, description, id, ...props }, ref) => {
    const inputId = id || props.name;

    return (
      <div className="w-full">
        <label
          htmlFor={inputId}
          className={cn(
            'flex items-start gap-3 cursor-pointer',
            props.disabled && 'cursor-not-allowed opacity-50'
          )}
        >
          <input
            type="checkbox"
            id={inputId}
            ref={ref}
            className={cn(
              'mt-1 h-5 w-5 rounded border-dark-border bg-dark-elevated',
              'text-primary-500 focus:ring-primary-500 focus:ring-offset-dark-bg',
              error && 'border-error',
              className
            )}
            {...props}
          />
          <div>
            {label && (
              <span className="text-sm font-medium text-dark-text">{label}</span>
            )}
            {description && (
              <p className="text-xs text-dark-text-secondary mt-1">{description}</p>
            )}
          </div>
        </label>
        {error && <p className="error-message mt-1">{error}</p>}
      </div>
    );
  }
);

Checkbox.displayName = 'Checkbox';

// Multi-select checkbox group
export interface CheckboxGroupProps {
  label?: string;
  error?: string;
  options: { value: string; label: string; description?: string }[];
  value: string[];
  onChange: (value: string[]) => void;
  required?: boolean;
}

export function CheckboxGroup({
  label,
  error,
  options,
  value,
  onChange,
  required,
}: CheckboxGroupProps) {
  const handleChange = (optionValue: string, checked: boolean) => {
    if (checked) {
      onChange([...value, optionValue]);
    } else {
      onChange(value.filter((v) => v !== optionValue));
    }
  };

  return (
    <div className="w-full">
      {label && (
        <label className="label">
          {label}
          {required && <span className="text-error ml-1">*</span>}
        </label>
      )}
      <div className="space-y-3">
        {options.map((option) => (
          <Checkbox
            key={option.value}
            label={option.label}
            description={option.description}
            checked={value.includes(option.value)}
            onChange={(e) => handleChange(option.value, e.target.checked)}
          />
        ))}
      </div>
      {error && <p className="error-message mt-2">{error}</p>}
    </div>
  );
}
