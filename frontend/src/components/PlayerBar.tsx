import {
  ListMusic,
  Pause,
  Play,
  Repeat,
  Shuffle,
  SkipBack,
  SkipForward,
  Volume2
} from 'lucide-react'
import { usePlayer } from '../lib/player'

export function formatTime(seconds: number): string {
  if (!seconds || isNaN(seconds)) return '0:00'
  const m = Math.floor(seconds / 60)
  const s = Math.floor(seconds % 60)
  return `${m}:${s.toString().padStart(2, '0')}`
}

export function PlayerBar() {
  const player = usePlayer()
  const { current, isPlaying, progress, duration, volume, shuffle, repeat } = player

  if (!current) return null

  const title = current.metadata?.title ?? 'Faixa'
  const artist = current.metadata?.artist ?? 'Artista desconhecido'
  const cover = current.metadata?.cover_url

  return (
    <div className="fixed inset-x-0 bottom-0 z-40 border-t border-border bg-surface/95 backdrop-blur-xl">
      <div className="mx-auto grid max-w-7xl grid-cols-3 items-center gap-3 px-4 py-3 sm:px-6">
        <div className="flex min-w-0 items-center gap-3">
          {cover ? (
            <img src={cover} alt="" className="h-12 w-12 rounded-lg object-cover" />
          ) : (
            <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-white/10">
              <ListMusic className="h-5 w-5 text-neutral-400" />
            </div>
          )}
          <div className="min-w-0">
            <p className="truncate text-sm font-semibold text-white">{title}</p>
            <p className="truncate text-xs text-neutral-400">{artist}</p>
          </div>
        </div>

        <div className="flex flex-col items-center gap-1">
          <div className="flex items-center gap-4">
            <button
              onClick={player.toggleShuffle}
              className={`transition ${shuffle ? 'text-brand' : 'text-neutral-400 hover:text-white'}`}
              aria-label="Aleatório"
            >
              <Shuffle className="h-4 w-4" />
            </button>
            <button onClick={player.prev} className="text-neutral-300 hover:text-white" aria-label="Anterior">
              <SkipBack className="h-5 w-5" />
            </button>
            <button
              onClick={player.toggle}
              className="flex h-10 w-10 items-center justify-center rounded-full bg-white text-black transition hover:scale-105"
              aria-label={isPlaying ? 'Pausar' : 'Reproduzir'}
            >
              {isPlaying ? <Pause className="h-5 w-5" /> : <Play className="h-5 w-5 translate-x-px" />}
            </button>
            <button onClick={player.next} className="text-neutral-300 hover:text-white" aria-label="Próxima">
              <SkipForward className="h-5 w-5" />
            </button>
            <button
              onClick={player.toggleRepeat}
              className={`transition ${repeat ? 'text-brand' : 'text-neutral-400 hover:text-white'}`}
              aria-label="Repetir"
            >
              <Repeat className="h-4 w-4" />
            </button>
          </div>
          <div className="hidden w-full items-center gap-2 sm:flex">
            <span className="w-10 text-right text-xs tabular-nums text-neutral-400">
              {formatTime(progress)}
            </span>
            <input
              type="range"
              min={0}
              max={duration || 0}
              value={progress}
              onChange={(e) => player.seek(Number(e.target.value))}
              className="w-full max-w-md"
            />
            <span className="w-10 text-xs tabular-nums text-neutral-400">{formatTime(duration)}</span>
          </div>
        </div>

        <div className="hidden items-center justify-end gap-2 md:flex">
          <Volume2 className="h-4 w-4 text-neutral-400" />
          <input
            type="range"
            min={0}
            max={1}
            step={0.01}
            value={volume}
            onChange={(e) => player.setVolume(Number(e.target.value))}
            className="w-24"
          />
        </div>
      </div>
    </div>
  )
}