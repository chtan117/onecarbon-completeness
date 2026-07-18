import os
import sqlite3
import json
from datetime import datetime, timezone
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from dotenv import load_dotenv

from email_report import send_report_email

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "data" / "leads.db"
DB_PATH.parent.mkdir(exist_ok=True)

app = FastAPI(title="OneCarbon Completeness Check")


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS leads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL,
            sector TEXT,
            scope1_present INTEGER,
            scope2_present INTEGER,
            scope3_present INTEGER,
            unsure_count INTEGER,
            unsure_items TEXT,
            raw_answers TEXT,
            created_at TEXT
        )
        """
    )
    return conn


@app.post("/api/submit")
async def submit(request: Request):
    body = await request.json()
    email = (body.get("email") or "").strip()
    if not email or "@" not in email:
        return JSONResponse({"error": "valid email required"}, status_code=400)

    conn = get_db()
    conn.execute(
        """
        INSERT INTO leads (email, sector, scope1_present, scope2_present, scope3_present,
                            unsure_count, unsure_items, raw_answers, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            email,
            body.get("sector"),
            body.get("scope1_present", 0),
            body.get("scope2_present", 0),
            body.get("scope3_present", 0),
            body.get("unsure_count", 0),
            json.dumps(body.get("unsure_items", []), ensure_ascii=False),
            json.dumps(body.get("answers", {}), ensure_ascii=False),
            datetime.now(timezone.utc).isoformat(),
        ),
    )
    conn.commit()
    conn.close()

    email_sent = True
    try:
        send_report_email(email, body)
    except Exception as exc:  # noqa: BLE001 - never fail the lead capture over email issues
        email_sent = False
        print(f"[email] failed to send report to {email}: {exc}")

    return {"status": "ok", "email_sent": email_sent}


app.mount("/", StaticFiles(directory=BASE_DIR / "static", html=True), name="static")
