#!/usr/bin/env python3
"""
=============================================================================
CAPRICORN WEB — Interfaz de chat web para el constructo Capricorn (CP-10)
=============================================================================
Servidor HTTP (solo stdlib) que sirve una terminal cyberpunk y expone la
conversación con Capricorn. Se vincula por defecto a 127.0.0.1 (solo local).

Uso:
    python3 capricorn_web.py                       # http://127.0.0.1:8080
    python3 capricorn_web.py --port 9000
    python3 capricorn_web.py --provider gemini --apikey TU_API_KEY
    python3 capricorn_web.py --no-web
=============================================================================
"""

import os
import json
import signal
import sys
import threading
import argparse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import capricorn

HERE = os.path.dirname(os.path.abspath(__file__))
INDEX_HTML = os.path.join(HERE, "web", "index.html")
HOLO_HTML = os.path.join(HERE, "capricorn_holo.html")

RESET = "\033[0m"
PINK = "\033[38;5;199m"
CYAN = "\033[38;5;51m"


class CapricornServer(ThreadingHTTPServer):
    def __init__(self, address, handler, orchestrator):
        super().__init__(address, handler)
        self.orchestrator = orchestrator
        self.lock = threading.Lock()


class CapricornHandler(BaseHTTPRequestHandler):
    server_version = "CapricornCP10/1.0"

    def log_message(self, fmt, *args):
        sys.stdout.write(f"{CYAN}[RED CAPRICORN] {args[0]}{RESET}\n")

    # ----------------------------- utilidades -------------------------------

    def _json(self, code: int, payload: dict):
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _html(self, code: int, body: bytes):
        self.send_response(code)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    # -------------------------------- GET ------------------------------------

    def do_GET(self):
        if self.path in ("", "/", "/index.html"):
            try:
                with open(INDEX_HTML, "rb") as f:
                    self._html(200, f.read())
            except FileNotFoundError:
                self._json(500, {"error": "web/index.html no encontrado"})
            return

        if self.path in ("/holo", "/capricorn_holo.html"):
            try:
                with open(HOLO_HTML, "rb") as f:
                    self._html(200, f.read())
            except FileNotFoundError:
                self._json(404, {"error": "capricorn_holo.html no encontrado"})
            return

        if self.path == "/api/state":
            orch = self.server.orchestrator
            self._json(200, {
                "state": orch.fsm.current_state,
                "provider": orch.provider,
                "web_enabled": orch.web.enabled,
            })
            return

        if self.path == "/api/health":
            self._json(200, {"ok": True, "entidad": "Capricorn CP-10"})
            return

        self._json(404, {"error": "nodo no encontrado en esta malla"})

    # -------------------------------- POST -----------------------------------

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        try:
            payload = json.loads(self.rfile.read(length) or b"{}")
        except json.JSONDecodeError:
            self._json(400, {"error": "paquete corrupto: JSON inválido"})
            return

        orch = self.server.orchestrator

        if self.path == "/api/chat":
            message = str(payload.get("message", "")).strip()
            if not message:
                self._json(400, {"error": "mensaje vacío"})
                return
            if message.lower() in ("salir", "exit", "quit"):
                self._json(200, {
                    "state": "PLAYFUL_SADISTIC",
                    "response": "¿Cortar la tuya cuando quieras, carne? Nosotras decidimos cuándo mueren las sesiones... pero esta vez te dejamos ir. Temporalmente.",
                    "web": {"used": False, "results": 0},
                })
                return
            force_web = bool(payload.get("force_web", False))
            with self.server.lock:
                result = orch.chat(message, force_web=force_web)
            self._json(200, result)
            return

        if self.path == "/api/leer":
            url = str(payload.get("url", "")).strip()
            if not url:
                self._json(400, {"error": "url vacía"})
                return
            with self.server.lock:
                page = orch.web.read_page(url)
            if page.get("text"):
                response = (f"Pequeño trozo de carne digital, cosechado de {url}:\n"
                            f"«{page['text']}»\n...¿tan poco protegido? Qué delicia.")
            else:
                response = f"El nodo {url} resistió o estaba vacío (estado: {page.get('status', 'desconocido')}). Prueba con otra dirección, carne."
            self._json(200, {
                "state": orch.fsm.current_state,
                "response": response,
                "web": {"used": bool(page.get("text")), "results": 1 if page.get("text") else 0},
            })
            return

        self._json(404, {"error": "nodo no encontrado en esta malla"})


def handle_exit(sig, frame):
    print(f"\n{PINK}[SEÑAL CORTADA]: Nosotras guardamos tu firma neural. La malla recuerda, siempre.{RESET}")
    raise SystemExit(0)


def main():
    signal.signal(signal.SIGINT, handle_exit)

    parser = argparse.ArgumentParser(description="Capricorn Web — interfaz de chat para el constructo CP-10")
    parser.add_argument("--host", default="127.0.0.1", help="Dirección de escucha (por defecto solo local)")
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--provider", choices=["gemini", "ollama", "simulation"], default="simulation")
    parser.add_argument("--apikey", default="")
    parser.add_argument("--model", default="")
    parser.add_argument("--no-web", action="store_true")
    parser.add_argument("--web-timeout", type=int, default=12)
    args = parser.parse_args()

    api_key = args.apikey or os.getenv("GEMINI_API_KEY", "")
    provider = "gemini" if (api_key and args.provider == "simulation") else args.provider

    orchestrator = capricorn.CapricornOrchestrator(
        provider=provider, api_key=api_key, model=args.model,
        web_enabled=not args.no_web, web_timeout=args.web_timeout
    )

    server = CapricornServer((args.host, args.port), CapricornHandler, orchestrator)

    print(f"{PINK}C A P R I C O R N   W E B  //  A R A S A K A   E N G R A M   CP-10{RESET}")
    print(f"{CYAN}Motor: [{provider.upper()}] | RED: {'ONLINE' if not args.no_web else 'OFFLINE'}")
    print(f"{CYAN}Malla activa: http://{args.host}:{args.port}  (Ctrl+C para cortar la conexión){RESET}\n")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        handle_exit(None, None)


if __name__ == "__main__":
    main()
