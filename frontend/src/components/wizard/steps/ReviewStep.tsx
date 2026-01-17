/**
 * Step 7: Review & Submit - Review all information and submit application.
 */

import type { UseFormReturn } from 'react-hook-form';
import type { ApplicationFormData } from '../../../types/application';
import { formatCurrency, formatMoneyInWords } from '../../../lib/utils';
import { Checkbox } from '../../ui';
import { useState } from 'react';

interface ReviewStepProps {
  form: UseFormReturn<ApplicationFormData>;
}

export function ReviewStep({ form }: ReviewStepProps) {
  const { watch } = form;
  const data = watch();
  const [declarationAccepted, setDeclarationAccepted] = useState(false);

  const applicantType = data.applicant_type;

  // Section component for displaying review data
  const Section = ({
    title,
    children,
  }: {
    title: string;
    children: React.ReactNode;
  }) => (
    <div className="card mb-4">
      <h3 className="text-lg font-semibold text-primary-500 border-b border-dark-border pb-2 mb-4">
        {title}
      </h3>
      {children}
    </div>
  );

  const Field = ({ label, value }: { label: string; value?: string | number | boolean | null }) => {
    if (value === undefined || value === null || value === '') return null;

    let displayValue: string;
    if (typeof value === 'boolean') {
      displayValue = value ? 'Yes' : 'No';
    } else if (Array.isArray(value)) {
      displayValue = value.join(', ');
    } else {
      displayValue = String(value);
    }

    return (
      <div className="flex flex-col sm:flex-row sm:items-start gap-1 py-2 border-b border-dark-border/50 last:border-0">
        <span className="text-sm text-dark-text-secondary sm:w-1/3">{label}:</span>
        <span className="text-sm text-dark-text font-medium sm:w-2/3">{displayValue}</span>
      </div>
    );
  };

  return (
    <div className="space-y-6">
      <div className="text-center mb-8">
        <h2 className="text-2xl font-semibold text-dark-text mb-2">
          Review Your Application
        </h2>
        <p className="text-dark-text-secondary">
          Please review all the information before submitting your application.
        </p>
      </div>

      {/* Bond Details */}
      <Section title="Bond Details">
        <Field label="Tenor" value={data.tenor} />
        <Field label="Month of Offer" value={data.month_of_offer} />
        <Field label="Bond Value" value={formatCurrency(data.bond_value)} />
        <Field label="Amount in Words" value={formatMoneyInWords(data.bond_value) + ' Only'} />
        <Field label="Applicant Type" value={data.applicant_type} />
      </Section>

      {/* Applicant Information */}
      <Section title={applicantType === 'Corporate' ? 'Company Information' : 'Applicant Information'}>
        {applicantType === 'Corporate' ? (
          <>
            <Field label="Company Name" value={data.company_name} />
            <Field label="RC Number" value={data.rc_number} />
            <Field label="Business Type" value={data.business_type} />
            <Field label="Contact Person" value={data.contact_person} />
            <Field label="Phone Number" value={data.corp_phone_number} />
            <Field label="Email" value={data.corp_email} />
            <Field label="Passport/ID Number" value={data.corp_passport_no} />
          </>
        ) : (
          <>
            <Field label="Title" value={data.title} />
            <Field label="Full Name" value={data.full_name} />
            <Field label="Date of Birth" value={data.date_of_birth} />
            <Field label="Phone Number" value={data.phone_number} />
            <Field label="Email" value={data.email} />
            <Field label="Occupation" value={data.occupation} />
            <Field label="Passport/ID Number" value={data.passport_no} />
            <Field label="Next of Kin" value={data.next_of_kin} />
            <Field label="Mother's Maiden Name" value={data.mothers_maiden_name} />
            <Field label="Address" value={data.address} />
            <Field label="CSCS Number" value={data.cscs_number} />
            <Field label="CHN Number" value={data.chn_number} />
          </>
        )}
      </Section>

      {/* Joint Applicant Information */}
      {applicantType === 'Joint' && (
        <Section title="Joint Applicant Information">
          <Field label="Title" value={data.joint_title} />
          <Field label="Full Name" value={data.joint_full_name} />
          <Field label="Date of Birth" value={data.joint_date_of_birth} />
          <Field label="Phone Number" value={data.joint_phone_number} />
          <Field label="Email" value={data.joint_email} />
          <Field label="Occupation" value={data.joint_occupation} />
          <Field label="Passport/ID Number" value={data.joint_passport_no} />
          <Field label="Next of Kin" value={data.joint_next_of_kin} />
          <Field label="Address" value={data.joint_address} />
        </Section>
      )}

      {/* Bank Details */}
      <Section title={applicantType === 'Joint' ? "Primary Applicant's Bank Details" : 'Bank Details'}>
        <Field label="Bank Name" value={data.bank_name} />
        <Field label="Bank Branch" value={data.bank_branch} />
        <Field label="Account Number" value={data.account_number} />
        <Field label="Sort Code" value={data.sort_code} />
        <Field label="BVN" value={data.bvn} />
      </Section>

      {/* Joint Bank Details */}
      {applicantType === 'Joint' && data.joint_bank_name && (
        <Section title="Joint Applicant's Bank Details">
          <Field label="Bank Name" value={data.joint_bank_name} />
          <Field label="Bank Branch" value={data.joint_bank_branch} />
          <Field label="Account Number" value={data.joint_account_number} />
          <Field label="Sort Code" value={data.joint_sort_code} />
          <Field label="BVN" value={data.joint_bvn} />
        </Section>
      )}

      {/* Classification */}
      <Section title="Classification">
        <Field label="Residency Status" value={data.is_resident ? 'Resident' : 'Non-Resident'} />
        <Field label="Investor Category" value={data.investor_category?.join(', ')} />
      </Section>

      {/* Distribution Agent */}
      {(data.agent_name || data.stockbroker_code) && (
        <Section title="Distribution Agent">
          <Field label="Agent Name" value={data.agent_name} />
          <Field label="Stockbroker Code" value={data.stockbroker_code} />
        </Section>
      )}

      {/* Witness */}
      {data.needs_witness && (
        <Section title="Witness">
          <Field label="Witness Name" value={data.witness_name} />
          <Field label="Witness Address" value={data.witness_address} />
        </Section>
      )}

      {/* Declaration */}
      <div className="card bg-primary-900/10 border-primary-700">
        <h3 className="text-lg font-semibold text-dark-text mb-4">Declaration</h3>
        <p className="text-sm text-dark-text-secondary mb-4">
          I/We hereby apply to subscribe for the Federal Government of Nigeria Savings Bond
          for the amount stated above. I/We confirm that the information provided is accurate
          and complete to the best of my/our knowledge.
        </p>
        <p className="text-sm text-dark-text-secondary mb-6">
          I/We understand that this subscription is subject to the terms and conditions of
          the FGN Savings Bond as prescribed by the Debt Management Office (DMO).
        </p>
        <Checkbox
          label="I/We agree to the terms and conditions and confirm that all information provided is accurate"
          checked={declarationAccepted}
          onChange={(e) => setDeclarationAccepted(e.target.checked)}
        />
      </div>

      {!declarationAccepted && (
        <p className="text-sm text-warning text-center">
          Please accept the declaration to submit your application.
        </p>
      )}
    </div>
  );
}
