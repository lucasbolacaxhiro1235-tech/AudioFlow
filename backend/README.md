# AudioFlow Backend

API REST em FastAPI para plataforma de áudio/música.

## Stack

- **FastAPI 0.109** - Framework web async
- **SQLAlchemy 2.0** - ORM async com PostgreSQL
- **Pydantic 2** - Validação e serialização
- **PostgreSQL 15+** - Banco de dados principal
- **Redis 7+** - Cache + Celery broker
- **Celery 5.3** - Background workers
- **JWT (python-jose)** - Autenticação stateless
- **bcrypt (passlib)** - Hash de senhas
- **Cloudflare R2 (boto3)** - Storage S3-compatível
- **yt-dlp + FFmpeg** - Download e conversão de áudio
- **Docker** - Containerização

## Estrutura

```text
backend/
├── app/
│   ├── main.py              # App FastAPI + lifespan
│   ├── config.py            # Settings (pydantic-settings)
│   ├── database.py          # Engine, session, init_db
│   ├── models/              # SQLAlchemy models
│   │   └── __init__.py      # User, Artist, Album, Song, Playlist, Favorite, History, Download
│   ├── schemas/             # Pydantic schemas
│   │   └── __init__.py      # Request/Response models
│   ├── api/                 # Rotas da API
│   │   ├── auth.py          # /api/auth
│   │   ├── users.py         # /api/users
│   │   ├── songs.py         # /api/songs
│   │   ├── search.py        # /api/search
│   │   ├── artists.py       # /api/artists
│   │   ├── albums.py        # /api/albums
│   │   ├── playlists.py     # /api/playlists
│   │   ├── favorites.py     # /api/favorites
│   │   ├── history.py       # /api/history
│   │   └── downloads.py     # /api/downloads
│   ├── services/            # Lógica de negócio
│   │   └── auth.py          # Auth service
│   ├── workers/             # Celery tasks
│   │   ├── tasks.py         # Celery app + tasks
│   │   └── audio_processor.py  # yt-dlp + FFmpeg logic
│   └── storage/             # Storage abstraction
│       └── r2.py            # Cloudflare R2 client
│
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── .env.example
├── alembic.ini              # Migrations config
└── README.md
```

## Endpoints da API

### Auth (`/api/auth`)
| Método | Endpoint | Descrição |
|--------|----------|-----------|
| POST | `/register` | Registrar usuário |
| POST | `/login` | Login (retorna access + refresh token) |
| POST | `/refresh` | Renovar access token |
| GET | `/me` | Usuário autenticado |
| PATCH | `/me` | Atualizar perfil |

### Users (`/api/users`)
| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/me/playlists` | Playlists do usuário (paginado) |
| GET | `/me/favorites` | Favoritos (filtrável por tipo) |
| GET | `/me/history` | Histórico de reprodução |
| DELETE | `/me/history` | Limpar histórico |
| GET | `/{user_id}` | Perfil público |

### Songs (`/api/songs`)
| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/` | Listar (paginado, filtros: artist_id, album_id, search) |
| GET | `/popular` | Mais tocadas |
| GET | `/recent` | Adicionadas recentemente |
| GET | `/{id}` | Detalhes + is_favorite |
| POST | `/{id}/play` | Incrementar play count |
| POST | `/` | Criar (admin) |
| PATCH | `/{id}` | Atualizar (admin) |
| DELETE | `/{id}` | Excluir (admin) |

### Search (`/api/search`)
| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/` | Busca unificada (tracks, artists, albums, playlists) |
| GET | `/suggestions` | Autocomplete |

### Artists (`/api/artists`)
| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/` | Listar (paginado, search) |
| GET | `/featured` | Top artistas |
| GET | `/{id}` | Detalhes |
| GET | `/{id}/songs` | Músicas do artista |
| GET | `/{id}/albums` | Álbuns do artista |

### Albums (`/api/albums`)
| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/` | Listar (paginado, artist_id, search) |
| GET | `/popular` | Álbuns recentes |
| GET | `/{id}` | Detalhes |
| GET | `/{id}/songs` | Faixas do álbum |

### Playlists (`/api/playlists`)
| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/` | Listar (paginado, user_id, is_public) |
| GET | `/featured` | Playlists públicas |
| GET | `/{id}` | Detalhes com músicas |
| POST | `/` | Criar playlist |
| PATCH | `/{id}` | Atualizar (owner) |
| DELETE | `/{id}` | Excluir (owner) |
| POST | `/{id}/songs` | Adicionar música |
| DELETE | `/{id}/songs/{song_id}` | Remover música |
| PUT | `/{id}/songs/reorder` | Reordenar (array de song_ids) |

### Favorites (`/api/favorites`)
| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/` | Listar (paginado, type filter) |
| GET | `/songs` | Músicas favoritas |
| GET | `/albums` | Álbuns favoritos |
| GET | `/artists` | Artistas favoritos |
| GET | `/playlists` | Playlists favoritas |
| POST | `/` | Adicionar (song_id OU album_id OU artist_id OU playlist_id) |
| DELETE | `/songs/{id}` | Remover música |
| DELETE | `/albums/{id}` | Remover álbum |
| DELETE | `/artists/{id}` | Remover artista |
| DELETE | `/playlists/{id}` | Remover playlist |
| GET | `/check/songs/{id}` | Verificar se favoritado |

### History (`/api/history`)
| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/` | Histórico paginado |
| GET | `/recent` | Últimas reproduzidas |
| POST | `/` | Registrar play (progress, completed) |
| DELETE | `/` | Limpar tudo |
| DELETE | `/{id}` | Remover item |

### Downloads (`/api/downloads`)
| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/` | Listar downloads do usuário |
| GET | `/{id}` | Status do download |
| POST | `/` | Iniciar download (trigger worker) |
| POST | `/playlist` | Download de playlist inteira |
| DELETE | `/{id}` | Cancelar (se pending/processing) |
| GET | `/{id}/file` | URL assinada R2 (completed only) |

## Autenticação

### Headers
```
Authorization: Bearer <access_token>
```

### Tokens
- **Access**: 30 min (configurável)
- **Refresh**: 7 dias (configurável)
- **Payload**: `{"sub": "user_id", "type": "access|refresh", "exp": timestamp}`

### Fluxo
1. `POST /auth/login` → `{access_token, refresh_token}`
2. Use `access_token` nas requisições
3. Quando expirar: `POST /auth/refresh` com `refresh_token`
4. Recebe novo par de tokens

## Background Workers

### Celery App
```python
# app/workers/tasks.py
celery_app = Celery("audioflow", broker=REDIS_URL, backend=REDIS_URL)
```

### Tasks
- `process_download_task(download_id)` - Processa 1 download
- `process_playlist_task(playlist_url, user_id)` - Processa playlist inteira

### Queues
- `downloads` - Processamento de áudio (concurrency=4)

### Executar Worker
```bash
celery -A app.workers.tasks worker --loglevel=info --queues=downloads --concurrency=4
```

## Processamento de Áudio

### Fluxo
1. Usuário cria download via `POST /api/downloads`
2. API cria registro `Download` com status `pending`
3. Worker pega task da queue
4. **yt-dlp** baixa áudio do Spotify/YouTube (URL)
5. **FFmpeg** converte para MP3 192kbps
6. Upload para **Cloudflare R2**
7. Cria/atualiza `Song` com `audio_url` (R2 public URL)
8. Atualiza `Download` status `completed`

### Configuração
```env
YTDLP_PATH=yt-dlp
FFMPEG_PATH=ffmpeg
FFPROBE_PATH=ffprobe
AUDIO_OUTPUT_FORMAT=mp3
AUDIO_QUALITY=192k
MAX_CONCURRENT_DOWNLOADS=4
```

## Cloudflare R2

### Client
```python
# app/storage/r2.py
r2_storage = R2Storage()
```

### Métodos
- `upload_file(file, key, content_type, metadata)`
- `upload_bytes(data, key, content_type, metadata)`
- `download_file(key)` → bytes
- `delete_file(key)`
- `generate_presigned_url(key, expiration=3600)`
- `get_public_url(key)`
- `file_exists(key)`
- `get_file_size(key)`

### Estrutura de Keys
```
songs/{user_id}/{uuid}.mp3
covers/{user_id}/{uuid}.jpg
temporary/{user_id}/{uuid}.tmp
```

## Banco de Dados

### Migrations (Alembic)
```bash
# Configurar alembic.ini com DATABASE_URL
alembic revision --autogenerate -m "initial"
alembic upgrade head
```

### Models Principais
- `User` - Usuários + auth
- `Artist` - Artistas
- `Album` - Álbuns
- `Song` - Músicas (FK artist, album)
- `Playlist` - Playlists (FK owner)
- `playlist_songs` - Many-to-many (position)
- `Favorite` - Polymorphic (song/album/artist/playlist)
- `History` - Reproduções
- `Download` - Jobs de download

## Desenvolvimento

### Setup Local
```bash
cd backend
cp .env.example .env
# Edite .env

# Com Docker
docker-compose up -d

# Manual
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload
```

### Testes
```bash
pytest tests/ -v --cov=app
```

### Lint/Type Check
```bash
ruff check .
black --check .
mypy app/
```

### Formatar
```bash
black .
ruff check --fix .
```

## Deploy

### Railway
1. New Project → GitHub Repo
2. Add PostgreSQL + Redis plugins
3. Settings → Environment Variables (copie do .env)
4. Deploy

### Render
1. New Web Service
2. Build: `pip install -r requirements.txt`
3. Start: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
4. Add PostgreSQL + Redis
5. Environment Variables

### Fly.io
```bash
fly launch --dockerfile Dockerfile
fly secrets set DATABASE_URL=... JWT_SECRET_KEY=... R2_ENDPOINT=...
fly deploy
```

### Dockerfile (Produção)
```dockerfile
FROM python:3.11-slim
# Instala ffmpeg
# Copia requirements, instala
# Copia app
# User non-root
# EXPOSE 8000
# CMD uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## Variáveis de Ambiente Obrigatórias

| Variável | Descrição | Exemplo |
|----------|-----------|---------|
| `DATABASE_URL` | PostgreSQL async URL | `postgresql+asyncpg://user:pass@host:5432/db` |
| `JWT_SECRET_KEY` | Chave secreta JWT (32+ chars) | `super-secret-key-change-me` |
| `R2_ENDPOINT` | R2 S3 endpoint | `https://xxx.r2.cloudflarestorage.com` |
| `R2_ACCESS_KEY` | R2 Access Key | `xxx` |
| `R2_SECRET_KEY` | R2 Secret Key | `xxx` |
| `R2_BUCKET` | Nome do bucket | `audioflow` |
| `R2_PUBLIC_URL` | Public bucket URL | `https://pub-xxx.r2.dev` |
| `FRONTEND_URL` | Frontend origin (CORS) | `https://audioflow.com.br` |
| `REDIS_URL` | Redis URL | `redis://localhost:6379/0` |

## Segurança

- ✅ bcrypt cost=12
- ✅ JWT HS256 + expiration
- ✅ Refresh token rotation (opcional)
- ✅ CORS restrito a FRONTEND_URL
- ✅ Pydantic validation em todos inputs
- ✅ SQLAlchemy params (SQL injection safe)
- ✅ Secrets apenas em .env (nunca no código)
- ✅ R2 presigned URLs (expiração 1h)
- ✅ Rate limiting (implementar no proxy)

## Monitoramento

- Health: `GET /health`
- Logs: uvicorn + structlog (adicionar)
- Métricas: Prometheus (adicionar)
- Sentry: error tracking (adicionar)

## Troubleshooting

### yt-dlp falha
```bash
# Atualizar
pip install -U yt-dlp
# Testar
yt-dlp --version
```

### FFmpeg não encontrado
```bash
which ffmpeg
# Adicionar ao PATH ou configurar FFMPEG_PATH no .env
```

### Worker não processa
- Verificar Redis conectado
- Verificar queue name: `--queues=downloads`
- Logs: `celery -A app.workers.tasks worker --loglevel=debug`

### R2 upload falha
- Verificar credenciais
- Verificar CORS no bucket R2
- Verificar bucket policy

## Próximos Passos

- [ ] Rate limiting middleware
- [ ] WebSocket para progresso real-time
- [ ] Push notifications
- [ ] Admin dashboard
- [ ] Analytics/Telemetria
- [ ] Testes de integração
- [ ] CI/CD pipeline