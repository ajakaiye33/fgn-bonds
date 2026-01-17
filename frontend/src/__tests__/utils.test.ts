/**
 * Tests for utility functions.
 */

import { describe, expect, it } from 'vitest';
import {
  cn,
  formatCurrency,
  formatMoneyInWords,
  getCurrentMonth,
  normalizePhoneNumber,
  numberToWords,
} from '../lib/utils';

describe('cn (classname merge)', () => {
  it('should merge class names', () => {
    expect(cn('foo', 'bar')).toBe('foo bar');
  });

  it('should handle conditional classes', () => {
    const condition = false;
    expect(cn('foo', condition && 'bar', 'baz')).toBe('foo baz');
  });

  it('should handle empty input', () => {
    expect(cn()).toBe('');
  });
});

describe('numberToWords', () => {
  it('should convert 0', () => {
    expect(numberToWords(0)).toBe('Zero');
  });

  it('should convert single digits', () => {
    expect(numberToWords(1)).toBe('One');
    expect(numberToWords(5)).toBe('Five');
    expect(numberToWords(9)).toBe('Nine');
  });

  it('should convert teens', () => {
    expect(numberToWords(10)).toBe('Ten');
    expect(numberToWords(11)).toBe('Eleven');
    expect(numberToWords(15)).toBe('Fifteen');
    expect(numberToWords(19)).toBe('Nineteen');
  });

  it('should convert tens', () => {
    expect(numberToWords(20)).toBe('Twenty');
    expect(numberToWords(25)).toBe('Twenty Five');
    expect(numberToWords(99)).toBe('Ninety Nine');
  });

  it('should convert hundreds', () => {
    expect(numberToWords(100)).toBe('One Hundred');
    expect(numberToWords(101)).toBe('One Hundred and One');
    expect(numberToWords(150)).toBe('One Hundred and Fifty');
    expect(numberToWords(999)).toBe('Nine Hundred and Ninety Nine');
  });

  it('should convert thousands', () => {
    expect(numberToWords(1000)).toBe('One Thousand');
    expect(numberToWords(1001)).toBe('One Thousand One');
    expect(numberToWords(5000)).toBe('Five Thousand');
    expect(numberToWords(10000)).toBe('Ten Thousand');
    expect(numberToWords(100000)).toBe('One Hundred Thousand');
  });

  it('should convert millions', () => {
    expect(numberToWords(1000000)).toBe('One Million');
    expect(numberToWords(5000000)).toBe('Five Million');
    expect(numberToWords(50000000)).toBe('Fifty Million');
  });

  it('should convert complex numbers', () => {
    expect(numberToWords(12345)).toContain('Twelve Thousand');
    expect(numberToWords(123456)).toContain('Hundred');
    expect(numberToWords(1234567)).toContain('Million');
  });
});

describe('formatMoneyInWords', () => {
  it('should format whole Naira amounts', () => {
    expect(formatMoneyInWords(100)).toBe('One Hundred Naira');
    expect(formatMoneyInWords(5000)).toBe('Five Thousand Naira');
    expect(formatMoneyInWords(1000000)).toBe('One Million Naira');
  });

  it('should format amounts with Kobo', () => {
    const result = formatMoneyInWords(100.50);
    expect(result).toContain('Naira');
    expect(result).toContain('Kobo');
    expect(result).toContain('Fifty');
  });

  it('should not include Kobo for whole numbers', () => {
    expect(formatMoneyInWords(100)).not.toContain('Kobo');
  });
});

describe('formatCurrency', () => {
  it('should format as Nigerian Naira', () => {
    const result = formatCurrency(5000);
    expect(result).toContain('5,000');
    // Check for NGN symbol or ₦
    expect(result.includes('₦') || result.includes('NGN')).toBe(true);
  });

  it('should format large amounts with commas', () => {
    const result = formatCurrency(1000000);
    expect(result).toContain('1,000,000');
  });

  it('should handle zero', () => {
    const result = formatCurrency(0);
    expect(result).toContain('0');
  });
});

describe('normalizePhoneNumber', () => {
  it('should convert 0-prefix to +234', () => {
    expect(normalizePhoneNumber('08012345678')).toBe('+2348012345678');
  });

  it('should add + to 234-prefix', () => {
    expect(normalizePhoneNumber('2348012345678')).toBe('+2348012345678');
  });

  it('should keep +234 prefix as is', () => {
    expect(normalizePhoneNumber('+2348012345678')).toBe('+2348012345678');
  });

  it('should remove non-digit characters except +', () => {
    expect(normalizePhoneNumber('080-1234-5678')).toBe('+2348012345678');
    expect(normalizePhoneNumber('(080) 1234 5678')).toBe('+2348012345678');
  });
});

describe('getCurrentMonth', () => {
  it('should return a valid month name', () => {
    const months = [
      'January', 'February', 'March', 'April', 'May', 'June',
      'July', 'August', 'September', 'October', 'November', 'December',
    ];
    const result = getCurrentMonth();
    expect(months).toContain(result);
  });

  it('should return current month', () => {
    const expected = [
      'January', 'February', 'March', 'April', 'May', 'June',
      'July', 'August', 'September', 'October', 'November', 'December',
    ][new Date().getMonth()];
    expect(getCurrentMonth()).toBe(expected);
  });
});
