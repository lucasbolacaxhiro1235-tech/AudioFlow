import { useEffect, useState } from 'react'
import { Link, useSearchParams } from 'react-router-dom'
import { CheckCircle2, XCircle } from 'lucide-react'
import { Logo } from '../components/Logo'
import { authApi } from '../lib/api'

export function VerifyEmail() {
  const [params] = useSearchParams()
  const token = params.get('token') ?? ''
  const [state, setState] = useState<'loading' | 'success' | 'error'>('loading')

  useEffect(() => {
    async function verify() {
      if (!token) {
        setState('error')
        return
      }
      try {
        await authApi.verifyEmail(token)
        setState('success')
      } catch {
        setState('error')
      }
    }
    verify()
  }, [token])

  return (
    <div className="flex min-h-screen items-center justify-center bg-base px-4">
      <div className="w-full max-w-sm text-center">
        <div className="mb-8 flex justify-center">
          <Link to="/"><Logo /></Link>
        </div>
        <div className="card p-8">
          {state === 'loading' && <p className="text-neutral-400">Verificando seu e-mail…</p>}
          {state === 'success' && (
            <>
              <CheckCircle2 className="mx-auto mb-4 h-12 w-12 text-brand" />
              <h1 className="text-lg font-bold">E-mail verificado!</h1>
              <p className="mt-2 text-sm text-neutral-400">Sua conta está pronta.</p>
              <Link to="/login" className="btn-primary mt-6 w-full">Fazer login</Link>
            </>
          )}
          {state === 'error' && (
            <>
              <XCircle className="mx-auto mb-4 h-12 w-12 text-red-400" />
              <h1 className="text-lg font-bold">Link inválido ou expirado</h1>
              <p className="mt-2 text-sm text-neutral-400">Solicite um novo link de verificação.</p>
              <Link to="/login" className="btn-secondary mt-6 w-full">Voltar</Link>
            </>
          )}
        </div>
      </div>
    </div>
  )
}