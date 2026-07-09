# A-Frame Heatmap com FastAPI

Este projeto renderiza um ambiente A-Frame com panorama e sobrepoe bolhas de calor baseadas nos dados de `data.json`.

## Requisitos

- Python 3.10+
- `pip`

## Instalar dependencias

```bash
pip install -r requirements.txt
```

## Rodar o backend

Inicie o servidor FastAPI com recarga automatica:

```bash
uvicorn backend:app --reload
```

Depois abra no navegador:

```text
http://127.0.0.1:8000/
```

## Como funciona

- O frontend A-Frame fica em `web/index.html`
- O backend FastAPI fica em `backend.py`
- Os dados brutos ficam em `data.json`
- O frontend consulta `GET /api/heatmap` a cada 2 segundos
- O backend le `data.json`, agrupa por `camera_id` e retorna o registro mais recente de cada camera

## Estrutura da API

Endpoint:

```text
GET /api/heatmap
```

Resposta esperada:

```json
{
  "updated_at": "2026-07-07T21:00:00Z",
  "points": [
    {
      "id": "webcam1",
      "camera_id": "webcam1",
      "timestamp": "2026-05-07T22:02:43.512279+00:00",
      "x": -3,
      "z": 0,
      "pessoas": 8
    }
  ]
}
```

## Atualizacao automatica

Quando `data.json` mudar:

- o backend vai ler os dados novos na proxima chamada da API
- o frontend vai buscar os dados novamente em ate 2 segundos
- as bolinhas serao redesenhadas automaticamente

Nao e necessario recarregar a pagina para ver mudancas novas.

## Onde ajustar as posicoes das cameras

As posicoes das bolinhas por camera ficam em `CAMERA_POSITIONS` dentro de `backend.py`.

Exemplo:

```python
CAMERA_POSITIONS = {
    "webcam1": {"x": -3, "z": 0},
    "webcam2": {"x": 0, "z": 1},
    "webcam3": {"x": 3, "z": -1},
}
```

## Formato atual de `data.json`

O arquivo esta em JSON por linha, por exemplo:

```json
{"camera_id": "webcam1", "timestamp": "2026-05-07T21:54:23.512279+00:00", "in": 1, "out": 1, "total": 2}
{"camera_id": "webcam1", "timestamp": "2026-05-07T21:54:33.512279+00:00", "in": 2, "out": 2, "total": 4}
```

O backend usa o valor de `total` como quantidade de pessoas.

## Observacoes

- Se voce tiver varias cameras, cada `camera_id` pode receber uma posicao propria no panorama.
- Se quiser atualizacao realmente instantanea, o proximo passo e trocar o polling por WebSocket ou SSE.
