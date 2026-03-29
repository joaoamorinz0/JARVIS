import json
import requests
import os
from groq import Groq
from dotenv import load_dotenv
from datetime import date

load_dotenv()

usuario = {
    "nome": "João",
    "cidade": "Goiás"
}

hoje = date.today().strftime("%d/%m/%Y")

cliente = Groq(api_key=os.getenv("GROQ_API_KEY"))

def carregar_historico():
    try:
        with open("historico.json", "r") as arquivo:
            return json.load(arquivo)
    except FileNotFoundError:
        return []

def salvar_historico():
    with open("historico.json", "w") as arquivo:
        json.dump(historico, arquivo)
    print("Jarvis: Histórico salvo!")

def saudacao(hora):
    if hora < 12:
        return "Bom dia"
    elif hora < 18:
        return "Boa tarde"
    else:
        return "Boa noite"

def buscar_cep(cep):
    cep = cep.replace(" ", "").replace("-", "")
    resposta = requests.get(f"https://viacep.com.br/ws/{cep}/json/")
    dados = resposta.json()
    if "erro" in dados:
        return "CEP não encontrado."
    return f"{dados['logradouro']}, {dados['bairro']} - {dados['localidade']}/{dados['uf']}"

def buscar_clima(cidade):
    geo = requests.get(f"https://geocoding-api.open-meteo.com/v1/search?name={cidade}&count=1&language=pt&format=json")
    geo_dados = geo.json()
    if not geo_dados.get("results"):
        return "Cidade não encontrada."
    lat = geo_dados["results"][0]["latitude"]
    lon = geo_dados["results"][0]["longitude"]
    nome_cidade = geo_dados["results"][0]["name"]
    clima = requests.get(f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m&timezone=auto")
    clima_dados = clima.json()
    temp = clima_dados["current"]["temperature_2m"]
    return f"Agora em {nome_cidade}: {temp}°C"

def perguntar_ia(mensagem, hora):
    historico.append({
        "role": "user",
        "content": mensagem
    })

    resposta = cliente.chat.completions.create(
        model="llama-3.3-70b-versatile",
        max_tokens=1000,
     messages=[
        {
            "role": "system",
           "content": f"""Você é o Jarvis, assistente pessoal de {usuario['nome']} de {usuario['cidade']}.
Hoje é {hoje} e são exatamente {hora}h.
Seja direto e útil. Quando o usuário pedir CEP, responda apenas: BUSCAR_CEP: [cep].
Quando pedir clima, responda apenas: BUSCAR_CLIMA: [cidade].
Para todo o resto, responda normalmente."""
        },
        *historico
    ]
    )

    resposta_texto = resposta.choices[0].message.content

    historico.append({
        "role": "assistant",
        "content": resposta_texto
    })

    if "BUSCAR_CEP:" in resposta_texto:
            cep = resposta_texto.split("BUSCAR_CEP:")[1].strip()
            return buscar_cep(cep)
    elif "BUSCAR_CLIMA:" in resposta_texto:
        cidade = resposta_texto.split("BUSCAR_CLIMA:")[1].strip()
        return buscar_clima(cidade)

    return resposta_texto

def iniciar_jarvis():
    hora = int(input("Que horas são? "))
    msg = saudacao(hora)
    print(f"\n{msg}, {usuario['nome']}! Jarvis online.\n")

    while True:
        comando = input("Você: ")
        if comando.lower() == "sair":
            salvar_historico()
            print("Jarvis desligando...")
            break

        resposta = perguntar_ia(comando,hora)
        print(f"\nJarvis: {resposta}\n")

historico = carregar_historico()
iniciar_jarvis()