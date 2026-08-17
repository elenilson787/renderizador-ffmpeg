import os
import requests
from flask import Flask, request

app = Flask(__name__)

TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]
GITHUB_TOKEN = os.environ["GITHUB_TOKEN"]
REPO = "elenilson787/renderizador-ffmpeg"   # substitua pelo seu repositório
WORKFLOW = "choppy-trending.yml"  # nome do workflow

def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": chat_id, "text": text, "parse_mode": "Markdown"})

@app.route("/", methods=["POST"])
def webhook():
    data = request.json
    chat_id = data["message"]["chat"]["id"]
    text = data["message"]["text"]

    if text == "/ajuda":
        msg = (
            "🤖 *Bot Choppy Afiliados*\n\n"
            "Comandos disponíveis:\n"
            "/atualizar - Gera nova lista de produtos em alta\n"
            "/posts - Mostra posts prontos para redes sociais\n"
            "/ajuda - Exibe esta mensagem"
        )
        send_message(chat_id, msg)

    elif text == "/atualizar":
        # dispara workflow no GitHub
        url = f"https://api.github.com/repos/{REPO}/actions/workflows/{WORKFLOW}/dispatches"
        headers = {"Authorization": f"Bearer {GITHUB_TOKEN}"}
        payload = {"ref": "main"}  # branch principal
        requests.post(url, headers=headers, json=payload)
        send_message(chat_id, "🔄 Workflow disparado! Aguarde a lista de produtos...")

    elif text == "/posts":
        # aqui você pode ler o arquivo gerado e enviar posts prontos
        try:
            with open("social_posts.txt", "r", encoding="utf-8") as f:
                posts = f.read()
            send_message(chat_id, posts)
        except:
            send_message(chat_id, "Nenhum post disponível ainda. Use /atualizar primeiro.")

    else:
        send_message(chat_id, "Comando não reconhecido. Use /ajuda para ver opções.")

    return "ok"
