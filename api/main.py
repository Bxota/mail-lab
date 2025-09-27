from fastapi import FastAPI, UploadFile, Form, File, Response, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional

import smtplib, imaplib, email
from email.message import EmailMessage

SMTP_HOST, SMTP_PORT = "localhost", 3025
IMAP_HOST, IMAP_PORT = "localhost", 3143
IMAP_USER, IMAP_PASS = "test1", "pass1"

app = FastAPI()

# Dev CORS (frontend on localhost)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------- Models --------
class SendMail(BaseModel):
    to: str
    subject: str
    text: str
    html: Optional[str] = None
    smtp_user: Optional[str] = None
    smtp_pass: Optional[str] = None

# -------- SMTP --------
@app.post("/mail/send")
def send_mail(payload: SendMail):
    msg = EmailMessage()
    msg["From"] = "sender@dev.local"
    msg["To"] = payload.to
    msg["Subject"] = payload.subject
    msg.set_content(payload.text or "")
    if payload.html:
        msg.add_alternative(payload.html, subtype="html")

    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as s:
        if payload.smtp_user:
            s.login(payload.smtp_user, payload.smtp_pass or "")
        s.send_message(msg)
    return {"status": "ok"}

@app.post("/mail/send_multipart")
def send_mail_multipart(
    to: str = Form(...),
    subject: str = Form(...),
    text: str = Form(""),
    html: Optional[str] = Form(None),
    smtp_user: Optional[str] = Form(None),
    smtp_pass: Optional[str] = Form(None),
    files: Optional[List[UploadFile]] = File(None),
):
    """Send email with optional attachments via multipart/form-data."""
    msg = EmailMessage()
    msg["From"] = "sender@dev.local"
    msg["To"] = to
    msg["Subject"] = subject
    if html:
        msg.set_content(text or "")
        msg.add_alternative(html, subtype="html")
    else:
        msg.set_content(text or "")

    if files:
        for f in files:
            content = f.file.read()
            ctype = f.content_type or "application/octet-stream"
            maintype, subtype = ctype.split("/", 1)
            msg.add_attachment(content, maintype=maintype, subtype=subtype, filename=f.filename)

    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as s:
        if smtp_user:
            s.login(smtp_user, smtp_pass or "")
        s.send_message(msg)
    return {"status": "ok", "attachments": [getattr(f, 'filename', None) for f in (files or [])]}

# -------- IMAP: list & read --------
@app.get("/mail/messages")
def list_messages(user: Optional[str] = None, password: Optional[str] = None):
    M = imaplib.IMAP4(IMAP_HOST, IMAP_PORT)
    try:
        M.login(user or IMAP_USER, password or IMAP_PASS)
        typ, _ = M.select("INBOX")
        if typ != "OK":
            raise HTTPException(status_code=500, detail="Cannot select INBOX")
        typ, data = M.search(None, "ALL")
        if typ != "OK":
            return {"messages": []}
        ids = data[0].split()
        out = []
        for mid in ids[-50:]:  # last 50
            typ, msg_data = M.fetch(mid, "(RFC822)")
            if typ != "OK" or not msg_data:
                continue
            msg = email.message_from_bytes(msg_data[0][1])
            out.append({"id": mid.decode(), "subject": msg.get("Subject"), "from": msg.get("From")})
        return {"messages": out}
    finally:
        try:
            M.logout()
        except Exception:
            pass

@app.get("/mail/messages/{mid}")
def get_message(mid: str, user: Optional[str] = None, password: Optional[str] = None):
    M = imaplib.IMAP4(IMAP_HOST, IMAP_PORT)
    try:
        M.login(user or IMAP_USER, password or IMAP_PASS)
        typ, _ = M.select("INBOX")
        if typ != "OK":
            raise HTTPException(status_code=500, detail="Cannot select INBOX")
        typ, msg_data = M.fetch(mid.encode(), "(RFC822)")
        if typ != "OK" or not msg_data or not msg_data[0]:
            raise HTTPException(status_code=404, detail="Message not found")
        raw = msg_data[0][1]
        msg = email.message_from_bytes(raw)

        attachments = []
        if msg.is_multipart():
            idx = 0
            for part in msg.walk():
                if part.get_content_disposition() == "attachment":
                    filename = part.get_filename() or f"attachment-{idx}"
                    ctype = part.get_content_type()
                    payload = part.get_payload(decode=True) or b""
                    attachments.append({
                        "index": idx,
                        "filename": filename,
                        "content_type": ctype,
                        "size": len(payload),
                    })
                    idx += 1

        return {
            "id": mid,
            "subject": msg.get("Subject"),
            "from": msg.get("From"),
            "to": msg.get("To"),
            "has_attachments": bool(attachments),
            "attachments": attachments,
            "raw": raw.decode(errors="ignore"),
        }
    finally:
        try:
            M.logout()
        except Exception:
            pass

# -------- IMAP: download attachment --------
@app.get("/mail/messages/{mid}/attachments/{index}")
def download_attachment(mid: str, index: int, user: Optional[str] = None, password: Optional[str] = None):
    M = imaplib.IMAP4(IMAP_HOST, IMAP_PORT)
    try:
        M.login(user or IMAP_USER, password or IMAP_PASS)
        typ, _ = M.select("INBOX")
        if typ != "OK":
            raise HTTPException(status_code=500, detail="Cannot select INBOX")
        typ, msg_data = M.fetch(mid.encode(), "(RFC822)")
        if typ != "OK" or not msg_data or not msg_data[0]:
            raise HTTPException(status_code=404, detail="Message not found")
        raw = msg_data[0][1]
        msg = email.message_from_bytes(raw)

        parts = [part for part in msg.walk() if part.get_content_disposition() == "attachment"]
        if index < 0 or index >= len(parts):
            raise HTTPException(status_code=404, detail="Attachment not found")

        part = parts[index]
        data = part.get_payload(decode=True) or b""
        filename = part.get_filename() or f"attachment-{index}"
        ctype = part.get_content_type()

        headers = {"Content-Disposition": f"attachment; filename=\"{filename}\""}
        return Response(content=data, media_type=ctype, headers=headers)
    finally:
        try:
            M.logout()
        except Exception:
            pass