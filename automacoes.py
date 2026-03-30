import schedule
import time
import subprocess
import requests
from datetime import datetime

def bom_dia():
    clima = requests.get("http://127.0.0.1:8000/clima").json()["clima"]
    hora = datetime.now().strftime("%H:%M")
    print(f"Jarvis: Bom dia João! São {hora}. {clima}")

def desligar_pc():
    print("Jarvis: Desligando o PC...")
    subprocess.run(["shutdown", "/s", "/t", "60"])  # 60 segundos de aviso

# agenda
schedule.every().day.at("07:00").do(bom_dia)
schedule.every().day.at("23:00").do(desligar_pc)

print("Automações rodando...")
while True:
    schedule.run_pending()
    time.sleep(30)