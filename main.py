import json
import requests  # ← linha nova

usuario = {
    "nome": "João",
    "cidade": "Goiás"
}

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

def buscar_cep(cep):  # ← função nova
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

    clima = requests.get(f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,weathercode&timezone=auto")
    clima_dados = clima.json()

    temp = clima_dados["current"]["temperature_2m"]
    return f"Agora em {nome_cidade}: {temp}°C"

def processar_comando(comando, hora):
    if "hora" in comando:
        return f"São {hora}h no momento."
    elif "nome" in comando:
        return f"Você é {usuario['nome']}, de {usuario['cidade']}."
    elif "historico" in comando:
        if len(historico) == 0:
            return "Nenhuma conversa ainda."
        return f"Você já mandou {len(historico)} mensagens: {historico}"
    elif "clima" in comando:
        cidade = comando.replace("clima", "").strip()
        if not cidade:
            cidade = usuario["cidade"]  # usa a cidade do usuário se não especificar
        return buscar_clima(cidade)

    elif "cep" in comando:  # ← bloco novo
        cep = comando.replace("cep", "").strip()
        return buscar_cep(cep)
    else:
        return "Não entendi esse comando ainda."

def iniciar_jarvis():
    hora = int(input("Que horas são? "))
    msg = saudacao(hora)
    print(f"\n{msg}, {usuario['nome']}! Jarvis online.\n")

    while True:
        comando = input("Você: ").lower()
        if comando == "sair":
            salvar_historico()
            print("Jarvis desligando...")
            break

        historico.append(comando)
        resposta = processar_comando(comando, hora)
        print(f"Jarvis: {resposta}\n")

historico = carregar_historico()
iniciar_jarvis()