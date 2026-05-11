import client from './client';

export async function fetchSessions(userId) {
  const response = await client.get(`/sessions/user/${parseInt(userId, 10)}`);
  return response.data.sessions || [];
}

export async function fetchMessages(sessionId, userId) {
  const response = await client.post('/session/history', {
    session_id: sessionId,
    user_id: parseInt(userId, 10),
  });
  return response.data.messages || [];
}

export async function createSession(userId, title) {
  const response = await client.post('/session/new', {
    user_id: parseInt(userId, 10),
    title,
  });
  return response.data.session;
}

export async function deleteSession(sessionId, userId) {
  await client.delete(`/session/${sessionId}?user_id=${parseInt(userId, 10)}`);
}

export async function deleteAllSessions(userId) {
  await client.delete(`/sessions/user/${parseInt(userId, 10)}`);
}
