// hooks/useRetry.js — Generic retry hook with exponential backoff
// Usage: const { execute, isLoading, error, attempts } = useRetry(asyncFn, options)
import { useState, useCallback, useRef } from 'react';

const DEFAULT_OPTIONS = {
  maxAttempts: 3,       // Maximum number of tries (including the first)
  baseDelayMs: 500,     // Initial delay before first retry (ms)
  maxDelayMs: 10_000,   // Cap on backoff delay (ms)
  factor: 2,            // Exponential backoff multiplier
  retryOn: () => true,  // Predicate — return false to abort retries early
};

/**
 * useRetry — wraps an async function with configurable retry/backoff logic.
 *
 * @param {Function} asyncFn  - The async function to retry. Receives forwarded args.
 * @param {Object}   options  - Optional overrides for DEFAULT_OPTIONS.
 * @returns {{ execute, isLoading, error, attempts, reset }}
 */
export function useRetry(asyncFn, options = {}) {
  const config = { ...DEFAULT_OPTIONS, ...options };
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError]         = useState(null);
  const [attempts, setAttempts]   = useState(0);
  const abortedRef = useRef(false); // prevents state updates after unmount

  const reset = useCallback(() => {
    setIsLoading(false);
    setError(null);
    setAttempts(0);
  }, []);

  const execute = useCallback(async (...args) => {
    abortedRef.current = false;
    setIsLoading(true);
    setError(null);
    setAttempts(0);

    let lastError = null;

    for (let attempt = 1; attempt <= config.maxAttempts; attempt++) {
      if (abortedRef.current) break;

      try {
        if (!abortedRef.current) setAttempts(attempt);
        const result = await asyncFn(...args);
        if (!abortedRef.current) {
          setIsLoading(false);
          setError(null);
        }
        return result;
      } catch (err) {
        lastError = err;

        const isLastAttempt = attempt === config.maxAttempts;
        const shouldRetry = !isLastAttempt && config.retryOn(err, attempt);

        if (!shouldRetry) break;

        // Exponential backoff with jitter
        const delay = Math.min(
          config.baseDelayMs * Math.pow(config.factor, attempt - 1) + Math.random() * 200,
          config.maxDelayMs
        );
        await new Promise((resolve) => setTimeout(resolve, delay));
      }
    }

    if (!abortedRef.current) {
      setIsLoading(false);
      setError(lastError);
    }
    return null;
  }, [asyncFn, config.maxAttempts, config.baseDelayMs, config.maxDelayMs, config.factor]); // eslint-disable-line react-hooks/exhaustive-deps

  // Call this in useEffect cleanup to prevent stale state updates
  const abort = useCallback(() => {
    abortedRef.current = true;
  }, []);

  return { execute, isLoading, error, attempts, reset, abort };
}
