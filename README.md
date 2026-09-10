# AudioFlow

Plataforma moderna de áudio/música com frontend no Cloudflare Pages e backend em FastAPI.

## Arquitetura

```text
audioflow.com.br (Cloudflare Pages)
       ↓
api.audioflow.com.br (FastAPI + Railway/Render/Fly.io)
       ↓
Workers (Celery + Redis)
       ↓
FFmpeg / yt-dlp
       ↓
Cloudflare R2 (Storage)
       ↓
PostgreSQL (Database)
```

## Estrutura do Projeto

```text
AudioFlow/
│
├── frontend/                 # Cloudflare Pages
│   ├── index.html
│   ├── style.css
│   ├── script.js
│   ├── assets/
│   │   ├── images/
│   │   └── icons/
│   └── README.md
│
├── backend/                  # FastAPI Backend
│   ├── app/
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── api/
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── services/
│   │   ├── workers/
│   │   └── storage/
│   │
│   ├── requirements.txt
│   ├── Dockerfile
│   ├── docker-compose.yml
│   ├── .env.example
│   └── README.md
│
└── README.md
```

## Funcionalidades

### Frontend
- **Home**: Hero section, features, CTA
- **Explorar**: Músicas populares, recentes, artistas, álbuns, playlists, categorias
- **Busca em tempo real**: Músicas, artistas, álbuns, playlists
- **Player profissional**: Play/pause, anterior/próxima, volume, progresso, repetir, aleatório, fila
- **Biblioteca**: Músicas curtidas, playlists, histórico, baixadas
- **Playlists**: Criar, editar, adicionar/remover músicas, reordenar, excluir
- **Favoritos**: Músicas, álbuns, artistas, playlists
- **Autenticação**: Login, registro, logout, perfil
- **Tema**: Dark/Light mode
- **Responsivo**: Mobile, tablet, desktop

### Backend
- **Autenticação JWT**: Access + Refresh tokens, bcrypt
- **API REST**: `/api/auth`, `/api/users`, `/api/songs`, `/api/search`, `/api/artists`, `/api/albums`, `/api/playlists`, `/api/favorites`, `/api/history`, `/api/downloads`
- **Banco de dados**: PostgreSQL com SQLAlchemy 2.0 async
- **Storage**: Cloudflare R2 (compatível S3)
- **Processamento de áudio**: yt-dlp + FFmpeg via Celery workers
- **Background jobs**: Download de playlists, conversão de áudio
- **Documentação automática**: Swagger UI em `/docs`

## Requisitos

- Python 3.11+
- PostgreSQL 15+
- Redis 7+
- FFmpeg
- yt-dlp
- Node.js 18+ (para desenvolvimento frontend)
- Docker & Docker Compose (opcional)

## Instalação Rápida (Docker)

```bash
cd backend
cp .env.example .env
# Edite .env com suas configurações
docker-compose up -d
```

A API estará disponível em `http://localhost:8000`
Documentação em `http://localhost:8000/docs`

## Instalação Manual

### 1. Banco de Dados (PostgreSQL)

```bash
# Criar banco e usuário
sudo -u postgres psql
CREATE DATABASE audioflow;
CREATE USER audioflow WITH ENCRYPTED PASSWORD 'senha_segura';
GRANT ALL PRIVILEGES ON DATABASE audioflow TO audioflow;
\q
```

### 2. Redis

```bash
# Ubuntu/Debian
sudo apt install redis-server

# macOS
brew install redis
brew services start redis
```

### 3. FFmpeg e yt-dlp

```bash
# Ubuntu/Debian
sudo apt install ffmpeg
pip install yt-dlp

# macOS
brew install ffmpeg yt-dlp

# Windows (via winget)
winget install ffmpeg
pip install yt-dlp
```

### 4. Backend

```bash
cd backend

# Criar venv
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate   # Windows

# Instalar dependências
pip install -r requirements.txt

# Configurar ambiente
cp .env.example .env
# Edite .env com suas configurações

# Inicializar banco
alembic upgrade head

# Executar API
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Em outro terminal, executar worker
celery -A app.workers.tasks worker --loglevel=info --queues=downloads --concurrency=4
```

### 5. Frontend (Desenvolvimento)

```bash
cd frontend

# Servir arquivos estáticos
# Opção 1: Python
python -m http.server 3000

# Opção 2: Node.js (live-server)
npx live-server --port 3000

# Opção 3: VS Code Live Server extension
```

## Configuração do .env

```env
# Database
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/audioflow

# JWT
JWT_SECRET_KEY=sua-chave-secreta-super-segura
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# Cloudflare R2
R2_ENDPOINT=https://seu-account-id.r2.cloudflarestorage.com
R2_ACCESS_KEY=sua-access-key
R2_SECRET_KEY=sua-secret-key
R2_BUCKET=audioflow
R2_PUBLIC_URL=https://pub-seu-bucket-id.r2.dev

# Frontend
FRONTEND_URL=https://audioflow.com.br

# API
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=false

# Redis
REDIS_URL=redis://localhost:6379/0

# yt-dlp / FFmpeg
YTDLP_PATH=yt-dlp
FFMPEG_PATH=ffmpeg
FFPROBE_PATH=ffprobe

# Audio
AUDIO_OUTPUT_FORMAT=mp3
AUDIO_QUALITY=192k
MAX_CONCURRENT_DOWNLOADS=4
```

## Configuração do Cloudflare

### 1. Cloudflare Pages (Frontend)

1. Conecte seu repositório GitHub ao Cloudflare Pages
2. Configuração de build:
   - **Build command**: (vazio - arquivos estáticos)
   - **Build output directory**: `frontend`
   - **Root directory**: `/`
3. Domínio personalizado: `audioflow.com.br`
4. Variáveis de ambiente (se necessário):
   - `API_URL=https://api.audioflow.com.br`

### 2. Cloudflare R2 (Storage)

1. No painel Cloudflare, vá em **R2 Object Storage**
2. Crie um bucket: `audioflow`
3. Crie credenciais API (Access Key + Secret Key)
4. Configure CORS no bucket:
```json
[
  {
    "AllowedOrigins": ["https://audioflow.com.br"],
    "AllowedMethods": ["GET", "PUT", "POST", "DELETE"],
    "AllowedHeaders": ["*"],
    "ExposeHeaders": ["ETag"],
    "MaxAgeSeconds": 3600
  }
]
```
5. (Opcional) Configure domínio público para o bucket

### 3. DNS

No painel Cloudflare DNS:
```
Type    Name    Content                    Proxy
A       @       <pages-ip>                 Proxied
CNAME   api     <railway/render-url>       Proxied
```

## Deploy

### Frontend (Cloudflare Pages)

1. Push para GitHub
2. Cloudflare Pages detecta automaticamente
3. Deploy automático a cada push na main

### Backend (Railway)

1. Conecte repositório no Railway
2. Adicione PostgreSQL e Redis (plugins Railway)
3. Configure variáveis de ambiente
4. Deploy automático

**railway.toml** (opcional):
```toml
[build]
builder = "docker"
dockerfilePath = "backend/Dockerfile"

[deploy]
healthcheckPath = "/health"
healthcheckTimeout = 300
restartPolicyType = "on_failure"
restartPolicyMaxRetries = 10
```

### Backend (Render)

1. New Web Service → Connect GitHub
2. Build Command: `pip install -r backend/requirements.txt`
3. Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
4. Add PostgreSQL e Redis
4. Environment variables

### Backend (Fly.io)

```bash
fly launch --dockerfile backend/Dockerfile
fly secrets set DATABASE_URL=... JWT_SECRET_KEY=... R2_...=...
fly deploy
```

### Worker (Separado)

No Railway/Render/Fly.io, crie um serviço worker separado:
- **Command**: `celery -A app.workers.tasks worker --loglevel=info --queues=downloads --concurrency=4`
- Mesmas variáveis de ambiente da API

## CORS

Configure no `app/main.py`:
```python
allow_origins=[
    "https://audioflow.com.br",
    "https://www.audioflow.com.br",
    "http://localhost:3000",
    "http://localhost:5173",
]
```

## Endpoints Principais

### Auth
- `POST /api/auth/register` - Registro
- `POST /api/auth/login` - Login
- `POST /api/auth/refresh` - Refresh token
- `GET /api/auth/me` - Usuário atual

### Songs
- `GET /api/songs` - Listar (paginado, filtros)
- `GET /api/songs/popular` - Populares
- `GET /api/songs/recent` - Recentes
- `GET /api/songs/{id}` - Detalhes
- `POST /api/songs/{id}/play` - Incrementar play count

### Search
- `GET /api/search?q=termo` - Busca completa
- `GET /api/search/suggestions?q=termo` - Sugestões

### Artists
- `GET /api/artists` - Listar
- `GET /api/artists/featured` - Em destaque
- `GET /api/artists/{id}` - Detalhes
- `GET /api/artists/{id}/songs` - Músicas
- `GET /api/artists/{id}/albums` - Álbuns

### Albums
- `GET /api/albums` - Listar
- `GET /api/albums/popular` - Populares
- `GET /api/albums/{id}` - Detalhes
- `GET /api/albums/{id}/songs` - Músicas

### Playlists
- `GET /api/playlists` - Listar
- `GET /api/playlists/featured` - Em destaque
- `GET /api/playlists/{id}` - Detalhes (com músicas)
- `POST /api/playlists` - Criar
- `PATCH /api/playlists/{id}` - Atualizar
- `DELETE /api/playlists/{id}` - Excluir
- `POST /api/playlists/{id}/songs` - Adicionar música
- `DELETE /api/playlists/{id}/songs/{song_id}` - Remover música
- `PUT /api/playlists/{id}/songs/reorder` - Reordenar

### Favorites
- `GET /api/favorites` - Listar (com filtro por tipo)
- `GET /api/favorites/songs` - Músicas favoritas
- `GET /api/favorites/albums` - Álbuns favoritos
- `GET /api/favorites/artists` - Artistas favoritos
- `GET /api/favorites/playlists` - Playlists favoritas
- `POST /api/favorites` - Adicionar
- `DELETE /api/favorites/songs/{id}` - Remover música
- `DELETE /api/favorites/albums/{id}` - Remover álbum
- `DELETE /api/favorites/artists/{id}` - Remover artista
- `DELETE /api/favorites/playlists/{id}` - Remover playlist
- `GET /api/favorites/check/songs/{id}` - Verificar se favorito

### History
- `GET /api/history` - Histórico paginado
- `GET /api/history/recent` - Recentes
- `POST /api/history` - Adicionar
- `DELETE /api/history` - Limpar tudo
- `DELETE /api/history/{id}` - Remover item

### Downloads
- `GET /api/downloads` - Listar downloads
- `GET /api/downloads/{id}` - Detalhes
- `POST /api/downloads` - Criar download (trigger worker)
- `POST /api/downloads/playlist` - Download de playlist
- `DELETE /api/downloads/{id}` - Cancelar
- `GET /api/downloads/{id}/file` - URL assinada do arquivo

## Desenvolvimento

### Executar Testes
```bash
cd backend
pytest tests/ -v
```

### Lint
```bash
ruff check .
black --check .
mypy .
```

### Migrations
```bash
# Criar migration
alembic revision --autogenerate -m "descrição"

# Aplicar
alembic upgrade head
```

## Estrutura do Banco de Dados

```sql
users
  id, email, hashed_password, name, avatar_url, role, is_active, created_at, updated_at

artists
  id, name, image_url, bio, genres, spotify_id, followers_count, created_at, updated_at

albums
  id, title, artist_id, cover_url, release_date, total_tracks, spotify_id, created_at, updated_at

songs
  id, title, artist_id, album_id, duration, cover_url, audio_url, r2_key, format, bitrate, file_size, spotify_id, is_explicit, play_count, created_at, updated_at

playlists
  id, name, description, cover_url, owner_id, is_public, is_collaborative, total_tracks, total_duration, created_at, updated_at

playlist_songs (many-to-many)
  playlist_id, song_id, position, added_at

favorites
  id, user_id, song_id, album_id, artist_id, playlist_id, created_at

history
  id, user_id, song_id, played_at, progress, completed

downloads
  id, user_id, song_id, spotify_url, status, progress, error_message, r2_key, file_size, format, quality, created_at, updated_at, completed_at
```

## Segurança

- ✅ Senhas hasheadas com bcrypt
- ✅ JWT com access + refresh tokens
- ✅ CORS configurado
- ✅ Variáveis de ambiente para secrets
- ✅ Validação de entrada com Pydantic
- ✅ Rate limiting (configurar via proxy/nginx)
- ✅ HTTPS via Cloudflare
- ✅ URLs assinadas para arquivos R2
- ✅ Não expõe chaves no frontend

## Monitoramento

- Health check: `GET /health`
- Logs estruturados
- Métricas: play count, downloads, usuários ativos

## Licença

MIT License - veja [LICENSE](LICENSE) para detalhes.

## Contribuindo

1. Fork o projeto
2. Crie branch: `git checkout -b feature/nova-funcionalidade`
3. Commit: `git commit -m 'Add nova funcionalidade'`
4. Push: `git push origin feature/nova-funcionalidade`
5. Abra Pull Request

## Suporte

- Issues: GitHub Issues
- Docs: `/docs` (Swagger UI)
- Email: suporte@audioflow.com.br