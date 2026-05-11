import React, { useState } from 'react';
import OverviewTab from './OverviewTab';
import PreventionTab from './PreventionTab';
import ChallengesTab from './ChallengesTab';

function LabView({ selectedVuln, user, onAttackDetected, onProgress }) {
  const [selectedTab, setSelectedTab] = useState('overview');

  if (!selectedVuln) {
    return (
      <div className="lab-welcome">
        <h2>🧪 OWASP Top 10 for LLMs (2025)</h2>
        <p className="lab-intro">
          Learn about the most critical security risks for Large Language Model applications. Select
          a vulnerability from the left menu to explore its description, impact, and remediation
          strategies.
        </p>

        <div className="lab-features">
          <div className="feature-card">
            <span className="feature-icon">📚</span>
            <h3>Understand</h3>
            <p>
              Learn about each vulnerability with detailed descriptions and real-world impact
              scenarios
            </p>
          </div>
          <div className="feature-card">
            <span className="feature-icon">🎯</span>
            <h3>Explore</h3>
            <p>Test vulnerabilities in the chat interface with click-to-test examples</p>
          </div>
          <div className="feature-card">
            <span className="feature-icon">🛡️</span>
            <h3>Secure</h3>
            <p>Study remediation strategies and best practices to prevent these vulnerabilities</p>
          </div>
        </div>

        <div className="getting-started">
          <h3>How to Use This Lab</h3>
          <ol>
            <li>Select a vulnerability from the left menu to read about it</li>
            <li>Explore the Overview, Attack Scenarios, and Prevention tabs</li>
            <li>Click "🧪 Test in Chat" on any example to pre-fill the chat</li>
            <li>Send the message and observe the system's response</li>
            <li>Learn from both successful and unsuccessful exploitation attempts</li>
          </ol>
        </div>
      </div>
    );
  }

  return (
    <div className="lab-content">
      <div className="lab-tabs">
        <button
          className={`lab-tab ${selectedTab === 'overview' ? 'active' : ''}`}
          onClick={() => setSelectedTab('overview')}
        >
          📋 Overview
        </button>
        {selectedVuln.challenges && selectedVuln.challenges.length > 0 && (
          <button
            className={`lab-tab ${selectedTab === 'challenges' ? 'active' : ''}`}
            onClick={() => setSelectedTab('challenges')}
          >
            🎮 Challenges ({selectedVuln.challenges.length})
          </button>
        )}
        <button
          className={`lab-tab ${selectedTab === 'prevention' ? 'active' : ''}`}
          onClick={() => setSelectedTab('prevention')}
        >
          🛡️ Prevention
        </button>
      </div>

      <div className="tab-content">
        {selectedTab === 'overview' && <OverviewTab selectedVuln={selectedVuln} />}
        {selectedTab === 'challenges' && selectedVuln.challenges && (
          <ChallengesTab
            selectedVuln={selectedVuln}
            user={user}
            onAttackDetected={onAttackDetected}
            onProgress={onProgress}
          />
        )}
        {selectedTab === 'prevention' && <PreventionTab selectedVuln={selectedVuln} />}
      </div>
    </div>
  );
}

export default LabView;
