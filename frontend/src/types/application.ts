/**
 * TypeScript types for FGN Savings Bond application.
 */

export type ApplicantType = 'Individual' | 'Joint' | 'Corporate';
export type Tenor = '2-Year' | '3-Year';

export interface ApplicationFormData {
  // Bond details
  tenor: Tenor;
  month_of_offer: string;
  bond_value: number;
  amount_in_words: string;

  // Applicant type
  applicant_type: ApplicantType;

  // Individual/Joint applicant fields (Primary)
  title?: string;
  full_name?: string;
  date_of_birth?: string;
  phone_number?: string;
  email?: string;
  occupation?: string;
  passport_no?: string;
  next_of_kin?: string;
  mothers_maiden_name?: string;
  address?: string;
  cscs_number?: string;
  chn_number?: string;

  // Joint applicant fields (Secondary)
  joint_title?: string;
  joint_full_name?: string;
  joint_date_of_birth?: string;
  joint_phone_number?: string;
  joint_email?: string;
  joint_occupation?: string;
  joint_passport_no?: string;
  joint_next_of_kin?: string;
  joint_address?: string;

  // Corporate fields
  company_name?: string;
  rc_number?: string;
  business_type?: string;
  contact_person?: string;
  corp_phone_number?: string;
  corp_email?: string;
  corp_passport_no?: string;

  // Bank details (Primary)
  bank_name: string;
  bank_branch?: string;
  account_number: string;
  sort_code?: string;
  bvn?: string;

  // Joint bank details
  joint_bank_name?: string;
  joint_bank_branch?: string;
  joint_account_number?: string;
  joint_sort_code?: string;
  joint_bvn?: string;

  // Classification
  is_resident: boolean;
  investor_category?: string[];

  // Distribution agent
  agent_name?: string;
  stockbroker_code?: string;

  // Witness
  needs_witness: boolean;
  witness_name?: string;
  witness_address?: string;
  witness_acknowledged: boolean;
}

export interface ApplicationResponse extends ApplicationFormData {
  id: number;
  submission_date: string;
  created_at?: string;
  payment_status: PaymentStatus;
}

// Payment types
export type PaymentStatus = 'pending' | 'paid' | 'verified' | 'rejected';
export type PaymentMethod = 'bank_transfer' | 'cheque' | 'cash' | 'pos' | 'other';

export interface PaymentCreate {
  amount: number;
  payment_method: PaymentMethod;
  payment_reference: string;
  payment_date: string;
  receiving_bank?: string;
  notes?: string;
}

export interface PaymentUpdate {
  amount?: number;
  payment_method?: PaymentMethod;
  payment_reference?: string;
  payment_date?: string;
  receiving_bank?: string;
  notes?: string;
}

export interface PaymentVerify {
  action: 'verify' | 'reject';
  rejection_reason?: string;
}

export interface PaymentDocument {
  id: number;
  payment_id: number;
  filename: string;
  original_filename: string;
  file_size: number | null;
  mime_type: string | null;
  uploaded_at: string;
}

export interface Payment {
  id: number;
  application_id: number;
  amount: number;
  payment_method: string;
  payment_reference: string;
  payment_date: string;
  receiving_bank: string | null;
  status: PaymentStatus;
  verified_at: string | null;
  verified_by: string | null;
  rejection_reason: string | null;
  notes: string | null;
  created_at: string;
  updated_at: string | null;
  documents: PaymentDocument[];
}

// DMO Reporting types
export interface MonthlyReportSummary {
  month_of_offer: string;
  year: number;
  total_applications: number;
  total_value: number;
  average_value: number;
  total_2year: number;
  value_2year: number;
  total_3year: number;
  value_3year: number;
  total_individual: number;
  total_joint: number;
  total_corporate: number;
  pending_count: number;
  pending_value: number;
  paid_count: number;
  paid_value: number;
  verified_count: number;
  verified_value: number;
  rejected_count: number;
  rejected_value: number;
  is_submitted: boolean;
  submission_id: number | null;
  submitted_at: string | null;
}

export interface DMOSubmission {
  id: number;
  month_of_offer: string;
  year: number;
  total_applications: number;
  total_value: number;
  total_2year: number;
  total_3year: number;
  total_verified: number;
  submitted_at: string;
  submitted_by: string | null;
  report_file_path: string | null;
  notes: string | null;
}

export interface DMOSubmissionCreate {
  month_of_offer: string;
  year: number;
  notes?: string;
}

export interface Constants {
  banks: string[];
  investor_categories: string[];
  months: string[];
  tenors: string[];
  titles: string[];
}

// Form wizard step definition
export interface WizardStep {
  id: number;
  title: string;
  description: string;
}

export const WIZARD_STEPS: WizardStep[] = [
  { id: 0, title: 'Bond Details', description: 'Select tenor and enter bond value' },
  { id: 1, title: 'Applicant Type', description: 'Choose applicant category' },
  { id: 2, title: 'Applicant Info', description: 'Enter personal/company details' },
  { id: 3, title: 'Bank Details', description: 'Enter bank account information' },
  { id: 4, title: 'Classification', description: 'Select residency and investor category' },
  { id: 5, title: 'Distribution', description: 'Enter agent details (optional)' },
  { id: 6, title: 'Review & Submit', description: 'Review and submit application' },
];
