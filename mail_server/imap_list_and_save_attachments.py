import imaplib
import email
from email.header import decode_header, make_header
from pathlib import Path

IMAP_HOST = "localhost"
IMAP_PORT = 3143
IMAP_USER = "test1"     # ✅ avec GreenMail tel que configuré : login = "test1"
IMAP_PASS = "pass1"

SAVE_DIR = Path("attachments")
SAVE_DIR.mkdir(exist_ok=True)

def decode_str(s):
    # gère les sujets encodés (=?utf-8?Q?...?=)
    try:
        return str(make_header(decode_header(s)))
    except Exception:
        return s

def main():
    M = imaplib.IMAP4(IMAP_HOST, IMAP_PORT)
    M.login(IMAP_USER, IMAP_PASS)
    typ, _ = M.select("INBOX")
    assert typ == "OK", "Impossible d'ouvrir INBOX"

    typ, data = M.search(None, "ALL")
    assert typ == "OK"
    ids = data[0].split()
    print(f"📬 {len(ids)} message(s) dans INBOX")

    for mid in ids:
        typ, msg_data = M.fetch(mid, "(RFC822)")
        if typ != "OK":
            continue
        raw = msg_data[0][1]
        msg = email.message_from_bytes(raw)

        subject = decode_str(msg.get("Subject", "(sans sujet)"))
        from_ = decode_str(msg.get("From", ""))
        print(f"\n— ID {mid.decode()}: {subject} | From: {from_}")

        # Parcours MIME pour extraire les pièces jointes
        if msg.is_multipart():
            for part in msg.walk():
                cdisp = part.get("Content-Disposition", "")
                if cdisp and "attachment" in cdisp.lower():
                    filename = decode_str(part.get_filename() or "attachment.bin")
                    payload = part.get_payload(decode=True)
                    if payload:
                        out = SAVE_DIR / filename
                        out.write_bytes(payload)
                        print(f"   📎 Pièce jointe sauvegardée: {out}")
        else:
            # Message non multipart : affiche un bout du corps texte
            payload = msg.get_payload(decode=True) or b""
            snippet = payload.decode(errors="ignore")[:120].replace("\n", " ")
            print(f"   ✉️  Corps: {snippet}...")

    M.logout()

if __name__ == "__main__":
    main()