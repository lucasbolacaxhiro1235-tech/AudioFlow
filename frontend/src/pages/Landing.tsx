import { Link } from 'react-router-dom'
import {
  ArrowRight,
  Check,
  Download,
  Gauge,
  ListMusic,
  Lock,
  Music2,
  Shield,
  Sparkles,
  Waves
} from 'lucide-react'
import { Logo } from '../components/Logo'
import { useAuth } from '../lib/auth'
import { AUDIO_FORMATS } from '../lib/format'

const features = [
  {
    icon: Download,
    title: 'Downloads rápidos',
    desc: 'Baixe músicas, álbuns e playlists inteiras em segundos com processamento em paralelo.'
  },
  {
    icon: ListMusic,
    title: 'Sua biblioteca',
    desc: 'Organize tudo o que você baixou com capas, metadados e playlists personalizadas.'
  },
  {
    icon: Waves,
    title: 'Múltiplos formatos',
    desc: 'MP3, M4A, Opus, FLAC e WAV com qualidade configurável para cada faixa.'
  },
  {
    icon: Gauge,
    title: 'Progresso em tempo real',
    desc: 'Acompanhe cada download com velocidade, tamanho e progresso ao vivo.'
  },
  {
    icon: Shield,
    title: 'Seguro e privado',
    desc: 'Sessões seguras, criptografia de senhas e armazenamento isolado por usuário.'
  },
  {
    icon: Sparkles,
    title: 'Experiência premium',
    desc: 'Interface moderna, player imersivo e suporte completo para celular.'
  }
]

const steps = [
  { n: '1', t: 'Cole o link', d: 'Adicione um link de música, álbum ou playlist.' },
  { n: '2', t: 'Escolha o formato', d: 'Selecione formato e qualidade desejados.' },
  { n: '3', t: 'Baixe e escute', d: 'Acompanhe o progresso e ouça na sua biblioteca.' }
]

const faqs = [
  { q: 'O AudioFlow é gratuito?', a: 'Sim. O plano Free permite até 10 downloads por dia, com opção de planos Pro e Premium para mais capacidade.' },
  { q: 'Quais formatos são suportados?', a: 'MP3, M4A, Opus, FLAC e WAV. O MP3 oferece qualidade de até 320kbps.' },
  { q: 'Meus arquivos ficam salvos?', a: 'Sim, cada conta possui armazenamento próprio. No plano Free você tem 1 GB.' },
  { q: 'Funciona no celular?', a: 'Sim. O AudioFlow é um PWA instalável e funciona muito bem em qualquer dispositivo.' },
  { q: 'Meus dados são protegidos?', a: 'Usamos criptografia de senhas (Argon2), sessões seguras e isolamento de dados por usuário.' }
]

const plans = [
  { tier: 'free', name: 'Free', price: 'R$ 0', features: ['10 downloads/dia', '1 download simultâneo', '1 GB de armazenamento', 'Formato MP3'], cta: 'Começar agora', highlight: false },
  { tier: 'pro', name: 'Pro', price: 'R$ 9,99', features: ['100 downloads/dia', '4 downloads simultâneos', '20 GB de armazenamento', 'Todos os formatos', 'Prioridade na fila'], cta: 'Começar agora', highlight: true },
  { tier: 'premium', name: 'Premium', price: 'R$ 19,99', features: ['Downloads ilimitados', '8 downloads simultâneos', '100 GB de armazenamento', 'Todos os formatos', 'Prioridade máxima', 'Suporte dedicado'], cta: 'Começar agora', highlight: false }
]

export function Landing() {
  const { user } = useAuth()

  return (
    <div className="min-h-screen bg-base">
      <header className="sticky top-0 z-40 border-b border-border bg-base/80 backdrop-blur-xl">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-4 py-3 sm:px-6">
          <Logo />
          <div className="flex items-center gap-2">
            {user ? (
              <Link to="/dashboard" className="btn-primary">Ir para o dashboard</Link>
            ) : (
              <>
                <Link to="/login" className="btn-ghost">Entrar</Link>
                <Link to="/register" className="btn-primary">Começar agora</Link>
              </>
            )}
          </div>
        </div>
      </header>

      <main>
        {/* Hero */}
        <section className="relative overflow-hidden">
          <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(ellipse_at_top,rgba(30,215,96,0.15),transparent_60%)]" />
          <div className="relative mx-auto max-w-7xl px-4 py-24 text-center sm:px-6">
            <div className="mx-auto mb-6 inline-flex items-center gap-2 rounded-full border border-brand/30 bg-brand/10 px-4 py-1.5 text-sm text-brand">
              <Sparkles className="h-4 w-4" />
              Plataforma de áudio de nova geração
            </div>
            <h1 className="mx-auto max-w-3xl text-5xl font-extrabold leading-tight tracking-tight sm:text-7xl">
              Seu áudio.{' '}
              <span className="logo-gradient">Do seu jeito.</span>
            </h1>
            <p className="mx-auto mt-6 max-w-xl text-lg text-neutral-400 sm:text-xl">
              Uma plataforma rápida e moderna para gerenciar seus downloads e sua biblioteca de áudio.
            </p>
            <div className="mt-10 flex flex-col items-center justify-center gap-3 sm:flex-row">
              <Link to={user ? '/dashboard' : '/register'} className="btn-primary px-8 py-3 text-base">
                Começar agora <ArrowRight className="h-5 w-5" />
              </Link>
              <Link to="/login" className="btn-secondary px-8 py-3 text-base">
                Entrar
              </Link>
            </div>

            {/* Mock preview */}
            <div className="mx-auto mt-16 max-w-3xl">
              <div className="glass rounded-2xl p-4 shadow-2xl">
                <div className="flex items-center gap-4 rounded-xl bg-white/5 p-3">
                  <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-gradient-to-br from-brand to-cyan-500">
                    <Music2 className="h-6 w-6 text-black" />
                  </div>
                  <div className="min-w-0 flex-1 text-left">
                    <p className="truncate font-semibold">Sua música favorita</p>
                    <p className="text-sm text-neutral-400">Artista</p>
                  </div>
                  <div className="hidden items-center gap-3 sm:flex">
                    <div className="h-2 w-40 overflow-hidden rounded-full bg-white/10">
                      <div className="h-full w-2/3 rounded-full bg-brand" />
                    </div>
                    <span className="text-xs text-neutral-400">2:34 / 3:48</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* Features */}
        <section className="mx-auto max-w-7xl px-4 py-20 sm:px-6">
          <h2 className="text-center text-3xl font-bold sm:text-4xl">Tudo o que você precisa</h2>
          <p className="mx-auto mt-3 max-w-md text-center text-neutral-400">
            Ferramentas poderosas para gerenciar sua música de forma simples.
          </p>
          <div className="mt-12 grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
            {features.map((f) => (
              <div key={f.title} className="card group p-6 transition hover:border-brand/40">
                <div className="mb-4 flex h-11 w-11 items-center justify-center rounded-xl bg-brand/10 text-brand transition group-hover:bg-brand group-hover:text-black">
                  <f.icon className="h-5 w-5" />
                </div>
                <h3 className="text-lg font-semibold">{f.title}</h3>
                <p className="mt-2 text-sm text-neutral-400">{f.desc}</p>
              </div>
            ))}
          </div>
        </section>

        {/* How it works */}
        <section className="border-y border-border bg-surface/50">
          <div className="mx-auto max-w-7xl px-4 py-20 sm:px-6">
            <h2 className="text-center text-3xl font-bold sm:text-4xl">Como funciona</h2>
            <div className="mt-12 grid gap-6 md:grid-cols-3">
              {steps.map((s) => (
                <div key={s.n} className="text-center">
                  <div className="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-full bg-gradient-to-br from-brand to-cyan-400 text-xl font-bold text-black">
                    {s.n}
                  </div>
                  <h3 className="text-lg font-semibold">{s.t}</h3>
                  <p className="mt-2 text-sm text-neutral-400">{s.d}</p>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* Formats */}
        <section className="mx-auto max-w-7xl px-4 py-20 sm:px-6">
          <h2 className="text-center text-3xl font-bold sm:text-4xl">Formatos suportados</h2>
          <div className="mt-10 flex flex-wrap items-center justify-center gap-4">
            {AUDIO_FORMATS.map((f) => (
              <div key={f.value} className="card flex flex-col items-center gap-2 px-8 py-6">
                <span className="text-2xl font-bold logo-gradient">{f.label}</span>
                <span className="text-xs text-neutral-500">{f.hint}</span>
              </div>
            ))}
          </div>
        </section>

        {/* Security */}
        <section className="border-y border-border bg-surface/50">
          <div className="mx-auto max-w-4xl px-4 py-20 text-center sm:px-6">
            <div className="mx-auto mb-6 flex h-14 w-14 items-center justify-center rounded-2xl bg-brand/10 text-brand">
              <Lock className="h-7 w-7" />
            </div>
            <h2 className="text-3xl font-bold sm:text-4xl">Segurança em primeiro lugar</h2>
            <p className="mx-auto mt-4 max-w-xl text-neutral-400">
              Senhas protegidas com Argon2, sessões seguras com tokens rotativos, proteção contra
              abuso e isolamento completo dos seus dados.
            </p>
          </div>
        </section>

        {/* Plans */}
        <section className="mx-auto max-w-7xl px-4 py-20 sm:px-6">
          <h2 className="text-center text-3xl font-bold sm:text-4xl">Planos</h2>
          <p className="mx-auto mt-3 max-w-md text-center text-neutral-400">
            Comece grátis e evolua quando precisar.
          </p>
          <div className="mt-12 grid gap-6 lg:grid-cols-3">
            {plans.map((p) => (
              <div
                key={p.tier}
                className={`card relative p-6 ${p.highlight ? 'border-brand/60 bg-gradient-to-b from-brand/5 to-transparent' : ''}`}
              >
                {p.highlight && (
                  <span className="absolute -top-3 left-1/2 -translate-x-1/2 rounded-full bg-brand px-3 py-1 text-xs font-bold text-black">
                    Mais popular
                  </span>
                )}
                <h3 className="text-lg font-semibold">{p.name}</h3>
                <p className="mt-2 text-3xl font-extrabold">
                  {p.price}
                  <span className="text-sm font-normal text-neutral-500">/mês</span>
                </p>
                <ul className="mt-6 space-y-3">
                  {p.features.map((f) => (
                    <li key={f} className="flex items-center gap-2 text-sm text-neutral-300">
                      <Check className="h-4 w-4 shrink-0 text-brand" /> {f}
                    </li>
                  ))}
                </ul>
                <Link to="/register" className={`mt-6 w-full ${p.highlight ? 'btn-primary' : 'btn-secondary'}`}>
                  {p.cta}
                </Link>
              </div>
            ))}
          </div>
        </section>

        {/* FAQ */}
        <section className="mx-auto max-w-3xl px-4 py-20 sm:px-6">
          <h2 className="text-center text-3xl font-bold sm:text-4xl">Perguntas frequentes</h2>
          <div className="mt-10 space-y-3">
            {faqs.map((f) => (
              <details key={f.q} className="card group p-5">
                <summary className="flex cursor-pointer list-none items-center justify-between font-medium">
                  {f.q}
                  <span className="text-neutral-500 transition group-open:rotate-45">+</span>
                </summary>
                <p className="mt-3 text-sm text-neutral-400">{f.a}</p>
              </details>
            ))}
          </div>
        </section>

        {/* CTA */}
        <section className="border-t border-border">
          <div className="mx-auto max-w-3xl px-4 py-20 text-center sm:px-6">
            <h2 className="text-3xl font-bold sm:text-5xl">Pronto para começar?</h2>
            <p className="mt-4 text-neutral-400">Crie sua conta gratuita e comece a organizar sua música.</p>
            <Link to={user ? '/dashboard' : '/register'} className="btn-primary mt-8 px-8 py-3 text-base">
              Começar agora <ArrowRight className="h-5 w-5" />
            </Link>
          </div>
        </section>
      </main>

      <footer className="border-t border-border">
        <div className="mx-auto flex max-w-7xl flex-col items-center justify-between gap-4 px-4 py-8 sm:flex-row sm:px-6">
          <Logo size="sm" />
          <p className="text-sm text-neutral-500">© {new Date().getFullYear()} AudioFlow. Todos os direitos reservados.</p>
        </div>
      </footer>
    </div>
  )
}