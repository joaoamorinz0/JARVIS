import json
import requests
import os
from groq import Groq
from dotenv import load_dotenv
from datetime import date
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import tempfile
from playsound import playsound
from elevenlabs.client import ElevenLabs
import sounddevice as sd
import soundfile as sf
import numpy as np
import whisper




load_dotenv()

usuario = {
    "nome": "João",
    "cidade": "Goiás"
}

hoje = date.today().strftime("%d/%m/%Y")

cliente = Groq(api_key=os.getenv("GROQ_API_KEY"))
elevenlabs = ElevenLabs(api_key=os.getenv("ELEVENLABS_API_KEY"))
modelo_whisper = whisper.load_model("base")


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

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=os.getenv("SPOTIFY_CLIENT_ID"),
    client_secret=os.getenv("SPOTIFY_CLIENT_SECRET"),
    redirect_uri=os.getenv("SPOTIFY_REDIRECT_URI"),
    scope="user-modify-playback-state user-read-playback-state"
))

def tocar_musica(query):
    resultados = sp.search(q=query, limit=1, type="track")
    tracks = resultados["tracks"]["items"]
    if not tracks:
        return "Música não encontrada."
    track = tracks[0]
    sp.start_playback(uris=[track["uri"]])
    return f"Tocando: {track['name']} - {track['artists'][0]['name']}"

def pausar_musica():
    sp.pause_playback()
    return "Música pausada."

def proxima_musica():
    sp.next_track()
    return "Pulando para a próxima música."

def falar(texto):
    audio = elevenlabs.text_to_speech.convert(
        text=texto,
        voice_id="pNInz6obpgDQGcFmaJgB",    
        model_id="eleven_multilingual_v2" 
    )
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as f:
        for chunk in audio:
            f.write(chunk)
        tmp_path = f.name
    
    playsound(tmp_path)

def ouvir():
    print("Ouvindo...")
    duracao = 6
    sample_rate = 16000
    audio = sd.rec(int(duracao * sample_rate), samplerate=sample_rate, channels=1, dtype='float32')
    sd.wait()
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as f:
        sf.write(f.name, audio, sample_rate)
        tmp_path = f.name
    
    resultado = modelo_whisper.transcribe(tmp_path, language="pt")
    texto = resultado["text"].strip()
    return texto if texto else None

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
           "content": f"""Você é o Jarvis, assistente pessoal de {usuario['nome']}.
Hoje é {hoje} e são exatamente {hora}h.
Seja direto e útil. Quando o usuário pedir CEP, responda apenas: BUSCAR_CEP: [cep].
Quando pedir clima, responda apenas: BUSCAR_CLIMA: [cidade].
Quando o usuário pedir para tocar música, responda apenas: TOCAR_MUSICA: [nome da música ou artista].
Quando pedir para pausar, responda apenas: PAUSAR_MUSICA.
Quando pedir para pular, responda apenas: PROXIMA_MUSICA.
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
    elif "TOCAR_MUSICA:" in resposta_texto:
        query = resposta_texto.split("TOCAR_MUSICA:")[1].strip()
        return tocar_musica(query)
    elif "PAUSAR_MUSICA" in resposta_texto:
        return pausar_musica()
    elif "PROXIMA_MUSICA" in resposta_texto:
        return proxima_musica()

    return resposta_texto

def iniciar_jarvis():
    hora = int(input("Que horas são? "))
    msg = saudacao(hora)
    print(f"\n{msg}, {usuario['nome']}! Jarvis online.\n")

    while True:  # ← 4 espaços de indentação
        comando = input("Você: ")
        if not comando:
            print("Não entendi, tente novamente.")
            continue
        print(f"Você: {comando}")
        if comando.lower() == "sair":
            salvar_historico()
            print("Jarvis desligando...")
            break
        resposta = perguntar_ia(comando, hora)
        print(f"\nJarvis: {resposta}\n")
        falar(resposta)

historico = carregar_historico()
iniciar_jarvis()