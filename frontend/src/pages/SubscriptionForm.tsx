/**
 * FGN Savings Bond Subscription Form - Multi-Step Wizard
 *
 * A 7-step wizard for submitting Federal Government of Nigeria
 * Savings Bond applications.
 *
 * @author Hedgar Ajakaiye
 * @license MIT
 */

import { useState } from 'react';
import { FormWizard } from '../components/wizard';
import { publicApi } from '../services/api';
import { Button } from '../components/ui';

export function SubscriptionForm() {
  const [submittedId, setSubmittedId] = useState<number | null>(null);
  const [isDownloading, setIsDownloading] = useState(false);

  const handleSuccess = (applicationId: number) => {
    setSubmittedId(applicationId);
  };

  const handleDownloadPdf = async () => {
    if (!submittedId) return;

    setIsDownloading(true);
    try {
      const blob = await publicApi.downloadPdf(submittedId);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `fgn_bond_application_${submittedId}.pdf`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (error) {
      console.error('Failed to download PDF:', error);
      alert('Failed to download PDF. Please try again.');
    } finally {
      setIsDownloading(false);
    }
  };

  const handleNewApplication = () => {
    setSubmittedId(null);
  };

  // Success state
  if (submittedId) {
    return (
      <div className="min-h-screen bg-dark-bg">
        <Header />
        <main className="max-w-2xl mx-auto px-4 py-12">
          <div className="card text-center">
            {/* Success icon */}
            <div className="w-20 h-20 mx-auto mb-6 rounded-full bg-primary-500 flex items-center justify-center">
              <svg
                className="w-10 h-10 text-white"
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
            </div>

            <h1 className="text-2xl font-bold text-dark-text mb-2">
              Application Submitted Successfully!
            </h1>
            <p className="text-dark-text-secondary mb-6">
              Your FGN Savings Bond application has been submitted.
              <br />
              Application Reference: <span className="font-semibold text-primary-500">#{submittedId}</span>
            </p>

            <div className="space-y-4">
              <Button
                variant="primary"
                size="lg"
                onClick={handleDownloadPdf}
                isLoading={isDownloading}
                className="w-full"
              >
                <svg
                  className="w-5 h-5 mr-2"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                  />
                </svg>
                Download Application PDF
              </Button>

              <Button
                variant="secondary"
                size="lg"
                onClick={handleNewApplication}
                className="w-full"
              >
                Submit Another Application
              </Button>
            </div>

            <div className="mt-8 p-4 bg-primary-900/10 border border-primary-700 rounded-lg text-left">
              <h3 className="font-semibold text-dark-text mb-2">What's Next?</h3>
              <ul className="text-sm text-dark-text-secondary space-y-2">
                <li className="flex items-start gap-2">
                  <span className="text-primary-500">1.</span>
                  Download and print the PDF application form
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-primary-500">2.</span>
                  Sign the form in the designated areas
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-primary-500">3.</span>
                  Submit to your bank or stockbroker with payment
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-primary-500">4.</span>
                  Keep a copy for your records
                </li>
              </ul>
            </div>
          </div>
        </main>
        <Footer />
      </div>
    );
  }

  // Form state
  return (
    <div className="min-h-screen bg-dark-bg">
      <Header />
      <main className="max-w-6xl mx-auto px-4 py-8">
        <FormWizard onSuccess={handleSuccess} />
      </main>
      <Footer />
    </div>
  );
}

// Header component
function Header() {
  return (
    <header className="bg-dark-surface border-b border-dark-border">
      <div className="max-w-6xl mx-auto px-4 py-4">
        <div className="flex items-center gap-4">
          {/* DMO Logo placeholder */}
          <div className="w-12 h-12 bg-primary-900 rounded-lg flex items-center justify-center">
            <span className="text-white font-bold text-lg">FGN</span>
          </div>
          <div>
            <h1 className="text-xl font-bold text-dark-text">
              FGN Savings Bond
            </h1>
            <p className="text-sm text-dark-text-secondary">
              Debt Management Office - Subscription Form
            </p>
          </div>
        </div>
      </div>
    </header>
  );
}

// Footer component
function Footer() {
  return (
    <footer className="bg-dark-surface border-t border-dark-border mt-auto">
      <div className="max-w-6xl mx-auto px-4 py-6">
        <div className="text-center text-sm text-dark-text-secondary">
          <p>
            &copy; {new Date().getFullYear()} Debt Management Office (DMO),
            Federal Republic of Nigeria
          </p>
          <p className="mt-1">
            For enquiries, please contact your bank or stockbroker
          </p>
        </div>
      </div>
    </footer>
  );
}
