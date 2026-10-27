// Paste into the Flow project grid page with the built-in browser's javascript_tool (UI as of 2026-10-27 09:30).
//   await window.__dl(k)   // k = thumbnail index, 0 = newest clip
// Opens thumbnail k, reads the first quoted line of its prompt, opens the header "More options" (⋮) menu,
// clicks "Download media" → "720p Original size", then goes back to the grid with the in-app Back button
// (so window.__dl survives; a full navigate would wipe it). Run at most 3 per javascript_tool call (45 s limit).
// Downloads land in ~/Downloads, sometimes as hidden temp files (.Q6L2SF6YDW.com.anthropic.claudefordesktop.*),
// sometimes renamed to "<Title>_<timestamp>.mp4". Map files to clips by download order, using a marker file:
//   touch marker before; afterwards `find . -maxdepth 1 -newer marker -type f` sorted by mtime.
// COPY (cp) them into place — moving a hidden temp file before Chrome finishes leaves a 0-byte stub.
// NEVER click Flow's toolbar by coordinates: "Move to trash" is in the same menu as Download.
window.__dl = async function (k) {
  const sleep = ms => new Promise(r => setTimeout(r, ms));
  for (let i = 0; i < 20 && document.querySelectorAll('img[alt="Generated video thumbnail"]').length <= k; i++) await sleep(500);
  const th = document.querySelectorAll('img[alt="Generated video thumbnail"]');
  if (k >= th.length) return 'k' + k + ' out of range';
  th[k].click(); await sleep(3000);
  const q = ((document.body.innerText.match(/"([^"]{8,160})"/) || [])[1] || '');
  document.querySelectorAll('button[aria-label="More options"]')[0].click(); await sleep(900);
  const mi = [...document.querySelectorAll('[role=menuitem]')].find(e => /Download media/.test(e.innerText));
  if (!mi) return 'k' + k + ' no DL item ' + q.slice(0, 25);
  mi.click(); await sleep(1000);
  const o = [...document.querySelectorAll('[role=menuitem]')].filter(e => /^\s*720p/.test(e.innerText) && e.offsetParent);
  if (!o.length) return 'k' + k + ' no 720 ' + q.slice(0, 25);
  o[0].click(); await sleep(4000);
  document.dispatchEvent(new KeyboardEvent('keydown', { key: 'Escape', bubbles: true })); await sleep(300);
  const back = document.querySelector('button[aria-label="Back button to go to previous page"]');
  back && back.click(); await sleep(2500);
  return 'k' + k + ' DL "' + q.slice(0, 30) + '"';
};
'defined';
