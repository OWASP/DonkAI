import client from './client';

export async function sendChatMessage(message, userId, sessionId) {
  const response = await client.post('/chat', {
    message,
    user_id: parseInt(userId, 10),
    session_id: sessionId || null,
  });
  return response.data;
}
