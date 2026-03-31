# JARVIS 🤖

Assistente pessoal com IA, integrado com Spotify, Gmail, Google Calendar, clima, CEP e pesquisa na internet. Interface web em React com backend em Python/FastAPI.

## Funcionalidades

- 💬 Chat com IA em português (Groq + LLaMA 3.3)
- 🎵 Controle do Spotify — tocar, pausar, pular, capa do álbum
- 📧 Leitura de emails não lidos via Gmail
- 📅 Agenda do dia via Google Calendar
- 🌡️ Clima em tempo real (Open-Meteo)
- 📮 Busca de CEP (ViaCEP)
- 🔍 Pesquisa na internet (Tavily)
- 🔔 Notificações no celular (Ntfy)
- 💻 Automações agendadas (bom dia, desligamento do PC)
- 📱 Interface responsiva — acesso via celular na rede local

## Stack

- **Frontend:** React
- **Backend:** Python + FastAPI
- **IA:** Groq (LLaMA 3.3-70b)
- **Voz:** ElevenLabs (TTS)
- **Casa inteligente:** em breve

## Instalação

### Pré-requisitos

- Python 3.10+
- Node.js 18+
- Conta no [Groq](https://console.groq.com)
- Conta no [Spotify Developer](https://developer.spotify.com)
- Conta no [Tavily](https://tavily.com)
- Conta no [ElevenLabs](https://elevenlabs.io)
- Projeto no [Google Cloud Console](https://console.cloud.google.com) com Gmail API e Calendar API ativadas

### 1. Clone o repositório

```bash
git clone https://github.com/joaoamorinz0/JARVIS.git
cd JARVIS
```

### 2. Instale as dependências Python

```bash
pip install fastapi uvicorn groq python-dotenv spotipy tavily-python \
            google-auth-oauthlib google-auth-httplib2 google-api-python-client \
            elevenlabs requests schedule playsound==1.2.2
```

### 3. Configure as variáveis de ambiente

Crie um arquivo `.env` na raiz do projeto:

```env
GROQ_API_KEY=sua_key_aqui
SPOTIFY_CLIENT_ID=seu_client_id
SPOTIFY_CLIENT_SECRET=seu_client_secret
SPOTIFY_REDIRECT_URI=http://127.0.0.1:8888/callback
TAVILY_API_KEY=sua_key_aqui
ELEVENLABS_API_KEY=sua_key_aqui
```

### 4. Configure o Google (Gmail + Calendar)

Baixe o `credentials.json` do Google Cloud Console e coloque na raiz do projeto. Execute a autenticação:

```bash
python google_auth.py
```

### 5. Instale as dependências do frontend

```bash
cd jarvis-ui
npm install
```

### 6. Inicie o projeto

No Windows, execute o arquivo `.bat`:

```bash
iniciar_jarvis.bat
```

Ou manualmente em três terminais separados:

```bash
# Terminal 1 — Backend
python -m uvicorn server:app --host 0.0.0.0 --port 8000 --reload

# Terminal 2 — Automações
python automacoes.py

# Terminal 3 — Frontend
cd jarvis-ui
set HOST=0.0.0.0
npm start
```

Acesse em `http://localhost:3000`

## Acesso via celular

Na mesma rede WiFi, acesse `http://SEU_IP_LOCAL:3000`. Para descobrir seu IP:

```bash
ipconfig  # Windows
```

## Estrutura do projeto

```
JARVIS/
├── server.py          # Backend FastAPI + todas as integrações
├── main.py            # Versão terminal (sem interface web)
├── automacoes.py      # Automações agendadas
├── google_auth.py     # Autenticação Google OAuth
├── google_services.py # Gmail + Google Calendar
├── iniciar_jarvis.bat # Inicialização automática (Windows)
└── jarvis-ui/         # Interface React
    └── src/
        └── App.js
```

## Variáveis necessárias

| Variável | Onde obter |
|---|---|
| `GROQ_API_KEY` | [console.groq.com](https://console.groq.com) |
| `SPOTIFY_CLIENT_ID` | [developer.spotify.com](https://developer.spotify.com) |
| `SPOTIFY_CLIENT_SECRET` | [developer.spotify.com](https://developer.spotify.com) |
| `TAVILY_API_KEY` | [tavily.com](https://tavily.com) |
| `ELEVENLABS_API_KEY` | [elevenlabs.io](https://elevenlabs.io) |

## Próximos passos

- [ ] Integração com Home Assistant (casa inteligente)
- [ ] Reconhecimento de voz (Whisper)
- [ ] Interface Next.js
- [ ] Deploy em nuvem

---

Desenvolvido por [João](https://github.com/joaoamorinz0)
