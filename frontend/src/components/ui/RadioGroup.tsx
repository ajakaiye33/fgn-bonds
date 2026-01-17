/**
 * Radio group component for single selection.
 */

import { cn } from '../../lib/utils';

export interface RadioOption {
  value: string;
  label: string;
  description?: string;
}

export interface RadioGroupProps {
  label?: string;
  error?: string;
  options: RadioOption[];
  value?: string;
  onChange: (value: string) => void;
  name: string;
  required?: boolean;
  orientation?: 'horizontal' | 'vertical';
  size?: 'sm' | 'md' | 'lg';
}

export function RadioGroup({
  label,
  error,
  options,
  value,
  onChange,
  name,
  required,
  orientation = 'vertical',
  size = 'md',
}: RadioGroupProps) {
  return (
    <div className="w-full">
      {label && (
        <label className="label">
          {label}
          {required && <span className="text-error ml-1">*</span>}
        </label>
      )}
      <div
        className={cn(
          orientation === 'horizontal'
            ? 'flex flex-wrap gap-4'
            : 'space-y-3'
        )}
      >
        {options.map((option) => (
          <label
            key={option.value}
            className={cn(
              'flex items-start gap-3 cursor-pointer group',
              size === 'lg' &&
                'p-4 rounded-lg border-2 transition-all duration-200',
              size === 'lg' && value === option.value
                ? 'border-primary-500 bg-primary-900/20'
                : size === 'lg' && 'border-dark-border hover:border-primary-700'
            )}
          >
            <input
              type="radio"
              name={name}
              value={option.value}
              checked={value === option.value}
              onChange={(e) => onChange(e.target.value)}
              className={cn(
                'mt-0.5 h-5 w-5 border-dark-border bg-dark-elevated',
                'text-primary-500 focus:ring-primary-500 focus:ring-offset-dark-bg'
              )}
            />
            <div className="flex-1">
              <span
                className={cn(
                  'font-medium text-dark-text',
                  size === 'sm' && 'text-sm',
                  size === 'lg' && 'text-lg'
                )}
              >
                {option.label}
              </span>
              {option.description && (
                <p className="text-xs text-dark-text-secondary mt-1">
                  {option.description}
                </p>
              )}
            </div>
          </label>
        ))}
      </div>
      {error && <p className="error-message mt-2">{error}</p>}
    </div>
  );
}
