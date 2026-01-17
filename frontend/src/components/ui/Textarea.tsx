/**
 * Textarea component with validation support.
 */

import { forwardRef, type TextareaHTMLAttributes } from 'react';
import { cn } from '../../lib/utils';

export interface TextareaProps extends TextareaHTMLAttributes<HTMLTextAreaElement> {
  label?: string;
  error?: string;
  hint?: string;
}

export const Textarea = forwardRef<HTMLTextAreaElement, TextareaProps>(
  ({ className, label, error, hint, id, ...props }, ref) => {
    const textareaId = id || props.name;

    return (
      <div className="w-full">
        {label && (
          <label htmlFor={textareaId} className="label">
            {label}
            {props.required && <span className="text-error ml-1">*</span>}
          </label>
        )}
        <textarea
          id={textareaId}
          ref={ref}
          className={cn(
            'input min-h-[100px] resize-y',
            error && 'input-error',
            className
          )}
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

Textarea.displayName = 'Textarea';
