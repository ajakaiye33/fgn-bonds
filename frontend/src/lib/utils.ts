/**
 * Utility functions for the application.
 */

import { clsx, type ClassValue } from 'clsx';

/**
 * Merge class names with clsx.
 */
export function cn(...inputs: ClassValue[]) {
  return clsx(inputs);
}

/**
 * Convert a number to English words.
 */
export function numberToWords(num: number): string {
  const units = ['', 'One', 'Two', 'Three', 'Four', 'Five', 'Six', 'Seven', 'Eight', 'Nine'];
  const teens = ['Ten', 'Eleven', 'Twelve', 'Thirteen', 'Fourteen', 'Fifteen', 'Sixteen', 'Seventeen', 'Eighteen', 'Nineteen'];
  const tens = ['', '', 'Twenty', 'Thirty', 'Forty', 'Fifty', 'Sixty', 'Seventy', 'Eighty', 'Ninety'];
  const suffixes = ['', 'Thousand', 'Million', 'Billion'];

  if (num === 0) return 'Zero';

  function getNumber(n: string): string {
    if (n === '0') return '';
    if (n.length === 1) return units[parseInt(n)];
    if (n.length === 2) {
      if (n[0] === '1') return teens[parseInt(n[1])];
      const tenPart = tens[parseInt(n[0])];
      const unitPart = parseInt(n[1]) !== 0 ? units[parseInt(n[1])] : '';
      return [tenPart, unitPart].filter(Boolean).join(' ');
    }
    if (n.length === 3) {
      if (n[0] === '0') return getNumber(n.slice(1));
      const rest = getNumber(n.slice(1));
      return units[parseInt(n[0])] + ' Hundred' + (rest ? ' and ' + rest : '');
    }
    return '';
  }

  function getGroups(n: string): string[] {
    const groups: string[] = [];
    if (n === '0') return ['0'];
    while (n.length > 0) {
      groups.push(n.length >= 3 ? n.slice(-3) : n);
      n = n.slice(0, -3);
    }
    return groups.reverse();
  }

  const numStr = Math.floor(num).toString();
  const groups = getGroups(numStr);
  const words: string[] = [];

  groups.forEach((group, i) => {
    if (parseInt(group) !== 0) {
      const word = getNumber(group);
      const suffix = suffixes[groups.length - i - 1];
      words.push(suffix ? word + ' ' + suffix : word);
    }
  });

  return words.join(' ');
}

/**
 * Format amount in Naira words.
 */
export function formatMoneyInWords(amount: number): string {
  const naira = Math.floor(amount);
  const kobo = Math.round((amount - naira) * 100);

  let result = numberToWords(naira) + ' Naira';
  if (kobo > 0) {
    result += ' and ' + numberToWords(kobo) + ' Kobo';
  }

  return result;
}

/**
 * Format number as Nigerian Naira currency.
 */
export function formatCurrency(amount: number): string {
  return new Intl.NumberFormat('en-NG', {
    style: 'currency',
    currency: 'NGN',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(amount);
}

/**
 * Normalize Nigerian phone number to +234 format.
 */
export function normalizePhoneNumber(phone: string): string {
  const cleaned = phone.replace(/[^\d+]/g, '');
  if (cleaned.startsWith('0')) {
    return '+234' + cleaned.slice(1);
  }
  if (cleaned.startsWith('234')) {
    return '+' + cleaned;
  }
  return cleaned;
}

/**
 * Get current month name.
 */
export function getCurrentMonth(): string {
  const months = [
    'January', 'February', 'March', 'April', 'May', 'June',
    'July', 'August', 'September', 'October', 'November', 'December'
  ];
  return months[new Date().getMonth()];
}
