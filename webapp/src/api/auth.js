import client from './client';

export async function login(username, password) {
  const response = await client.post('/auth/login', { username, password });
  return response.data?.user;
}

export async function register(username, password) {
  const response = await client.post('/auth/register', { username, password });
  return response.data?.user;
}
