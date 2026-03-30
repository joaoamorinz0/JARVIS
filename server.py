from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import json
import requests
import os
from groq import Groq
from dotenv import load_dotenv
from datetime import date
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import subprocess
from tavily import TavilyClient
from google_services import ler_emails, agenda_hoje, criar_evento

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

usuario = {
    "nome": "João",
    "cidade": "Goiás"
}

hoje = date.today().strftime("%d/%m/%Y")
cliente = Groq(api_key=os.getenv("GROQ_API_KEY"))
tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
historico = []

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=os.getenv("SPOTIFY_CLIENT_ID"),
    client_secret=os.getenv("SPOTIFY_CLIENT_SECRET"),
    redirect_uri="http://127.0.0.1:8888/callback",
    scope="user-modify-playback-state user-read-playback-state"
))

def buscar_clima(cidade):
    geo = requests.get(f"https://geocoding-api.open-meteo.com/v1/search?name={cidade}&count=1&language=pt&format=json")
    geo_dados = geo.json()
    if not geo_dados.get("results"):
        return "Cidade não encontrada."
    lat = geo_dados["results"][0]["latitude"]
    lon = geo_dados["results"][0]["longitude"]
    nome_cidade = geo_dados["results"][0]["name"]
    clima = requests.get(f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m&timezone=auto")
    temp = clima.json()["current"]["temperature_2m"]
    return f"Agora em {nome_cidade}: {temp}°C"

def buscar_cep(cep):
    cep = cep.replace(" ", "").replace("-", "")
    dados = requests.get(f"https://viacep.com.br/ws/{cep}/json/").json()
    if "erro" in dados:
        return "CEP não encontrado."
    return f"{dados['logradouro']}, {dados['bairro']} - {dados['localidade']}/{dados['uf']}"

def tocar_musica(query):
    resultados = sp.search(q=query, limit=1, type="track")
    tracks = resultados["tracks"]["items"]
    if not tracks:
        return "Música não encontrada."
 
    devices = sp.devices()
    if not devices["devices"]:
        return "Nenhum dispositivo Spotify ativo. Abra o Spotify primeiro."
    
    device_id = devices["devices"][0]["id"]
    track = tracks[0]
    sp.start_playback(device_id=device_id, uris=[track["uri"]])
    return f"Tocando: {track['name']} - {track['artists'][0]['name']}"

def modo_alcool():
    devices = sp.devices()
    if not devices["devices"]:
        return "Nenhum dispositivo Spotify ativo."
    device_id = devices["devices"][0]["id"]
    sp.start_playback(device_id=device_id, context_uri="spotify:playlist:211DtusAlTCjHkh7bEs1Ls")
    subprocess.Popen(["code", "."], shell=True, creationflags=subprocess.DETACHED_PROCESS)
    return "Playlist ativada. VS Code aberto. Boa sorte, João."

def pesquisar(query):
    resultado = tavily.search(query=query, search_depth="basic")
    if not resultado["results"]:
        return "Não encontrei nada sobre isso."
    top = resultado["results"][0]
    conteudo = top['content'][:300]

    resumo = cliente.chat.completions.create(
        model="llama-3.3-70b-versatile",
        max_tokens=300,
        messages=[{
            "role": "user",
            "content": f"Resuma em português de forma curta e direta: {conteudo}"
        }]
    )
    return resumo.choices[0].message.content

class Mensagem(BaseModel):
    texto: str
    hora: int

@app.post("/chat")
def chat(msg: Mensagem):
    historico.append({"role": "user", "content": msg.texto})

    resposta = cliente.chat.completions.create(
        model="llama-3.3-70b-versatile",
        max_tokens=1000,
        messages=[
            {
                "role": "system",
                "content": f"""Você é o Jarvis, assistente pessoal de {usuario['nome']} de {usuario['cidade']}.
Hoje é {hoje} e são exatamente {msg.hora}h.
Quando pedir CEP, responda apenas: BUSCAR_CEP: [cep].
Quando pedir clima, responda apenas: BUSCAR_CLIMA: [cidade].
Quando pedir música, responda apenas: TOCAR_MUSICA: [música].
Quando pedir pausa, responda apenas: PAUSAR_MUSICA.
Quando pedir próxima, responda apenas: PROXIMA_MUSICA.
Para todo o resto, responda normalmente.
Quando o usuário disser "mais álcool" ou "modo álcool", responda EXATAMENTE com uma única palavra: MODO_ALCOOL. Nada mais.
Quando o usuário pedir para pesquisar algo, responda apenas: PESQUISAR: [o que pesquisar].
Quando pedir emails, responda apenas: LER_EMAILS.
Quando pedir agenda, responda apenas: AGENDA_HOJE."""
            },
            *historico
        ]
    )

    resposta_texto = resposta.choices[0].message.content
    historico.append({"role": "assistant", "content": resposta_texto})

    if "BUSCAR_CEP:" in resposta_texto:
        return {"resposta": buscar_cep(resposta_texto.split("BUSCAR_CEP:")[1].strip())}
    elif "BUSCAR_CLIMA:" in resposta_texto:
        return {"resposta": buscar_clima(resposta_texto.split("BUSCAR_CLIMA:")[1].strip())}
    elif "TOCAR_MUSICA:" in resposta_texto:
        return {"resposta": tocar_musica(resposta_texto.split("TOCAR_MUSICA:")[1].strip())}
    elif "PAUSAR_MUSICA" in resposta_texto:
        sp.pause_playback()
        return {"resposta": "Música pausada."}
    elif "PROXIMA_MUSICA" in resposta_texto:
        sp.next_track()
        return {"resposta": "Próxima música."}
    elif "MODO_ALCOOL" in resposta_texto:
        return {"resposta": modo_alcool()}
    elif "PESQUISAR:" in resposta_texto:
        query = resposta_texto.split("PESQUISAR:")[1].strip()
        return {"resposta": pesquisar(query)}
    elif "LER_EMAILS" in resposta_texto:
        return {"resposta": ler_emails()}
    elif "AGENDA_HOJE" in resposta_texto:
        return {"resposta": agenda_hoje()}

    return {"resposta": resposta_texto}

@app.get("/clima")
def clima():
    return {"clima": buscar_clima(usuario["cidade"])}

@app.get("/spotify")
def spotify_status():
    try:
        atual = sp.current_playback()
        if atual and atual["is_playing"]:
            track = atual["item"]
            return {
                "tocando": True,
                "musica": track["name"],
                "artista": track["artists"][0]["name"],
                "capa": track["album"]["images"][0]["url"]  # ← linha nova
            }
        return {"tocando": False}
    except:
        return {"tocando": False}