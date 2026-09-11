import { useEffect, useState } from 'react'
import {
  Activity,
  HardDrive,
  Music2,
  Shield,
  Trash2,
  Users
} from 'lucide-react'
import { adminApi } from '../lib/api'
import { useToast } from '../lib/toast'
import { Skeleton } from '../components/Loader'
import { formatBytes } from '../lib/format'

interface AdminUser {
  id: string
  name: string
  email: string
  role: string
  is_active: boolean
  plan: string
  storage_bytes: number
  file_count: number
  total_download_count: number
}

export function Admin() {
  const { toast } = useToast()
  const [stats, setStats] = useState<Record<string, unknown> | null>(null)
  const [status, setStatus] = useState<Record<string, string> | null>(null)
  const [users, setUsers] = useState<AdminUser[]>([])
  const [loading, setLoading] = useState(true)

  async function load() {
    try {
      const [s, st, u] = await Promise.all([adminApi.stats(), adminApi.status(), adminApi.users(1)])
      setStats(s)
      setStatus(st)
      setUsers(u as AdminUser[])
    } catch {
      /* ignore */
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    load()
  }, [])

  async function toggleActive(u: AdminUser) {
    try {
      await adminApi.updateUser(u.id, { is_active: !u.is_active })
      toast(u.is_active ? 'Usuário bloqueado' : 'Usuário desbloqueado', 'success')
      load()
    } catch (e) {
      toast(e instanceof Error ? e.message : 'Erro', 'error')
    }
  }

  async function setPlan(u: AdminUser, tier: string) {
    try {
      await adminApi.updateUser(u.id, { plan_tier: tier })
      toast('Plano alterado', 'success')
      load()
    } catch (e) {
      toast(e instanceof Error ? e.message : 'Erro', 'error')
    }
  }

  async function remove(u: AdminUser) {
    try {
      await adminApi.deleteUser(u.id)
      toast('Usuário excluído', 'success')
      load()
    } catch (e) {
      toast(e instanceof Error ? e.message : 'Erro', 'error')
    }
  }

  const cards = [
    { label: 'Usuários', value: String(stats?.total_users ?? '—'), icon: Users },
    { label: 'Downloads', value: String(stats?.total_downloads ?? '—'), icon: Music2 },
    { label: 'Ativos agora', value: String(stats?.active_downloads ?? '—'), icon: Activity },
    { label: 'Armazenamento', value: formatBytes(Number(stats?.total_storage_bytes ?? 0)), icon: HardDrive }
  ]

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Painel administrativo</h1>
        <p className="text-neutral-400">Visão geral do sistema.</p>
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
              </div>
            ))}
      </div>

      <div className="card p-5">
        <h2 className="mb-3 font-semibold">Status dos serviços</h2>
        <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
          {loading
            ? Array.from({ length: 4 }).map((_, i) => <Skeleton key={i} className="h-14" />)
            : Object.entries(status ?? {}).map(([k, v]) => (
                <div key={k} className="rounded-xl bg-white/5 p-3">
                  <p className="text-xs uppercase text-neutral-500">{k}</p>
                  <p className={`mt-1 font-medium ${v === 'connected' || v === 'installed' || v === 'configured' ? 'text-brand' : 'text-amber-400'}`}>
                    {v}
                  </p>
                </div>
              ))}
        </div>
      </div>

      <div className="card overflow-hidden">
        <div className="border-b border-border p-4">
          <h2 className="font-semibold">Usuários</h2>
        </div>
        {loading ? (
          <div className="space-y-2 p-4">
            {Array.from({ length: 4 }).map((_, i) => <Skeleton key={i} className="h-12" />)}
          </div>
        ) : (
          <div className="divide-y divide-border">
            {users.map((u) => (
              <div key={u.id} className="flex flex-wrap items-center gap-3 p-4">
                <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-gradient-to-br from-brand to-cyan-500 text-sm font-bold text-black">
                  {u.name?.[0]?.toUpperCase() ?? 'U'}
                </div>
                <div className="min-w-0 flex-1">
                  <p className="flex items-center gap-2 truncate font-medium">
                    {u.name}
                    {u.role === 'admin' && <Shield className="h-3.5 w-3.5 text-brand" />}
                    {!u.is_active && <span className="rounded-full bg-red-500/10 px-2 py-0.5 text-xs text-red-400">bloqueado</span>}
                  </p>
                  <p className="truncate text-sm text-neutral-400">{u.email}</p>
                </div>
                <span className="hidden text-sm text-neutral-400 sm:block">{u.file_count} arquivos</span>
                <select
                  value={u.plan}
                  onChange={(e) => setPlan(u, e.target.value)}
                  className="rounded-lg bg-white/5 border border-white/10 px-2 py-1.5 text-sm text-white outline-none"
                >
                  <option value="free">Free</option>
                  <option value="pro">Pro</option>
                  <option value="premium">Premium</option>
                </select>
                <button onClick={() => toggleActive(u)} className="btn-secondary px-3 py-1.5 text-xs">
                  {u.is_active ? 'Bloquear' : 'Desbloquear'}
                </button>
                <button onClick={() => remove(u)} className="btn-ghost p-2 text-red-400 hover:text-red-300" aria-label="Excluir">
                  <Trash2 className="h-4 w-4" />
                </button>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}