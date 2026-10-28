// TikTok Shop ads: download Flow clips by matching any distinctive phrase of the clip's prompt
// (works for hero clips, which have no quoted voice-over line). Kilabot keeps using flow_download.js.
// Paste into the Flow project grid page with the built-in browser's javascript_tool, then call
//   await window.__ad(k, {"<unique phrase from the prompt>": <clip number>, ...})
// for k = 0 .. (number of thumbnails - 1), clicking the project's back arrow (top-left) between calls.
// NEVER click Flow's toolbar by coordinates: the trash icon sits next to download and the toolbar shifts.
window.__ad = async function (k, need) {
  const sleep = ms => new Promise(r => setTimeout(r, ms));
  const thumbs = document.querySelectorAll('img[alt="Generated video thumbnail"]');
  if (k >= thumbs.length) return 'k' + k + ' out of range (' + thumbs.length + ')';
  thumbs[k].click();
  await sleep(3500);
  const text = (document.body.innerText || '').replace(/\s+/g, ' ').toLowerCase();
  let clip = null, hit = '';
  for (const p in need) {
    if (text.includes(p.replace(/\s+/g, ' ').toLowerCase())) {
      if (clip !== null && clip !== need[p]) return 'k' + k + ' AMBIGUOUS (' + clip + ' / ' + need[p] + ')';
      clip = need[p]; hit = p;
    }
  }
  let res = 'k' + k + ' "' + hit.slice(0, 30) + '" -> ' + (clip || 'skip');
  if (clip) {
    const b = document.querySelector('button[aria-label="Download media"]');
    if (!b) return res + ' NO-BUTTON';
    b.click(); await sleep(1200);
    const opt = [...document.querySelectorAll('*')]
      .filter(e => e.children.length <= 3 && /^\s*720p/.test(e.innerText || '') && e.offsetParent).pop();
    if (opt) { opt.click(); res += ' DL'; } else res += ' NO720';
    await sleep(3500);
  }
  return res;
};
'defined';
