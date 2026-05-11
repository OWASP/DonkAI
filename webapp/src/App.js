import React, { useState, useEffect } from 'react';
import ChatInterface from './components/ChatInterface';
import './styles/App.css';
import { login, register } from './api/auth';
import { parseApiError, normalizeUser } from './utils/helpers';

function App() {
  const [user, setUser] = useState(null);
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [isRegister, setIsRegister] = useState(false);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    try {
      const storedUser = localStorage.getItem('user');
      if (storedUser) {
        const parsed = normalizeUser(JSON.parse(storedUser));
        if (parsed && !isNaN(parsed.id)) {
          setUser(parsed);
        } else {
          localStorage.removeItem('user');
        }
      }
    } catch {
      localStorage.removeItem('user');
    }
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      const rawUser = isRegister
        ? await register(username, password)
        : await login(username, password);

      const userData = normalizeUser(rawUser);
      if (!userData || isNaN(userData.id)) {
        setError(`${isRegister ? 'Registration' : 'Login'} failed: invalid server response`);
        return;
      }

      setUser(userData);
      localStorage.setItem('user', JSON.stringify(userData));
      setUsername('');
      setPassword('');
      if (isRegister) setIsRegister(false);
    } catch (err) {
      setError(parseApiError(err));
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    setUser(null);
    localStorage.removeItem('user');
  };

  if (user) {
    return <ChatInterface user={user} onLogout={handleLogout} />;
  }

  return (
    <div className="App">
      <div className="auth-container">
        <div className="auth-card">
          <div className="auth-header">
            <h1>🔐 DonkAI</h1>
            <p className="auth-subtitle">OWASP Top 10 for LLMs 2025</p>
          </div>

          <form onSubmit={handleSubmit} className="auth-form">
            <div className="form-group">
              <label htmlFor="username">Username</label>
              <input
                id="username"
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                placeholder="Enter username"
                required
                disabled={loading}
              />
            </div>

            <div className="form-group">
              <label htmlFor="password">Password</label>
              <input
                id="password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Enter password"
                required
                disabled={loading}
              />
            </div>

            {error && <div className="error-message">{error}</div>}

            <button type="submit" className="auth-button" disabled={loading}>
              {loading ? 'Please wait...' : isRegister ? 'Register' : 'Login'}
            </button>

            <button
              type="button"
              onClick={() => {
                setIsRegister(!isRegister);
                setError('');
              }}
              className="toggle-auth-button"
              disabled={loading}
            >
              {isRegister ? 'Already have an account? Login' : 'Need an account? Register'}
            </button>
          </form>

          <div className="auth-footer">
            <p className="warning-text">
              ⚠️ <strong>Educational Environment</strong>
              <br />
              This system contains intentional vulnerabilities for learning purposes.
            </p>
            <p className="demo-credentials">
              <strong>Demo Account:</strong> alice / password123
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
