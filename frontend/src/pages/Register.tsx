import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { Loader2, UserPlus } from 'lucide-react'
import { Logo } from '../components/Logo'
import { useAuth } from '../lib/auth'
import { useToast } from '../lib/toast'

export function Register() {
  const { register } = useAuth()
  const { toast } = useToast()
  const navigate = useNavigate()
  const [name, setName] = useState('')
  const [email, setEmail] = useState('')
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    if (password.length < 8) {
      toast('A senha deve ter pelo menos 8 caracteres', 'error')
      return
    }
    setLoading(true)
    try {
      await register({
        name,
        email,
        username: username || undefined,
        password
      })
      toast('Conta criada! Verifique seu e-mail.', 'success')
      navigate('/login')
    } catch (err) {
      toast(err instanceof Error ? err.message : 'Falha no cadastro', 'error')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-base px-4 py-10">
      <div className="w-full max-w-sm">
        <div className="mb-8 flex justify-center">
          <Link to="/">
            <Logo size="lg" />
          </Link>
        </div>
        <div className="card p-7">
          <h1 className="text-xl font-bold">Criar conta</h1>
          <p className="mt-1 text-sm text-neutral-400">Comece a organizar sua música</p>
          <form onSubmit={handleSubmit} className="mt-6 space-y-4">
            <div>
              <label className="label" htmlFor="name">Nome</label>
              <input id="name" className="input" autoComplete="name" value={name} onChange={(e) => setName(e.target.value)} required />
            </div>
            <div>
              <label className="label" htmlFor="email">E-mail</label>
              <input id="email" type="email" className="input" autoComplete="email" value={email} onChange={(e) => setEmail(e.target.value)} required />
            </div>
            <div>
              <label className="label" htmlFor="username">Nome de usuário (opcional)</label>
              <input id="username" className="input" placeholder="apenas letras, números, . _ -" value={username} onChange={(e) => setUsername(e.target.value)} />
            </div>
            <div>
              <label className="label" htmlFor="password">Senha</label>
              <input id="password" type="password" className="input" autoComplete="new-password" value={password} onChange={(e) => setPassword(e.target.value)} required />
              <p className="mt-1 text-xs text-neutral-500">Mínimo de 8 caracteres</p>
            </div>
            <button type="submit" className="btn-primary w-full" disabled={loading}>
              {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : <UserPlus className="h-4 w-4" />}
              Criar conta
            </button>
          </form>
          <p className="mt-6 text-center text-sm text-neutral-400">
            Já tem conta?{' '}
            <Link to="/login" className="font-medium text-brand hover:underline">
              Entrar
            </Link>
          </p>
        </div>
      </div>
    </div>
  )
}