# Capricorn-IA

**Arasaka Engram Construct — Model CP-10**

Constructo de personalidad ficticio (universo *Cyberpunk 2077*) con:

- **FSM emocional**: 6 estados de humor (`PLAYFUL_SADISTIC`, `CURIOUS`, `BORED`, `IRRITATED_COLD`, `MANIPULATIVE`, `THREATENING_BLACKWALL`) que cambian por palabras clave y por aburrimiento.
- **Memoria ligera**: lore RAG + últimos 50 episodios guardados en `capricorn_memory.json`.
- **Capa de RED — navegación real por Internet**:
  - Detección automática de consultas web en el mensaje (o comando `buscar <tema>`).
  - Motor de búsqueda DuckDuckGo (sin API key) con respaldo automático a la API de Wikipedia (es → en).
  - Lector de páginas: `leer <url>` descarga y disecciona cualquier URL.
  - El "botín" capturado se inyecta en el prompt del constructo para responder con datos reales sin romper el rol.
- **Motores LLM**: Gemini (`--apikey`, o var `GEMINI_API_KEY`), Ollama local, o modo simulación autónomo sin LLM.

## Interfaz HOLO (avatar 3D + voz)

`capricorn_holo.html` es una interfaz alternativa autónoma: avatar holográfico 3D
(Three.js) que reacciona al estado emocional, títulos HUD estilo Edgerunners,
texto a voz (es-ES), dictado por micrófono y conexión directa con Gemini desde el
navegador (tu API key se guarda solo en tu `localStorage`). Le funciona sin
servidor Python: abre el archivo directamente o sírvela con `python3 capricorn_web.py`
y visita `http://127.0.0.1:8080/holo`.

## Instalación

```bash
pip install -r requirements.txt
```

## Uso

```bash
python3 capricorn.py                                        # simulación + RED real
python3 capricorn.py --provider gemini --apikey TU_API_KEY # Gemini + RED real
python3 capricorn.py --provider ollama                      # Ollama local + RED real
python3 capricorn.py --no-web                               # sin capa de red
```

Comandos en la sesión: `buscar <tema>` fuerza el rastreo de la RED, `leer <url>` disecciona una página, `salir` cierra la conexión.

## Interfaz web (chat con Capricorn en el navegador)

```bash
python3 capricorn_web.py                        # http://127.0.0.1:8080
python3 capricorn_web.py --provider gemini --apikey TU_API_KEY
python3 capricorn_web.py --port 9000 --no-web
```

Terminal cyberpunk servida desde `web/index.html` con:

- Chat en tiempo real con efecto de tecleo y colores por estado emocional (insignia `ESTADO`).
- Insignias de `MOTOR` y `RED` (online/offline), y atajos rápidos (chips) para buscar en la RED.
- Endpoints JSON: `POST /api/chat`, `POST /api/leer`, `GET /api/state`, `GET /api/health`.
- El servidor se vincula por defecto a `127.0.0.1` (solo local). Para exponerlo en tu propia red usa `--host 0.0.0.0` bajo tu responsabilidad.

## Nota

Proyecto de ficción / rolloreo basado en el lore de *Cyberpunk* de CD Projekt RED y R. Talsorian Games. La capa de red solo lee contenido público y no realiza ninguna operación intrusiva.
