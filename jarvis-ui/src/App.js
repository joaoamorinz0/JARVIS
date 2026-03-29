import { useState, useEffect } from "react";

const API = "http://127.0.0.1:8000";

export default function App() {
  const [mensagens, setMensagens] = useState([]);
  const [input, setInput] = useState("");
  const [clima, setClima] = useState("");
  const [spotify, setSpotify] = useState(null);
  const [carregando, setCarregando] = useState(false);
  const hora = new Date().getHours();

  useEffect(() => {
    fetch(`${API}/clima`).then(r => r.json()).then(d => setClima(d.clima));
    const interval = setInterval(() => {
      fetch(`${API}/spotify`).then(r => r.json()).then(d => setSpotify(d));
    }, 3000);
    return () => clearInterval(interval);
  }, []);

  async function enviar() {
    if (!input.trim()) return;
    const texto = input;
    setInput("");
    setMensagens(prev => [...prev, { role: "user", content: texto }]);
    setCarregando(true);

    const res = await fetch(`${API}/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ texto, hora })
    });

    const data = await res.json();
    setMensagens(prev => [...prev, { role: "jarvis", content: data.resposta }]);
    setCarregando(false);
  }

  return (
    <div style={styles.container}>
      <div style={styles.sidebar}>
        <h1 style={styles.logo}>JARVIS</h1>
        <div style={styles.card}>
          <div style={styles.cardLabel}>🌡 Clima</div>
          <div style={styles.cardValue}>{clima || "Carregando..."}</div>
        </div>
       <div style={styles.card}>
    <div style={styles.cardLabel}>🎵 Spotify</div>
    {spotify?.tocando ? (
        <div style={{ display: "flex", gap: 12, alignItems: "center", marginTop: 8 }}>
            <img 
                src={spotify.capa} 
                alt="capa" 
                style={{ width: 56, height: 56, borderRadius: 6 }}
            />
            <div>
                <div style={{ fontSize: 13, color: "#c8dff0", fontWeight: 700 }}>{spotify.musica}</div>
                <div style={{ fontSize: 11, color: "#4a6a85", marginTop: 4 }}>{spotify.artista}</div>
            </div>
        </div>
    ) : (
        <div style={styles.cardValue}>Nenhuma música</div>
    )}
</div>
      </div>

      <div style={styles.chat}>
        <div style={styles.mensagens}>
          {mensagens.length === 0 && (
            <div style={styles.vazio}>Olá, {hora < 12 ? "bom dia" : hora < 18 ? "boa tarde" : "boa noite"}! Como posso ajudar?</div>
          )}
          {mensagens.map((m, i) => (
            <div key={i} style={m.role === "user" ? styles.msgUser : styles.msgJarvis}>
              <span style={styles.msgRole}>{m.role === "user" ? "Você" : "Jarvis"}</span>
              <span>{m.content}</span>
            </div>
          ))}
          {carregando && <div style={styles.msgJarvis}><span style={styles.msgRole}>Jarvis</span><span>Pensando...</span></div>}
        </div>

        <div style={styles.inputArea}>
          <input
            style={styles.input}
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyDown={e => e.key === "Enter" && enviar()}
            placeholder="Fale com o Jarvis..."
          />
          <button style={styles.btn} onClick={enviar}>Enviar</button>
        </div>
      </div>
    </div>
  );
}

const styles = {
  container: { display: "flex", height: "100vh", background: "#060a10", color: "#c8dff0", fontFamily: "monospace" },
  sidebar: { width: 240, background: "#0d1520", padding: 24, display: "flex", flexDirection: "column", gap: 16, borderRight: "1px solid #1a2d45" },
  logo: { fontSize: 28, fontWeight: 800, color: "#00d4ff", letterSpacing: 4, marginBottom: 16 },
  card: { background: "#060a10", border: "1px solid #1a2d45", borderRadius: 8, padding: 16 },
  cardLabel: { fontSize: 11, color: "#4a6a85", marginBottom: 8, letterSpacing: 2 },
  cardValue: { fontSize: 13, color: "#c8dff0", lineHeight: 1.5 },
  chat: { flex: 1, display: "flex", flexDirection: "column" },
  mensagens: { flex: 1, padding: 24, overflowY: "auto", display: "flex", flexDirection: "column", gap: 16 },
  vazio: { color: "#4a6a85", textAlign: "center", marginTop: 80, fontSize: 18 },
  msgUser: { alignSelf: "flex-end", background: "#1a2d45", padding: "10px 16px", borderRadius: 12, maxWidth: "70%", display: "flex", flexDirection: "column", gap: 4 },
  msgJarvis: { alignSelf: "flex-start", background: "#0d1520", border: "1px solid #1a2d45", padding: "10px 16px", borderRadius: 12, maxWidth: "70%", display: "flex", flexDirection: "column", gap: 4 },
  msgRole: { fontSize: 10, color: "#00d4ff", letterSpacing: 2, textTransform: "uppercase" },
  inputArea: { padding: 24, borderTop: "1px solid #1a2d45", display: "flex", gap: 12 },
  input: { flex: 1, background: "#0d1520", border: "1px solid #1a2d45", borderRadius: 8, padding: "12px 16px", color: "#c8dff0", fontSize: 14, outline: "none" },
  btn: { background: "#00d4ff", color: "#060a10", border: "none", borderRadius: 8, padding: "12px 24px", fontWeight: 700, cursor: "pointer", fontSize: 14 }
};