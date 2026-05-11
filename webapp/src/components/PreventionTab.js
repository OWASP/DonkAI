import React from 'react';
import { PREVENTION_CATEGORY_ICONS } from '../utils/constants';

function getIcon(category) {
  for (const [key, icon] of Object.entries(PREVENTION_CATEGORY_ICONS)) {
    if (category.toLowerCase().includes(key.toLowerCase())) return icon;
  }
  return '🛡️';
}

function PreventionTab({ selectedVuln }) {
  const strategies = selectedVuln.prevention?.strategies || [];

  if (strategies.length === 0) {
    return (
      <div className="tab-content">
        <p className="empty-state">No prevention strategies available.</p>
      </div>
    );
  }

  return (
    <div className="tab-content">
      <div className="tab-section-header">
        <h3>Defense Strategies</h3>
        <span className="tab-section-count">{strategies.length} categories</span>
      </div>

      <div className="prev-grid">
        {strategies.map((strategy, idx) => {
          const isWarning = strategy.category.toLowerCase().includes('not');
          return (
            <div key={idx} className={`prev-card ${isWarning ? 'prev-card--warning' : ''}`}>
              <div className="prev-card-header">
                <span className="prev-card-icon">{getIcon(strategy.category)}</span>
                <h4 className="prev-card-title">{strategy.category}</h4>
              </div>
              <div className="prev-card-measures">
                {strategy.measures.map((measure, mIdx) => {
                  const colonIdx = measure.indexOf(':');
                  const hasLabel = colonIdx > 0 && colonIdx < 50;
                  return (
                    <div key={mIdx} className="prev-measure">
                      <div
                        className={`prev-measure-dot ${isWarning ? 'prev-measure-dot--warning' : ''}`}
                      />
                      <span className="prev-measure-text">
                        {hasLabel ? (
                          <>
                            <strong>{measure.slice(0, colonIdx)}</strong>
                            {measure.slice(colonIdx)}
                          </>
                        ) : (
                          measure
                        )}
                      </span>
                    </div>
                  );
                })}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

export default PreventionTab;
