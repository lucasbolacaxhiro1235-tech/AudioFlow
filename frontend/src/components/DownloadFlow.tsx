import { useEffect, useRef, useState } from 'react'
import { ArrowDown, CheckCircle2, Link2, Loader2, Music2, XCircle } from 'lucide-react'
import type { Download, DownloadEvent, ResolveResult } from '../lib/types'
import { downloadsApi, parseEventSource } from '../lib/api'
import { useToast } from '../lib/toast'
import { AUDIO_FORMATS, QUALITIES, formatBytes, formatSpeed } from '../lib/format'
import { Loader } from './Loader'

const STATUS_LABEL: Record<string, string> = {
  pending: 'Na fila',
  validating: 'Validando',
  processing: 'Processando',
  converting: 'Convertendo',
  completed: 'Concluído',
  failed: 'Falhou',
  cancelled: 'Cancelado'
}

export function DownloadFlow({ onComplete }: { onComplete?: () => void }) {
  const { toast } = useToast()
  const [url, setUrl] = useState('')
  const [resolving, setResolving] = useState(false)
  const [resolved, setResolved] = useState<ResolveResult | null>(null)
  const [format, setFormat] = useState('mp3')
  const [quality, setQuality] = useState('192k')
  const [active, setActive] = useState<Download | null>(null)
  const [event, setEvent] = useState<DownloadEvent | null>(null)
  const doneRef = useRef(false)

  async function handleResolve() {
    const trimmed = url.trim()
    if (!trimmed) {
      toast('Cole um link primeiro', 'error')
      return
    }
    setResolving(true)
    setResolved(null)
    setEvent(null)
    try {
      const result = await downloadsApi.resolve(trimmed)
      if (result.kind === 'invalid' || result.error) {
        toast(result.error ?? 'Link inválido', 'error')
        setResolved(null)
      } else {
        setResolved(result)
      }
    } catch (e) {
      toast(e instanceof Error ? e.message : 'Falha ao resolver link', 'error')
    } finally {
      setResolving(false)
    }
  }

  async function handleDownload() {
    if (!resolved) return
    doneRef.current = false
    try {
      const d = await downloadsApi.create({
        url: url.trim(),
        format,
        quality: format === 'mp3' ? quality : undefined
      })
      setActive(d)
      setEvent(null)
      toast('Download iniciado', 'success')
    } catch (e) {
      toast(e instanceof Error ? e.message : 'Falha ao iniciar download', 'error')
    }
  }

  useEffect(() => {
    if (!active || active.status === 'completed' || active.status === 'failed' || active.status === 'cancelled') return
    const close = parseEventSource(active.id, (ev) => {
      setEvent(ev)
      if (!doneRef.current && (ev.status === 'completed' || ev.status === 'failed')) {
        doneRef.current = true
        if (ev.status === 'completed') {
          toast('Download concluído', 'success')
          onComplete?.()
        }
      }
    })
    return close
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [active?.id])

  function reset() {
    setResolved(null)
    setEvent(null)
    setActive(null)
    setUrl('')
  }

  const progress = event?.progress ?? (event?.status === 'completed' ? 100 : 0)

  return (
    <div className="card p-5">
      <div className="mb-4">
        <label className="label" htmlFor="download-url">
          Cole o link da música, álbum ou playlist
        </label>
        <div className="flex flex-col gap-2 sm:flex-row">
          <div className="relative flex-1">
            <Link2 className="pointer-events-none absolute left-3 top-1/2 h-5 w-5 -translate-y-1/2 text-neutral-500" />
            <input
              id="download-url"
              className="input pl-10"
              placeholder="https://open.spotify.com/… ou https://youtube.com/…"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleResolve()}
            />
          </div>
          <button className="btn-primary" onClick={handleResolve} disabled={resolving || !url.trim()}>
            {resolving ? <Loader2 className="h-4 w-4 animate-spin" /> : <Music2 className="h-4 w-4" />}
            Analisar
          </button>
        </div>
      </div>

      {resolving && (
        <div className="flex justify-center py-6">
          <Loader />
        </div>
      )}

      {resolved && !active && (
        <div className="animate-slideUp">
          <div className="flex items-center gap-4 rounded-xl bg-white/5 p-4">
            {resolved.cover_url ? (
              <img src={resolved.cover_url} alt="" className="h-16 w-16 rounded-lg object-cover" />
            ) : (
              <div className="flex h-16 w-16 items-center justify-center rounded-lg bg-white/10">
                <Music2 className="h-7 w-7 text-neutral-400" />
              </div>
            )}
            <div className="min-w-0 flex-1">
              <p className="truncate font-semibold text-white">{resolved.title}</p>
              <p className="truncate text-sm text-neutral-400">{resolved.artist}</p>
              {resolved.kind !== 'track' && (
                <span className="mt-1 inline-block rounded-full bg-brand/10 px-2 py-0.5 text-xs font-medium text-brand">
                  {resolved.track_count} faixas
                </span>
              )}
            </div>
          </div>

          <div className="mt-4 grid grid-cols-2 gap-4">
            <div>
              <span className="label">Formato</span>
              <div className="flex flex-wrap gap-2">
                {AUDIO_FORMATS.map((f) => (
                  <button
                    key={f.value}
                    onClick={() => setFormat(f.value)}
                    className={`rounded-lg px-3 py-1.5 text-sm font-medium transition ${
                      format === f.value
                        ? 'bg-brand text-black'
                        : 'bg-white/5 text-neutral-300 hover:bg-white/10'
                    }`}
                  >
                    {f.label}
                  </button>
                ))}
              </div>
            </div>
            {format === 'mp3' && (
              <div>
                <span className="label">Qualidade</span>
                <div className="flex flex-wrap gap-2">
                  {QUALITIES.map((q) => (
                    <button
                      key={q}
                      onClick={() => setQuality(q)}
                      className={`rounded-lg px-3 py-1.5 text-sm font-medium transition ${
                        quality === q
                          ? 'bg-brand text-black'
                          : 'bg-white/5 text-neutral-300 hover:bg-white/10'
                      }`}
                    >
                      {q}
                    </button>
                  ))}
                </div>
              </div>
            )}
          </div>

          <div className="mt-4 flex gap-2">
            <button className="btn-primary flex-1" onClick={handleDownload}>
              <ArrowDown className="h-4 w-4" />
              Iniciar download
            </button>
            <button className="btn-ghost" onClick={reset}>
              Cancelar
            </button>
          </div>
        </div>
      )}

      {active && (
        <div className="animate-slideUp">
          <div className="flex items-center gap-3">
            <span className="font-medium text-neutral-300">
              {STATUS_LABEL[event?.status ?? active.status]}
            </span>
            {['pending', 'validating', 'processing', 'converting'].includes(
              event?.status ?? active.status
            ) && <Loader2 className="h-4 w-4 animate-spin text-brand" />}
            {event?.status === 'completed' && <CheckCircle2 className="h-5 w-5 text-brand" />}
            {event?.status === 'failed' && <XCircle className="h-5 w-5 text-red-400" />}
          </div>

          <div className="mt-3 h-2 w-full overflow-hidden rounded-full bg-white/10">
            <div
              className="h-full rounded-full bg-gradient-to-r from-brand to-cyan-400 transition-all duration-500"
              style={{ width: `${progress}%` }}
            />
          </div>

          <div className="mt-2 flex flex-wrap items-center justify-between gap-2 text-sm text-neutral-400">
            <span className="font-semibold text-white">{progress}%</span>
            <span>
              {formatBytes(event?.downloaded_bytes ?? 0)} /{' '}
              {event?.total_bytes ? formatBytes(event.total_bytes) : '—'}
            </span>
            <span>{formatSpeed(event?.speed_bps)}</span>
          </div>

          {event?.status === 'failed' && event.error_message && (
            <p className="mt-2 rounded-lg bg-red-500/10 px-3 py-2 text-sm text-red-300">
              {event.error_message}
            </p>
          )}

          {event?.status === 'completed' && (
            <button className="btn-primary mt-4" onClick={reset}>
              Baixar outro
            </button>
          )}
        </div>
      )}
    </div>
  )
}