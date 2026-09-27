/* Shared browser/coach voice selection. Voice metadata does not expose gender. */
globalThis.EESpeech = (() => {
  const regions = ['en-US', 'en-GB', 'en-CA', 'en-AU', 'en-NZ'];
  const male = /\b(David|Guy|Mark|Daniel|Alex|Fred|Male|Christopher|Eric|Ryan|Andrew|Brian|Davis|Tony|James|Thomas|Oliver|William|Liam|George|Sean|Russell|Lee|Gordon|Arthur)\b/i;
  const female = /\b(Aria|Jenny|Zira|Samantha|Female|Ava|Emma|Susan|Karen|Moira|Libby|Sonia|Michelle|Ana|Allison|Victoria|Tessa|Serena|Hazel|Catherine|Natasha|Clara|Linda|Emily|Olivia|Fiona)\b/i;
  const lang = v => String(v.lang || '').replace(/_/g, '-').toLowerCase();
  const gender = v => female.test(v.name) ? 'female' : male.test(v.name) ? 'male' : 'unknown';
  function pool(voices, accent = 'en-US') {
    const english = voices.filter(v => /^en(?:-|$)/i.test(lang(v)));
    const eligible = english.filter(v => regions.some(r => lang(v) === r.toLowerCase()));
    if (accent === 'mixed') return eligible.length ? eligible : english;
    const exact = eligible.filter(v => lang(v) === accent.toLowerCase());
    return exact.length ? exact : eligible.length ? eligible : english;
  }
  function hash(text) { let n=2166136261; for (const c of String(text)) { n ^= c.charCodeAt(0); n = Math.imul(n,16777619); } return n >>> 0; }
  function pick(voices, options = {}) {
    const draw = salt => options.seed ? hash(options.seed + salt) / 4294967296 : Math.random();
    const pinned = options.voice && voices.find(v => v.name === options.voice && /^en(?:-|$)/i.test(lang(v)));
    if (pinned) return pinned;
    const candidates = pool(voices, options.accent);
    const desired = options.gender === 'mixed' ? (draw(':gender') < .5 ? 'male' : 'female') : options.gender || 'male';
    const score = v => (gender(v) === desired ? 100 : gender(v) === 'unknown' ? 40 : 0)
      + (/natural|neural|online/i.test(v.name) ? 10 : 0);
    // Mix regions first, so a plentiful US voice inventory does not dominate.
    let selected = candidates;
    if (options.accent === 'mixed' && candidates.length) {
      const langs = [...new Set(candidates.map(lang))].sort();
      const chosen = langs[Math.floor(draw(':accent') * langs.length)];
      selected = candidates.filter(v => lang(v) === chosen);
    }
    const ranked = selected.slice().sort((a, b) => score(b) - score(a) || a.name.localeCompare(b.name));
    const top = ranked.filter(v => score(v) === score(ranked[0]));
    return top[Math.floor(draw(':voice') * top.length)] || null;
  }
  return { regions, gender, pool, pick };
})();
