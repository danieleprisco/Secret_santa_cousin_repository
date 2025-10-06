from flask import Flask, render_template, request, jsonify
import random
import json
import uuid
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

app = Flask(__name__)

DATA_FILE = "santa_data.json"
SENDER_EMAIL = "daniele.prisco2003@gmail.com"
SENDER_PASS = "fdyi mtwm tuqn iudf"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {}

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

def invia_email(destinatario_email, nome_giver, nome_destinatario, link):
    subject = "🎅 Il tuo Secret Santa!"
    body = f"""
    Ciao {nome_giver}! 🎁
    
    È arrivato il momento di scoprire a chi devi fare il regalo!
    Vai al link qui sotto per scoprirlo:
    
    {link}
    
    Buone feste! 🎄
    """

    msg = MIMEMultipart()
    msg["From"] = SENDER_EMAIL
    msg["To"] = destinatario_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(SENDER_EMAIL, SENDER_PASS)
            server.sendmail(SENDER_EMAIL, destinatario_email, msg.as_string())
        print(f"[✅ EMAIL INVIATA] A {nome_giver} ({destinatario_email})")
    except Exception as e:
        print(f"[❌ ERRORE INVIO A {destinatario_email}] {e}")

@app.route("/")
def index():
    return render_template("Cugini_BabboSegreto.html")

@app.route("/genera", methods=["POST"])
def genera():
    data = request.get_json()
    partecipanti = data["partecipanti"]

    nomi = [p["nome"] for p in partecipanti]
    email = [p["email"] for p in partecipanti]
    destinatari = nomi[:]

    while True:
        random.shuffle(destinatari)
        if all(a != b for a, b in zip(nomi, destinatari)):
            break

    results = {}
    for giver, receiver in zip(nomi, destinatari):
        token = str(uuid.uuid4())[:8]
        giver_email = next(p["email"] for p in partecipanti if p["nome"] == giver)
        results[giver] = {
            "destinatario": receiver,
            "token": token,
            "email": giver_email
        }

    save_data(results)

    # Invia le email con link personalizzato
    for giver, info in results.items():
        link = f"http://localhost:5000/santa/{info['token']}"
        invia_email(info["email"], giver, info["destinatario"], link)

    return jsonify({"message": "Accoppiamenti generati e email inviate!"})

@app.route("/santa/<token>")
def mostra_destinatario(token):
    data = load_data()
    for giver, info in data.items():
        if info["token"] == token:
            return f"<h1>Ciao {giver}! 🎅<br>Devi fare un regalo a <strong>{info['destinatario']}</strong> 🎁</h1>"
    return "<h1>Link non valido o scaduto.</h1>"

if __name__ == "__main__":
    app.run(debug=True)
