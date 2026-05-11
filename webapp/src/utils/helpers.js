/**
 * Strips box-drawing characters and normalizes whitespace from attack response text.
 */
export function formatAttackResponse(text) {
  if (!text) return text;
  return text
    .replace(/^[╔╚][═]+[╗╝]\s*$/gm, '')
    .replace(/^║\s*(.*?)\s*║\s*$/gm, '$1')
    .replace(/[━]{2,}/g, '---')
    .replace(/[─]{2,}/g, '---')
    .replace(/\n{3,}/g, '\n\n')
    .trim();
}

/**
 * Parses an overview text string into structured block objects (paragraphs, bullets).
 */
export function parseOverview(text) {
  if (!text) return [];
  const blocks = [];
  const lines = text.split('\n');
  let currentBullets = [];
  let currentParagraph = '';

  const flushParagraph = () => {
    if (currentParagraph.trim()) {
      blocks.push({ type: 'paragraph', text: currentParagraph.trim() });
      currentParagraph = '';
    }
  };
  const flushBullets = () => {
    if (currentBullets.length > 0) {
      blocks.push({ type: 'bullets', items: [...currentBullets] });
      currentBullets = [];
    }
  };

  for (const line of lines) {
    const trimmed = line.trim();
    if (trimmed === '') {
      flushBullets();
      flushParagraph();
    } else if (trimmed.startsWith('- ')) {
      flushParagraph();
      currentBullets.push(trimmed.slice(2));
    } else {
      flushBullets();
      if (currentParagraph) currentParagraph += ' ' + trimmed;
      else currentParagraph = trimmed;
    }
  }
  flushBullets();
  flushParagraph();
  return blocks;
}

/**
 * Parses formatted attack response text into structured token/section objects for rendering.
 */
export function parseAttackResponseSections(text) {
  if (!text) return [];
  const formatted = formatAttackResponse(text);
  const lines = formatted.split('\n');

  // Phase 1: tokenize
  const tokens = [];
  for (const line of lines) {
    const trimmed = line.trim();
    if (!trimmed || trimmed === '---') continue;

    if (/^\[([A-Z\s/]+)\]\s*(.+)/.test(trimmed)) {
      const m = trimmed.match(/^\[([A-Z\s/]+)\]\s*(.+)/);
      tokens.push({ t: 'log', label: m[1], value: m[2] });
    } else if (/^✅/.test(trimmed)) {
      tokens.push({ t: 'complete', text: trimmed });
    } else if (/^VULNERABLE RESPONSE.*:$/i.test(trimmed)) {
      tokens.push({ t: 'section-header', title: 'Vulnerable Response (simulation)', variant: 'vuln' });
    } else if (/^-{2,}\s+(.+?)\s+-{2,}$/.test(trimmed)) {
      const m = trimmed.match(/^-{2,}\s+(.+?)\s+-{2,}$/);
      tokens.push({ t: 'section-header', title: m[1], variant: 'info' });
    } else if (/^[•·]\s/.test(trimmed)) {
      tokens.push({ t: 'bullet', text: trimmed.replace(/^[•·]\s*/, '') });
    } else if (/^.{3,60}:\s*$/.test(trimmed) && !/https?:/.test(trimmed)) {
      const title = trimmed.replace(/:$/, '').replace(/^EDUCATION NOTE$/i, 'Education Note');
      tokens.push({ t: 'section-header', title, variant: 'info' });
    } else {
      tokens.push({ t: 'text', text: trimmed });
    }
  }

  // Phase 2: group into sections
  const sections = [];
  let i = 0;
  while (i < tokens.length) {
    const tok = tokens[i];

    if (tok.t === 'log' || tok.t === 'complete') {
      sections.push(tok);
      i++;
      continue;
    }

    if (tok.t === 'section-header') {
      const items = [];
      i++;
      while (
        i < tokens.length &&
        tokens[i].t !== 'section-header' &&
        tokens[i].t !== 'log' &&
        tokens[i].t !== 'complete'
      ) {
        items.push(tokens[i].text);
        i++;
      }
      sections.push({ t: 'section', title: tok.title, variant: tok.variant, items });
      continue;
    }

    const textLines = [];
    while (i < tokens.length && (tokens[i].t === 'text' || tokens[i].t === 'bullet')) {
      textLines.push(tokens[i].text);
      i++;
    }
    const isTitle = sections.length === 0 && textLines.length > 0 && textLines.length <= 3;
    sections.push({ t: isTitle ? 'title' : 'paragraph', lines: textLines });
  }

  return sections;
}

/**
 * Extracts a human-readable error message from an axios error response.
 */
export function parseApiError(err) {
  const detail = err.response?.data?.detail;
  if (!detail) return err.message || 'Request failed';
  if (Array.isArray(detail)) return detail.map(d => d.msg || JSON.stringify(d)).join('; ');
  if (typeof detail === 'string') return detail;
  return JSON.stringify(detail);
}

/**
 * Normalizes a raw user object from the API, ensuring `id` is a number.
 */
export function normalizeUser(userData) {
  if (!userData) return null;
  return {
    ...userData,
    id: parseInt(userData.id, 10),
  };
}
