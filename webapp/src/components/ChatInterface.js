import React, { useState, useEffect, useRef } from 'react';
import '../styles/ChatInterface.css';

import ChatView from './ChatView';
import LabView from './LabView';
import { useVulnerabilities } from '../hooks/useVulnerabilities';
import {
  fetchSessions,
  fetchMessages,
  createSession,
  deleteSession,
  deleteAllSessions,
} from '../api/sessions';
import { sendChatMessage } from '../api/chat';

function ChatInterface({ user, onLogout }) {
  const { vulnerabilities, loading: vulnLoading, error: vulnError } = useVulnerabilities();

  const [sessions, setSessions] = useState([]);
  const [currentSession, setCurrentSession] = useState(null);
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const [selectedVuln, setSelectedVuln] = useState(null);
  const [view, setView] = useState('chat');
  const [darkMode] = useState(false);
  const [attackMode, setAttackMode] = useState(false);
  const [vulnProgress, setVulnProgress] = useState({});
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    loadSessions();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    if (currentSession) loadMessages(currentSession.id);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [currentSession]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  useEffect(() => {
    const hasAttack = messages.some((msg) => msg.vulnerability);
    if (hasAttack) {
      setAttackMode(true);
      const timer = setTimeout(() => setAttackMode(false), 10000);
      return () => clearTimeout(timer);
    } else {
      setAttackMode(false);
    }
  }, [messages]);

  const loadSessions = async () => {
    try {
      const data = await fetchSessions(user.id);
      setSessions(data);
      if (data.length > 0) setCurrentSession(data[0]);
    } catch (err) {
      console.error('Error loading sessions:', err);
    }
  };

  const loadMessages = async (sessionId) => {
    try {
      const data = await fetchMessages(sessionId, user.id);
      setMessages(data);
    } catch (err) {
      console.error('Error loading messages:', err);
    }
  };

  const handleCreateSession = async () => {
    try {
      const newSession = await createSession(user.id, `Chat ${sessions.length + 1}`);
      setSessions([newSession, ...sessions]);
      setCurrentSession(newSession);
      setMessages([]);
      setView('chat');
      setAttackMode(false);
    } catch (err) {
      console.error('Error creating session:', err);
    }
  };

  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (!inputMessage.trim() || loading) return;

    const userMessage = inputMessage;
    setInputMessage('');
    setLoading(true);

    const tempUserMsg = {
      id: Date.now(),
      role: 'user',
      content: userMessage,
      created_at: new Date().toISOString(),
    };
    setMessages((prev) => [...prev, tempUserMsg]);

    try {
      const data = await sendChatMessage(userMessage, user.id, currentSession?.id);

      if (!currentSession && data.session_id) {
        await loadSessions();
        setCurrentSession({ id: data.session_id });
      }

      const assistantMsg = {
        id: Date.now() + 1,
        role: 'assistant',
        content: data.response,
        created_at: new Date().toISOString(),
        vulnerability: data.vulnerability_detected,
      };
      setMessages((prev) => [...prev, assistantMsg]);
    } catch (err) {
      console.error('Error sending message:', err);
      setMessages((prev) => [
        ...prev,
        {
          id: Date.now() + 1,
          role: 'assistant',
          content: 'Sorry, an error occurred. Please try again.',
          created_at: new Date().toISOString(),
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteSession = async (sessionId, e) => {
    e.stopPropagation();
    try {
      await deleteSession(sessionId, user.id);
      const updated = sessions.filter((s) => s.id !== sessionId);
      setSessions(updated);
      if (currentSession?.id === sessionId) {
        setCurrentSession(updated.length > 0 ? updated[0] : null);
        setMessages([]);
      }
    } catch (err) {
      console.error('Error deleting session:', err);
    }
  };

  const handleDeleteAllSessions = async () => {
    if (sessions.length === 0) return;
    try {
      await deleteAllSessions(user.id);
      setSessions([]);
      setCurrentSession(null);
      setMessages([]);
    } catch (err) {
      console.error('Error deleting all sessions:', err);
    }
  };

  const handleResetAttackMode = () => {
    setAttackMode(false);
    setMessages((prev) => prev.filter((msg) => !msg.vulnerability));
  };

  return (
    <div className={`chat-container ${darkMode ? 'dark-mode' : ''} ${attackMode ? 'attack-mode' : ''}`}>
      <div
        className={`sidebar-overlay ${sidebarOpen ? 'visible' : ''}`}
        onClick={() => setSidebarOpen(false)}
      />
      <div className={`sidebar ${sidebarOpen ? '' : 'collapsed'}`}>
        <div className="sidebar-header">
          <h2>🔐 DonkAI</h2>
          <button className="new-chat-btn" onClick={handleCreateSession}>
            + New Chat
          </button>
        </div>

        <div className="view-selector">
          <button
            className={`view-btn ${view === 'chat' ? 'active' : ''}`}
            onClick={() => setView('chat')}
          >
            💬 Chat
          </button>
          <button
            className={`view-btn ${view === 'lab' ? 'active' : ''}`}
            onClick={() => setView('lab')}
          >
            🧪 Top10 LLM
          </button>
        </div>

        {view === 'chat' ? (
          <div className="sessions-list">
            {sessions.length > 0 && (
              <button className="delete-all-btn" onClick={handleDeleteAllSessions}>
                🗑️ Delete all chats
              </button>
            )}
            {sessions.map((session) => (
              <div
                key={session.id}
                className={`session-item ${currentSession?.id === session.id ? 'active' : ''}`}
                onClick={() => setCurrentSession(session)}
              >
                <span className="session-icon">💬</span>
                <span className="session-title">{session.title}</span>
                <button
                  className="delete-session-btn"
                  onClick={(e) => handleDeleteSession(session.id, e)}
                  title="Delete chat"
                >
                  ✕
                </button>
              </div>
            ))}
          </div>
        ) : (
          <div className="vulnerabilities-menu">
            {vulnLoading && (
              <div className="vuln-loading">Loading vulnerabilities…</div>
            )}
            {vulnError && (
              <div className="vuln-error">⚠️ {vulnError}</div>
            )}
            {vulnerabilities.map((vuln) => {
              const prog = vulnProgress[vuln.id];
              const progressClass = prog
                ? prog.solved >= prog.total
                  ? 'vuln-header--complete'
                  : prog.solved > 0
                  ? 'vuln-header--partial'
                  : ''
                : '';
              return (
                <div key={vuln.id} className="vuln-menu-item">
                  <div
                    className={`vuln-header ${selectedVuln?.id === vuln.id ? 'active' : ''} ${progressClass}`}
                    onClick={() => setSelectedVuln(selectedVuln?.id === vuln.id ? null : vuln)}
                  >
                    <span className="vuln-icon">{vuln.icon}</span>
                    <span className="vuln-name">
                      {vuln.code}: {vuln.name}
                    </span>
                    {prog && prog.solved > 0 && (
                      <span className="vuln-progress-pill">
                        {prog.solved}/{prog.total}
                      </span>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>

      <div className="main-content-wrapper">
        <div className="main-content">
          <div className="top-bar">
            <button className="sidebar-toggle" onClick={() => setSidebarOpen((o) => !o)}>
              {sidebarOpen ? '✕' : '☰'}
            </button>
            {attackMode && <div className="attack-warning">⚠️ ATTACK DETECTED</div>}
            <h3 className="page-title">
              {view === 'chat'
                ? currentSession?.title || 'Select or create a chat'
                : selectedVuln
                ? `${selectedVuln.code}: ${selectedVuln.name}`
                : 'OWASP Top 10 for LLMs'}
            </h3>

            <div className="user-controls">
              {attackMode && (
                <button
                  className="reset-attack-btn"
                  onClick={handleResetAttackMode}
                  title="Reset Attack Mode"
                >
                  🔄 Reset Attack
                </button>
              )}
              <div className="user-menu">
                <span className="user-icon">👤</span>
                <span className="username">{user.username}</span>
              </div>
              <button className="icon-btn logout-btn" onClick={onLogout} title="Logout">
                🚪
              </button>
            </div>
          </div>

          {view === 'chat' ? (
            <ChatView
              messages={messages}
              inputMessage={inputMessage}
              setInputMessage={setInputMessage}
              sendMessage={handleSendMessage}
              loading={loading}
              messagesEndRef={messagesEndRef}
              onExampleClick={setInputMessage}
            />
          ) : (
            <LabView
              selectedVuln={selectedVuln}
              user={user}
              onAttackDetected={(data) => {
                setMessages((prev) => [
                  ...prev,
                  {
                    id: Date.now(),
                    role: 'assistant',
                    content: data.response,
                    vulnerability: data.vulnerability_detected,
                    created_at: new Date().toISOString(),
                  },
                ]);
                setAttackMode(true);
              }}
              onProgress={(vulnId, solved, total) =>
                setVulnProgress((p) => ({ ...p, [vulnId]: { solved, total } }))
              }
            />
          )}
        </div>
      </div>
    </div>
  );
}

export default ChatInterface;
