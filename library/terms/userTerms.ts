/**
 * User-Added Terminology Terms
 * 
 * This file stores terms that users add via the Knowledge Base Modal.
 * These terms are merged with system-defined terms from other files.
 * 
 * Structure follows the TermMapping interface from types/terminology.ts
 */

import { TermMapping } from '../../types/terminology';

// User-added terms storage (initially empty, populated at runtime)
export const USER_ADDED_TERMS: TermMapping[] = [];

// Helper to get combined user terms
export function getUserTerms(): TermMapping[] {
    // Try to load from localStorage
    try {
        const stored = localStorage.getItem('financial_calculator_user_terms');
        if (stored) {
            return JSON.parse(stored);
        }
    } catch (e) {
        console.warn('Failed to load user terms from localStorage:', e);
    }
    return USER_ADDED_TERMS;
}

// Helper to save user terms
export function saveUserTerms(terms: TermMapping[]): void {
    try {
        localStorage.setItem('financial_calculator_user_terms', JSON.stringify(terms));
    } catch (e) {
        console.error('Failed to save user terms to localStorage:', e);
    }
}

// Helper to identify user-added terms (those not in system defaults)
export function isUserAddedTerm(termId: string, systemTermIds: Set<string>): boolean {
    return !systemTermIds.has(termId);
}

export default USER_ADDED_TERMS;
