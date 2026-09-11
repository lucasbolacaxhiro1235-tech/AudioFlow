import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { ListMusic, Plus, Trash2, X } from 'lucide-react'
import type { Playlist } from '../lib/types'
import { playlistsApi } from '../lib/api'
import { useToast } from '../lib/toast'
import { Skeleton } from '../components/Loader'
import { formatBytes } from '../lib/format'

export function Playlists() {
  const { toast } = useToast()
  const [playlists, setPlaylists] = useState<Playlist[]>([])
  const [loading, setLoading] = useState(true)
  const [creating, setCreating] = useState(false)
  const [name, setName] = useState('')
  const [description, setDescription] = useState('')

  async function load() {
    try {
      setPlaylists(await playlistsApi.list())
    } catch {
      /* ignore */
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    load()
  }, [])

  async function handleCreate(e: React.FormEvent) {
    e.preventDefault()
    if (!name.trim()) return
    try {
      const p = await playlistsApi.create({ name, description: description || undefined })
      toast('Playlist criada', 'success')
      setPlaylists((prev) => [p, ...prev])
      setCreating(false)
      setName('')
      setDescription('')
    } catch (err) {
      toast(err instanceof Error ? err.message : 'Falha ao criar', 'error')
    }
  }

  async function handleDelete(id: string, e: React.MouseEvent) {
    e.preventDefault()
    try {
      await playlistsApi.remove(id)
      setPlaylists((prev) => prev.filter((p) => p.id !== id))
      toast('Playlist excluída', 'success')
    } catch (err) {
      toast(err instanceof Error ? err.message : 'Falha ao excluir', 'error')
    }
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Playlists</h1>
          <p className="text-neutral-400">{playlists.length} playlist(s)</p>
        </div>
        <button className="btn-primary" onClick={() => setCreating(true)}>
          <Plus className="h-4 w-4" /> Nova playlist
        </button>
      </div>

      {creating && (
        <div className="card p-5 animate-slideUp">
          <form onSubmit={handleCreate} className="space-y-3">
            <div className="flex items-center justify-between">
              <h2 className="font-semibold">Nova playlist</h2>
              <button type="button" onClick={() => setCreating(false)}><X className="h-4 w-4" /></button>
            </div>
            <input className="input" placeholder="Nome da playlist" value={name} onChange={(e) => setName(e.target.value)} required />
            <input className="input" placeholder="Descrição (opcional)" value={description} onChange={(e) => setDescription(e.target.value)} />
            <button type="submit" className="btn-primary">Criar</button>
          </form>
        </div>
      )}

      {loading ? (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {Array.from({ length: 6 }).map((_, i) => <Skeleton key={i} className="h-40" />)}
        </div>
      ) : playlists.length === 0 ? (
        <div className="card flex flex-col items-center justify-center gap-3 p-12 text-center">
          <ListMusic className="h-12 w-12 text-neutral-600" />
          <p className="text-neutral-400">Nenhuma playlist ainda.</p>
          <p className="text-sm text-neutral-500">Crie uma para organizar sua música.</p>
        </div>
      ) : (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {playlists.map((p) => (
            <Link key={p.id} to={`/playlists/${p.id}`} className="card group relative p-5 transition hover:border-brand/40">
              <div className="mb-3 flex h-16 w-16 items-center justify-center rounded-xl bg-gradient-to-br from-brand/30 to-cyan-500/30 text-brand">
                <ListMusic className="h-8 w-8" />
              </div>
              <h3 className="truncate font-semibold">{p.name}</h3>
              <p className="mt-1 text-sm text-neutral-400">
                {p.track_count} faixas · {formatBytes(p.total_size_bytes)}
              </p>
              <p className="mt-1 text-xs text-neutral-500">
                Criada em {new Date(p.created_at).toLocaleDateString('pt-BR')}
              </p>
              <button
                onClick={(e) => handleDelete(p.id, e)}
                className="absolute right-3 top-3 rounded-lg p-2 text-neutral-500 opacity-0 transition hover:bg-white/10 hover:text-red-400 group-hover:opacity-100"
                aria-label="Excluir"
              >
                <Trash2 className="h-4 w-4" />
              </button>
            </Link>
          ))}
        </div>
      )}
    </div>
  )
}