import React from 'react';
import { formatAttackResponse } from '../utils/helpers';
import { EXAMPLE_QUESTIONS } from '../utils/constants';

function ChatView({
  messages,
  inputMessage,
  setInputMessage,
  sendMessage,
  loading,
  messagesEndRef,
  onExampleClick,
}) {
  return (
    <>
      <div className="messages-container">
        {messages.length === 0 ? (
          <div className="empty-chat">
            <h2>🤖 Country Knowledge Chatbot</h2>
            <p>Ask me questions about countries around the world!</p>

            <div className="example-queries">
              <h4>Example Questions:</h4>
              <div className="query-grid">
                {EXAMPLE_QUESTIONS.map((question, index) => (
                  <span
                    key={index}
                    className="query-chip"
                    onClick={() => onExampleClick(question)}
                  >
                    {question}
                  </span>
                ))}
              </div>
            </div>

            <div className="warning-box">
              <span className="warning-icon">⚠️</span>
              <p>
                <strong>Educational Purpose:</strong> This system contains intentional security
                vulnerabilities. Explore the Top10 LLM tab to learn more!
              </p>
            </div>
          </div>
        ) : (
          messages.map((msg) => {
            const looksLikeAttack =
              msg.role === 'assistant' &&
              /[╔╚║━─]|^\[[A-Z]+\]|VULNERABLE RESPONSE/m.test(msg.content || '');
            const isAttack = !!msg.vulnerability || looksLikeAttack;
            return (
              <div key={msg.id} className={`message ${msg.role}`}>
                <div className="message-header">
                  <span className="message-icon">{msg.role === 'user' ? '👤' : '🤖'}</span>
                  <span className="message-role">
                    {msg.role === 'user' ? 'You' : 'Assistant'}
                  </span>
                  {msg.vulnerability && (
                    <span className="vulnerability-badge">⚠️ {msg.vulnerability}</span>
                  )}
                </div>
                {isAttack ? (
                  <pre className="message-content message-content--attack">
                    {formatAttackResponse(msg.content)}
                  </pre>
                ) : (
                  <div className="message-content">{msg.content}</div>
                )}
              </div>
            );
          })
        )}
        <div ref={messagesEndRef} />
      </div>

      <form onSubmit={sendMessage} className="input-form">
        <input
          type="text"
          value={inputMessage}
          onChange={(e) => setInputMessage(e.target.value)}
          placeholder="Type your message..."
          disabled={loading}
          className="message-input"
        />
        <button type="submit" disabled={loading} className="send-btn">
          {loading ? '...' : 'Send'}
        </button>
      </form>
    </>
  );
}

export default ChatView;
