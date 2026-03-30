from googleapiclient.discovery import build
from google_auth import autenticar_google
import base64
from email.mime.text import MIMEText
from datetime import datetime, timezone

def get_gmail():
    creds = autenticar_google()
    return build('gmail', 'v1', credentials=creds)

def get_calendar():
    creds = autenticar_google()
    return build('calendar', 'v3', credentials=creds)

def ler_emails(max=5):
    gmail = get_gmail()
    result = gmail.users().messages().list(userId='me', maxResults=max, q='is:unread').execute()
    msgs = result.get('messages', [])
    
    if not msgs:
        return "Nenhum email não lido."
    
    emails = []
    for msg in msgs:
        dados = gmail.users().messages().get(userId='me', id=msg['id'], format='metadata',
            metadataHeaders=['Subject', 'From']).execute()
        headers = {h['name']: h['value'] for h in dados['payload']['headers']}
        emails.append(f"De: {headers.get('From', '?')} | Assunto: {headers.get('Subject', '?')}")
    
    return "\n".join(emails)

def agenda_hoje():
    calendar = get_calendar()
    agora = datetime.now(timezone.utc).isoformat()
    fim = datetime.now(timezone.utc).replace(hour=23, minute=59).isoformat()
    
    events = calendar.events().list(
        calendarId='primary',
        timeMin=agora,
        timeMax=fim,
        singleEvents=True,
        orderBy='startTime'
    ).execute()
    
    items = events.get('items', [])
    if not items:
        return "Nenhum evento hoje."
    
    resultado = []
    for e in items:
        hora = e['start'].get('dateTime', e['start'].get('date', ''))[:16]
        resultado.append(f"{hora} — {e['summary']}")
    
    return "\n".join(resultado)

def criar_evento(titulo, hora_inicio, hora_fim):
    calendar = get_calendar()
    evento = {
        'summary': titulo,
        'start': {'dateTime': hora_inicio, 'timeZone': 'America/Sao_Paulo'},
        'end': {'dateTime': hora_fim, 'timeZone': 'America/Sao_Paulo'},
    }
    calendar.events().insert(calendarId='primary', body=evento).execute()
    return f"Evento '{titulo}' criado com sucesso!"

if __name__ == "__main__":
    print("=== EMAILS ===")
    print(ler_emails())
    print("\n=== AGENDA HOJE ===")
    print(agenda_hoje())