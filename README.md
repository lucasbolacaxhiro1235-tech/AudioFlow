# AudioFlow

Plataforma SaaS moderna de áudio: downloads, biblioteca e playlists com player imersivo.

- **Frontend**: React + TypeScript + Vite + Tailwind CSS + PWA (implantado no Cloudflare Pages)
- **Backend**: Python FastAPI + SQLAlchemy (async) + PostgreSQL + Redis/Celery + FFmpeg/yt-dlp
- **Storage**: armazenamento local ou S3-compatível (Cloudflare R2)

## Arquitetura

```
audioflow.pages.dev (Frontend — Cloudflare Pages)
      ↓
api.<dominio> (FastAPI — qualquer host compatível com FastAPI/Celery/FFmpeg)
      ↓
Workers (Celery + Redis)
      ↓
FFmpeg / yt-dlp
      ↓
Storage (local / S3 / Cloudflare R2)
      ↓
PostgreSQL
```

## Estado atual

- **Sem tela de login**: o site abre direto no Dashboard. Qualquer visitante pode usar a interface por meio de uma conta "Visitante" anônima, isolada por dispositivo (`client_id`).
- **Autenticação pronta, mas desativada na interface**: todo o sistema de contas (JWT, usuários, sessões, verificação de e-mail, recuperação de senha, admin) está implementado no backend e pode ser ativado futuramente.

## Funcionalidades

- Dashboard com estatísticas em tempo real
- Download de músicas por link com progresso ao vivo (SSE)
- Formatos: MP3, M4A, Opus, FLAC, WAV
- Biblioteca com reprodução, download e exclusão
- Playlists com criação, edição, reordenação, adição/remoção de faixas
- Player global estilo plataforma de streaming
- Painel administrativo
- Autenticação JWT + Argon2 (acesso anônimo opcional) e planos (Free/Pro/Premium)
- PWA instalável, responsivo para desktop/tablet/celular

## Rodando localmente

### Com Docker (tudo em um)

```bash
cp .env.example .env
# edite .env com suas senhas/chaves
docker compose up -d --build
```

Acesse:
- Site: http://localhost
- API + docs: http://localhost:8000/docs

### Sem Docker (desenvolvimento)

#### Backend (requer PostgreSQL + Redis)

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
alembic upgrade head
uvicorn app.main:app --reload
# em outro terminal:
celery -A app.workers.tasks worker --loglevel=info --queues=downloads
```

#### Frontend

```bash
cd frontend
npm install
npm run dev   # proxy /api e /media para localhost:8000
```

## Testes

```bash
cd backend
pip install pytest pytest-asyncio
pytest tests/ -v
```

## Estrutura

```
AudioFlow/
├── frontend/          # React + TS + Tailwind + PWA (Cloudflare Pages)
├── backend/           # FastAPI + models + workers + testes
├── nginx/             # nginx.conf (reverse proxy, opcional)
├── docker-compose.yml
├── .env.example
├── DEPLOY.md          # guia completo de deploy
└── LICENSE
```

Veja [DEPLOY.md](DEPLOY.md) para o passo a passo de deploy (Cloudflare Pages + backend + storage R2).