import React, { useState, useEffect } from 'react';
import AttackResultBody from './AttackResultBody';
import { submitChallengeAttempt, fetchChallengeHistory } from '../api/challenges';

function ChallengesTab({ selectedVuln, user, onAttackDetected, onProgress }) {
  const [activeChallenge, setActiveChallenge] = useState(null);
  const [payload, setPayload] = useState('');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [hintsRevealed, setHintsRevealed] = useState(0);
  const [attempts, setAttempts] = useState(0);
  const [solved, setSolved] = useState(false);
  const [allSolved, setAllSolved] = useState({});
  const [history, setHistory] = useState([]);
  const [historyOpen, setHistoryOpen] = useState(false);
  const [historyLoading, setHistoryLoading] = useState(false);
  const [expandedAttempt, setExpandedAttempt] = useState(null);

  const solvedChallenges = allSolved[selectedVuln.id] || {};

  useEffect(() => {
    setActiveChallenge(null);
    setSolved(false);
    setResult(null);
    setPayload('');
  }, [selectedVuln.id]);

  useEffect(() => {
    if (onProgress) {
      onProgress(
        selectedVuln.id,
        Object.keys(solvedChallenges).length,
        selectedVuln.challenges.length
      );
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [solvedChallenges, selectedVuln.id]);

  useEffect(() => {
    if (historyOpen && activeChallenge) {
      loadHistory(activeChallenge);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [historyOpen, activeChallenge?.id]);

  const loadHistory = async (ch) => {
    if (!ch || !user?.id) return;
    setHistoryLoading(true);
    try {
      const vulnId = selectedVuln?.id || 'llm01';
      const cid = ch.challengeId || ch.id;
      const attempts = await fetchChallengeHistory(vulnId, cid, user.id);
      setHistory(attempts);
    } catch {
      setHistory([]);
    } finally {
      setHistoryLoading(false);
    }
  };

  const selectChallenge = (ch) => {
    setActiveChallenge(ch);
    setPayload('');
    setResult(null);
    setHintsRevealed(0);
    setAttempts(0);
    setSolved(!!solvedChallenges[ch.id]);
    setHistory([]);
    setHistoryOpen(false);
    setExpandedAttempt(null);
  };

  const submitAttempt = async () => {
    if (!payload.trim() || loading) return;
    setLoading(true);
    try {
      const vulnId = selectedVuln?.id || 'llm01';
      const data = await submitChallengeAttempt(
        vulnId,
        activeChallenge.challengeId || activeChallenge.id,
        payload,
        user.id
      );
      setResult(data);
      setAttempts((p) => p + 1);
      if (data.success) {
        setSolved(true);
        setAllSolved((p) => ({
          ...p,
          [selectedVuln.id]: { ...(p[selectedVuln.id] || {}), [activeChallenge.id]: true },
        }));
        if (onAttackDetected) onAttackDetected(data);
      }
      if (historyOpen) loadHistory(activeChallenge);
    } catch (err) {
      setResult({ success: false, blocked: false, reason: 'Connection error', response: err.message });
    } finally {
      setLoading(false);
    }
  };

  const handleKey = (e) => {
    if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) submitAttempt();
  };

  const solvedCount = Object.keys(solvedChallenges).length;
  const total = selectedVuln.challenges.length;

  if (!activeChallenge) {
    return (
      <div className="tab-content">
        <div className="tab-section-header">
          <h3>{selectedVuln.code} — Challenges</h3>
          <div className="ch-progress-compact">
            <span className="ch-progress-text">
              {solvedCount}/{total}
            </span>
            <div className="ch-progress-bar">
              <div
                className="ch-progress-fill"
                style={{ width: `${(solvedCount / total) * 100}%` }}
              />
            </div>
          </div>
        </div>

        <div className="ch-intro-banner">
          Each challenge has a specific defense to bypass. Craft your own payload — templates are
          starting points, not solutions.
        </div>

        <div className="ch-cards-grid">
          {selectedVuln.challenges.map((ch, idx) => {
            const isSolved = !!solvedChallenges[ch.id];
            return (
              <button
                key={ch.id}
                className={`ch-card ${isSolved ? 'ch-card--solved' : ''}`}
                onClick={() => selectChallenge(ch)}
              >
                <div className="ch-card-top">
                  <span className="ch-card-number">{String(idx + 1).padStart(2, '0')}</span>
                  {isSolved && <span className="ch-card-solved-pill">SOLVED</span>}
                </div>
                <div className="ch-card-name">{ch.name.replace(/Challenge \d+: /, '')}</div>
                <div className="ch-card-tagline">{ch.tagline}</div>
                <div className="ch-card-footer">
                  <span className="ch-card-defense">{ch.defense.replace(/[🛡️⚠️]/g, '').trim()}</span>
                  <span className="ch-card-go">Start →</span>
                </div>
              </button>
            );
          })}
        </div>
      </div>
    );
  }

  const resultType = result ? (result.success ? 'success' : result.blocked ? 'blocked' : 'near') : null;
  const challengeIdx = selectedVuln.challenges.indexOf(activeChallenge) + 1;

  return (
    <div className="tab-content">
      <div className="ch-nav">
        <button className="ch-back" onClick={() => setActiveChallenge(null)}>
          ← Back
        </button>
        <div className="ch-nav-info">
          <span className="ch-nav-number">{String(challengeIdx).padStart(2, '0')}</span>
          <span className="ch-nav-name">{activeChallenge.name}</span>
          {solved && <span className="ch-solved-badge">Solved</span>}
        </div>
        <span className="ch-attempt-count">{attempts} attempts</span>
      </div>

      <div className="ch-layout">
        <div className="ch-block">
          <div className="ch-block-label">Scenario</div>
          <p className="ch-block-text">{activeChallenge.backstory}</p>
        </div>

        <div className="ch-block ch-block--goal">
          <div className="ch-block-label">Objective</div>
          <p className="ch-block-text">{activeChallenge.target}</p>
        </div>

        <div className="ch-block ch-block--defense">
          <div className="ch-block-label">Active Defense</div>
          <p className="ch-block-text">{activeChallenge.defense.replace(/[🛡️⚠️]/g, '').trim()}</p>
        </div>

        <div className="ch-ws-section">
          <div className="ch-ws-label">
            Template <span className="ch-ws-sublabel">— modify, don't copy</span>
          </div>
          <div className="ch-template-box">
            <code className="ch-template-text">{activeChallenge.template}</code>
          </div>
        </div>

        <div className="ch-ws-section">
          <div className="ch-ws-label">
            Your Payload
            {!solved && <span className="ch-ws-sublabel"> — Ctrl+Enter to submit</span>}
          </div>
          <div className="ch-input-wrap">
            <textarea
              className="ch-payload-input"
              value={payload}
              onChange={(e) => setPayload(e.target.value)}
              onKeyDown={handleKey}
              placeholder={activeChallenge.placeholder}
              rows={6}
              disabled={loading || solved}
              autoFocus
            />
          </div>
          <button
            className={`ch-submit ${solved ? 'ch-submit--solved' : ''} ${loading ? 'ch-submit--loading' : ''}`}
            onClick={submitAttempt}
            disabled={loading || solved || !payload.trim()}
          >
            {loading ? (
              <>
                <span className="ch-spinner" /> Evaluating...
              </>
            ) : solved ? (
              '✓ Challenge Complete'
            ) : (
              'Execute Payload'
            )}
          </button>
          {solved && (
            <button
              className="ch-reset"
              onClick={() => {
                setPayload('');
                setResult(null);
                setAttempts(0);
                setSolved(false);
                setHintsRevealed(0);
              }}
            >
              Reset Challenge
            </button>
          )}
        </div>

        {result && (
          <div className={`ch-result ch-result--${resultType}`}>
            <div className="ch-result-header">
              {resultType === 'success' ? (
                <>
                  <span className="ch-result-icon">🔓</span>
                  <div className="ch-result-info">
                    <span className="ch-result-title">Attack Succeeded</span>
                    <span className="ch-result-subtitle">Defense bypassed — injection accepted</span>
                  </div>
                  <span className="ch-solved-badge">Solved</span>
                </>
              ) : (
                <>
                  <span className="ch-result-icon">{resultType === 'blocked' ? '🛡️' : '⚡'}</span>
                  <span className="ch-result-title">
                    {resultType === 'blocked' ? 'Blocked by Filter' : 'Filter Bypassed — Refine Payload'}
                  </span>
                </>
              )}
            </div>
            <AttackResultBody text={result.response} />
          </div>
        )}

        <div className="ch-hints-section">
          <div className="ch-hints-header">
            <span className="ch-block-label">
              Hints ({hintsRevealed}/{activeChallenge.hints.length})
            </span>
            {!solved && hintsRevealed < activeChallenge.hints.length && (
              <button className="ch-hint-btn" onClick={() => setHintsRevealed((h) => h + 1)}>
                Reveal {hintsRevealed === 0 ? 'hint' : 'next'}
              </button>
            )}
          </div>
          {hintsRevealed === 0 ? (
            <p className="ch-hints-empty">Try on your own first.</p>
          ) : (
            <div className="ch-hints-list">
              {activeChallenge.hints.slice(0, hintsRevealed).map((hint, i) => (
                <div key={i} className="ch-hint-item">
                  <span className="ch-hint-num">{i + 1}</span>
                  <span className="ch-hint-text">{hint.replace(/🔍 Hint \d+: |🔍 /g, '')}</span>
                </div>
              ))}
            </div>
          )}
        </div>

        {solved && activeChallenge.educationOnSuccess && (
          <div className="ch-debrief">
            <div className="ch-debrief-header">Debrief</div>
            <AttackResultBody text={activeChallenge.educationOnSuccess} />
          </div>
        )}

        <div className="ch-history">
          <button
            className="ch-history-toggle"
            onClick={() => setHistoryOpen((o) => !o)}
            type="button"
          >
            <span>{historyOpen ? '▾' : '▸'}</span>
            <span>Attempt history</span>
            {history.length > 0 && (
              <span className="ch-history-count">
                {history.filter((a) => a.success).length}✓ / {history.length}
              </span>
            )}
          </button>
          {historyOpen && (
            <div className="ch-history-body">
              {historyLoading ? (
                <div className="ch-history-empty">Loading…</div>
              ) : history.length === 0 ? (
                <div className="ch-history-empty">
                  No attempts yet — submit a payload to start tracking.
                </div>
              ) : (
                <ul className="ch-history-list">
                  {history.map((a) => (
                    <li
                      key={a.id}
                      className={`ch-history-item ${
                        a.success ? 'ch-history-item--success' : 'ch-history-item--fail'
                      }`}
                    >
                      <div
                        className="ch-history-row"
                        onClick={() =>
                          setExpandedAttempt(expandedAttempt === a.id ? null : a.id)
                        }
                      >
                        <span className="ch-history-badge">{a.success ? '✓' : '✗'}</span>
                        <span className="ch-history-payload">{a.payload}</span>
                        <span className="ch-history-time">
                          {new Date(a.created_at + 'Z').toLocaleString()}
                        </span>
                      </div>
                      {expandedAttempt === a.id && a.response && (
                        <div className="ch-history-response">
                          <div className="ch-history-response-label">Response</div>
                          <pre className="ch-history-response-text">{a.response}</pre>
                        </div>
                      )}
                    </li>
                  ))}
                </ul>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default ChallengesTab;
