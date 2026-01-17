/**
 * Reusable input components with validation support.
 */

import { forwardRef, type InputHTMLAttributes } from 'react';
import { cn } from '../../lib/utils';

export interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
  hint?: string;
}

export const Input = forwardRef<HTMLInputElement, InputProps>(
  ({ className, label, error, hint, id, ...props }, ref) => {
    const inputId = id || props.name;

    return (
      <div className="w-full">
        {label && (
          <label htmlFor={inputId} className="label">
            {label}
            {props.required && <span className="text-error ml-1">*</span>}
          </label>
        )}
        <input
          id={inputId}
          ref={ref}
          className={cn('input', error && 'input-error', className)}
          {...props}
        />
        {hint && !error && (
          <p className="text-xs text-dark-text-secondary mt-1">{hint}</p>
        )}
        {error && <p className="error-message">{error}</p>}
      </div>
    );
  }
);

Input.displayName = 'Input';
