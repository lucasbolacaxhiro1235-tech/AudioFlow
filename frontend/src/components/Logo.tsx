import { AudioLines } from 'lucide-react'

export function Logo({ size = 'md' }: { size?: 'sm' | 'md' | 'lg' }) {
  const cls = size === 'lg' ? 'h-9 w-9' : size === 'sm' ? 'h-6 w-6' : 'h-7 w-7'
  return (
    <div className="flex items-center gap-2">
      <div className={`${cls} flex items-center justify-center rounded-lg bg-gradient-to-br from-brand to-cyan-400`}>
        <AudioLines className="h-1/2 w-1/2 text-black" strokeWidth={2.75} />
      </div>
      <span className={`font-extrabold tracking-tight text-white ${size === 'lg' ? 'text-2xl' : 'text-xl'}`}>
        Audio<span className="logo-gradient">Flow</span>
      </span>
    </div>
  )
}