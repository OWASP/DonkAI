import client from './client';

export async function submitChallengeAttempt(vulnId, challengeId, payload, userId) {
  const response = await client.post(`/challenges/${vulnId}/attempt`, {
    challenge_id: challengeId,
    payload,
    user_id: parseInt(userId, 10),
  });
  return response.data;
}

export async function fetchChallengeHistory(vulnId, challengeId, userId) {
  const response = await client.get(`/challenges/${vulnId}/${challengeId}/history`, {
    params: { user_id: parseInt(userId, 10) },
  });
  return response.data.attempts || [];
}
