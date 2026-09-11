import { useEffect, useState } from 'react'
import { Download, Music2, Play, Plus, Trash2 } from 'lucide-react'
import type { FileItem, Playlist } from '../lib/types'
import { libraryApi, playlistsApi } from '../lib/api'
import { usePlayer } from '../lib/player'
import { useToast } from '../lib/toast'
import { Skeleton } from '../components/Loader'
import { formatBytes, formatDuration } from '../lib/format'

export function Library() {
  const { play } = usePlayer()
  const { toast } = useToast()
  const [files, setFiles] = useState<FileItem[]>([])
  const [playlists, setPlaylists] = useState<Playlist[]>([])
  const [loading, setLoading] = useState(true)
  const [menuFor, setMenuFor] = useState<string | null>(null)

  async function load() {
    try {
      const [lib, pl] = await Promise.all([libraryApi.list(), playlistsApi.list()])
      setFiles(lib.items)
      setPlaylists(pl)
    } catch {
      /* ignore */
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    load()
  }, [])

  function handlePlay(f: FileItem) {
    if (f.download_url) {
      play(f, files)
    }
  }

  async function handleDelete(f: FileItem) {
    try {
      await libraryApi.remove(f.id)
      toast('Arquivo excluído', 'success')
      setFiles((prev) => prev.filter((x) => x.id !== f.id))
    } catch (e) {
      toast(e instanceof Error ? e.message : 'Falha ao excluir', 'error')
    }
  }

  async function handleAddToPlaylist(f: FileItem, playlistId: string) {
    try {
      await playlistsApi.addItem(playlistId, f.id)
      toast('Adicionado à playlist', 'success')
      setMenuFor(null)
    } catch (e) {
      toast(e instanceof Error ? e.message : 'Falha ao adicionar', 'error')
    }
  }

  return (
    <div className="space-y-4">
      <div>
        <h1 className="text-2xl font-bold">Biblioteca</h1>
        <p className="text-neutral-400">{files.length} arquivo(s)</p>
      </div>

      {loading ? (
        <div className="space-y-2">
          {Array.from({ length: 5 }).map((_, i) => <Skeleton key={i} className="h-16" />)}
        </div>
      ) : files.length === 0 ? (
        <div className="card flex flex-col items-center justify-center gap-3 p-12 text-center">
          <Music2 className="h-12 w-12 text-neutral-600" />
          <p className="text-neutral-400">Sua biblioteca está vazia.</p>
          <p className="text-sm text-neutral-500">Baixe uma música para começar.</p>
        </div>
      ) : (
        <div className="card divide-y divide-border overflow-hidden">
          {files.map((f, i) => (
            <div key={f.id} className="flex items-center gap-4 p-3 transition hover:bg-white/[0.03]">
              <div className="flex w-8 justify-center">
                <span className="text-sm tabular-nums text-neutral-500">{i + 1}</span>
              </div>
              {f.metadata?.cover_url ? (
                <img src={f.metadata.cover_url} alt="" className="h-12 w-12 rounded-lg object-cover" />
              ) : (
                <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-white/10">
                  <Music2 className="h-5 w-5 text-neutral-400" />
                </div>
              )}
              <button
                onClick={() => handlePlay(f)}
                className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full text-neutral-300 transition hover:bg-white/10 hover:text-white"
                aria-label="Reproduzir"
              >
                <Play className="h-4 w-4" />
              </button>
              <div className="min-w-0 flex-1">
                <p className="truncate font-medium">{f.metadata?.title ?? 'Faixa'}</p>
                <p className="truncate text-sm text-neutral-400">{f.metadata?.artist ?? 'Artista desconhecido'}</p>
              </div>
              <div className="hidden w-32 min-w-0 md:block">
                <p className="truncate text-sm text-neutral-400">{f.metadata?.album || '—'}</p>
              </div>
              <div className="hidden w-16 text-right text-sm text-neutral-400 sm:block">
                {formatDuration(f.metadata?.duration_seconds)}
              </div>
              <div className="hidden w-16 text-right text-sm text-neutral-400 sm:block">
                {f.format.toUpperCase()}
              </div>
              <div className="hidden w-20 text-right text-sm text-neutral-400 lg:block">
                {formatBytes(f.size_bytes)}
              </div>
              <div className="flex items-center gap-1">
                <button
                  onClick={() => (f.download_url ? window.open(f.download_url, '_blank') : null)}
                  className="btn-ghost p-2"
                  aria-label="Baixar"
                >
                  <Download className="h-4 w-4" />
                </button>
                <button onClick={() => setMenuFor(menuFor === f.id ? null : f.id)} className="btn-ghost p-2" aria-label="Mais">
                  <Plus className="h-4 w-4" />
                </button>
                <button onClick={() => handleDelete(f)} className="btn-ghost p-2 text-red-400 hover:text-red-300" aria-label="Excluir">
                  <Trash2 className="h-4 w-4" />
                </button>
              </div>

              {menuFor === f.id && (
                <div className="absolute right-4 mt-24 z-20 card p-2 shadow-2xl w-52">
                  <p className="px-3 py-2 text-xs font-semibold text-neutral-400">Adicionar à playlist</p>
                  {playlists.length === 0 ? (
                    <p className="px-3 py-2 text-sm text-neutral-500">Nenhuma playlist</p>
                  ) : (
                    playlists.map((p) => (
                      <button
                        key={p.id}
                        onClick={() => handleAddToPlaylist(f, p.id)}
                        className="block w-full rounded-lg px-3 py-2 text-left text-sm hover:bg-white/10"
                      >
                        {p.name}
                      </button>
                    ))
                  )}
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  )
}