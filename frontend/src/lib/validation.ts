/**
 * Zod validation schemas for the FGN Savings Bond application form.
 * Updated for Zod v4 syntax.
 */

import { z } from 'zod';

// Custom validators
const phoneRegex = /^(\+234|234|0)[789]\d{9}$/;
const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
const bvnRegex = /^\d{11}$/;
const accountNumberRegex = /^\d{10}$/;

// Step 1: Bond Details
export const bondDetailsSchema = z.object({
  tenor: z.enum(['2-Year', '3-Year'], {
    message: 'Please select a tenor',
  }),
  month_of_offer: z.string().min(1, 'Please select the month of offer'),
  bond_value: z
    .number({
      message: 'Bond value is required and must be a number',
    })
    .min(5000, 'Minimum bond value is ₦5,000')
    .max(50000000, 'Maximum bond value is ₦50,000,000'),
  amount_in_words: z.string().min(1, 'Amount in words is required'),
});

// Step 2: Applicant Type
export const applicantTypeSchema = z.object({
  applicant_type: z.enum(['Individual', 'Joint', 'Corporate'], {
    message: 'Please select an applicant type',
  }),
});

// Individual applicant fields
const individualFieldsSchema = z.object({
  title: z.string().min(1, 'Title is required'),
  full_name: z.string().min(2, 'Full name is required'),
  date_of_birth: z.string().min(1, 'Date of birth is required'),
  phone_number: z
    .string()
    .min(1, 'Phone number is required')
    .regex(phoneRegex, 'Invalid Nigerian phone number'),
  email: z
    .string()
    .min(1, 'Email is required')
    .regex(emailRegex, 'Invalid email address'),
  occupation: z.string().optional(),
  passport_no: z.string().optional(),
  next_of_kin: z.string().min(1, 'Next of kin is required'),
  mothers_maiden_name: z.string().optional(),
  address: z.string().min(5, 'Address is required'),
  cscs_number: z.string().optional(),
  chn_number: z.string().optional(),
});

// Joint applicant fields (secondary)
const jointApplicantFieldsSchema = z.object({
  joint_title: z.string().min(1, 'Joint applicant title is required'),
  joint_full_name: z.string().min(2, 'Joint applicant full name is required'),
  joint_date_of_birth: z.string().min(1, 'Joint applicant date of birth is required'),
  joint_phone_number: z
    .string()
    .min(1, 'Joint applicant phone number is required')
    .regex(phoneRegex, 'Invalid Nigerian phone number'),
  joint_email: z
    .string()
    .min(1, 'Joint applicant email is required')
    .regex(emailRegex, 'Invalid email address'),
  joint_occupation: z.string().optional(),
  joint_passport_no: z.string().optional(),
  joint_next_of_kin: z.string().min(1, 'Joint applicant next of kin is required'),
  joint_address: z.string().min(5, 'Joint applicant address is required'),
});

// Corporate fields
const corporateFieldsSchema = z.object({
  company_name: z.string().min(2, 'Company name is required'),
  rc_number: z.string().min(1, 'RC number is required'),
  business_type: z.string().min(1, 'Business type is required'),
  contact_person: z.string().min(2, 'Contact person is required'),
  corp_phone_number: z
    .string()
    .min(1, 'Phone number is required')
    .regex(phoneRegex, 'Invalid Nigerian phone number'),
  corp_email: z
    .string()
    .min(1, 'Email is required')
    .regex(emailRegex, 'Invalid email address'),
  corp_passport_no: z.string().optional(),
});

// Step 4: Bank Details
export const bankDetailsSchema = z.object({
  bank_name: z.string().min(1, 'Bank name is required'),
  bank_branch: z.string().optional(),
  account_number: z
    .string()
    .min(1, 'Account number is required')
    .regex(accountNumberRegex, 'Account number must be 10 digits'),
  sort_code: z.string().optional(),
  bvn: z
    .string()
    .optional()
    .refine(
      (val) => !val || bvnRegex.test(val),
      'BVN must be 11 digits'
    ),
});

// Joint bank details (conditional)
export const jointBankDetailsSchema = z.object({
  joint_bank_name: z.string().min(1, 'Joint bank name is required'),
  joint_bank_branch: z.string().optional(),
  joint_account_number: z
    .string()
    .min(1, 'Joint account number is required')
    .regex(accountNumberRegex, 'Account number must be 10 digits'),
  joint_sort_code: z.string().optional(),
  joint_bvn: z
    .string()
    .optional()
    .refine(
      (val) => !val || bvnRegex.test(val),
      'BVN must be 11 digits'
    ),
});

// Step 5: Classification
export const classificationSchema = z.object({
  is_resident: z.boolean(),
  investor_category: z.array(z.string()).min(1, 'Select at least one investor category'),
});

// Step 6: Distribution Agent
export const distributionSchema = z.object({
  agent_name: z.string().optional(),
  stockbroker_code: z.string().optional(),
  needs_witness: z.boolean(),
  witness_name: z.string().optional(),
  witness_address: z.string().optional(),
  witness_acknowledged: z.boolean(),
});

// Complete form schema
export const applicationFormSchema = z
  .object({
    // Bond Details
    tenor: z.enum(['2-Year', '3-Year']),
    month_of_offer: z.string().min(1),
    bond_value: z.number().min(5000).max(50000000),
    amount_in_words: z.string().min(1),

    // Applicant Type
    applicant_type: z.enum(['Individual', 'Joint', 'Corporate']),

    // Individual/Joint fields (optional based on type)
    title: z.string().optional(),
    full_name: z.string().optional(),
    date_of_birth: z.string().optional(),
    phone_number: z.string().optional(),
    email: z.string().optional(),
    occupation: z.string().optional(),
    passport_no: z.string().optional(),
    next_of_kin: z.string().optional(),
    mothers_maiden_name: z.string().optional(),
    address: z.string().optional(),
    cscs_number: z.string().optional(),
    chn_number: z.string().optional(),

    // Joint applicant fields
    joint_title: z.string().optional(),
    joint_full_name: z.string().optional(),
    joint_date_of_birth: z.string().optional(),
    joint_phone_number: z.string().optional(),
    joint_email: z.string().optional(),
    joint_occupation: z.string().optional(),
    joint_passport_no: z.string().optional(),
    joint_next_of_kin: z.string().optional(),
    joint_address: z.string().optional(),

    // Corporate fields
    company_name: z.string().optional(),
    rc_number: z.string().optional(),
    business_type: z.string().optional(),
    contact_person: z.string().optional(),
    corp_phone_number: z.string().optional(),
    corp_email: z.string().optional(),
    corp_passport_no: z.string().optional(),

    // Bank Details
    bank_name: z.string().min(1),
    bank_branch: z.string().optional(),
    account_number: z.string().regex(accountNumberRegex),
    sort_code: z.string().optional(),
    bvn: z.string().optional(),

    // Joint Bank Details
    joint_bank_name: z.string().optional(),
    joint_bank_branch: z.string().optional(),
    joint_account_number: z.string().optional(),
    joint_sort_code: z.string().optional(),
    joint_bvn: z.string().optional(),

    // Classification
    is_resident: z.boolean(),
    investor_category: z.array(z.string()).optional(),

    // Distribution
    agent_name: z.string().optional(),
    stockbroker_code: z.string().optional(),

    // Witness
    needs_witness: z.boolean(),
    witness_name: z.string().optional(),
    witness_address: z.string().optional(),
    witness_acknowledged: z.boolean(),
  });

export type ApplicationFormData = z.infer<typeof applicationFormSchema>;

// Re-export partial schemas for step validation
export { individualFieldsSchema, jointApplicantFieldsSchema, corporateFieldsSchema };
