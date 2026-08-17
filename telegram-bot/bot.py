import os
import requests
import hashlib
import time
from flask import Flask, request

app = Flask(__name__)

TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]
GITHUB_TOKEN = os.environ["MY_GITHUB_TOKEN"]
REPO = "elenilson787/renderizador-ffmpeg"   # substitua pelo seu repositório
WORKFLOW = "choppy-trending.yml"  # nome do workflow

CHOPPY_APP_ID = os.environ["CHOPPY_APP_ID"]
CHOPPY_APP_SECRET = os.environ["CHOPPY_APP_SECRET"]

def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": chat_id, "text": text, "parse_mode": "Markdown"})

def fetch_trending_products():
    timestamp = int(time.time())
    sign = hashlib.sha256(f"{CHOPPY_APP_ID}{CHOPPY_APP_SECRET}{timestamp}".encode()).hexdigest()
    url = "https://api.shopee.com/affiliate/trending"
    headers = {"Authorization": f"{CHOPPY_APP_ID}:{sign}:{timestamp}"}
    params = {"limit": 10, "sort": "commission"}
    r = requests.get(url, headers=headers, params=params)
    return r.json()

@app.route("/", methods=["POST"])
def webhook():
    data = request.json
    chat_id = data["message"]["chat"]["id"]
    text = data["message"]["text"]

    if text == "/ajuda":
        msg = (
            "🤖 *Bot Choppy Afiliados*\n\n"
            "Comandos disponíveis:\n"
            "/atualizar - Dispara workflow no GitHub\n"
            "/posts - Mostra posts prontos para redes sociais\n"
            "/produtos - Lista produtos em alta direto da API\n"
            "/ajuda - Exibe esta mensagem"
        )
        send_message(chat_id, msg)

    elif text == "/atualizar":
        url = f"https://api.github.com/repos/{REPO}/actions/workflows/{WORKFLOW}/dispatches"
        headers = {"Authorization": f"Bearer {GITHUB_TOKEN}"}
        payload = {"ref": "main"}
        requests.post(url, headers=headers, json=payload)
        send_message(chat_id, "🔄 Workflow disparado! Aguarde a lista de produtos...")

    elif text == "/posts":
        try:
            with open("social_posts.txt", "r", encoding="utf-8") as f:
                posts = f.read()
            send_message(chat_id, posts)
        except:
            send_message(chat_id, "Nenhum post disponível ainda. Use /atualizar primeiro.")

    elif text == "/produtos":
        data = fetch_trending_products()
        text_out = "📊 *Produtos em alta agora:*\n\n"
        for p in data.get("products", []):
            text_out += f"🔥 {p['name']} - R${p['price']} | Comissão {p['commission_rate']}%\n{p['affiliate_link']}\n\n"
        send_message(chat_id, text_out)

    else:
        send_message(chat_id, "Comando não reconhecido. Use /ajuda para ver opções.")

    return "ok"
