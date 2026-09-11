# AudioFlow

Plataforma SaaS moderna de áudio: downloads, biblioteca e playlists com player imersivo.

- **Frontend**: React + TypeScript + Vite + Tailwind CSS + PWA
- **Backend**: Python FastAPI + SQLAlchemy (async) + PostgreSQL + Redis/Celery + FFmpeg/yt-dlp
- **Infra**: Docker Compose + Nginx (reverse proxy)

## Arquitetura

```
audioflow.com (Frontend)
      ↓
api.audioflow.com (FastAPI)
      ↓
Workers (Celery + Redis)
      ↓
FFmpeg / yt-dlp
      ↓
Storage (local / S3 / Cloudflare R2)
      ↓
PostgreSQL
```

## Funcionalidades

- Dashboard com estatísticas em tempo real
- Download de músicas por link com progresso ao vivo (SSE)
- Formatos: MP3, M4A, Opus, FLAC, WAV
- Biblioteca com reprodução, download e exclusão
- Playlists com criação, edição e reordenação
- Player global estilo plataforma de streaming
- Painel administrativo
- Autenticação JWT (acesso anônimo opcional) e planos (Free/Pro/Premium)
- PWA instalável, responsivo para desktop/tablet/celular

## Início rápido (Docker)

```bash
cp .env.example .env
# edite .env com suas senhas/chaves
docker compose up -d
```

Acesse:
- Site: http://localhost
- API + docs: http://localhost:8000/docs (por trás do nginx: https://api.audioflow.com)

## Rodando sem Docker (desenvolvimento)

### Backend

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
alembic upgrade head
uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

## Estrutura

```
AudioFlow/
├── frontend/          # React + TS + Tailwind + PWA
├── backend/           # FastAPI + models + workers
├── nginx/             # nginx.conf (reverse proxy)
├── docker-compose.yml
├── .env.example
├── DEPLOY.md          # guia completo de deploy em VPS
└── LICENSE
```

Veja [DEPLOY.md](DEPLOY.md) para o passo a passo de deploy em servidor Linux.