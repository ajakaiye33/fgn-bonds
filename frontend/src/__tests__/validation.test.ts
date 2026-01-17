/**
 * Tests for Zod validation schemas.
 */

import { describe, expect, it } from 'vitest';
import {
  applicantTypeSchema,
  bankDetailsSchema,
  bondDetailsSchema,
  classificationSchema,
  corporateFieldsSchema,
  distributionSchema,
  individualFieldsSchema,
  jointApplicantFieldsSchema,
} from '../lib/validation';

describe('bondDetailsSchema', () => {
  const validData = {
    tenor: '2-Year' as const,
    month_of_offer: 'January',
    bond_value: 100000,
    amount_in_words: 'One Hundred Thousand Naira Only',
  };

  it('should accept valid bond details', () => {
    const result = bondDetailsSchema.safeParse(validData);
    expect(result.success).toBe(true);
  });

  it('should reject invalid tenor', () => {
    const result = bondDetailsSchema.safeParse({
      ...validData,
      tenor: '5-Year',
    });
    expect(result.success).toBe(false);
  });

  it('should reject bond value below minimum', () => {
    const result = bondDetailsSchema.safeParse({
      ...validData,
      bond_value: 1000,
    });
    expect(result.success).toBe(false);
  });

  it('should reject bond value above maximum', () => {
    const result = bondDetailsSchema.safeParse({
      ...validData,
      bond_value: 100000000,
    });
    expect(result.success).toBe(false);
  });

  it('should accept minimum bond value (5000)', () => {
    const result = bondDetailsSchema.safeParse({
      ...validData,
      bond_value: 5000,
    });
    expect(result.success).toBe(true);
  });

  it('should accept maximum bond value (50000000)', () => {
    const result = bondDetailsSchema.safeParse({
      ...validData,
      bond_value: 50000000,
    });
    expect(result.success).toBe(true);
  });

  it('should reject empty month of offer', () => {
    const result = bondDetailsSchema.safeParse({
      ...validData,
      month_of_offer: '',
    });
    expect(result.success).toBe(false);
  });
});

describe('applicantTypeSchema', () => {
  it('should accept Individual', () => {
    const result = applicantTypeSchema.safeParse({ applicant_type: 'Individual' });
    expect(result.success).toBe(true);
  });

  it('should accept Joint', () => {
    const result = applicantTypeSchema.safeParse({ applicant_type: 'Joint' });
    expect(result.success).toBe(true);
  });

  it('should accept Corporate', () => {
    const result = applicantTypeSchema.safeParse({ applicant_type: 'Corporate' });
    expect(result.success).toBe(true);
  });

  it('should reject invalid type', () => {
    const result = applicantTypeSchema.safeParse({ applicant_type: 'Partnership' });
    expect(result.success).toBe(false);
  });
});

describe('individualFieldsSchema', () => {
  const validData = {
    title: 'Mr.',
    full_name: 'John Doe',
    date_of_birth: '1990-01-15',
    phone_number: '+2348012345678',
    email: 'john.doe@example.com',
    next_of_kin: 'Jane Doe',
    address: '123 Test Street, Lagos',
  };

  it('should accept valid individual data', () => {
    const result = individualFieldsSchema.safeParse(validData);
    expect(result.success).toBe(true);
  });

  it('should accept valid phone formats', () => {
    const formats = ['+2348012345678', '2348012345678', '08012345678'];
    formats.forEach((phone) => {
      const result = individualFieldsSchema.safeParse({
        ...validData,
        phone_number: phone,
      });
      expect(result.success).toBe(true);
    });
  });

  it('should reject invalid phone number', () => {
    const result = individualFieldsSchema.safeParse({
      ...validData,
      phone_number: '12345',
    });
    expect(result.success).toBe(false);
  });

  it('should reject invalid email', () => {
    const result = individualFieldsSchema.safeParse({
      ...validData,
      email: 'not-an-email',
    });
    expect(result.success).toBe(false);
  });

  it('should require full name', () => {
    const { full_name, ...dataWithoutName } = validData;
    const result = individualFieldsSchema.safeParse(dataWithoutName);
    expect(result.success).toBe(false);
  });
});

describe('jointApplicantFieldsSchema', () => {
  const validData = {
    joint_title: 'Mrs.',
    joint_full_name: 'Jane Doe',
    joint_date_of_birth: '1992-05-20',
    joint_phone_number: '+2348087654321',
    joint_email: 'jane.doe@example.com',
    joint_next_of_kin: 'John Doe',
    joint_address: '456 Test Avenue, Abuja',
  };

  it('should accept valid joint applicant data', () => {
    const result = jointApplicantFieldsSchema.safeParse(validData);
    expect(result.success).toBe(true);
  });

  it('should require joint full name', () => {
    const { joint_full_name, ...dataWithoutName } = validData;
    const result = jointApplicantFieldsSchema.safeParse(dataWithoutName);
    expect(result.success).toBe(false);
  });
});

describe('corporateFieldsSchema', () => {
  const validData = {
    company_name: 'Test Company Ltd',
    rc_number: 'RC123456',
    business_type: 'Technology',
    contact_person: 'Jane Smith',
    corp_phone_number: '+2348012345678',
    corp_email: 'info@testcompany.com',
  };

  it('should accept valid corporate data', () => {
    const result = corporateFieldsSchema.safeParse(validData);
    expect(result.success).toBe(true);
  });

  it('should require company name', () => {
    const { company_name, ...dataWithoutName } = validData;
    const result = corporateFieldsSchema.safeParse(dataWithoutName);
    expect(result.success).toBe(false);
  });

  it('should require RC number', () => {
    const { rc_number, ...dataWithoutRc } = validData;
    const result = corporateFieldsSchema.safeParse(dataWithoutRc);
    expect(result.success).toBe(false);
  });
});

describe('bankDetailsSchema', () => {
  const validData = {
    bank_name: 'Access Bank',
    account_number: '0123456789',
  };

  it('should accept valid bank details', () => {
    const result = bankDetailsSchema.safeParse(validData);
    expect(result.success).toBe(true);
  });

  it('should reject account number not 10 digits', () => {
    const result = bankDetailsSchema.safeParse({
      ...validData,
      account_number: '12345',
    });
    expect(result.success).toBe(false);
  });

  it('should accept valid BVN (11 digits)', () => {
    const result = bankDetailsSchema.safeParse({
      ...validData,
      bvn: '12345678901',
    });
    expect(result.success).toBe(true);
  });

  it('should reject invalid BVN (not 11 digits)', () => {
    const result = bankDetailsSchema.safeParse({
      ...validData,
      bvn: '12345',
    });
    expect(result.success).toBe(false);
  });

  it('should allow empty BVN', () => {
    const result = bankDetailsSchema.safeParse({
      ...validData,
      bvn: '',
    });
    expect(result.success).toBe(true);
  });
});

describe('classificationSchema', () => {
  it('should accept valid classification', () => {
    const result = classificationSchema.safeParse({
      is_resident: true,
      investor_category: ['Retail Investor'],
    });
    expect(result.success).toBe(true);
  });

  it('should require at least one investor category', () => {
    const result = classificationSchema.safeParse({
      is_resident: true,
      investor_category: [],
    });
    expect(result.success).toBe(false);
  });

  it('should accept multiple investor categories', () => {
    const result = classificationSchema.safeParse({
      is_resident: false,
      investor_category: ['Retail Investor', 'Pension Fund'],
    });
    expect(result.success).toBe(true);
  });
});

describe('distributionSchema', () => {
  it('should accept valid distribution data', () => {
    const result = distributionSchema.safeParse({
      agent_name: 'Test Agent',
      stockbroker_code: 'SB001',
      needs_witness: true,
      witness_name: 'John Witness',
      witness_address: '123 Witness Street',
      witness_acknowledged: true,
    });
    expect(result.success).toBe(true);
  });

  it('should accept empty optional fields', () => {
    const result = distributionSchema.safeParse({
      needs_witness: false,
      witness_acknowledged: false,
    });
    expect(result.success).toBe(true);
  });
});
