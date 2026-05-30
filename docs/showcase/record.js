const { chromium } = require("playwright");
const fs = require("fs");
const path = require("path");

const SHOTS = path.resolve(__dirname, "screenshots");
const VID = path.resolve(__dirname, "video_tmp");
const PDF = "C:/Users/ra-pombo/Downloads/berkshireStock.pdf";
const BASE = "http://localhost:3000/";

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

async function main() {
  if (!fs.existsSync(VID)) fs.mkdirSync(VID, { recursive: true });
  if (!fs.existsSync(SHOTS)) fs.mkdirSync(SHOTS, { recursive: true });

  const browser = await chromium.launch();
  const context = await browser.newContext({
    viewport: { width: 1440, height: 900 },
    recordVideo: { dir: VID, size: { width: 1440, height: 900 } },
  });
  const page = await context.newPage();
  const killToasts = async () => {
    try { await page.evaluate(() => document.querySelectorAll('[role="alert"]').forEach((e) => e.remove())); } catch {}
  };
  const log = (m) => console.log("[rec] " + m);

  // Reliable streaming signal: the chat input is disabled while the assistant
  // streams and re-enabled when it finishes. Wait for start (disabled) then end.
  const CHAT_INPUT = 'input[placeholder*="Ask about"], textarea[placeholder*="Ask about"]';
  const waitChatIdle = async (endTimeout) => {
    await page.waitForFunction((sel) => { const e = document.querySelector(sel); return e && e.disabled; }, CHAT_INPUT, { timeout: 20000 }).catch(() => {});
    await page.waitForFunction((sel) => { const e = document.querySelector(sel); return e && !e.disabled; }, CHAT_INPUT, { timeout: endTimeout }).catch(() => log("chat idle wait timeout"));
  };
  const sendChat = async (text) => {
    await page.waitForFunction((sel) => { const e = document.querySelector(sel); return e && !e.disabled; }, CHAT_INPUT, { timeout: 120000 }).catch(() => {});
    await page.evaluate(({ sel, t }) => {
      const el = document.querySelector(sel);
      if (!el) return;
      const proto = el.tagName === 'TEXTAREA' ? window.HTMLTextAreaElement.prototype : window.HTMLInputElement.prototype;
      Object.getOwnPropertyDescriptor(proto, 'value').set.call(el, t);
      el.dispatchEvent(new Event('input', { bubbles: true }));
    }, { sel: CHAT_INPUT, t: text });
    await sleep(500);
    await page.evaluate(() => {
      const b = [...document.querySelectorAll('button')].find((x) => x.textContent.trim() === 'Send');
      if (b && !b.disabled) b.click();
    });
  };

  await page.goto(BASE, { waitUntil: "networkidle" });
  await sleep(2500);
  await killToasts();
  await page.screenshot({ path: path.join(SHOTS, "01-upload.png"), fullPage: true });
  log("intro/upload shown");

  // UPLOAD
  await page.locator('input[type=file]').setInputFiles(PDF);
  log("file set, parsing...");
  await sleep(7000);
  await killToasts();

  // SELECT + EXTRACT
  await page.evaluate(() => {
    const cb = document.querySelector('input[type=checkbox]');
    if (cb && !cb.checked) cb.click();
  });
  await sleep(900);
  await page.evaluate(() => {
    const b = [...document.querySelectorAll('button')].find((x) => x.textContent.trim() === 'Extract');
    if (b) b.click();
  });
  log("extract clicked, waiting for metrics...");
  await page.waitForFunction(
    () => /Key Risks|Guidance/.test(document.body.innerText) && /\$\s?\d|Revenue/.test(document.body.innerText),
    { timeout: 180000 }
  ).catch(() => log("extract wait timeout"));
  await sleep(2500);
  await killToasts();
  await page.screenshot({ path: path.join(SHOTS, "02-extracted-metrics.png"), fullPage: true });
  log("metrics captured");

  // CHAT QUESTION
  const q = "What was Berkshire Hathaway's total revenue and what are the main business risks mentioned?";
  await sendChat(q);
  log("question sent, streaming...");
  await waitChatIdle(300000);
  await sleep(2500);
  const ragLen = await page.evaluate(() => { const l = document.querySelector('[aria-label="Chat messages"]'); return l ? l.innerText.length : 0; });
  await page.evaluate(() => { const l = document.querySelector('[aria-label="Chat messages"]'); if (l) l.scrollTop = l.scrollHeight; });
  await sleep(800);
  await killToasts();
  await page.screenshot({ path: path.join(SHOTS, "03-chat-rag.png"), fullPage: true });
  log("chat answer captured (standard RAG, agent OFF) len=" + ragLen);

  // HOVER HELP ICON: show the tooltip that explains Standard RAG vs Agent mode
  await page.evaluate(() => {
    const l = document.querySelector('[aria-label="Chat messages"]');
    if (l) l.scrollTop = l.scrollHeight;
  });
  await sleep(800);
  const helpIcon = page.locator('[aria-label="Agent mode help"]');
  await helpIcon.scrollIntoViewIfNeeded().catch(() => {});
  await helpIcon.hover().catch(() => {});
  // ensure the tooltip is shown (mouseenter on the wrapping span)
  await page.evaluate(() => {
    const svg = document.querySelector('[aria-label="Agent mode help"]');
    const span = svg ? svg.closest('span') : null;
    if (span) span.dispatchEvent(new MouseEvent('mouseenter', { bubbles: true }));
  });
  await page.waitForSelector('[role="tooltip"]', { timeout: 5000 }).catch(() => log("tooltip not shown"));
  await sleep(2200);
  await killToasts();
  await page.screenshot({ path: path.join(SHOTS, "04-agent-mode-help.png"), fullPage: true });
  log("agent-mode help tooltip captured");
  // hide tooltip again
  await page.evaluate(() => {
    const svg = document.querySelector('[aria-label="Agent mode help"]');
    const span = svg ? svg.closest('span') : null;
    if (span) span.dispatchEvent(new MouseEvent('mouseleave', { bubbles: true }));
  });
  await sleep(800);

  // AGENT MODE ON: toggle, ask a question that triggers autonomous tool-calling
  await page.evaluate(() => {
    const sw = document.querySelector('[role="switch"]');
    if (sw && sw.getAttribute('aria-checked') !== 'true') sw.click();
  });
  await sleep(1500);
  await killToasts();
  const aq = 'Call get_company_financials with the ticker exactly "BRK-B" (Berkshire Hathaway) and then tell me, in one short sentence, its sector, industry and market cap.';
  await sendChat(aq);
  log("agent question sent, tool-calling...");
  await waitChatIdle(360000);
  // ensure the Tools badges have rendered
  await page.waitForFunction(() => {
    const l = document.querySelector('[aria-label="Chat messages"]');
    return l && /Tools:/.test(l.innerText) && /search_documents|get_company_financials/.test(l.innerText);
  }, { timeout: 30000 }).catch(() => log("agent tools badge wait timeout"));
  await sleep(2500);
  const agentLen = await page.evaluate(() => { const l = document.querySelector('[aria-label="Chat messages"]'); return l ? l.innerText.length : 0; });
  await page.evaluate(() => { const l = document.querySelector('[aria-label="Chat messages"]'); if (l) l.scrollTop = l.scrollHeight; });
  await sleep(1200);
  await killToasts();
  await page.screenshot({ path: path.join(SHOTS, "05-agent-mode.png"), fullPage: true });
  log("agent answer captured (agent ON, tools used) len=" + agentLen);

  // FINANCIAL INTELLIGENCE - NVDA
  await page.evaluate(() => {
    const t = [...document.querySelectorAll('[role="tab"]')].find((x) => /Financial Intelligence/i.test(x.textContent));
    if (t) t.click();
  });
  await sleep(1500);
  await page.locator('input[placeholder*="ticker"], input[placeholder*="company"]').first().fill('NVDA');
  await sleep(600);
  await page.evaluate(() => {
    const b = [...document.querySelectorAll('button')].find((x) => x.textContent.trim() === 'Analyze');
    if (b && !b.disabled) b.click();
  });
  log("NVDA analyze clicked, waiting...");
  await page.waitForFunction(
    () => /AI Analysis Report/i.test(document.body.innerText) && !document.querySelector('.animate-spin'),
    { timeout: 300000 }
  ).catch(() => log("financial wait timeout"));
  await sleep(3000);
  await killToasts();
  await page.screenshot({ path: path.join(SHOTS, "06-financial-intelligence.png"), fullPage: true });
  log("financial top captured");

  // SCROLL THROUGH WHOLE REPORT
  const delta = await page.evaluate(() => {
    let best = null, max = 0;
    document.querySelectorAll('*').forEach((el) => {
      const d = el.scrollHeight - el.clientHeight;
      if (d > max && el.clientHeight > 200) { max = d; best = el; }
    });
    if (best) best.setAttribute('data-scrollme', '1');
    return max;
  });
  log("scroll delta=" + delta);
  const steps = 16;
  for (let i = 1; i <= steps; i++) {
    await page.evaluate((frac) => {
      const el = document.querySelector('[data-scrollme="1"]');
      if (el) el.scrollTop = el.scrollHeight * frac;
    }, i / steps);
    await sleep(1000);
  }
  await killToasts();
  await page.screenshot({ path: path.join(SHOTS, "07-financial-intelligence-detail.png"), fullPage: true });
  log("financial detail captured");
  await sleep(1500);
  await page.evaluate(() => { const el = document.querySelector('[data-scrollme="1"]'); if (el) el.scrollTop = 0; });
  await sleep(2000);

  const videoPath = await page.video().path();
  await context.close();
  await browser.close();

  const finalDir = path.resolve(__dirname, "video");
  if (!fs.existsSync(finalDir)) fs.mkdirSync(finalDir, { recursive: true });
  const finalPath = path.join(finalDir, "finsight-workflow.webm");
  if (fs.existsSync(finalPath)) fs.rmSync(finalPath);
  fs.copyFileSync(videoPath, finalPath);
  const size = fs.statSync(finalPath).size;
  log("VIDEO SAVED: " + finalPath + " (" + Math.round(size / 1024) + " KB)");
}

main().catch((e) => { console.error("FATAL", e); process.exit(1); });
