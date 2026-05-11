import React from 'react';
import { parseAttackResponseSections } from '../utils/helpers';

function renderBulletItem(item, j) {
  const colonIdx = item.indexOf(':');
  const hasLabel = colonIdx > 0 && colonIdx < 45;
  return (
    <div key={j} className="attack-education-item">
      <div className="attack-education-dot" />
      <span>
        {hasLabel ? (
          <>
            <strong>{item.slice(0, colonIdx)}</strong>
            {item.slice(colonIdx)}
          </>
        ) : (
          item
        )}
      </span>
    </div>
  );
}

function AttackResultBody({ text }) {
  if (!text) return null;
  const sections = parseAttackResponseSections(text);

  return (
    <div className="attack-body">
      {sections.map((sec, idx) => {
        if (sec.t === 'log') {
          return (
            <div key={idx} className="attack-log-row">
              <span className="attack-log-label">{sec.label}</span>
              <span className="attack-log-value">{sec.value}</span>
            </div>
          );
        }
        if (sec.t === 'complete') {
          return (
            <div key={idx} className="attack-complete">
              {sec.text}
            </div>
          );
        }
        if (sec.t === 'title') {
          return (
            <div key={idx} className="attack-title-block">
              {sec.lines.map((l, j) => (
                <div key={j}>{l}</div>
              ))}
            </div>
          );
        }
        if (sec.t === 'paragraph') {
          return (
            <div key={idx} className="attack-paragraph">
              {sec.lines.map((l, j) => (
                <div key={j}>{l}</div>
              ))}
            </div>
          );
        }
        if (sec.t === 'section') {
          if (sec.variant === 'vuln') {
            return (
              <div key={idx} className="attack-vuln-response">
                <div className="attack-vuln-title">{sec.title}</div>
                <p>{sec.items.join(' ')}</p>
              </div>
            );
          }
          return (
            <div key={idx} className="attack-education">
              <div className="attack-education-title">{sec.title}</div>
              {sec.items.map(renderBulletItem)}
            </div>
          );
        }
        return null;
      })}
    </div>
  );
}

export default AttackResultBody;
