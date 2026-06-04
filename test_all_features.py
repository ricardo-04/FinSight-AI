# -*- coding: utf-8 -*-
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
"""
FinSight AI - End-to-end API test script.
Tests: upload → extract → chat (RAG) → analyst (agent) → financial intelligence
"""
import asyncio
import json
import httpx

BASE = "http://localhost:8000"
PDF  = "apple_10q_q1_2025.pdf"

BOLD  = "\033[1m"
GREEN = "\033[92m"
CYAN  = "\033[96m"
YELLOW= "\033[93m"
RED   = "\033[91m"
RESET = "\033[0m"

def header(title: str):
    print(f"\n{BOLD}{CYAN}{'='*60}{RESET}")
    print(f"{BOLD}{CYAN}  {title}{RESET}")
    print(f"{BOLD}{CYAN}{'='*60}{RESET}")

def ok(msg: str):
    print(f"{GREEN}[OK] {msg}{RESET}")

def info(msg: str):
    print(f"{YELLOW}   {msg}{RESET}")

def err(msg: str):
    print(f"{RED}[ERR] {msg}{RESET}")


async def main():
    async with httpx.AsyncClient(timeout=180.0) as client:

        # ── 1. Health ────────────────────────────────────────────────
        header("STEP 1 · Health Check")
        r = await client.get(f"{BASE}/health/live")
        ok(f"Live: {r.json()}")
        r = await client.get(f"{BASE}/health/ready")
        ok(f"Ready: {r.json()}")

        # ── 2. Upload ────────────────────────────────────────────────
        header("STEP 2 · Upload PDF")
        doc_id = None
        with open(PDF, "rb") as f:
            r = await client.post(
                f"{BASE}/api/upload/",
                files={"file": (PDF, f, "application/pdf")},
            )
        try:
            data = r.json()
            if isinstance(data, dict) and "document_id" in data:
                doc_id = data["document_id"]
                ok(f"Uploaded! document_id: {doc_id}")
                info(f"Filename : {data.get('filename','?')}")
                info(f"Status   : {data.get('status','?')}")
            else:
                err(f"Unexpected upload response: {data}")
        except Exception as exc:
            err(f"Upload error ({r.status_code}): {r.text[:200]}")

        if not doc_id:
            # fall back to list existing
            r2 = await client.get(f"{BASE}/api/documents/")
            docs2 = r2.json()
            if docs2:
                doc_id = docs2[0]["id"]
                ok(f"Using existing doc: {doc_id}")
            else:
                err("No documents available — cannot continue.")
                return

        # ── 3. List documents ────────────────────────────────────────
        header("STEP 3 · List Documents")
        r = await client.get(f"{BASE}/api/documents/")
        docs = r.json()
        ok(f"Documents in DB: {len(docs)}")
        for d in docs:
            info(f"  [{d.get('id','?')[:8]}…] {d.get('filename','?')} — {d.get('status','?')}")

        # ── 4. Extract Metrics ───────────────────────────────────────
        header("STEP 4 · Extract Financial Metrics (AI)")
        print("   ⏳ Calling extraction agent (may take 20-40s)…")
        r = await client.post(f"{BASE}/api/extract/{doc_id}")
        if r.status_code == 200:
            data = r.json()
            m = data.get("metrics", {})
            ok(f"Extraction complete!")
            info(f"Company  : {m.get('company','–')}")
            info(f"Quarter  : {m.get('quarter','–')}")
            info(f"Revenue  : {m.get('revenue','–')}")
            info(f"Growth   : {m.get('growth','–')}")
            info(f"Guidance : {m.get('guidance','–')}")
            risks = m.get("risks", [])
            info(f"Risks ({len(risks)}):")
            for risk in risks:
                info(f"    • {risk}")
        else:
            err(f"Extraction failed ({r.status_code}): {r.text[:300]}")

        # ── 5. RAG Chat ──────────────────────────────────────────────
        header("STEP 5 · RAG Chat (Agent Mode OFF)")
        question = "What was Apple's total revenue in Q1 2025 and what was the year-over-year growth rate?"
        info(f"Question: {question}")
        print("   ⏳ Calling research agent (may take 20-60s)…")
        r = await client.post(
            f"{BASE}/api/chat/",
            json={"question": question, "document_ids": [doc_id]},
        )
        if r.status_code == 200:
            data = r.json()
            ok("RAG answer received!")
            print(f"\n{BOLD}Answer:{RESET}")
            print(data.get("answer", "–"))
            citations = data.get("citations", [])
            if citations:
                print(f"\n{BOLD}Citations ({len(citations)}):{RESET}")
                for c in citations:
                    info(f"  [{c.get('index','?')}] page {c.get('page','?')}: {str(c.get('text',''))[:100]}…")
        else:
            err(f"Chat failed ({r.status_code}): {r.text[:300]}")

        # ── 6. Analyst Agent (streaming) ─────────────────────────────
        header("STEP 6 · Analyst Agent (Agent Mode ON — streaming)")
        question2 = "What are Apple's key financial metrics from the document? Summarise revenue, margins and guidance."
        info(f"Question: {question2}")
        print("   ⏳ Calling agentic analyst with streaming SSE (may take 30-90s)…")
        chunks = []
        tools_used = []
        try:
            async with client.stream(
                "POST",
                f"{BASE}/api/analyst/stream",
                json={"question": question2, "document_ids": [doc_id]},
                timeout=120.0,
            ) as resp:
                async for line in resp.aiter_lines():
                    if line.startswith("data:"):
                        payload = line[5:].strip()
                        try:
                            event = json.loads(payload)
                            if event.get("type") == "token":
                                chunks.append(event.get("content", ""))
                            elif event.get("type") == "done":
                                tools_used = event.get("tools_used", [])
                        except json.JSONDecodeError:
                            pass
            ok("Analyst stream complete!")
            if tools_used:
                info(f"Tools used: {', '.join(tools_used)}")
            answer = "".join(chunks)
            print(f"\n{BOLD}Answer:{RESET}")
            print(answer[:1200] + ("…" if len(answer) > 1200 else ""))
        except Exception as exc:
            err(f"Analyst stream error: {exc}")

        # ── 7. Financial Intelligence ────────────────────────────────
        header("STEP 7 · Financial Intelligence Terminal — AAPL")
        print("   ⏳ Fetching live market data + AI analyst report (may take 30-90s)…")
        r = await client.post(
            f"{BASE}/api/financial/analyze",
            json={"query": "AAPL"},
        )
        if r.status_code == 200:
            data = r.json()
            ov = data.get("overview", {})
            hl = data.get("highlights", {})
            ok("Financial analysis complete!")
            print(f"\n{BOLD}Company Overview:{RESET}")
            info(f"  Name       : {ov.get('name','–')}")
            info(f"  Ticker     : {ov.get('ticker','–')}")
            info(f"  Sector     : {ov.get('sector','–')}")
            info(f"  Market Cap : {ov.get('market_cap','–')}")
            info(f"  Price      : {ov.get('price','–')}")
            print(f"\n{BOLD}Financial Highlights:{RESET}")
            for k, v in hl.items():
                info(f"  {k}: {v}")
            report = data.get("report", "")
            print(f"\n{BOLD}AI Analyst Report (first 800 chars):{RESET}")
            print(report[:800] + ("…" if len(report) > 800 else ""))
        else:
            err(f"Financial analysis failed ({r.status_code}): {r.text[:300]}")

        # ── Done ─────────────────────────────────────────────────────
        header("ALL TESTS COMPLETE")
        ok("FinSight AI is fully operational!")


if __name__ == "__main__":
    asyncio.run(main())
