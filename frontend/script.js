const API_BASE = '/api';
const STORAGE_KEYS = {
    TOKEN: 'audioflow_token',
    USER: 'audioflow_user',
    THEME: 'audioflow_theme',
    VOLUME: 'audioflow_volume',
    QUEUE: 'audioflow_queue',
    CURRENT_TRACK: 'audioflow_current_track',
    PLAYBACK_STATE: 'audioflow_playback_state',
    FAVORITES: 'audioflow_favorites',
    PLAYLISTS: 'audioflow_playlists',
    HISTORY: 'audioflow_history'
};

const mockData = {
    tracks: [
        { id: '1', title: 'Blinding Lights', artist: 'The Weeknd', album: 'After Hours', duration: 200, cover: 'https://i.scdn.co/image/ab67616d0000b2738863bc11d2aa12b54f5aeb36', audioUrl: 'https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3', artistId: 'artist1', albumId: 'album1', isFavorite: false },
        { id: '2', title: 'Shape of You', artist: 'Ed Sheeran', album: '÷ (Divide)', duration: 233, cover: 'https://i.scdn.co/image/ab67616d0000b273ba5db46f4b838ef6027e6f96', audioUrl: 'https://www.soundhelix.com/examples/mp3/SoundHelix-Song-2.mp3', artistId: 'artist2', albumId: 'album2', isFavorite: true },
        { id: '3', title: 'Levitating', artist: 'Dua Lipa', album: 'Future Nostalgia', duration: 203, cover: 'https://i.scdn.co/image/ab67616d0000b273bd0e8e81f4c4f83b5c6e0b8e', audioUrl: 'https://www.soundhelix.com/examples/mp3/SoundHelix-Song-3.mp3', artistId: 'artist3', albumId: 'album3', isFavorite: false },
        { id: '4', title: 'Bad Guy', artist: 'Billie Eilish', album: 'WHEN WE ALL FALL ASLEEP, WHERE DO WE GO?', duration: 194, cover: 'https://i.scdn.co/image/ab67616d0000b273b3a2b8e8f4c4f83b5c6e0b8e', audioUrl: 'https://www.soundhelix.com/examples/mp3/SoundHelix-Song-4.mp3', artistId: 'artist4', albumId: 'album4', isFavorite: true },
        { id: '5', title: 'Watermelon Sugar', artist: 'Harry Styles', album: 'Fine Line', duration: 174, cover: 'https://i.scdn.co/image/ab67616d0000b273c8d8e8f4c4f83b5c6e0b8e', audioUrl: 'https://www.soundhelix.com/examples/mp3/SoundHelix-Song-5.mp3', artistId: 'artist5', albumId: 'album5', isFavorite: false },
        { id: '6', title: 'Good 4 U', artist: 'Olivia Rodrigo', album: 'SOUR', duration: 178, cover: 'https://i.scdn.co/image/ab67616d0000b273d8e8f4c4f83b5c6e0b8e', audioUrl: 'https://www.soundhelix.com/examples/mp3/SoundHelix-Song-6.mp3', artistId: 'artist6', albumId: 'album6', isFavorite: false },
        { id: '7', title: 'Stay', artist: 'The Kid LAROI, Justin Bieber', album: 'F*CK LOVE 3+: OVER YOU', duration: 138, cover: 'https://i.scdn.co/image/ab67616d0000b273e8f4c4f83b5c6e0b8e', audioUrl: 'https://www.soundhelix.com/examples/mp3/SoundHelix-Song-7.mp3', artistId: 'artist7', albumId: 'album7', isFavorite: true },
        { id: '8', title: 'Industry Baby', artist: 'Lil Nas X, Jack Harlow', album: 'MONTERO', duration: 212, cover: 'https://i.scdn.co/image/ab67616d0000b273f4c4f83b5c6e0b8e', audioUrl: 'https://www.soundhelix.com/examples/mp3/SoundHelix-Song-8.mp3', artistId: 'artist8', albumId: 'album8', isFavorite: false },
        { id: '9', title: 'Heat Waves', artist: 'Glass Animals', album: 'Dreamland', duration: 238, cover: 'https://i.scdn.co/image/ab67616d0000b273a8e8f4c4f83b5c6e0b8e', audioUrl: 'https://www.soundhelix.com/examples/mp3/SoundHelix-Song-9.mp3', artistId: 'artist9', albumId: 'album9', isFavorite: false },
        { id: '10', title: 'As It Was', artist: 'Harry Styles', album: 'Harry\'s House', duration: 168, cover: 'https://i.scdn.co/image/ab67616d0000b273b4c4f83b5c6e0b8e', audioUrl: 'https://www.soundhelix.com/examples/mp3/SoundHelix-Song-10.mp3', artistId: 'artist5', albumId: 'album10', isFavorite: true },
        { id: '11', title: 'Unholy', artist: 'Sam Smith, Kim Petras', album: 'Gloria', duration: 156, cover: 'https://i.scdn.co/image/ab67616d0000b273c4f83b5c6e0b8e', audioUrl: 'https://www.soundhelix.com/examples/mp3/SoundHelix-Song-11.mp3', artistId: 'artist10', albumId: 'album11', isFavorite: false },
        { id: '12', title: 'Calm Down', artist: 'Rema, Selena Gomez', album: 'Rave & Roses', duration: 239, cover: 'https://i.scdn.co/image/ab67616d0000b273d4f83b5c6e0b8e', audioUrl: 'https://www.soundhelix.com/examples/mp3/SoundHelix-Song-12.mp3', artistId: 'artist11', albumId: 'album12', isFavorite: false }
    ],
    artists: [
        { id: 'artist1', name: 'The Weeknd', image: 'https://i.scdn.co/image/ab6761610000e5eb8863bc11d2aa12b54f5aeb36', followers: 85000000, genres: ['pop', 'r&b'] },
        { id: 'artist2', name: 'Ed Sheeran', image: 'https://i.scdn.co/image/ab6761610000e5ebba5db46f4b838ef6027e6f96', followers: 92000000, genres: ['pop', 'folk'] },
        { id: 'artist3', name: 'Dua Lipa', image: 'https://i.scdn.co/image/ab6761610000e5ebbd0e8e81f4c4f83b5c6e0b8e', followers: 68000000, genres: ['pop', 'dance'] },
        { id: 'artist4', name: 'Billie Eilish', image: 'https://i.scdn.co/image/ab6761610000e5ebb3a2b8e8f4c4f83b5c6e0b8e', followers: 72000000, genres: ['pop', 'alternative'] },
        { id: 'artist5', name: 'Harry Styles', image: 'https://i.scdn.co/image/ab6761610000e5ebc8d8e8f4c4f83b5c6e0b8e', followers: 78000000, genres: ['pop', 'rock'] },
        { id: 'artist6', name: 'Olivia Rodrigo', image: 'https://i.scdn.co/image/ab6761610000e5ebd8e8f4c4f83b5c6e0b8e', followers: 55000000, genres: ['pop', 'rock'] },
        { id: 'artist7', name: 'The Kid LAROI', image: 'https://i.scdn.co/image/ab6761610000e5ebe8f4c4f83b5c6e0b8e', followers: 32000000, genres: ['hip-hop', 'pop'] },
        { id: 'artist8', name: 'Lil Nas X', image: 'https://i.scdn.co/image/ab6761610000e5ebf4c4f83b5c6e0b8e', followers: 45000000, genres: ['hip-hop', 'pop'] },
        { id: 'artist9', name: 'Glass Animals', image: 'https://i.scdn.co/image/ab6761610000e5eba8e8f4c4f83b5c6e0b8e', followers: 18000000, genres: ['alternative', 'indie'] },
        { id: 'artist10', name: 'Sam Smith', image: 'https://i.scdn.co/image/ab6761610000e5ebc4f83b5c6e0b8e', followers: 48000000, genres: ['pop', 'r&b'] },
        { id: 'artist11', name: 'Rema', image: 'https://i.scdn.co/image/ab6761610000e5ebd4f83b5c6e0b8e', followers: 25000000, genres: ['afrobeats', 'pop'] }
    ],
    albums: [
        { id: 'album1', title: 'After Hours', artist: 'The Weeknd', cover: 'https://i.scdn.co/image/ab67616d0000b2738863bc11d2aa12b54f5aeb36', releaseDate: '2020-03-20', totalTracks: 14, artistId: 'artist1' },
        { id: 'album2', title: '÷ (Divide)', artist: 'Ed Sheeran', cover: 'https://i.scdn.co/image/ab67616d0000b273ba5db46f4b838ef6027e6f96', releaseDate: '2017-03-03', totalTracks: 16, artistId: 'artist2' },
        { id: 'album3', title: 'Future Nostalgia', artist: 'Dua Lipa', cover: 'https://i.scdn.co/image/ab67616d0000b273bd0e8e81f4c4f83b5c6e0b8e', releaseDate: '2020-03-27', totalTracks: 11, artistId: 'artist3' },
        { id: 'album4', title: 'WHEN WE ALL FALL ASLEEP, WHERE DO WE GO?', artist: 'Billie Eilish', cover: 'https://i.scdn.co/image/ab67616d0000b273b3a2b8e8f4c4f83b5c6e0b8e', releaseDate: '2019-03-29', totalTracks: 14, artistId: 'artist4' },
        { id: 'album5', title: 'Fine Line', artist: 'Harry Styles', cover: 'https://i.scdn.co/image/ab67616d0000b273c8d8e8f4c4f83b5c6e0b8e', releaseDate: '2019-12-13', totalTracks: 12, artistId: 'artist5' },
        { id: 'album6', title: 'SOUR', artist: 'Olivia Rodrigo', cover: 'https://i.scdn.co/image/ab67616d0000b273d8e8f4c4f83b5c6e0b8e', releaseDate: '2021-05-21', totalTracks: 11, artistId: 'artist6' },
        { id: 'album7', title: 'F*CK LOVE 3+: OVER YOU', artist: 'The Kid LAROI', cover: 'https://i.scdn.co/image/ab67616d0000b273e8f4c4f83b5c6e0b8e', releaseDate: '2021-07-23', totalTracks: 18, artistId: 'artist7' },
        { id: 'album8', title: 'MONTERO', artist: 'Lil Nas X', cover: 'https://i.scdn.co/image/ab67616d0000b273f4c4f83b5c6e0b8e', releaseDate: '2021-09-17', totalTracks: 15, artistId: 'artist8' },
        { id: 'album9', title: 'Dreamland', artist: 'Glass Animals', cover: 'https://i.scdn.co/image/ab67616d0000b273a8e8f4c4f83b5c6e0b8e', releaseDate: '2020-08-07', totalTracks: 16, artistId: 'artist9' },
        { id: 'album10', title: 'Harry\'s House', artist: 'Harry Styles', cover: 'https://i.scdn.co/image/ab67616d0000b273b4c4f83b5c6e0b8e', releaseDate: '2022-05-20', totalTracks: 13, artistId: 'artist5' },
        { id: 'album11', title: 'Gloria', artist: 'Sam Smith', cover: 'https://i.scdn.co/image/ab67616d0000b273c4f83b5c6e0b8e', releaseDate: '2023-01-27', totalTracks: 13, artistId: 'artist10' },
        { id: 'album12', title: 'Rave & Roses', artist: 'Rema', cover: 'https://i.scdn.co/image/ab67616d0000b273d4f83b5c6e0b8e', releaseDate: '2022-03-25', totalTracks: 16, artistId: 'artist11' }
    ],
    playlists: [
        { id: 'pl1', name: 'Top Hits 2024', description: 'As músicas mais tocadas do momento', cover: 'https://i.scdn.co/image/ab67616d0000b2738863bc11d2aa12b54f5aeb36', tracks: ['1', '2', '3', '4', '5'], owner: 'AudioFlow', isOwner: true },
        { id: 'pl2', name: 'Chill Vibes', description: 'Para relaxar e curtir o momento', cover: 'https://i.scdn.co/image/ab67616d0000b273bd0e8e81f4c4f83b5c6e0b8e', tracks: ['3', '5', '9', '10', '12'], owner: 'AudioFlow', isOwner: true },
        { id: 'pl3', name: 'Workout Energy', description: 'Músicas para treinar com força total', cover: 'https://i.scdn.co/image/ab67616d0000b273b3a2b8e8f4c4f83b5c6e0b8e', tracks: ['1', '4', '6', '7', '8'], owner: 'AudioFlow', isOwner: true },
        { id: 'pl4', name: 'Late Night Drive', description: 'A trilha sonora perfeita para a noite', cover: 'https://i.scdn.co/image/ab67616d0000b273c8d8e8f4c4f83b5c6e0b8e', tracks: ['2', '5', '9', '10', '11'], owner: 'AudioFlow', isOwner: true },
        { id: 'pl5', name: 'Pop Rising', description: 'Os novos nomes do pop mundial', cover: 'https://i.scdn.co/image/ab67616d0000b273d8e8f4c4f83b5c6e0b8e', tracks: ['6', '7', '10', '11', '12'], owner: 'AudioFlow', isOwner: false },
        { id: 'pl6', name: 'Indie Gems', description: 'Descobertas independentes incríveis', cover: 'https://i.scdn.co/image/ab67616d0000b273a8e8f4c4f83b5c6e0b8e', tracks: ['9', '12'], owner: 'AudioFlow', isOwner: false }
    ],
    categories: [
        { id: 'pop', name: 'Pop', icon: '🎵', color: 'linear-gradient(135deg, #1db954, #1ed760)' },
        { id: 'rock', name: 'Rock', icon: '🎸', color: 'linear-gradient(135deg, #e01e5a, #ff6b6b)' },
        { id: 'hiphop', name: 'Hip-Hop', icon: '🎤', color: 'linear-gradient(135deg, #7c3aed, #a855f7)' },
        { id: 'electronic', name: 'Eletrônica', icon: '🎹', color: 'linear-gradient(135deg, #06b6d4, #22d3ee)' },
        { id: 'rnb', name: 'R&B', icon: '🎷', color: 'linear-gradient(135deg, #ec4899, #f472b6)' },
        { id: 'latin', name: 'Latina', icon: '💃', color: 'linear-gradient(135deg, #f97316, #fb923c)' },
        { id: 'indie', name: 'Indie', icon: '🎨', color: 'linear-gradient(135deg, #84cc16, #a3e635)' },
        { id: 'jazz', name: 'Jazz', icon: '🎺', color: 'linear-gradient(135deg, #6366f1, #818cf8)' }
    ]
};

let state = {
    currentPage: 'home',
    currentTrack: null,
    isPlaying: false,
    volume: 0.8,
    queue: [],
    queueIndex: -1,
    shuffle: false,
    repeat: 'off',
    favorites: [],
    playlists: [],
    history: [],
    user: null,
    searchQuery: '',
    searchResults: { tracks: [], artists: [], albums: [], playlists: [] },
    isSearchOpen: false,
    activeFilter: 'populares',
    activeLibraryTab: 'musicas',
    activeFavoriteTab: 'musicas'
};

const audio = document.getElementById('audio-element');

function init() {
    loadState();
    applyTheme();
    setupEventListeners();
    renderCurrentPage();
    updatePlayerUI();
    checkAuthState();
}

function loadState() {
    try {
        const savedTheme = localStorage.getItem(STORAGE_KEYS.THEME);
        if (savedTheme) document.documentElement.setAttribute('data-theme', savedTheme);

        const savedVolume = localStorage.getItem(STORAGE_KEYS.VOLUME);
        if (savedVolume !== null) state.volume = parseFloat(savedVolume);

        const savedFavorites = localStorage.getItem(STORAGE_KEYS.FAVORITES);
        if (savedFavorites) state.favorites = JSON.parse(savedFavorites);

        const savedPlaylists = localStorage.getItem(STORAGE_KEYS.PLAYLISTS);
        if (savedPlaylists) state.playlists = JSON.parse(savedPlaylists);

        const savedHistory = localStorage.getItem(STORAGE_KEYS.HISTORY);
        if (savedHistory) state.history = JSON.parse(savedHistory);

        const savedQueue = localStorage.getItem(STORAGE_KEYS.QUEUE);
        if (savedQueue) {
            const queueData = JSON.parse(savedQueue);
            state.queue = queueData.queue || [];
            state.queueIndex = queueData.index || -1;
        }

        const savedTrack = localStorage.getItem(STORAGE_KEYS.CURRENT_TRACK);
        if (savedTrack) state.currentTrack = JSON.parse(savedTrack);

        const savedPlayback = localStorage.getItem(STORAGE_KEYS.PLAYBACK_STATE);
        if (savedPlayback) {
            const playback = JSON.parse(savedPlayback);
            state.isPlaying = playback.isPlaying || false;
            state.shuffle = playback.shuffle || false;
            state.repeat = playback.repeat || 'off';
        }

        const savedUser = localStorage.getItem(STORAGE_KEYS.USER);
        if (savedUser) state.user = JSON.parse(savedUser);

        audio.volume = state.volume;
        document.getElementById('volume-slider').value = state.volume;
    } catch (e) {
        console.warn('Erro ao carregar estado:', e);
    }
}

function saveState() {
    try {
        localStorage.setItem(STORAGE_KEYS.VOLUME, state.volume.toString());
        localStorage.setItem(STORAGE_KEYS.FAVORITES, JSON.stringify(state.favorites));
        localStorage.setItem(STORAGE_KEYS.PLAYLISTS, JSON.stringify(state.playlists));
        localStorage.setItem(STORAGE_KEYS.HISTORY, JSON.stringify(state.history));
        localStorage.setItem(STORAGE_KEYS.QUEUE, JSON.stringify({ queue: state.queue, index: state.queueIndex }));
        localStorage.setItem(STORAGE_KEYS.CURRENT_TRACK, JSON.stringify(state.currentTrack));
        localStorage.setItem(STORAGE_KEYS.PLAYBACK_STATE, JSON.stringify({
            isPlaying: state.isPlaying,
            shuffle: state.shuffle,
            repeat: state.repeat
        }));
        if (state.user) localStorage.setItem(STORAGE_KEYS.USER, JSON.stringify(state.user));
    } catch (e) {
        console.warn('Erro ao salvar estado:', e);
    }
}

function applyTheme() {
    const theme = document.documentElement.getAttribute('data-theme') || 'dark';
    const themeToggle = document.getElementById('theme-toggle');
    if (themeToggle) {
        themeToggle.querySelector('.icon-sun').hidden = theme === 'dark';
        themeToggle.querySelector('.icon-moon').hidden = theme !== 'dark';
    }
}

function setupEventListeners() {
    document.querySelectorAll('.nav-link').forEach(link => {
        link.addEventListener('click', e => {
            e.preventDefault();
            navigateTo(link.dataset.page);
        });
    });

    document.querySelectorAll('.filter-tab').forEach(tab => {
        tab.addEventListener('click', () => setActiveFilter(tab.dataset.filter));
    });

    document.querySelectorAll('.library-tab').forEach(tab => {
        tab.addEventListener('click', () => setActiveLibraryTab(tab.dataset.library));
    });

    document.querySelectorAll('.favorite-tab').forEach(tab => {
        tab.addEventListener('click', () => setActiveFavoriteTab(tab.dataset.fav));
    });

    const searchInput = document.querySelector('.search-input');
    const searchResults = document.querySelector('.search-results');
    searchInput.addEventListener('input', debounce(handleSearch, 300));
    searchInput.addEventListener('focus', () => {
        if (searchInput.value.trim()) searchResults.classList.add('active');
    });
    document.addEventListener('click', e => {
        if (!e.target.closest('.navbar-search')) searchResults.classList.remove('active');
    });

    document.getElementById('theme-toggle').addEventListener('click', toggleTheme);

    document.getElementById('login-btn').addEventListener('click', () => openModal('auth-modal'));
    document.querySelectorAll('.auth-switch a').forEach(a => {
        a.addEventListener('click', e => {
            e.preventDefault();
            switchAuthForm(e.target.dataset.switch);
        });
    });
    document.getElementById('login-form').addEventListener('submit', handleLogin);
    document.getElementById('register-form').addEventListener('submit', handleRegister);
    document.getElementById('logout-btn').addEventListener('click', handleLogout);

    document.querySelectorAll('.modal-close, .modal-overlay').forEach(el => {
        el.addEventListener('click', e => {
            if (e.target === el) closeAllModals();
        });
    });
    document.addEventListener('keydown', e => {
        if (e.key === 'Escape') closeAllModals();
    });

    document.getElementById('create-playlist-btn').addEventListener('click', () => openModal('playlist-modal'));
    document.getElementById('new-playlist-btn').addEventListener('click', () => openModal('playlist-modal'));
    document.getElementById('cancel-playlist').addEventListener('click', closeAllModals);
    document.getElementById('playlist-form').addEventListener('submit', handleCreatePlaylist);

    audio.addEventListener('timeupdate', updateProgress);
    audio.addEventListener('ended', handleTrackEnded);
    audio.addEventListener('loadedmetadata', () => updateDuration());
    audio.addEventListener('error', handleAudioError);
    audio.addEventListener('waiting', () => showLoading(true));
    audio.addEventListener('canplay', () => showLoading(false));

    document.getElementById('player-play').addEventListener('click', togglePlay);
    document.getElementById('player-prev').addEventListener('click', playPrevious);
    document.getElementById('player-next').addEventListener('click', playNext);
    document.getElementById('player-shuffle').addEventListener('click', toggleShuffle);
    document.getElementById('player-repeat').addEventListener('click', toggleRepeat);
    document.getElementById('player-favorite').addEventListener('click', toggleCurrentTrackFavorite);
    document.getElementById('player-volume-btn').addEventListener('click', toggleMute);
    document.getElementById('volume-slider').addEventListener('input', e => setVolume(e.target.value));
    document.getElementById('progress-bar').addEventListener('click', seek);
    document.getElementById('player-queue').addEventListener('click', toggleQueue);
    document.getElementById('close-queue').addEventListener('click', toggleQueue);
    document.getElementById('explore-from-queue').addEventListener('click', () => {
        toggleQueue();
        navigateTo('explorar');
    });

    document.getElementById('navbar-hamburger').addEventListener('click', toggleMobileMenu);
    document.getElementById('sort-musicas').addEventListener('change', renderLibraryTracks);

    document.getElementById('cta-login').addEventListener('click', e => {
        e.preventDefault();
        openModal('auth-modal');
    });
}

function navigateTo(page) {
    document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
    document.querySelectorAll('.nav-link').forEach(l => l.classList.remove('active'));

    const targetPage = document.getElementById(`page-${page}`);
    const targetLink = document.querySelector(`.nav-link[data-page="${page}"]`);

    if (targetPage) targetPage.classList.add('active');
    if (targetLink) targetLink.classList.add('active');

    state.currentPage = page;
    renderCurrentPage();
    closeMobileMenu();
}

function renderCurrentPage() {
    switch (state.currentPage) {
        case 'home':
            renderHome();
            break;
        case 'explorar':
            renderExplore();
            break;
        case 'biblioteca':
            renderLibrary();
            break;
        case 'playlists':
            renderPlaylistsPage();
            break;
        case 'favoritos':
            renderFavorites();
            break;
    }
}

function renderHome() {
    renderTrackGrid('popular-tracks', mockData.tracks.slice(0, 8));
    renderTrackGrid('recent-tracks', [...mockData.tracks].sort((a, b) => b.id - a.id).slice(0, 8));
    renderArtistGrid('featured-artists', mockData.artists.slice(0, 8));
    renderAlbumGrid('popular-albums', mockData.albums.slice(0, 8));
    renderPlaylistGrid('featured-playlists', mockData.playlists.slice(0, 6));
    renderCategoryGrid('categories-grid', mockData.categories);
}

function renderExplore() {
    const sections = {
        populares: () => renderTrackGrid('popular-tracks', mockData.tracks.slice(0, 12)),
        recentes: () => renderTrackGrid('recent-tracks', [...mockData.tracks].sort((a, b) => b.id - a.id).slice(0, 12)),
        artistas: () => renderArtistGrid('featured-artists', mockData.artists),
        albuns: () => renderAlbumGrid('popular-albums', mockData.albums),
        playlists: () => renderPlaylistGrid('featured-playlists', mockData.playlists),
        categorias: () => renderCategoryGrid('categories-grid', mockData.categories)
    };
    sections[state.activeFilter]?.();
}

function renderLibrary() {
    renderLibraryTracks();
    renderPlaylistGrid('library-playlists', state.playlists);
    renderTrackList('history-tracks', getHistoryTracks());
    renderTrackList('downloaded-tracks', []);
}

function renderPlaylistsPage() {
    renderPlaylistGrid('all-playlists', [...mockData.playlists, ...state.playlists]);
}

function renderFavorites() {
    const favTracks = mockData.tracks.filter(t => state.favorites.includes(t.id));
    const favAlbums = mockData.albums.filter(a => state.favorites.includes(a.id));
    const favArtists = mockData.artists.filter(a => state.favorites.includes(a.id));

    renderTrackList('favorite-tracks', favTracks);
    renderAlbumGrid('favorite-albums', favAlbums);
    renderArtistGrid('favorite-artists', favArtists);
}

function renderTrackGrid(containerId, tracks) {
    const container = document.getElementById(containerId);
    if (!container) return;

    container.innerHTML = tracks.map(track => `
        <article class="track-card" data-track-id="${track.id}" role="listitem">
            <div class="card-cover">
                <img src="${track.cover}" alt="${track.title}" loading="lazy">
                <div class="card-play-overlay">
                    <button class="card-play-btn" aria-label="Tocar ${track.title}">
                        <svg viewBox="0 0 24 24" fill="currentColor"><polygon points="5 3 19 12 5 21 5 3"/></svg>
                    </button>
                </div>
            </div>
            <div class="card-info">
                <h3 class="card-title">${escapeHtml(track.title)}</h3>
                <p class="card-subtitle">${escapeHtml(track.artist)}</p>
            </div>
            <div class="card-actions">
                <button class="card-action-btn favorite ${track.isFavorite || state.favorites.includes(track.id) ? 'active' : ''}" data-track-id="${track.id}" aria-label="${state.favorites.includes(track.id) ? 'Remover dos favoritos' : 'Adicionar aos favoritos'}">
                    <svg viewBox="0 0 24 24" fill="${state.favorites.includes(track.id) ? 'currentColor' : 'none'}" stroke="currentColor" stroke-width="2"><path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"/></svg>
                </button>
                <button class="card-action-btn add-to-playlist" data-track-id="${track.id}" aria-label="Adicionar à playlist">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
                </button>
            </div>
        </article>
    `).join('');

    container.querySelectorAll('.track-card').forEach(card => {
        card.addEventListener('click', e => {
            if (!e.target.closest('.card-action-btn')) {
                playTrack(card.dataset.trackId);
            }
        });
    });

    container.querySelectorAll('.card-action-btn.favorite').forEach(btn => {
        btn.addEventListener('click', e => {
            e.stopPropagation();
            toggleFavorite(btn.dataset.trackId);
        });
    });

    container.querySelectorAll('.card-action-btn.add-to-playlist').forEach(btn => {
        btn.addEventListener('click', e => {
            e.stopPropagation();
            showAddToPlaylist(btn.dataset.trackId);
        });
    });
}

function renderTrackList(containerId, tracks) {
    const container = document.getElementById(containerId);
    if (!container) return;

    if (tracks.length === 0) {
        container.innerHTML = `
            <div class="empty-state" style="text-align: center; padding: 3rem; color: var(--color-text-muted);">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" style="width: 64px; height: 64px; margin: 0 auto 1rem; opacity: 0.5;">
                    <path d="M12 2L2 7l10 5 10-5-10-5z"/>
                    <path d="M2 17l10 5 10-5"/>
                    <path d="M2 12l10 5 10-5"/>
                </svg>
                <p>Nenhuma música encontrada</p>
            </div>
        `;
        return;
    }

    container.innerHTML = tracks.map((track, index) => `
        <div class="track-row ${state.currentTrack?.id === track.id && state.isPlaying ? 'playing' : ''}" data-track-id="${track.id}" role="listitem">
            <span class="track-number">${index + 1}</span>
            <div class="track-main">
                <div class="track-cover">
                    <img src="${track.cover}" alt="${track.title}" loading="lazy">
                </div>
                <div class="track-details">
                    <span class="track-title">${escapeHtml(track.title)}</span>
                    <span class="track-artist">${escapeHtml(track.artist)}</span>
                </div>
            </div>
            <span class="track-album">${escapeHtml(track.album)}</span>
            <span class="track-duration">${formatDuration(track.duration)}</span>
            <div class="track-actions">
                <button class="track-action-btn favorite ${state.favorites.includes(track.id) ? 'active' : ''}" data-track-id="${track.id}" aria-label="${state.favorites.includes(track.id) ? 'Remover dos favoritos' : 'Adicionar aos favoritos'}">
                    <svg viewBox="0 0 24 24" fill="${state.favorites.includes(track.id) ? 'currentColor' : 'none'}" stroke="currentColor" stroke-width="2"><path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"/></svg>
                </button>
                <button class="track-action-btn add-to-playlist" data-track-id="${track.id}" aria-label="Adicionar à playlist">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
                </button>
                <button class="track-action-btn more-options" data-track-id="${track.id}" aria-label="Mais opções">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="1"/><circle cx="19" cy="12" r="1"/><circle cx="5" cy="12" r="1"/></svg>
                </button>
            </div>
        </div>
    `).join('');

    container.querySelectorAll('.track-row').forEach(row => {
        row.addEventListener('click', e => {
            if (!e.target.closest('.track-action-btn')) {
                playTrack(row.dataset.trackId);
            }
        });
    });

    container.querySelectorAll('.track-action-btn.favorite').forEach(btn => {
        btn.addEventListener('click', e => {
            e.stopPropagation();
            toggleFavorite(btn.dataset.trackId);
        });
    });
}

function renderArtistGrid(containerId, artists) {
    const container = document.getElementById(containerId);
    if (!container) return;

    container.innerHTML = artists.map(artist => `
        <article class="artist-card" data-artist-id="${artist.id}" role="listitem">
            <div class="card-cover">
                <img src="${artist.image}" alt="${artist.name}" loading="lazy">
                <div class="card-play-overlay">
                    <button class="card-play-btn" aria-label="Tocar ${artist.name}">
                        <svg viewBox="0 0 24 24" fill="currentColor"><polygon points="5 3 19 12 5 21 5 3"/></svg>
                    </button>
                </div>
            </div>
            <div class="card-info">
                <h3 class="card-title">${escapeHtml(artist.name)}</h3>
                <p class="card-subtitle">Artista • ${formatNumber(artist.followers)} ouvintes</p>
            </div>
        </article>
    `).join('');

    container.querySelectorAll('.artist-card').forEach(card => {
        card.addEventListener('click', () => navigateToArtist(card.dataset.artistId));
    });
}

function renderAlbumGrid(containerId, albums) {
    const container = document.getElementById(containerId);
    if (!container) return;

    container.innerHTML = albums.map(album => `
        <article class="album-card" data-album-id="${album.id}" role="listitem">
            <div class="card-cover">
                <img src="${album.cover}" alt="${album.title}" loading="lazy">
                <div class="card-play-overlay">
                    <button class="card-play-btn" aria-label="Tocar ${album.title}">
                        <svg viewBox="0 0 24 24" fill="currentColor"><polygon points="5 3 19 12 5 21 5 3"/></svg>
                    </button>
                </div>
            </div>
            <div class="card-info">
                <h3 class="card-title">${escapeHtml(album.title)}</h3>
                <p class="card-subtitle">${escapeHtml(album.artist)}</p>
            </div>
            <div class="card-actions">
                <button class="card-action-btn favorite ${state.favorites.includes(album.id) ? 'active' : ''}" data-album-id="${album.id}" aria-label="${state.favorites.includes(album.id) ? 'Remover dos favoritos' : 'Adicionar aos favoritos'}">
                    <svg viewBox="0 0 24 24" fill="${state.favorites.includes(album.id) ? 'currentColor' : 'none'}" stroke="currentColor" stroke-width="2"><path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"/></svg>
                </button>
            </div>
        </article>
    `).join('');

    container.querySelectorAll('.album-card').forEach(card => {
        card.addEventListener('click', e => {
            if (!e.target.closest('.card-action-btn')) {
                navigateToAlbum(card.dataset.albumId);
            }
        });
    });

    container.querySelectorAll('.card-action-btn.favorite').forEach(btn => {
        btn.addEventListener('click', e => {
            e.stopPropagation();
            toggleFavoriteAlbum(btn.dataset.albumId);
        });
    });
}

function renderPlaylistGrid(containerId, playlists) {
    const container = document.getElementById(containerId);
    if (!container) return;

    container.innerHTML = playlists.map(playlist => `
        <article class="playlist-card" data-playlist-id="${playlist.id}" role="listitem">
            <div class="card-cover" style="background: ${playlist.cover?.startsWith('linear-gradient') ? playlist.cover : `url(${playlist.cover}) center/cover`};">
                ${!playlist.cover?.startsWith('linear-gradient') && !playlist.cover?.startsWith('http') ? `<div class="card-icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 2L2 7l10 5 10-5-10-5z"/><path d="M2 17l10 5 10-5"/><path d="M2 12l10 5 10-5"/></svg></div>` : ''}
                <div class="card-play-overlay">
                    <button class="card-play-btn" aria-label="Tocar playlist ${playlist.name}">
                        <svg viewBox="0 0 24 24" fill="currentColor"><polygon points="5 3 19 12 5 21 5 3"/></svg>
                    </button>
                </div>
            </div>
            <div class="card-info">
                <h3 class="card-title">${escapeHtml(playlist.name)}</h3>
                <p class="card-subtitle">${playlist.tracks?.length || 0} músicas • ${escapeHtml(playlist.owner)}</p>
            </div>
            <div class="card-actions">
                <button class="card-action-btn favorite ${state.favorites.includes(playlist.id) ? 'active' : ''}" data-playlist-id="${playlist.id}" aria-label="${state.favorites.includes(playlist.id) ? 'Remover dos favoritos' : 'Adicionar aos favoritos'}">
                    <svg viewBox="0 0 24 24" fill="${state.favorites.includes(playlist.id) ? 'currentColor' : 'none'}" stroke="currentColor" stroke-width="2"><path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"/></svg>
                </button>
                ${playlist.isOwner ? `
                    <button class="card-action-btn edit-playlist" data-playlist-id="${playlist.id}" aria-label="Editar playlist">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/></svg>
                    </button>
                    <button class="card-action-btn delete-playlist" data-playlist-id="${playlist.id}" aria-label="Excluir playlist">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/></svg>
                    </button>
                ` : ''}
            </div>
        </article>
    `).join('');

    container.querySelectorAll('.playlist-card').forEach(card => {
        card.addEventListener('click', e => {
            if (!e.target.closest('.card-action-btn')) {
                playPlaylist(card.dataset.playlistId);
            }
        });
    });

    container.querySelectorAll('.card-action-btn.favorite').forEach(btn => {
        btn.addEventListener('click', e => {
            e.stopPropagation();
            toggleFavoritePlaylist(btn.dataset.playlistId);
        });
    });

    container.querySelectorAll('.card-action-btn.edit-playlist').forEach(btn => {
        btn.addEventListener('click', e => {
            e.stopPropagation();
            editPlaylist(btn.dataset.playlistId);
        });
    });

    container.querySelectorAll('.card-action-btn.delete-playlist').forEach(btn => {
        btn.addEventListener('click', e => {
            e.stopPropagation();
            deletePlaylist(btn.dataset.playlistId);
        });
    });
}

function renderCategoryGrid(containerId, categories) {
    const container = document.getElementById(containerId);
    if (!container) return;

    container.innerHTML = categories.map(cat => `
        <article class="category-card" data-category="${cat.id}" role="listitem" style="--cat-color: ${cat.color};">
            <div class="card-cover" style="background: var(--cat-color);">
                <div class="card-icon">
                    <span style="font-size: 32px;">${cat.icon}</span>
                </div>
            </div>
            <div class="card-info">
                <h3 class="card-title">${cat.name}</h3>
            </div>
        </article>
    `).join('');

    container.querySelectorAll('.category-card').forEach(card => {
        card.addEventListener('click', () => filterByCategory(card.dataset.category));
    });
}

function setActiveFilter(filter) {
    state.activeFilter = filter;
    document.querySelectorAll('.filter-tab').forEach(tab => {
        tab.classList.toggle('active', tab.dataset.filter === filter);
        tab.setAttribute('aria-selected', tab.dataset.filter === filter);
    });
    document.querySelectorAll('.content-section').forEach(section => {
        section.classList.toggle('active', section.dataset.section === filter);
    });
    renderExplore();
}

function setActiveLibraryTab(tab) {
    state.activeLibraryTab = tab;
    document.querySelectorAll('.library-tab').forEach(t => {
        t.classList.toggle('active', t.dataset.library === tab);
        t.setAttribute('aria-selected', t.dataset.library === tab);
    });
    document.querySelectorAll('.library-panel').forEach(p => {
        p.classList.toggle('active', p.dataset.panel === tab);
    });
}

function setActiveFavoriteTab(tab) {
    state.activeFavoriteTab = tab;
    document.querySelectorAll('.favorite-tab').forEach(t => {
        t.classList.toggle('active', t.dataset.fav === tab);
        t.setAttribute('aria-selected', t.dataset.fav === tab);
    });
    document.querySelectorAll('.favorite-panel').forEach(p => {
        p.classList.toggle('active', p.dataset.favPanel === tab);
    });
    renderFavorites();
}

function renderLibraryTracks() {
    const sort = document.getElementById('sort-musicas').value;
    let tracks = [...mockData.tracks];

    switch (sort) {
        case 'alphabetical':
            tracks.sort((a, b) => a.title.localeCompare(b.title));
            break;
        case 'artist':
            tracks.sort((a, b) => a.artist.localeCompare(b.artist));
            break;
        case 'album':
            tracks.sort((a, b) => a.album.localeCompare(b.album));
            break;
        default:
            tracks.sort((a, b) => b.id - a.id);
    }

    renderTrackList('library-tracks', tracks);
}

function getHistoryTracks() {
    return state.history
        .map(id => mockData.tracks.find(t => t.id === id))
        .filter(Boolean)
        .reverse();
}

async function handleSearch() {
    const query = document.querySelector('.search-input').value.trim().toLowerCase();
    state.searchQuery = query;
    const results = document.querySelector('.search-results');

    if (!query) {
        results.classList.remove('active');
        results.innerHTML = '';
        return;
    }

    results.classList.add('active');
    results.innerHTML = '<div class="search-loading">Buscando...</div>';

    await new Promise(r => setTimeout(r, 300));

    const tracks = mockData.tracks.filter(t =>
        t.title.toLowerCase().includes(query) ||
        t.artist.toLowerCase().includes(query) ||
        t.album.toLowerCase().includes(query)
    );
    const artists = mockData.artists.filter(a =>
        a.name.toLowerCase().includes(query)
    );
    const albums = mockData.albums.filter(a =>
        a.title.toLowerCase().includes(query) ||
        a.artist.toLowerCase().includes(query)
    );
    const playlists = [...mockData.playlists, ...state.playlists].filter(p =>
        p.name.toLowerCase().includes(query)
    );

    state.searchResults = { tracks, artists, albums, playlists };

    if (tracks.length + artists.length + albums.length + playlists.length === 0) {
        results.innerHTML = '<div class="search-empty">Nenhum resultado encontrado</div>';
        return;
    }

    let html = '';
    if (tracks.length) {
        html += `<div class="search-section"><h4>Músicas</h4><div class="search-tracks">${tracks.slice(0, 5).map(t => `
            <button class="search-result-item" data-track-id="${t.id}">
                <img src="${t.cover}" alt="" style="width: 40px; height: 40px; border-radius: 4px;">
                <div>
                    <span class="search-result-title">${escapeHtml(t.title)}</span>
                    <span class="search-result-subtitle">${escapeHtml(t.artist)}</span>
                </div>
            </button>
        `).join('')}</div></div>`;
    }
    if (artists.length) {
        html += `<div class="search-section"><h4>Artistas</h4><div class="search-tracks">${artists.slice(0, 5).map(a => `
            <button class="search-result-item" data-artist-id="${a.id}">
                <img src="${a.image}" alt="" style="width: 40px; height: 40px; border-radius: 50%;">
                <div>
                    <span class="search-result-title">${escapeHtml(a.name)}</span>
                    <span class="search-result-subtitle">Artista</span>
                </div>
            </button>
        `).join('')}</div></div>`;
    }
    if (albums.length) {
        html += `<div class="search-section"><h4>Álbuns</h4><div class="search-tracks">${albums.slice(0, 5).map(a => `
            <button class="search-result-item" data-album-id="${a.id}">
                <img src="${a.cover}" alt="" style="width: 40px; height: 40px; border-radius: 4px;">
                <div>
                    <span class="search-result-title">${escapeHtml(a.title)}</span>
                    <span class="search-result-subtitle">${escapeHtml(a.artist)}</span>
                </div>
            </button>
        `).join('')}</div></div>`;
    }
    if (playlists.length) {
        html += `<div class="search-section"><h4>Playlists</h4><div class="search-tracks">${playlists.slice(0, 5).map(p => `
            <button class="search-result-item" data-playlist-id="${p.id}">
                <div style="width: 40px; height: 40px; border-radius: 4px; background: ${p.cover?.startsWith('linear-gradient') ? p.cover : `url(${p.cover}) center/cover`};"></div>
                <div>
                    <span class="search-result-title">${escapeHtml(p.name)}</span>
                    <span class="search-result-subtitle">Playlist • ${p.tracks?.length || 0} músicas</span>
                </div>
            </button>
        `).join('')}</div></div>`;
    }

    results.innerHTML = html;

    results.querySelectorAll('[data-track-id]').forEach(btn => {
        btn.addEventListener('click', () => {
            playTrack(btn.dataset.trackId);
            results.classList.remove('active');
        });
    });
    results.querySelectorAll('[data-artist-id]').forEach(btn => {
        btn.addEventListener('click', () => {
            navigateToArtist(btn.dataset.artistId);
            results.classList.remove('active');
        });
    });
    results.querySelectorAll('[data-album-id]').forEach(btn => {
        btn.addEventListener('click', () => {
            navigateToAlbum(btn.dataset.albumId);
            results.classList.remove('active');
        });
    });
    results.querySelectorAll('[data-playlist-id]').forEach(btn => {
        btn.addEventListener('click', () => {
            playPlaylist(btn.dataset.playlistId);
            results.classList.remove('active');
        });
    });
}

function toggleTheme() {
    const current = document.documentElement.getAttribute('data-theme');
    const newTheme = current === 'dark' ? 'light' : 'dark';
    document.documentElement.setAttribute('data-theme', newTheme);
    localStorage.setItem(STORAGE_KEYS.THEME, newTheme);
    applyTheme();
}

function checkAuthState() {
    const loginBtn = document.getElementById('login-btn');
    const userMenu = document.getElementById('user-menu');

    if (state.user) {
        loginBtn.hidden = true;
        userMenu.hidden = false;
        document.getElementById('user-name').textContent = state.user.name;
        document.getElementById('user-email').textContent = state.user.email;
        document.getElementById('user-avatar').textContent = state.user.name.charAt(0).toUpperCase();
    } else {
        loginBtn.hidden = false;
        userMenu.hidden = true;
    }
}

function handleLogin(e) {
    e.preventDefault();
    const email = document.getElementById('login-email').value;
    const password = document.getElementById('login-password').value;

    if (email && password) {
        state.user = { id: 'user1', name: email.split('@')[0], email };
        localStorage.setItem(STORAGE_KEYS.USER, JSON.stringify(state.user));
        closeAllModals();
        checkAuthState();
        showToast('Bem-vindo de volta!', 'success');
        document.getElementById('login-form').reset();
    }
}

function handleRegister(e) {
    e.preventDefault();
    const name = document.getElementById('register-name').value;
    const email = document.getElementById('register-email').value;
    const password = document.getElementById('register-password').value;
    const confirm = document.getElementById('register-confirm').value;

    if (password !== confirm) {
        showToast('As senhas não coincidem', 'error');
        return;
    }

    if (name && email && password) {
        state.user = { id: 'user1', name, email };
        localStorage.setItem(STORAGE_KEYS.USER, JSON.stringify(state.user));
        closeAllModals();
        checkAuthState();
        showToast('Conta criada com sucesso!', 'success');
        document.getElementById('register-form').reset();
    }
}

function handleLogout() {
    state.user = null;
    localStorage.removeItem(STORAGE_KEYS.USER);
    closeAllModals();
    checkAuthState();
    showToast('Você saiu da conta', 'info');
}

function switchAuthForm(form) {
    document.querySelectorAll('.auth-form').forEach(f => f.classList.remove('active'));
    document.getElementById(`${form}-form`).classList.add('active');
}

function openModal(modalId) {
    document.getElementById(modalId).classList.add('active');
    document.body.style.overflow = 'hidden';
    const firstInput = document.querySelector(`#${modalId} input`);
    if (firstInput) setTimeout(() => firstInput.focus(), 100);
}

function closeAllModals() {
    document.querySelectorAll('.modal-overlay').forEach(m => m.classList.remove('active'));
    document.body.style.overflow = '';
}

function handleCreatePlaylist(e) {
    e.preventDefault();
    const name = document.getElementById('playlist-name').value.trim();
    const description = document.getElementById('playlist-description').value.trim();
    const coverFile = document.getElementById('playlist-cover').files[0];

    if (!name) return;

    const newPlaylist = {
        id: 'pl_' + Date.now(),
        name,
        description,
        cover: coverFile ? URL.createObjectURL(coverFile) : `linear-gradient(135deg, ${getRandomColor()}, ${getRandomColor()})`,
        tracks: [],
        owner: state.user?.name || 'Você',
        isOwner: true,
        createdAt: new Date().toISOString()
    };

    state.playlists.unshift(newPlaylist);
    saveState();
    closeAllModals();
    showToast('Playlist criada!', 'success');
    document.getElementById('playlist-form').reset();

    if (state.currentPage === 'playlists' || state.currentPage === 'biblioteca') {
        renderCurrentPage();
    }
}

function editPlaylist(playlistId) {
    const playlist = state.playlists.find(p => p.id === playlistId) ||
                     mockData.playlists.find(p => p.id === playlistId);
    if (!playlist) return;

    document.getElementById('playlist-modal-title').textContent = 'Editar Playlist';
    document.getElementById('playlist-name').value = playlist.name;
    document.getElementById('playlist-description').value = playlist.description || '';
    document.getElementById('playlist-form').dataset.editId = playlistId;
    openModal('playlist-modal');
}

function deletePlaylist(playlistId) {
    if (confirm('Tem certeza que deseja excluir esta playlist?')) {
        state.playlists = state.playlists.filter(p => p.id !== playlistId);
        saveState();
        showToast('Playlist excluída', 'info');
        renderCurrentPage();
    }
}

function showAddToPlaylist(trackId) {
    if (state.playlists.length === 0) {
        showToast('Crie uma playlist primeiro', 'info');
        return;
    }

    const track = mockData.tracks.find(t => t.id === trackId);
    if (!track) return;

    const menu = document.createElement('div');
    menu.className = 'dropdown-menu';
    menu.style.cssText = `
        position: fixed;
        background: var(--color-surface);
        border: 1px solid var(--color-border);
        border-radius: var(--radius-lg);
        box-shadow: var(--shadow-xl);
        padding: 0.5rem;
        z-index: var(--z-dropdown);
        min-width: 200px;
    `;

    const rect = event.target.getBoundingClientRect();
    menu.style.top = `${rect.bottom + 8}px`;
    menu.style.left = `${rect.left}px`;

    state.playlists.forEach(pl => {
        const btn = document.createElement('button');
        btn.className = 'dropdown-item';
        btn.style.cssText = 'width: 100%; text-align: left; padding: 0.75rem 1rem; border-radius: var(--radius-md);';
        btn.textContent = pl.name;
        btn.addEventListener('click', () => {
            addTrackToPlaylist(trackId, pl.id);
            document.body.removeChild(menu);
        });
        menu.appendChild(btn);
    });

    document.body.appendChild(menu);
    const closeMenu = e => {
        if (!menu.contains(e.target)) {
            document.body.removeChild(menu);
            document.removeEventListener('click', closeMenu);
        }
    };
    setTimeout(() => document.addEventListener('click', closeMenu), 0);
}

function addTrackToPlaylist(trackId, playlistId) {
    const playlist = state.playlists.find(p => p.id === playlistId);
    if (playlist && !playlist.tracks.includes(trackId)) {
        playlist.tracks.push(trackId);
        saveState();
        showToast('Música adicionada à playlist', 'success');
    }
}

function playTrack(trackId, playlistTracks = null) {
    const track = mockData.tracks.find(t => t.id === trackId);
    if (!track) return;

    state.currentTrack = track;

    if (playlistTracks) {
        state.queue = playlistTracks.map(t => mockData.tracks.find(tr => tr.id === t)).filter(Boolean);
        state.queueIndex = state.queue.findIndex(t => t.id === trackId);
    } else {
        state.queue = [track];
        state.queueIndex = 0;
    }

    audio.src = track.audioUrl;
    audio.play().catch(err => {
        console.error('Erro ao reproduzir:', err);
        showToast('Erro ao reproduzir a música', 'error');
    });

    state.isPlaying = true;
    saveState();
    updatePlayerUI();
    addToHistory(trackId);
}

function playPlaylist(playlistId) {
    const playlist = state.playlists.find(p => p.id === playlistId) ||
                     mockData.playlists.find(p => p.id === playlistId);
    if (!playlist || !playlist.tracks.length) return;

    const firstTrack = mockData.tracks.find(t => t.id === playlist.tracks[0]);
    if (firstTrack) playTrack(firstTrack.id, playlist.tracks);
}

function togglePlay() {
    if (!state.currentTrack) {
        const firstTrack = mockData.tracks[0];
        if (firstTrack) playTrack(firstTrack.id);
        return;
    }

    if (state.isPlaying) {
        audio.pause();
    } else {
        audio.play().catch(err => {
            console.error('Erro ao reproduzir:', err);
            showToast('Erro ao reproduzir', 'error');
        });
    }
    state.isPlaying = !state.isPlaying;
    saveState();
    updatePlayerUI();
}

function playPrevious() {
    if (state.queue.length === 0) return;

    if (state.shuffle) {
        state.queueIndex = Math.floor(Math.random() * state.queue.length);
    } else {
        state.queueIndex = (state.queueIndex - 1 + state.queue.length) % state.queue.length;
    }
    playTrack(state.queue[state.queueIndex].id);
}

function playNext() {
    if (state.queue.length === 0) return;

    if (state.shuffle) {
        state.queueIndex = Math.floor(Math.random() * state.queue.length);
    } else {
        state.queueIndex = (state.queueIndex + 1) % state.queue.length;
    }
    playTrack(state.queue[state.queueIndex].id);
}

function handleTrackEnded() {
    if (state.repeat === 'one') {
        audio.currentTime = 0;
        audio.play();
        return;
    }
    playNext();
}

function toggleShuffle() {
    state.shuffle = !state.shuffle;
    document.getElementById('player-shuffle').classList.toggle('active', state.shuffle);
    saveState();
    showToast(state.shuffle ? 'Aleatório ativado' : 'Aleatório desativado', 'info');
}

function toggleRepeat() {
    const modes = ['off', 'all', 'one'];
    const currentIndex = modes.indexOf(state.repeat);
    state.repeat = modes[(currentIndex + 1) % modes.length];
    const btn = document.getElementById('player-repeat');
    btn.classList.toggle('active', state.repeat !== 'off');
    if (state.repeat === 'one') {
        btn.innerHTML = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 12a8 8 0 0 1 8-8V0M12 0v8M20 12a8 8 0 0 1-8 8v8M12 24v-8"/><text x="50%" y="50%" dominant-baseline="middle" text-anchor="middle" font-size="8" fill="currentColor">1</text></svg>';
    } else {
        btn.innerHTML = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 12a8 8 0 0 1 8-8V0M12 0v8M20 12a8 8 0 0 1-8 8v8M12 24v-8"/></svg>';
    }
    saveState();
    showToast(state.repeat === 'off' ? 'Repetir desativado' : state.repeat === 'one' ? 'Repetir uma' : 'Repetir tudo', 'info');
}

function toggleCurrentTrackFavorite() {
    if (!state.currentTrack) return;
    toggleFavorite(state.currentTrack.id);
}

function toggleFavorite(trackId) {
    const index = state.favorites.indexOf(trackId);
    if (index === -1) {
        state.favorites.push(trackId);
        showToast('Adicionado aos favoritos', 'success');
    } else {
        state.favorites.splice(index, 1);
        showToast('Removido dos favoritos', 'info');
    }
    saveState();
    updatePlayerUI();
    renderCurrentPage();
}

function toggleFavoriteAlbum(albumId) {
    const index = state.favorites.indexOf(albumId);
    if (index === -1) {
        state.favorites.push(albumId);
        showToast('Álbum adicionado aos favoritos', 'success');
    } else {
        state.favorites.splice(index, 1);
        showToast('Álbum removido dos favoritos', 'info');
    }
    saveState();
    renderCurrentPage();
}

function toggleFavoritePlaylist(playlistId) {
    const index = state.favorites.indexOf(playlistId);
    if (index === -1) {
        state.favorites.push(playlistId);
        showToast('Playlist adicionada aos favoritos', 'success');
    } else {
        state.favorites.splice(index, 1);
        showToast('Playlist removida dos favoritos', 'info');
    }
    saveState();
    renderCurrentPage();
}

function addToHistory(trackId) {
    state.history = state.history.filter(id => id !== trackId);
    state.history.unshift(trackId);
    if (state.history.length > 100) state.history = state.history.slice(0, 100);
    saveState();
}

function setVolume(value) {
    state.volume = parseFloat(value);
    audio.volume = state.volume;
    saveState();
    updateVolumeIcon();
}

function toggleMute() {
    if (audio.volume > 0) {
        audio.dataset.prevVolume = audio.volume;
        audio.volume = 0;
        document.getElementById('volume-slider').value = 0;
    } else {
        const prevVol = parseFloat(audio.dataset.prevVolume || state.volume);
        audio.volume = prevVol;
        document.getElementById('volume-slider').value = prevVol;
    }
    state.volume = audio.volume;
    saveState();
    updateVolumeIcon();
}

function updateVolumeIcon() {
    const btn = document.getElementById('player-volume-btn');
    const high = btn.querySelector('.icon-volume-high');
    const low = btn.querySelector('.icon-volume-low');
    const mute = btn.querySelector('.icon-volume-mute');

    high.hidden = true;
    low.hidden = true;
    mute.hidden = true;

    if (audio.volume === 0 || audio.muted) {
        mute.hidden = false;
    } else if (audio.volume < 0.5) {
        low.hidden = false;
    } else {
        high.hidden = false;
    }
}

function seek(e) {
    const bar = document.getElementById('progress-bar');
    const rect = bar.getBoundingClientRect();
    const percent = Math.max(0, Math.min(1, (e.clientX - rect.left) / rect.width));
    audio.currentTime = percent * audio.duration;
}

function updateProgress() {
    if (!audio.duration) return;
    const percent = (audio.currentTime / audio.duration) * 100;
    document.getElementById('progress-fill').style.width = `${percent}%`;
    document.getElementById('progress-handle').style.left = `${percent}%`;
    document.getElementById('player-current-time').textContent = formatTime(audio.currentTime);
    document.getElementById('progress-bar').setAttribute('aria-valuenow', Math.round(percent));
}

function updateDuration() {
    document.getElementById('player-duration').textContent = formatTime(audio.duration);
}

function updatePlayerUI() {
    if (!state.currentTrack) {
        document.getElementById('player-title').textContent = 'Nenhuma música tocando';
        document.getElementById('player-artist').textContent = 'Selecione uma música para começar';
        document.getElementById('player-cover').innerHTML = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M12 2L2 7l10 5 10-5-10-5z"/><path d="M2 17l10 5 10-5"/><path d="M2 12l10 5 10-5"/></svg>';
        document.getElementById('player-play').classList.remove('playing');
        document.getElementById('player-favorite').classList.remove('active');
        return;
    }

    const track = state.currentTrack;
    document.getElementById('player-title').textContent = track.title;
    document.getElementById('player-artist').textContent = track.artist;

    const cover = document.getElementById('player-cover');
    cover.innerHTML = `<img src="${track.cover}" alt="${track.title}">`;

    document.getElementById('player-play').classList.toggle('playing', state.isPlaying);
    document.getElementById('player-favorite').classList.toggle('active', state.favorites.includes(track.id));

    updateQueueUI();
    updateVolumeIcon();
}

function updateQueueUI() {
    const queueList = document.getElementById('queue-list');
    const queueEmpty = document.querySelector('.queue-empty');

    if (state.queue.length === 0) {
        queueList.innerHTML = '';
        queueEmpty.hidden = false;
        return;
    }

    queueEmpty.hidden = true;
    queueList.innerHTML = state.queue.map((track, index) => `
        <div class="queue-item ${index === state.queueIndex && state.isPlaying ? 'playing' : ''}" data-index="${index}">
            <div class="queue-item-cover">
                <img src="${track.cover}" alt="${track.title}">
            </div>
            <div class="queue-item-info">
                <span class="queue-item-title">${escapeHtml(track.title)}</span>
                <span class="queue-item-artist">${escapeHtml(track.artist)}</span>
            </div>
            <button class="queue-item-remove" data-index="${index}" aria-label="Remover da fila">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
            </button>
        </div>
    `).join('');

    queueList.querySelectorAll('.queue-item').forEach(item => {
        item.addEventListener('click', e => {
            if (!e.target.closest('.queue-item-remove')) {
                state.queueIndex = parseInt(item.dataset.index);
                playTrack(state.queue[state.queueIndex].id);
            }
        });
    });

    queueList.querySelectorAll('.queue-item-remove').forEach(btn => {
        btn.addEventListener('click', e => {
            e.stopPropagation();
            const index = parseInt(btn.dataset.index);
            state.queue.splice(index, 1);
            if (index <= state.queueIndex && state.queueIndex > 0) state.queueIndex--;
            saveState();
            updateQueueUI();
        });
    });
}

function toggleQueue() {
    const panel = document.getElementById('queue-panel');
    panel.classList.toggle('active');
    panel.setAttribute('aria-hidden', !panel.classList.contains('active'));
}

function toggleMobileMenu() {
    const hamburger = document.getElementById('navbar-hamburger');
    const menu = document.querySelector('.navbar-menu');
    hamburger.classList.toggle('active');
    menu.classList.toggle('active');
    hamburger.setAttribute('aria-expanded', hamburger.classList.contains('active'));
}

function closeMobileMenu() {
    document.getElementById('navbar-hamburger').classList.remove('active');
    document.querySelector('.navbar-menu').classList.remove('active');
}

function showLoading(show) {
    const playBtn = document.getElementById('player-play');
    if (show) {
        playBtn.innerHTML = '<div class="spinner" style="width: 18px; height: 18px; border: 2px solid transparent; border-top-color: currentColor; border-radius: 50%; animation: spin 0.8s linear infinite;"></div>';
    } else {
        playBtn.innerHTML = '<svg class="icon-play" viewBox="0 0 24 24" fill="currentColor"><polygon points="5 3 19 12 5 21 5 3"/></svg><svg class="icon-pause" viewBox="0 0 24 24" fill="currentColor" hidden><rect x="6" y="4" width="4" height="16"/><rect x="14" y="4" width="4" height="16"/></svg>';
    }
}

function handleAudioError() {
    showToast('Erro ao carregar a música', 'error');
    state.isPlaying = false;
    updatePlayerUI();
}

function navigateToArtist(artistId) {
    showToast(`Navegar para artista: ${artistId}`, 'info');
}

function navigateToAlbum(albumId) {
    showToast(`Navegar para álbum: ${albumId}`, 'info');
}

function filterByCategory(categoryId) {
    showToast(`Filtrar por categoria: ${categoryId}`, 'info');
}

function showToast(message, type = 'info') {
    const container = document.getElementById('toast-container');
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;

    const icons = {
        success: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>',
        error: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="15" y1="9" x2="9" y2="15"/><line x1="9" y1="9" x2="15" y2="15"/></svg>',
        warning: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>',
        info: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/></svg>'
    };

    toast.innerHTML = `
        <div class="toast-icon">${icons[type]}</div>
        <span class="toast-message">${escapeHtml(message)}</span>
        <button class="toast-close" aria-label="Fechar">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
        </button>
    `;

    toast.querySelector('.toast-close').addEventListener('click', () => toast.remove());
    container.appendChild(toast);

    setTimeout(() => {
        toast.style.animation = 'slideInRight 0.3s ease reverse';
        setTimeout(() => toast.remove(), 300);
    }, 4000);
}

function formatTime(seconds) {
    if (!seconds || isNaN(seconds)) return '0:00';
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
}

function formatDuration(seconds) {
    return formatTime(seconds);
}

function formatNumber(num) {
    if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M';
    if (num >= 1000) return (num / 1000).toFixed(1) + 'K';
    return num.toString();
}

function getRandomColor() {
    const colors = ['#1db954', '#e01e5a', '#7c3aed', '#06b6d4', '#ec4899', '#f97316', '#84cc16', '#6366f1'];
    return colors[Math.floor(Math.random() * colors.length)];
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function debounce(fn, delay) {
    let timeoutId;
    return (...args) => {
        clearTimeout(timeoutId);
        timeoutId = setTimeout(() => fn.apply(this, args), delay);
    };
}

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
} else {
    init();
}

export { state, mockData, API_BASE };