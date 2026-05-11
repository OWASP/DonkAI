import { useState, useEffect } from 'react';
import { fetchVulnerabilities } from '../api/vulnerabilities';

/**
 * Fetches the OWASP Top 10 LLM vulnerability list from the backend.
 * Caches the result for the lifetime of the app session.
 *
 * @returns {{ vulnerabilities: Array, loading: boolean, error: string|null }}
 */

let _cache = null;

export function useVulnerabilities() {
  const [vulnerabilities, setVulnerabilities] = useState(_cache || []);
  const [loading, setLoading] = useState(!_cache);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (_cache) return;

    let cancelled = false;
    setLoading(true);

    fetchVulnerabilities()
      .then((data) => {
        if (!cancelled) {
          _cache = data;
          setVulnerabilities(data);
        }
      })
      .catch((err) => {
        if (!cancelled) {
          setError(err.message || 'Failed to load vulnerabilities');
        }
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });

    return () => {
      cancelled = true;
    };
  }, []);

  return { vulnerabilities, loading, error };
}
