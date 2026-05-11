import React from 'react';
import { parseOverview } from '../utils/helpers';

function OverviewTab({ selectedVuln }) {
  const blocks = parseOverview(selectedVuln.overview);

  return (
    <div className="tab-content">
      <div className="tab-hero">
        <div className="tab-hero-badge">
          {selectedVuln.icon} {selectedVuln.code}
        </div>
        <h2 className="tab-hero-title">{selectedVuln.name}</h2>
        <div className="tab-hero-meta">
          <span
            className={`tab-hero-severity tab-hero-severity--${selectedVuln.severity?.toLowerCase()}`}
          >
            {selectedVuln.severity}
          </span>
          {selectedVuln.owasp_url && (
            <a
              href={selectedVuln.owasp_url}
              target="_blank"
              rel="noopener noreferrer"
              className="tab-hero-link"
            >
              OWASP Reference ↗
            </a>
          )}
        </div>
      </div>

      <div className="overview-flow">
        {blocks.map((block, idx) => {
          const isHeader = block.type === 'paragraph' && block.text.endsWith(':');
          if (isHeader) {
            return (
              <h4 key={idx} className="overview-section-title">
                {block.text.slice(0, -1)}
              </h4>
            );
          }
          if (block.type === 'paragraph') {
            return (
              <div key={idx} className={`overview-card ${idx === 0 ? 'overview-card--intro' : ''}`}>
                <p>{block.text}</p>
              </div>
            );
          }
          if (block.type === 'bullets') {
            return (
              <div key={idx} className="overview-list-card">
                {block.items.map((item, i) => {
                  const colonIdx = item.indexOf(':');
                  const hasLabel = colonIdx > 0 && colonIdx < 60;
                  return (
                    <div key={i} className="overview-list-item">
                      <div className="overview-list-dot" />
                      <div className="overview-list-text">
                        {hasLabel ? (
                          <>
                            <strong>{item.slice(0, colonIdx)}</strong>
                            {item.slice(colonIdx)}
                          </>
                        ) : (
                          item
                        )}
                      </div>
                    </div>
                  );
                })}
              </div>
            );
          }
          return null;
        })}
      </div>
    </div>
  );
}

export default OverviewTab;
