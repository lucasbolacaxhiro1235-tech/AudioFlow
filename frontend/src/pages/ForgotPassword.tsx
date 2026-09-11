import { useState } from 'react'
import { Link } from 'react-router-dom'
import { Loader2, Mail } from 'lucide-react'
import { Logo } from '../components/Logo'
import { authApi } from '../lib/api'
import { useToast } from '../lib/toast'

export function ForgotPassword() {
  const { toast } = useToast()
  const [email, setEmail] = useState('')
  const [loading, setLoading] = useState(false)
  const [sent, setSent] = useState(false)

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    setLoading(true)
    try {
      await authApi.forgotPassword(email)
      setSent(true)
    } catch (err) {
      toast(err instanceof Error ? err.message : 'Erro ao enviar', 'error')
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
          {sent ? (
            <div className="text-center">
              <Mail className="mx-auto mb-4 h-10 w-10 text-brand" />
              <h1 className="text-lg font-bold">Verifique seu e-mail</h1>
              <p className="mt-2 text-sm text-neutral-400">
                Se o e-mail existir, enviaremos um link de redefinição.
              </p>
              <Link to="/login" className="btn-secondary mt-6 w-full">Voltar ao login</Link>
            </div>
          ) : (
            <>
              <h1 className="text-xl font-bold">Recuperar senha</h1>
              <p className="mt-1 text-sm text-neutral-400">Enviaremos um link de redefinição.</p>
              <form onSubmit={handleSubmit} className="mt-6 space-y-4">
                <div>
                  <label className="label" htmlFor="email">E-mail</label>
                  <input id="email" type="email" className="input" value={email} onChange={(e) => setEmail(e.target.value)} required />
                </div>
                <button type="submit" className="btn-primary w-full" disabled={loading}>
                  {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : 'Enviar link'}
                </button>
              </form>
            </>
          )}
        </div>
      </div>
    </div>
  )
}