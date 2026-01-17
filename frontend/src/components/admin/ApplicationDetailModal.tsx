/**
 * Application Detail Modal
 *
 * Shows full application details and payment management interface.
 */

import { useState, useEffect } from 'react';
import { adminApi, publicApi } from '../../services/api';
import { Button, Input, Select, Textarea } from '../ui';
import { formatCurrency } from '../../lib/utils';
import type {
  ApplicationResponse,
  Payment,
  PaymentCreate,
  PaymentDocument,
} from '../../types/application';
import { DocumentUpload } from './DocumentUpload';

interface ApplicationDetailModalProps {
  applicationId: number | null;
  onClose: () => void;
  onPaymentUpdated: () => void;
}

const PAYMENT_METHODS = [
  { value: 'bank_transfer', label: 'Bank Transfer' },
  { value: 'cheque', label: 'Cheque' },
  { value: 'cash', label: 'Cash' },
  { value: 'pos', label: 'POS' },
  { value: 'other', label: 'Other' },
];

const PAYMENT_STATUS_STYLES: Record<string, string> = {
  pending: 'bg-gray-600/30 text-gray-400',
  paid: 'bg-yellow-900/30 text-yellow-400',
  verified: 'bg-green-900/30 text-green-400',
  rejected: 'bg-red-900/30 text-red-400',
};

export function ApplicationDetailModal({
  applicationId,
  onClose,
  onPaymentUpdated,
}: ApplicationDetailModalProps) {
  const [application, setApplication] = useState<ApplicationResponse | null>(null);
  const [payment, setPayment] = useState<Payment | null>(null);
  const [documents, setDocuments] = useState<PaymentDocument[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Payment form state
  const [showPaymentForm, setShowPaymentForm] = useState(false);
  const [paymentForm, setPaymentForm] = useState<PaymentCreate>({
    amount: 0,
    payment_method: 'bank_transfer',
    payment_reference: '',
    payment_date: new Date().toISOString().split('T')[0],
    receiving_bank: '',
    notes: '',
  });
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Verify/Reject state
  const [showRejectDialog, setShowRejectDialog] = useState(false);
  const [rejectionReason, setRejectionReason] = useState('');

  useEffect(() => {
    if (applicationId) {
      fetchApplicationDetails();
    }
  }, [applicationId]);

  const fetchApplicationDetails = async () => {
    if (!applicationId) return;

    setIsLoading(true);
    setError(null);

    try {
      // Fetch application details using the public API
      const applicationData = await publicApi.getApplication(applicationId);
      setApplication(applicationData);

      // Try to fetch payment
      try {
        const paymentData = await adminApi.getPayment(applicationId);
        setPayment(paymentData);

        // Fetch documents if payment exists
        if (paymentData?.id) {
          const docs = await adminApi.listDocuments(paymentData.id);
          setDocuments(docs);
        }
      } catch {
        // No payment recorded yet
        setPayment(null);
        setDocuments([]);
      }
    } catch (err) {
      setError('Failed to load application details');
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleRecordPayment = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!applicationId) return;

    setIsSubmitting(true);
    try {
      const newPayment = await adminApi.recordPayment(applicationId, paymentForm);
      setPayment(newPayment);
      setShowPaymentForm(false);
      onPaymentUpdated();
    } catch (err) {
      console.error('Failed to record payment:', err);
      setError('Failed to record payment');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleVerifyPayment = async () => {
    if (!payment) return;

    setIsSubmitting(true);
    try {
      const updatedPayment = await adminApi.verifyPayment(payment.id, {
        action: 'verify',
      });
      setPayment(updatedPayment);
      onPaymentUpdated();
    } catch (err) {
      console.error('Failed to verify payment:', err);
      setError('Failed to verify payment');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleRejectPayment = async () => {
    if (!payment || !rejectionReason.trim()) return;

    setIsSubmitting(true);
    try {
      const updatedPayment = await adminApi.verifyPayment(payment.id, {
        action: 'reject',
        rejection_reason: rejectionReason,
      });
      setPayment(updatedPayment);
      setShowRejectDialog(false);
      setRejectionReason('');
      onPaymentUpdated();
    } catch (err) {
      console.error('Failed to reject payment:', err);
      setError('Failed to reject payment');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleDeletePayment = async () => {
    if (!payment || !confirm('Are you sure you want to delete this payment record?')) return;

    setIsSubmitting(true);
    try {
      await adminApi.deletePayment(payment.id);
      setPayment(null);
      setDocuments([]);
      onPaymentUpdated();
    } catch (err) {
      console.error('Failed to delete payment:', err);
      setError('Failed to delete payment');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleDocumentUploaded = async () => {
    if (payment?.id) {
      const docs = await adminApi.listDocuments(payment.id);
      setDocuments(docs);
    }
  };

  const handleDeleteDocument = async (documentId: number) => {
    if (!confirm('Delete this document?')) return;

    try {
      await adminApi.deleteDocument(documentId);
      setDocuments((prev) => prev.filter((d) => d.id !== documentId));
    } catch (err) {
      console.error('Failed to delete document:', err);
    }
  };

  if (!applicationId) return null;

  return (
    <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50 p-4">
      <div className="bg-dark-surface border border-dark-border rounded-lg w-full max-w-4xl max-h-[90vh] overflow-hidden flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-dark-border">
          <h2 className="text-lg font-semibold text-dark-text">
            Application #{applicationId}
          </h2>
          <button
            onClick={onClose}
            className="text-dark-text-secondary hover:text-dark-text p-1"
          >
            <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-4">
          {isLoading ? (
            <div className="flex items-center justify-center py-12">
              <div className="animate-spin w-8 h-8 border-4 border-primary-500 border-t-transparent rounded-full" />
            </div>
          ) : error ? (
            <div className="text-center py-12 text-error">{error}</div>
          ) : application ? (
            <div className="space-y-6">
              {/* Application Info */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <InfoCard title="Bond Details">
                  <InfoRow label="Tenor" value={application.tenor} />
                  <InfoRow label="Month of Offer" value={application.month_of_offer} />
                  <InfoRow label="Bond Value" value={formatCurrency(application.bond_value)} highlight />
                  <InfoRow label="Amount in Words" value={application.amount_in_words} />
                </InfoCard>

                <InfoCard title="Applicant Info">
                  <InfoRow label="Type" value={application.applicant_type} />
                  {application.applicant_type === 'Corporate' ? (
                    <>
                      <InfoRow label="Company" value={application.company_name} />
                      <InfoRow label="RC Number" value={application.rc_number} />
                      <InfoRow label="Contact" value={application.contact_person} />
                      <InfoRow label="Email" value={application.corp_email} />
                    </>
                  ) : (
                    <>
                      <InfoRow label="Name" value={application.full_name} />
                      <InfoRow label="Email" value={application.email} />
                      <InfoRow label="Phone" value={application.phone_number} />
                      <InfoRow label="BVN" value={application.bvn} />
                    </>
                  )}
                </InfoCard>

                <InfoCard title="Bank Details">
                  <InfoRow label="Bank" value={application.bank_name} />
                  <InfoRow label="Branch" value={application.bank_branch} />
                  <InfoRow label="Account No" value={application.account_number} />
                  <InfoRow label="Sort Code" value={application.sort_code} />
                </InfoCard>

                <InfoCard title="Classification">
                  <InfoRow label="Resident" value={application.is_resident ? 'Yes' : 'No'} />
                  <InfoRow label="Category" value={application.investor_category?.join(', ')} />
                  <InfoRow label="Agent" value={application.agent_name} />
                  <InfoRow label="Submission Date" value={new Date(application.submission_date).toLocaleDateString()} />
                </InfoCard>
              </div>

              {/* Payment Section */}
              <div className="border-t border-dark-border pt-6">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-lg font-semibold text-dark-text">Payment Information</h3>
                  <span className={`px-3 py-1 rounded text-sm font-medium ${PAYMENT_STATUS_STYLES[application.payment_status] || PAYMENT_STATUS_STYLES.pending}`}>
                    {application.payment_status.charAt(0).toUpperCase() + application.payment_status.slice(1)}
                  </span>
                </div>

                {payment ? (
                  <div className="space-y-4">
                    {/* Payment Details */}
                    <div className="bg-dark-elevated rounded-lg p-4">
                      <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                        <div>
                          <p className="text-xs text-dark-text-secondary">Amount</p>
                          <p className="text-dark-text font-medium">{formatCurrency(payment.amount)}</p>
                        </div>
                        <div>
                          <p className="text-xs text-dark-text-secondary">Method</p>
                          <p className="text-dark-text capitalize">{payment.payment_method.replace('_', ' ')}</p>
                        </div>
                        <div>
                          <p className="text-xs text-dark-text-secondary">Reference</p>
                          <p className="text-dark-text font-mono text-sm">{payment.payment_reference}</p>
                        </div>
                        <div>
                          <p className="text-xs text-dark-text-secondary">Payment Date</p>
                          <p className="text-dark-text">{new Date(payment.payment_date).toLocaleDateString()}</p>
                        </div>
                        <div>
                          <p className="text-xs text-dark-text-secondary">Receiving Bank</p>
                          <p className="text-dark-text">{payment.receiving_bank || '-'}</p>
                        </div>
                        <div>
                          <p className="text-xs text-dark-text-secondary">Status</p>
                          <p className={`font-medium ${payment.status === 'verified' ? 'text-green-400' : payment.status === 'rejected' ? 'text-red-400' : 'text-yellow-400'}`}>
                            {payment.status.charAt(0).toUpperCase() + payment.status.slice(1)}
                          </p>
                        </div>
                      </div>
                      {payment.notes && (
                        <div className="mt-4 pt-4 border-t border-dark-border">
                          <p className="text-xs text-dark-text-secondary">Notes</p>
                          <p className="text-dark-text text-sm">{payment.notes}</p>
                        </div>
                      )}
                      {payment.rejection_reason && (
                        <div className="mt-4 pt-4 border-t border-dark-border">
                          <p className="text-xs text-error">Rejection Reason</p>
                          <p className="text-error text-sm">{payment.rejection_reason}</p>
                        </div>
                      )}
                    </div>

                    {/* Documents */}
                    <div className="bg-dark-elevated rounded-lg p-4">
                      <h4 className="text-sm font-medium text-dark-text mb-3">Payment Evidence</h4>
                      {documents.length > 0 ? (
                        <ul className="space-y-2">
                          {documents.map((doc) => (
                            <li key={doc.id} className="flex items-center justify-between bg-dark-surface p-2 rounded">
                              <div className="flex items-center gap-2">
                                <svg className="w-4 h-4 text-dark-text-secondary" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
                                </svg>
                                <span className="text-sm text-dark-text">{doc.original_filename}</span>
                                <span className="text-xs text-dark-text-secondary">
                                  ({doc.file_size ? `${(doc.file_size / 1024).toFixed(1)} KB` : 'Unknown size'})
                                </span>
                              </div>
                              <div className="flex items-center gap-2">
                                <a
                                  href={adminApi.getDocumentDownloadUrl(doc.id)}
                                  target="_blank"
                                  rel="noopener noreferrer"
                                  className="text-primary-500 hover:text-primary-400 text-sm"
                                >
                                  Download
                                </a>
                                {payment.status !== 'verified' && (
                                  <button
                                    onClick={() => handleDeleteDocument(doc.id)}
                                    className="text-error hover:text-red-400 text-sm"
                                  >
                                    Delete
                                  </button>
                                )}
                              </div>
                            </li>
                          ))}
                        </ul>
                      ) : (
                        <p className="text-sm text-dark-text-secondary">No documents uploaded</p>
                      )}

                      {payment.status !== 'verified' && (
                        <div className="mt-4">
                          <DocumentUpload
                            paymentId={payment.id}
                            onUploaded={handleDocumentUploaded}
                          />
                        </div>
                      )}
                    </div>

                    {/* Actions */}
                    {payment.status === 'pending' && (
                      <div className="flex gap-3">
                        <Button variant="primary" onClick={handleVerifyPayment} disabled={isSubmitting}>
                          Verify Payment
                        </Button>
                        <Button variant="secondary" onClick={() => setShowRejectDialog(true)} disabled={isSubmitting}>
                          Reject Payment
                        </Button>
                        <Button variant="secondary" onClick={handleDeletePayment} disabled={isSubmitting}>
                          Delete
                        </Button>
                      </div>
                    )}

                    {payment.status === 'rejected' && (
                      <div className="flex gap-3">
                        <Button variant="primary" onClick={handleVerifyPayment} disabled={isSubmitting}>
                          Verify Payment
                        </Button>
                        <Button variant="secondary" onClick={handleDeletePayment} disabled={isSubmitting}>
                          Delete
                        </Button>
                      </div>
                    )}

                    {/* Reject Dialog */}
                    {showRejectDialog && (
                      <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
                        <div className="bg-dark-surface border border-dark-border rounded-lg p-6 w-full max-w-md">
                          <h4 className="text-lg font-semibold text-dark-text mb-4">Reject Payment</h4>
                          <Textarea
                            label="Rejection Reason"
                            value={rejectionReason}
                            onChange={(e) => setRejectionReason(e.target.value)}
                            placeholder="Enter reason for rejection..."
                            required
                          />
                          <div className="flex gap-3 mt-4">
                            <Button variant="primary" onClick={handleRejectPayment} disabled={!rejectionReason.trim() || isSubmitting}>
                              Confirm Rejection
                            </Button>
                            <Button variant="secondary" onClick={() => setShowRejectDialog(false)}>
                              Cancel
                            </Button>
                          </div>
                        </div>
                      </div>
                    )}
                  </div>
                ) : (
                  <div>
                    {showPaymentForm ? (
                      <form onSubmit={handleRecordPayment} className="bg-dark-elevated rounded-lg p-4 space-y-4">
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                          <Input
                            label="Amount (₦)"
                            type="number"
                            value={paymentForm.amount || ''}
                            onChange={(e) => setPaymentForm((prev) => ({ ...prev, amount: parseFloat(e.target.value) || 0 }))}
                            required
                            hint={`Expected: ${formatCurrency(application.bond_value)}`}
                          />
                          <Select
                            label="Payment Method"
                            options={PAYMENT_METHODS}
                            value={paymentForm.payment_method}
                            onChange={(e) => setPaymentForm((prev) => ({ ...prev, payment_method: e.target.value as PaymentCreate['payment_method'] }))}
                            required
                          />
                          <Input
                            label="Payment/Deposit Reference"
                            value={paymentForm.payment_reference}
                            onChange={(e) => setPaymentForm((prev) => ({ ...prev, payment_reference: e.target.value }))}
                            placeholder="e.g., TRF/2026/001234"
                            required
                            hint="Critical for DMO reconciliation"
                          />
                          <Input
                            label="Payment Date"
                            type="date"
                            value={paymentForm.payment_date}
                            onChange={(e) => setPaymentForm((prev) => ({ ...prev, payment_date: e.target.value }))}
                            required
                          />
                          <Input
                            label="Receiving Bank"
                            value={paymentForm.receiving_bank || ''}
                            onChange={(e) => setPaymentForm((prev) => ({ ...prev, receiving_bank: e.target.value }))}
                            placeholder="e.g., Zenith Bank"
                          />
                        </div>
                        <Textarea
                          label="Notes"
                          value={paymentForm.notes || ''}
                          onChange={(e) => setPaymentForm((prev) => ({ ...prev, notes: e.target.value }))}
                          placeholder="Additional notes about the payment..."
                        />
                        <div className="flex gap-3">
                          <Button variant="primary" type="submit" disabled={isSubmitting}>
                            {isSubmitting ? 'Recording...' : 'Record Payment'}
                          </Button>
                          <Button variant="secondary" type="button" onClick={() => setShowPaymentForm(false)}>
                            Cancel
                          </Button>
                        </div>
                      </form>
                    ) : (
                      <div className="bg-dark-elevated rounded-lg p-6 text-center">
                        <p className="text-dark-text-secondary mb-4">No payment recorded for this application</p>
                        <Button variant="primary" onClick={() => {
                          setPaymentForm((prev) => ({ ...prev, amount: application.bond_value }));
                          setShowPaymentForm(true);
                        }}>
                          Record Payment
                        </Button>
                      </div>
                    )}
                  </div>
                )}
              </div>
            </div>
          ) : (
            <div className="text-center py-12 text-dark-text-secondary">Application not found</div>
          )}
        </div>

        {/* Footer */}
        <div className="flex justify-end p-4 border-t border-dark-border">
          <Button variant="secondary" onClick={onClose}>
            Close
          </Button>
        </div>
      </div>
    </div>
  );
}

// Helper components
function InfoCard({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div className="bg-dark-elevated rounded-lg p-4">
      <h4 className="text-sm font-medium text-dark-text-secondary mb-3">{title}</h4>
      <div className="space-y-2">{children}</div>
    </div>
  );
}

function InfoRow({ label, value, highlight }: { label: string; value?: string | null; highlight?: boolean }) {
  return (
    <div className="flex justify-between">
      <span className="text-sm text-dark-text-secondary">{label}</span>
      <span className={`text-sm ${highlight ? 'text-primary-500 font-medium' : 'text-dark-text'}`}>
        {value || '-'}
      </span>
    </div>
  );
}
