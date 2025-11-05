import { clsx, type ClassValue } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

/**
 * Format currency in Indian Rupees
 */
export function formatCurrency(amount: number): string {
  const currencySymbol = import.meta.env.VITE_CURRENCY_SYMBOL || '₹';
  return `${currencySymbol}${amount.toFixed(2)}`;
}

/**
 * Format number in Indian numbering system (with commas)
 */
export function formatIndianNumber(num: number): string {
  return num.toLocaleString('en-IN');
}

/**
 * Format currency with Indian numbering system
 */
export function formatIndianCurrency(amount: number): string {
  const currencySymbol = import.meta.env.VITE_CURRENCY_SYMBOL || '₹';
  return `${currencySymbol}${formatIndianNumber(amount)}`;
}
