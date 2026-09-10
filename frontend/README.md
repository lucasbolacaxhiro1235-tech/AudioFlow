# AudioFlow Frontend

Frontend estático para Cloudflare Pages - HTML5, CSS3, JavaScript (ES Modules).

## Estrutura

```text
frontend/
├── index.html          # Entry point
├── style.css           # Estilos completos
├── script.js           # Lógica da aplicação
├── assets/
│   ├── images/         # Imagens estáticas
│   └── icons/          # Ícones (SVG preferido)
└── README.md
```

## Tecnologias

- **HTML5** semântico
- **CSS3** com Custom Properties (CSS Variables)
- **JavaScript ES Modules** (import/export)
- **Web Audio API** via `<audio>` element
- **localStorage** para persistência client-side

## Funcionalidades

### Páginas
- **Home** (`/`) - Hero, features, CTA
- **Explorar** (`/explorar`) - Abas: Populares, Recentes, Artistas, Álbuns, Playlists, Categorias
- **Biblioteca** (`/biblioteca`) - Músicas, Playlists, Histórico, Baixadas
- **Playlists** (`/playlists`) - Todas as playlists
- **Favoritos** (`/favoritos`) - Músicas, Álbuns, Artistas

### Componentes
- **Navbar** - Logo, navegação, busca, tema, menu usuário
- **Player Fixo** - Controles completos, progresso, volume, fila
- **Modal Auth** - Login/Registro
- **Modal Playlist** - Criar/Editar
- **Toast Notifications** - Success, Error, Warning, Info
- **Search Dropdown** - Resultados em tempo real
- **Queue Panel** - Fila lateral

### Estados
- Mock data para desenvolvimento
- Persistência: favoritos, playlists, histórico, fila, volume, tema, usuário
- Troca fácil para API real (variável `API_BASE`)

## Desenvolvimento

### Servir Localmente

```bash
# Python 3
cd frontend
python -m http.server 3000

# Node.js
npx live-server --port 3000

# PHP
php -S localhost:3000
```

Acesse: `http://localhost:3000`

### Conexão com Backend

Edite `script.js`:
```javascript
const API_BASE = 'http://localhost:8000/api';  // Desenvolvimento
// const API_BASE = 'https://api.audioflow.com.br/api';  // Produção
```

Substitua chamadas mock por fetch reais:
```javascript
// Exemplo: busca real
async function handleSearch() {
    const response = await fetch(`${API_BASE}/search?q=${query}`);
    const data = await response.json();
    // renderizar data.tracks, data.artists, etc.
}
```

## Deploy Cloudflare Pages

1. Push para GitHub
2. Cloudflare Dashboard → Pages → Create a project
3. Connect to Git → Selecione repo
4. Configuração:
   - **Project name**: `audioflow`
   - **Production branch**: `main`
   - **Build command**: (deixe vazio)
   - **Build output directory**: `frontend`
5. Save and Deploy

### Domínio Personalizado

1. Pages → Seu projeto → Custom domains
2. Add `audioflow.com.br`
3. Configure DNS no Cloudflare (CNAME para `*.pages.dev`)

### Variáveis de Ambiente (Pages)

Se necessário:
- `API_URL` = `https://api.audioflow.com.br`

## CSS Architecture

### Design Tokens (`:root`)
```css
--color-bg: #0d0d0d;
--color-bg-elevated: #141414;
--color-primary: #1db954;
--color-text: #ffffff;
--font-sans: 'Inter', system-ui;
--radius-md: 10px;
--shadow-md: 0 4px 12px rgba(0,0,0,0.4);
--transition-base: 250ms ease;
```

### Dark/Light Mode
```css
[data-theme="light"] {
    --color-bg: #f5f5f5;
    --color-text: #121212;
    /* ... */
}
```

### Componentes Principais
- `.btn`, `.btn-primary`, `.btn-secondary`, `.btn-ghost`, `.btn-icon`
- `.card`, `.track-card`, `.playlist-card`, `.album-card`, `.artist-card`
- `.player-bar`, `.progress-bar`, `.volume-slider`
- `.modal`, `.toast`, `.dropdown`

## JavaScript Architecture

### Estado Global
```javascript
const state = {
    currentPage, currentTrack, isPlaying, volume,
    queue, queueIndex, shuffle, repeat,
    favorites, playlists, history, user,
    searchQuery, activeFilter, activeLibraryTab, activeFavoriteTab
};
```

### Funções Principais
- `navigateTo(page)` - SPA navigation
- `renderCurrentPage()` - Render baseado em state.currentPage
- `playTrack(id, playlistTracks)` - Play com queue opcional
- `togglePlay()`, `playNext()`, `playPrevious()`
- `toggleFavorite(id)`, `addToHistory(id)`
- `openModal(id)`, `closeAllModals()`
- `showToast(msg, type)`

### Persistência
```javascript
const STORAGE_KEYS = {
    TOKEN, USER, THEME, VOLUME, QUEUE,
    CURRENT_TRACK, PLAYBACK_STATE,
    FAVORITES, PLAYLISTS, HISTORY
};
```

## Acessibilidade

- Semantic HTML5
- ARIA labels e roles
- Focus visible
- Keyboard navigation
- `prefers-reduced-motion`
- `prefers-contrast: high`
- Screen reader friendly

## Performance

- CSS otimizado (sem frameworks)
- JS modular (ES Modules)
- Lazy loading images
- Debounced search (300ms)
- CSS animations (transform/opacity)
- Minimal DOM manipulation

## Browser Support

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## Customização

### Cores
Edite `:root` em `style.css`

### Fonte
```html
<!-- index.html -->
<link href="https://fonts.googleapis.com/css2?family=Sua+Fonte:wght@400;500;600;700&display=swap" rel="stylesheet">
```
```css
/* style.css */
--font-sans: 'Sua Fonte', system-ui;
```

### Mock Data
Edite `mockData` em `script.js`

## Checklist Deploy

- [ ] `API_BASE` apontando para produção
- [ ] Remover `console.log` de debug
- [ ] Testar em mobile/tablet/desktop
- [ ] Verificar CORS no backend
- [ ] Configurar domínio no Cloudflare
- [ ] SSL/HTTPS ativo
- [ ] Cache headers (Cloudflare automático)