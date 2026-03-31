import schedule
import time
import subprocess
import requests
from datetime import date, datetime

def notificar(titulo, mensagem):
    requests.post(
        "https://ntfy.sh/jarvis-jvqa360",
        data=mensagem.encode('utf-8'),
        headers={"Title": titulo}
    )

def bom_dia():
    clima = requests.get("http://127.0.0.1:8000/clima").json()["clima"]
    notificar("☀️ Bom dia, João!", f"Hoje é {date.today().strftime('%d/%m/%Y')}. {clima}")
    print(f"Jarvis: Bom dia enviado!")


def desligar_pc():
    print("Jarvis: Desligando o PC...")
    subprocess.run(["shutdown", "/s", "/t", "60"])  # 60 segundos de aviso

def verificar_emails():
    try:
        from google_services import ler_emails
        emails = ler_emails(max=1)
        if "Nenhum" not in emails:
            notificar("📧 Email novo", emails)
    except:
        pass

# agenda
schedule.every().day.at("07:00").do(bom_dia)
schedule.every(30).minutes.do(verificar_emails)
schedule.every().day.at("23:00").do(desligar_pc)

print("Automações rodando...")
while True:
    schedule.run_pending()
    time.sleep(30)