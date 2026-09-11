# Deploy do AudioFlow em VPS Linux

Guia completo para colocar o AudioFlow em produção com `audioflow.com` e `api.audioflow.com`.

## Índice

1. [Requisitos](#1-requisitos)
2. [Comprar a VPS](#2-comprar-a-vps)
3. [Configurar DNS](#3-configurar-dns)
4. [Clonar o projeto](#4-clonar-o-projeto)
5. [Configurar o .env](#5-configurar-o-env)
6. [Executar com Docker Compose](#6-executar-com-docker-compose)
7. [Configurar SSL com Let's Encrypt](#7-configurar-ssl-com-lets-encrypt)
8. [Criar o primeiro administrador](#8-criar-o-primeiro-administrador)
9. [Backup e restauração do PostgreSQL](#9-backup-e-restauração-do-postgresql)
10. [Atualizar o sistema](#10-atualizar-o-sistema)
11. [Troubleshooting](#11-troubleshooting)

---

## 1. Requisitos

- Uma VPS Linux (Ubuntu 22.04/24.04 recomendado) com pelo menos **1 GB de RAM** e **20 GB de disco**.
- Um domínio (`audioflow.com`).
- Docker e Docker Compose instalados.

## 2. Comprar a VPS

Sugestões: Hetzner, DigitalOcean, Vultr, Linode ou AWS Lightsail.

1. Crie o servidor Ubuntu 22.04/24.04 LTS.
2. Acesse via SSH:

```bash
ssh root@SEU_IP_DA_VPS
```

3. Instale o Docker:

```bash
curl -fsSL https://get.docker.com | sh
systemctl enable --now docker
```

Verifique a instalação:

```bash
docker --version
docker compose version
```

## 3. Configurar DNS

No painel do seu registrador de domínio (Cloudflare, Namecheap, etc.), crie os registros apontando para o IP da VPS:

| Tipo  | Nome    | Conteúdo         | TTL   |
|-------|---------|------------------|-------|
| A     | @       | SEU_IP_DA_VPS    | Auto  |
| A     | www     | SEU_IP_DA_VPS    | Auto  |
| A     | api     | SEU_IP_DA_VPS    | Auto  |

Dica: se usar Cloudflare, você pode marcar o proxy (nuvem laranja). Para o `api`, deixe em **DNS only** (nuvem cinza) se quiser gerenciar o SSL com Certbot diretamente, ou use o SSL flexível da Cloudflare.

## 4. Clonar o projeto

```bash
cd /opt
git clone https://github.com/USUARIO/AudioFlow.git
cd AudioFlow
```

## 5. Configurar o .env

```bash
cp .env.example .env
nano .env
```

Preencha **obrigatoriamente**:

```
POSTGRES_PASSWORD=uma_senha_forte
JWT_SECRET_KEY=uma_chave_aleatoria_longa
FIRST_ADMIN_EMAIL=voce@exemplo.com
FIRST_ADMIN_PASSWORD=senha_forte_do_admin
```

Ajuste os domínios:

```
FRONTEND_URL=https://audioflow.com
API_BASE_URL=https://api.audioflow.com
CORS_ORIGINS=https://audioflow.com,https://www.audioflow.com
```

Gere uma chave JWT segura:

```bash
openssl rand -hex 32
```

## 6. Executar com Docker Compose

```bash
docker compose up -d --build
```

Verifique que tudo subiu:

```bash
docker compose ps
docker compose logs -f backend
```

A estrutura sobe: `postgres`, `redis`, `backend`, `worker`, `frontend` e `nginx`.

## 7. Configurar SSL com Let's Encrypt

Instale o Certbot:

```bash
apt update && apt install -y certbot
```

Gere os certificados para os dois domínios:

```bash
certbot certonly --standalone -d audioflow.com -d www.audioflow.com
certbot certonly --standalone -d api.audioflow.com
```

> O modo `--standalone` precisa da porta 80 livre por alguns segundos. Pare o nginx temporariamente se necessário: `docker compose stop nginx`.

Configure a renovação automática (Certbot instala um timer por padrão; verifique com `systemctl list-timers | grep certbot`).

### Integrar SSL no Nginx

Adicione os blocos SSL ao `nginx/nginx.conf` apontando para os certificados. Os certificados ficam em `/etc/letsencrypt/live/...`. Monte esse diretório no container nginx editando o `docker-compose.yml`:

```yaml
  nginx:
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/conf.d/default.conf:ro
      - /etc/letsencrypt:/etc/letsencrypt:ro
```

E adicione no `nginx.conf`:

```nginx
server {
    listen 443 ssl http2;
    server_name audioflow.com www.audioflow.com;
    ssl_certificate /etc/letsencrypt/live/audioflow.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/audioflow.com/privkey.pem;
    location / { proxy_pass http://frontend:80; ... }
}
```

Recarregue:

```bash
docker compose restart nginx
```

## 8. Criar o primeiro administrador

O primeiro admin é criado automaticamente no primeiro boot, usando `FIRST_ADMIN_EMAIL` e `FIRST_ADMIN_PASSWORD` do `.env`.

Se já subiu sem configurar, redefina o `.env`, reinicie e a conta será criada:

```bash
docker compose down
# edite .env com FIRST_ADMIN_*
docker compose up -d
```

Depois, acesse `https://audioflow.com/admin` e faça login com esse e-mail/senha.

## 9. Backup e restauração do PostgreSQL

### Backup

```bash
docker compose exec -T postgres pg_dump -U audioflow audioflow > backup_$(date +%F).sql
```

Para automatizar com cron (backup diário às 03:00):

```bash
crontab -e
# adicione:
0 3 * * * cd /opt/AudioFlow && docker compose exec -T postgres pg_dump -U audioflow audioflow > /opt/backups/audioflow_$(date +\%F).sql
```

### Restaurar

```bash
cat backup_2026-01-01.sql | docker compose exec -T postgres psql -U audioflow audioflow
```

## 10. Atualizar o sistema

```bash
cd /opt/AudioFlow
git pull
docker compose up -d --build
docker compose exec backend alembic upgrade head
docker compose restart worker
```

## 11. Troubleshooting

### Worker não processa downloads
```bash
docker compose logs -f worker
# verificar Redis:
docker compose exec redis redis-cli ping
```

### yt-dlp falha
```bash
docker compose exec backend pip install -U yt-dlp
docker compose restart worker
```

### FFmpeg não encontrado
Está instalado na imagem do backend. Em caso de problema, verifique:
```bash
docker compose exec backend ffmpeg -version
```

### Erros de CORS
Confira `CORS_ORIGINS` no `.env` e certifique-se de que inclui o domínio exato do frontend.

### Ver logs gerais
```bash
docker compose logs -f
```

---

## Acesso final

- **Site**: https://audioflow.com
- **API**: https://api.audioflow.com
- **Docs da API**: https://api.audioflow.com/docs
- **Admin**: https://audioflow.com/admin