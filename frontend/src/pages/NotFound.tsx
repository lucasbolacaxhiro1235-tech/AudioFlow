import { Link } from 'react-router-dom'
import { AudioLines } from 'lucide-react'

export function NotFound() {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-base px-4 text-center">
      <div className="mb-6 flex h-16 w-16 items-center justify-center rounded-2xl bg-gradient-to-br from-brand to-cyan-400">
        <AudioLines className="h-8 w-8 text-black" />
      </div>
      <h1 className="text-6xl font-extrabold logo-gradient">404</h1>
      <p className="mt-4 text-lg text-neutral-400">Página não encontrada.</p>
      <Link to="/" className="btn-primary mt-8">
        Voltar ao início
      </Link>
    </div>
  )
}