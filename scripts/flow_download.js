// Paste into the Flow project grid page with the built-in browser's javascript_tool, then call
//   await window.__kk(k, {"<first words of quoted line>": <clip number>, ...})
// for k = 0 .. (number of thumbnails - 1), clicking the project's back arrow (top-left) between calls.
// It opens thumbnail k, reads the first quoted line of its prompt, and if that line starts with one of the
// given prefixes it clicks the "Download media" button and the 720p option. Returns a log line.
// Downloads happen in the order of the calls; map files to clips by download order + the logged clip number.
// NEVER click Flow's toolbar by coordinates: the trash icon sits next to download and the toolbar shifts.
window.__kk = async function (k, need) {
  const sleep = ms => new Promise(r => setTimeout(r, ms));
  const thumbs = document.querySelectorAll('img[alt="Generated video thumbnail"]');
  if (k >= thumbs.length) return 'k' + k + ' out of range (' + thumbs.length + ')';
  thumbs[k].click();
  await sleep(3500);
  const q = ((document.body.innerText.match(/"([^"]{8,160})"/) || [])[1] || '');
  let clip = null;
  for (const p in need) { if (q.startsWith(p)) clip = need[p]; }
  let res = 'k' + k + ' ' + location.pathname.slice(-36, -28) + ' "' + q.slice(0, 30) + '" -> ' + (clip || 'skip');
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
