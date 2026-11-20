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

## Nota

Proyecto de ficción / rolloreo basado en el lore de *Cyberpunk* de CD Projekt RED y R. Talsorian Games. La capa de red solo lee contenido público y no realiza ninguna operación intrusiva.
