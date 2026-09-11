# Deploy do AudioFlow

Guia para colocar o AudioFlow em produção. A arquitetura inicial recomendada é:

- **Frontend** → **Cloudflare Pages** (`https://audioflow.pages.dev`)
- **Backend** → ambiente compatível com **FastAPI + Celery + FFmpeg** (Railway, Render, Fly.io ou uma VPS com Docker)
- **Storage** → **Cloudflare R2** ou qualquer armazenamento S3-compatível
- **Banco** → **PostgreSQL** (gerenciado no próprio host ou provedor)
- **Fila** → **Redis**

> Estado atual: o frontend funciona **sem login** (modo visitante anônimo). A autenticação está implementada no backend e preparada para ativação futura.

---

## Opção A — Frontend no Cloudflare Pages + Backend separado (recomendado)

### 1. Publicar o frontend no Cloudflare Pages

O frontend é uma aplicação Vite/React. O endpoint da API é injetado em build pela variável de ambiente `VITE_API_BASE`.

1. No painel Cloudflare, crie um projeto **Pages → Connect to Git** e selecione o repositório.
2. Configuração de build:
   - **Build command**: `npm run build`
   - **Build output directory**: `dist`
   - **Root directory**: `frontend`
3. Variável de ambiente do projeto:
   - `VITE_API_BASE` = `https://api.audioflow.pages.dev` (ou seu domínio de API)
4. Domínio padrão: `audioflow.pages.dev`.

### 2. Publicar o backend

Use qualquer plataforma que rode FastAPI + Celery + FFmpeg. Exemplos:

**Railway / Render / Fly.io**:
- Build: `pip install -r requirements.txt`
- Start (API): `alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- Start (Worker): `celery -A app.workers.tasks worker --loglevel=info --queues=downloads`
- Adicione PostgreSQL + Redis como plugins/serviços.

**VPS com Docker** (conforme `docker-compose.yml`):
```bash
git clone https://github.com/USUARIO/AudioFlow.git
cd AudioFlow
cp .env.example .env    # edite
docker compose up -d --build
```

### 3. Configurar o Storage (R2)

No `.env`, use o storage S3-compatível:

```
STORAGE_BACKEND=r2
S3_ENDPOINT_URL=https://<account_id>.r2.cloudflarestorage.com
S3_ACCESS_KEY=...
S3_SECRET_KEY=...
S3_BUCKET=audioflow
S3_PUBLIC_URL=https://pub-<hash>.r2.dev   # ou domínio público do bucket
S3_REGION=auto
```

Se preferir não configurar R2 agora, use `STORAGE_BACKEND=local` (arquivos ficam no disco do backend).

### 4. Variáveis de ambiente do backend

| Variável | Descrição |
|----------|-----------|
| `DATABASE_URL` | PostgreSQL async (`postgresql+asyncpg://...`) |
| `REDIS_URL` | URL do Redis |
| `JWT_SECRET_KEY` | Chave aleatória longa |
| `FRONTEND_URL` | `https://audioflow.pages.dev` |
| `CORS_ORIGINS` | `https://audioflow.pages.dev` |
| `STORAGE_BACKEND` | `local`, `s3` ou `r2` |
| `STORAGE_PUBLIC_BASE_URL` | base pública dos arquivos (se `local`) |
| `ALLOW_ANONYMOUS` | `true` = site sem login (padrão) |

### 5. Ativar o login (futuro)

Quando quiser exigir conta:
1. Defina `ALLOW_ANONYMOUS=false`.
2. Configure `SMTP_*` para e-mails de verificação/recuperação.
3. No frontend, envolva as rotas com `<Protected />` novamente (o componente já existe em `src/components/Protected.tsx`).

---

## Opção B — Tudo em uma VPS (Docker Compose + Nginx)

Para um deploy autocontido sem Cloudflare:

```bash
apt update && apt install -y docker.io docker-compose-plugin
git clone https://github.com/USUARIO/AudioFlow.git
cd AudioFlow
cp .env.example .env && nano .env
docker compose up -d --build
```

O `nginx/nginx.conf` já faz o reverse proxy de `audioflow.com` → frontend e `api.audioflow.com` → backend. Para HTTPS com Let's Encrypt:

```bash
apt install -y certbot
certbot certonly --standalone -d audioflow.com -d api.audioflow.com
# monte /etc/letsencrypt no container nginx (veja docker-compose.yml)
```

---

## Criar o primeiro administrador

O primeiro admin é criado automaticamente no boot, a partir de:

```
FIRST_ADMIN_EMAIL=admin@audioflow.com
FIRST_ADMIN_PASSWORD=...
```

Depois acesse `https://audioflow.pages.dev/admin` e entre com essas credenciais para liberar o painel administrativo.

---

## Backup e restauração do PostgreSQL

```bash
# backup
docker compose exec -T postgres pg_dump -U audioflow audioflow > backup_$(date +%F).sql

# restauração
cat backup_2026-01-01.sql | docker compose exec -T postgres psql -U audioflow audioflow
```

---

## Atualizar

```bash
git pull
docker compose up -d --build
docker compose exec backend alembic upgrade head
docker compose restart worker
```

---

## Troubleshooting

- **Worker não processa**: `docker compose logs -f worker`
- **yt-dlp falha**: `docker compose exec backend pip install -U yt-dlp && docker compose restart worker`
- **CORS**: confira `CORS_ORIGINS` (deve incluir `https://audioflow.pages.dev`).
- **Arquivos não aparecem**: verifique `STORAGE_BACKEND` e se o bucket/domínio público do R2 está correto.