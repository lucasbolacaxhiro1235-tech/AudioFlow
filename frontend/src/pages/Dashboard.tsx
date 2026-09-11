import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import {
  CheckCircle2,
  Clock,
  HardDrive,
  ListMusic,
  Music2,
  XCircle
} from 'lucide-react'
import type { Download, UserStats } from '../lib/types'
import { downloadsApi, meApi } from '../lib/api'
import { DownloadFlow } from '../components/DownloadFlow'
import { Skeleton } from '../components/Loader'
import { formatBytes } from '../lib/format'
import { useAuth } from '../lib/auth'

export function Dashboard() {
  const { user } = useAuth()
  const [stats, setStats] = useState<UserStats | null>(null)
  const [downloads, setDownloads] = useState<Download[]>([])
  const [loading, setLoading] = useState(true)

  async function load() {
    try {
      const [s, d] = await Promise.all([meApi.stats(), downloadsApi.list(1, 10)])
      setStats(s)
      setDownloads(d.items)
    } catch {
      /* ignore */
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    load()
  }, [])

  const cards = [
    { label: 'Armazenamento', value: stats ? formatBytes(stats.storage_bytes) : '—', icon: HardDrive, sub: stats ? `de ${formatBytes(stats.usage.storage_limit_bytes)}` : '' },
    { label: 'Downloads', value: stats ? String(stats.total_download_count) : '—', icon: Music2, sub: `${stats?.completed_downloads ?? 0} concluídos` },
    { label: 'Arquivos', value: stats ? String(stats.file_count) : '—', icon: ListMusic, sub: `${stats?.playlist_count ?? 0} playlists` },
    { label: 'Plano', value: stats ? stats.plan.toUpperCase() : '—', icon: Clock, sub: stats ? `${stats.usage.daily_download_count}/${stats.usage.daily_download_limit} hoje` : '' }
  ]

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Olá, {user?.name?.split(' ')[0] ?? 'Visitante'} 👋</h1>
        <p className="text-neutral-400">Baixe e gerencie sua música.</p>
      </div>

      <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
        {loading
          ? Array.from({ length: 4 }).map((_, i) => <Skeleton key={i} className="h-24" />)
          : cards.map((c) => (
              <div key={c.label} className="card p-5">
                <div className="mb-3 flex h-9 w-9 items-center justify-center rounded-lg bg-brand/10 text-brand">
                  <c.icon className="h-4 w-4" />
                </div>
                <p className="text-2xl font-bold">{c.value}</p>
                <p className="text-sm text-neutral-400">{c.label}</p>
                {c.sub && <p className="mt-0.5 text-xs text-neutral-500">{c.sub}</p>}
              </div>
            ))}
      </div>

      <DownloadFlow onComplete={load} />

      <div>
        <div className="mb-3 flex items-center justify-between">
          <h2 className="text-lg font-semibold">Downloads recentes</h2>
        </div>
        {loading ? (
          <div className="space-y-2">
            {Array.from({ length: 3 }).map((_, i) => <Skeleton key={i} className="h-16" />)}
          </div>
        ) : downloads.length === 0 ? (
          <div className="card flex flex-col items-center justify-center gap-3 p-10 text-center">
            <Music2 className="h-10 w-10 text-neutral-600" />
            <p className="text-neutral-400">Nenhum download ainda.</p>
            <p className="text-sm text-neutral-500">Cole um link acima para começar.</p>
          </div>
        ) : (
          <div className="space-y-2">
            {downloads.map((d) => (
              <Link
                key={d.id}
                to="/library"
                className="card flex items-center gap-4 p-4 transition hover:border-brand/40"
              >
                {d.cover_url ? (
                  <img src={d.cover_url} alt="" className="h-12 w-12 rounded-lg object-cover" />
                ) : (
                  <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-white/10">
                    <Music2 className="h-5 w-5 text-neutral-400" />
                  </div>
                )}
                <div className="min-w-0 flex-1">
                  <p className="truncate font-medium">{d.title ?? 'Faixa'}</p>
                  <p className="truncate text-sm text-neutral-400">{d.artist ?? '—'}</p>
                </div>
                <div className="hidden items-center gap-2 sm:flex">
                  <span className="rounded-md bg-white/5 px-2 py-1 text-xs uppercase text-neutral-400">
                    {d.format}
                  </span>
                </div>
                <div className="w-24">
                  {d.status === 'completed' && (
                    <span className="flex items-center gap-1 text-brand">
                      <CheckCircle2 className="h-4 w-4" /> Concluído
                    </span>
                  )}
                  {d.status === 'failed' && (
                    <span className="flex items-center gap-1 text-red-400">
                      <XCircle className="h-4 w-4" /> Falhou
                    </span>
                  )}
                  {(d.status === 'pending' || d.status === 'processing' || d.status === 'converting' || d.status === 'validating') && (
                    <div>
                      <span className="text-sm text-neutral-300">{d.progress}%</span>
                      <div className="mt-1 h-1.5 w-full overflow-hidden rounded-full bg-white/10">
                        <div className="h-full rounded-full bg-brand" style={{ width: `${d.progress}%` }} />
                      </div>
                    </div>
                  )}
                </div>
              </Link>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}