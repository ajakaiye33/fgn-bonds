/**
 * Step progress indicator for the form wizard.
 */

import { WIZARD_STEPS } from '../../types/application';
import { cn } from '../../lib/utils';

interface StepProgressProps {
  currentStep: number;
  onStepClick?: (step: number) => void;
  allowNavigation?: boolean;
}

export function StepProgress({
  currentStep,
  onStepClick,
  allowNavigation = false,
}: StepProgressProps) {
  return (
    <div className="w-full py-6">
      {/* Desktop view */}
      <div className="hidden md:flex items-center justify-between">
        {WIZARD_STEPS.map((step, index) => (
          <div key={step.id} className="flex items-center flex-1">
            {/* Step indicator */}
            <div className="flex flex-col items-center">
              <button
                type="button"
                onClick={() => allowNavigation && onStepClick?.(index)}
                disabled={!allowNavigation || index > currentStep}
                className={cn(
                  'step-indicator',
                  index === currentStep && 'step-indicator-active',
                  index < currentStep && 'step-indicator-completed',
                  index > currentStep && 'step-indicator-pending',
                  allowNavigation && index <= currentStep && 'cursor-pointer hover:scale-110'
                )}
              >
                {index < currentStep ? (
                  <svg
                    className="w-5 h-5"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M5 13l4 4L19 7"
                    />
                  </svg>
                ) : (
                  index + 1
                )}
              </button>
              <span
                className={cn(
                  'mt-2 text-xs font-medium text-center max-w-[80px]',
                  index === currentStep
                    ? 'text-primary-500'
                    : index < currentStep
                    ? 'text-primary-700'
                    : 'text-dark-text-secondary'
                )}
              >
                {step.title}
              </span>
            </div>

            {/* Connector line */}
            {index < WIZARD_STEPS.length - 1 && (
              <div
                className={cn(
                  'flex-1 h-0.5 mx-2',
                  index < currentStep ? 'bg-primary-500' : 'bg-dark-border'
                )}
              />
            )}
          </div>
        ))}
      </div>

      {/* Mobile view - compact */}
      <div className="md:hidden">
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm text-dark-text-secondary">
            Step {currentStep + 1} of {WIZARD_STEPS.length}
          </span>
          <span className="text-sm font-medium text-primary-500">
            {WIZARD_STEPS[currentStep].title}
          </span>
        </div>
        <div className="w-full bg-dark-border rounded-full h-2">
          <div
            className="bg-primary-500 h-2 rounded-full transition-all duration-300"
            style={{
              width: `${((currentStep + 1) / WIZARD_STEPS.length) * 100}%`,
            }}
          />
        </div>
        <p className="mt-2 text-xs text-dark-text-secondary">
          {WIZARD_STEPS[currentStep].description}
        </p>
      </div>
    </div>
  );
}
