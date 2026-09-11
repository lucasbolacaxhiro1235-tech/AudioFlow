import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { ArrowLeft, ListMusic, Play, Trash2 } from 'lucide-react'
import type { FileItem, Playlist } from '../lib/types'
import { playlistsApi } from '../lib/api'
import { usePlayer } from '../lib/player'
import { useToast } from '../lib/toast'
import { Skeleton } from '../components/Loader'
import { formatBytes, formatDuration } from '../lib/format'

export function PlaylistDetail() {
  const { id } = useParams<{ id: string }>()
  const { play } = usePlayer()
  const { toast } = useToast()
  const [playlist, setPlaylist] = useState<Playlist | null>(null)
  const [loading, setLoading] = useState(true)

  async function load() {
    if (!id) return
    try {
      setPlaylist(await playlistsApi.get(id))
    } catch {
      /* ignore */
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    load()
  }, [id])

  async function handleRemove(itemId: string) {
    if (!id) return
    try {
      const p = await playlistsApi.removeItem(id, itemId)
      setPlaylist(p)
      toast('Removido da playlist', 'success')
    } catch (e) {
      toast(e instanceof Error ? e.message : 'Erro', 'error')
    }
  }

  function handlePlayAll() {
    const tracks = playlist?.items.map((i) => i.file).filter((f): f is FileItem => !!f) ?? []
    if (tracks.length) play(tracks[0], tracks)
  }

  if (loading) {
    return (
      <div className="space-y-4">
        <Skeleton className="h-8 w-40" />
        <Skeleton className="h-32" />
        <Skeleton className="h-16" />
      </div>
    )
  }

  if (!playlist) {
    return (
      <div className="card flex flex-col items-center gap-3 p-12 text-center">
        <ListMusic className="h-12 w-12 text-neutral-600" />
        <p className="text-neutral-400">Playlist não encontrada.</p>
        <Link to="/playlists" className="btn-secondary">Voltar</Link>
      </div>
    )
  }

  const tracks = playlist.items.map((i) => i.file).filter((f): f is FileItem => !!f)

  return (
    <div className="space-y-4">
      <Link to="/playlists" className="btn-ghost -ml-2">
        <ArrowLeft className="h-4 w-4" /> Voltar
      </Link>

      <div className="card flex flex-col items-center gap-4 p-6 sm:flex-row sm:items-end">
        <div className="flex h-28 w-28 items-center justify-center rounded-2xl bg-gradient-to-br from-brand/30 to-cyan-500/30 text-brand">
          <ListMusic className="h-14 w-14" />
        </div>
        <div className="flex-1 text-center sm:text-left">
          <p className="text-xs uppercase tracking-wide text-neutral-500">Playlist</p>
          <h1 className="text-3xl font-bold">{playlist.name}</h1>
          {playlist.description && <p className="mt-1 text-neutral-400">{playlist.description}</p>}
          <p className="mt-2 text-sm text-neutral-500">
            {playlist.track_count} faixas · {formatBytes(playlist.total_size_bytes)}
          </p>
        </div>
        <button className="btn-primary" onClick={handlePlayAll} disabled={tracks.length === 0}>
          <Play className="h-4 w-4" /> Reproduzir
        </button>
      </div>

      {tracks.length === 0 ? (
        <div className="card flex flex-col items-center justify-center gap-3 p-10 text-center">
          <ListMusic className="h-10 w-10 text-neutral-600" />
          <p className="text-neutral-400">Esta playlist está vazia.</p>
          <p className="text-sm text-neutral-500">Adicione músicas pela biblioteca.</p>
        </div>
      ) : (
        <div className="card divide-y divide-border overflow-hidden">
          {playlist.items.map((item, idx) => {
            const f = item.file
            if (!f) return null
            return (
              <div key={item.id} className="flex items-center gap-4 p-3 transition hover:bg-white/[0.03]">
                <span className="w-6 text-center text-sm tabular-nums text-neutral-500">{idx + 1}</span>
                <button
                  onClick={() => play(f, tracks)}
                  className="flex h-8 w-8 items-center justify-center rounded-full text-neutral-300 transition hover:bg-white/10 hover:text-white"
                >
                  <Play className="h-4 w-4" />
                </button>
                <div className="min-w-0 flex-1">
                  <p className="truncate font-medium">{f.metadata?.title ?? 'Faixa'}</p>
                  <p className="truncate text-sm text-neutral-400">{f.metadata?.artist ?? '—'}</p>
                </div>
                <span className="hidden text-sm text-neutral-400 sm:block">
                  {formatDuration(f.metadata?.duration_seconds)}
                </span>
                <button onClick={() => handleRemove(item.id)} className="btn-ghost p-2 text-red-400 hover:text-red-300" aria-label="Remover">
                  <Trash2 className="h-4 w-4" />
                </button>
              </div>
            )
          })}
        </div>
      )}
    </div>
  )
}