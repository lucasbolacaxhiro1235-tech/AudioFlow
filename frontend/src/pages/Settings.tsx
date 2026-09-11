import { useState } from 'react'
import { Loader2, Save, ShieldCheck } from 'lucide-react'
import { useAuth } from '../lib/auth'
import { authApi, meApi } from '../lib/api'
import { useToast } from '../lib/toast'

export function Settings() {
  const { user, setUser } = useAuth()
  const { toast } = useToast()
  const [name, setName] = useState(user?.name ?? '')
  const [username, setUsername] = useState(user?.username ?? '')
  const [savingProfile, setSavingProfile] = useState(false)

  const [currentPw, setCurrentPw] = useState('')
  const [newPw, setNewPw] = useState('')
  const [confirmPw, setConfirmPw] = useState('')
  const [savingPw, setSavingPw] = useState(false)

  async function handleProfile(e: React.FormEvent) {
    e.preventDefault()
    setSavingProfile(true)
    try {
      const updated = await meApi.update({ name, username: username || undefined })
      setUser(updated)
      toast('Perfil atualizado', 'success')
    } catch (err) {
      toast(err instanceof Error ? err.message : 'Erro ao salvar', 'error')
    } finally {
      setSavingProfile(false)
    }
  }

  async function handlePassword(e: React.FormEvent) {
    e.preventDefault()
    if (newPw.length < 8) {
      toast('Nova senha muito curta', 'error')
      return
    }
    if (newPw !== confirmPw) {
      toast('As senhas não coincidem', 'error')
      return
    }
    setSavingPw(true)
    try {
      await authApi.changePassword(currentPw, newPw)
      toast('Senha alterada', 'success')
      setCurrentPw('')
      setNewPw('')
      setConfirmPw('')
    } catch (err) {
      toast(err instanceof Error ? err.message : 'Erro ao alterar', 'error')
    } finally {
      setSavingPw(false)
    }
  }

  return (
    <div className="mx-auto max-w-2xl space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Configurações</h1>
        <p className="text-neutral-400">Gerencie sua conta.</p>
      </div>

      <div className="card p-6">
        <h2 className="mb-4 font-semibold">Perfil</h2>
        <form onSubmit={handleProfile} className="space-y-4">
          <div>
            <label className="label">E-mail</label>
            <input className="input opacity-60" value={user?.email ?? ''} disabled />
            {!user?.email_verified && (
              <p className="mt-1 text-xs text-amber-400">E-mail ainda não verificado.</p>
            )}
          </div>
          <div>
            <label className="label" htmlFor="name">Nome</label>
            <input id="name" className="input" value={name} onChange={(e) => setName(e.target.value)} required />
          </div>
          <div>
            <label className="label" htmlFor="username">Nome de usuário</label>
            <input id="username" className="input" value={username} onChange={(e) => setUsername(e.target.value)} />
          </div>
          <button type="submit" className="btn-primary" disabled={savingProfile}>
            {savingProfile ? <Loader2 className="h-4 w-4 animate-spin" /> : <Save className="h-4 w-4" />}
            Salvar
          </button>
        </form>
      </div>

      <div className="card p-6">
        <h2 className="mb-4 font-semibold">Alterar senha</h2>
        <form onSubmit={handlePassword} className="space-y-4">
          <div>
            <label className="label" htmlFor="cpw">Senha atual</label>
            <input id="cpw" type="password" className="input" value={currentPw} onChange={(e) => setCurrentPw(e.target.value)} required />
          </div>
          <div>
            <label className="label" htmlFor="npw">Nova senha</label>
            <input id="npw" type="password" className="input" value={newPw} onChange={(e) => setNewPw(e.target.value)} required />
          </div>
          <div>
            <label className="label" htmlFor="cnpw">Confirmar nova senha</label>
            <input id="cnpw" type="password" className="input" value={confirmPw} onChange={(e) => setConfirmPw(e.target.value)} required />
          </div>
          <button type="submit" className="btn-primary" disabled={savingPw}>
            {savingPw ? <Loader2 className="h-4 w-4 animate-spin" /> : <ShieldCheck className="h-4 w-4" />}
            Alterar senha
          </button>
        </form>
      </div>
    </div>
  )
}