import smtplib
from email.message import EmailMessage
from pathlib import Path

SMTP_HOST = "localhost"
SMTP_PORT = 3025

FROM = "sender@dev.local"
TO = "test1@dev.local"

def build_message() -> EmailMessage:
    msg = EmailMessage()
    msg["Subject"] = "Hello GreenMail (HTML + Attachment)"
    msg["From"] = FROM
    msg["To"] = TO

    # Corps texte (fallback) + HTML
    msg.set_content("Version texte : Bonjour !\nCeci est un test avec pièce jointe.")
    msg.add_alternative("""\
    <html>
      <body>
        <h2 style="margin:0">Bonjour 👋</h2>
        <p>Ceci est un <b>message HTML</b> avec une pièce jointe.</p>
      </body>
    </html>
    """, subtype="html")

    # Pièce jointe (ex: un petit fichier texte)
    attachment_path = Path("demo.txt")
    if not attachment_path.exists():
        attachment_path.write_text("Contenu de l'attachement.\n")

    msg.add_attachment(
        attachment_path.read_bytes(),
        maintype="text",
        subtype="plain",
        filename=attachment_path.name,
    )
    return msg

def main():
    msg = build_message()
    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as s:
        # GreenMail en mode non authentifié côté SMTP test par défaut ; sinon s.login(...)
        s.send_message(msg)
        print("✅ Email envoyé à GreenMail.")

if __name__ == "__main__":
    main()