import { useState } from 'react'
import { Link, useNavigate, useSearchParams } from 'react-router-dom'
import { Loader2 } from 'lucide-react'
import { Logo } from '../components/Logo'
import { authApi } from '../lib/api'
import { useToast } from '../lib/toast'

export function ResetPassword() {
  const [params] = useSearchParams()
  const { toast } = useToast()
  const navigate = useNavigate()
  const [password, setPassword] = useState('')
  const [confirm, setConfirm] = useState('')
  const [loading, setLoading] = useState(false)
  const token = params.get('token') ?? ''

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    if (password.length < 8) {
      toast('A senha deve ter pelo menos 8 caracteres', 'error')
      return
    }
    if (password !== confirm) {
      toast('As senhas não coincidem', 'error')
      return
    }
    setLoading(true)
    try {
      await authApi.resetPassword(token, password)
      toast('Senha redefinida!', 'success')
      navigate('/login')
    } catch (err) {
      toast(err instanceof Error ? err.message : 'Link inválido ou expirado', 'error')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-base px-4">
      <div className="w-full max-w-sm">
        <div className="mb-8 flex justify-center">
          <Link to="/"><Logo /></Link>
        </div>
        <div className="card p-7">
          <h1 className="text-xl font-bold">Nova senha</h1>
          <form onSubmit={handleSubmit} className="mt-6 space-y-4">
            <div>
              <label className="label" htmlFor="password">Nova senha</label>
              <input id="password" type="password" className="input" value={password} onChange={(e) => setPassword(e.target.value)} required />
            </div>
            <div>
              <label className="label" htmlFor="confirm">Confirmar senha</label>
              <input id="confirm" type="password" className="input" value={confirm} onChange={(e) => setConfirm(e.target.value)} required />
            </div>
            <button type="submit" className="btn-primary w-full" disabled={loading}>
              {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : 'Redefinir senha'}
            </button>
          </form>
        </div>
      </div>
    </div>
  )
}