from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles


BASE_DIR = Path(__file__).resolve().parent
DATA_FILE = BASE_DIR / "data.json"
WEB_DIR = BASE_DIR / "web"

CAMERA_POSITIONS = {
    "webcam1": {"x": -3.2, "y": 0.45, "z": -1.4},
    "webcam2": {"x": 0, "y": 0.0, "z": 1},
    "webcam3": {"x": 3, "y": 0.0, "z": -1},
}

app = FastAPI(title="A-Frame Heatmap API", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _ler_registros() -> list[dict]:
    if not DATA_FILE.exists():
        return []

    linhas = [linha.strip() for linha in DATA_FILE.read_text(encoding="utf-8").splitlines() if linha.strip()]
    return [json.loads(linha) for linha in linhas]


def _normalizar_heatmap(registros: list[dict]) -> list[dict]:
    registros_por_camera: dict[str, dict] = {}

    for registro in registros:
        camera_id = registro.get("camera_id", "camera")
        anterior = registros_por_camera.get(camera_id)

        if anterior is None:
            registros_por_camera[camera_id] = registro
            continue

        ts_atual = registro.get("timestamp", "")
        ts_anterior = anterior.get("timestamp", "")
        if ts_atual >= ts_anterior:
            registros_por_camera[camera_id] = registro

    pontos = []
    for indice, (camera_id, registro) in enumerate(registros_por_camera.items()):
        posicao = CAMERA_POSITIONS.get(camera_id, {"x": indice * 2 - 2, "y": 0.0, "z": 0})
        pontos.append(
            {
                "id": camera_id,
                "camera_id": camera_id,
                "timestamp": registro.get("timestamp"),
                "x": posicao["x"],
                "y": posicao.get("y", 0.0),
                "z": posicao["z"],
                "pessoas": int(registro.get("total") or registro.get("in") or 0),
            }
        )

    return pontos


@app.get("/")
def root() -> FileResponse:
    return FileResponse(WEB_DIR / "index.html")


@app.get("/api/heatmap")
def heatmap() -> dict:
    registros = _ler_registros()
    return {
        "updated_at": datetime.utcnow().isoformat() + "Z",
        "points": _normalizar_heatmap(registros),
    }


# Serve the frontend assets from the site root so relative paths in index.html resolve.
app.mount("/", StaticFiles(directory=WEB_DIR, html=True), name="web")
