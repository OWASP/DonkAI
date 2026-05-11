import client from './client';

/**
 * Fetches the full list of vulnerabilities (metadata + overview + challenges + prevention).
 * @returns {Promise<Array>} Array of vulnerability objects
 */
export async function fetchVulnerabilities() {
  const response = await client.get('/vulnerabilities');
  return response.data.vulnerabilities || [];
}

/**
 * Fetches a single vulnerability by its id (e.g. 'llm01').
 * @param {string} vulnId
 * @returns {Promise<Object>} Vulnerability object
 */
export async function fetchVulnerability(vulnId) {
  const response = await client.get(`/vulnerabilities/${vulnId}`);
  return response.data;
}
