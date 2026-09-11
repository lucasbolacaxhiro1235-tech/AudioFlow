import { useState } from 'react'
import { Link, NavLink, useNavigate } from 'react-router-dom'
import {
  LayoutDashboard,
  Library,
  ListMusic,
  LogOut,
  Menu,
  Settings,
  Shield,
  X
} from 'lucide-react'
import { useAuth } from '../lib/auth'
import { Logo } from './Logo'

const links = [
  { to: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { to: '/library', label: 'Biblioteca', icon: Library },
  { to: '/playlists', label: 'Playlists', icon: ListMusic }
]

export function Navbar() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()
  const [open, setOpen] = useState(false)

  async function handleLogout() {
    await logout()
    navigate('/')
  }

  return (
    <header className="sticky top-0 z-40 border-b border-border bg-base/80 backdrop-blur-xl">
      <div className="mx-auto flex max-w-7xl items-center justify-between px-4 py-3 sm:px-6">
        <div className="flex items-center gap-6">
          <Link to="/dashboard">
            <Logo />
          </Link>
          <nav className="hidden items-center gap-1 md:flex">
            {links.map((l) => (
              <NavLink
                key={l.to}
                to={l.to}
                className={({ isActive }) =>
                  `flex items-center gap-2 rounded-lg px-3 py-2 text-sm font-medium transition ${
                    isActive ? 'bg-white/10 text-white' : 'text-neutral-400 hover:text-white'
                  }`
                }
              >
                <l.icon className="h-4 w-4" />
                {l.label}
              </NavLink>
            ))}
            {user?.role === 'admin' && (
              <NavLink
                to="/admin"
                className={({ isActive }) =>
                  `flex items-center gap-2 rounded-lg px-3 py-2 text-sm font-medium transition ${
                    isActive ? 'bg-white/10 text-white' : 'text-neutral-400 hover:text-white'
                  }`
                }
              >
                <Shield className="h-4 w-4" />
                Admin
              </NavLink>
            )}
          </nav>
        </div>

        <div className="flex items-center gap-2">
          <Link
            to="/settings"
            className="flex items-center gap-2 rounded-full p-1 pr-3 transition hover:bg-white/10"
          >
            <div className="flex h-8 w-8 items-center justify-center rounded-full bg-gradient-to-br from-brand to-cyan-500 text-sm font-bold text-black">
              {user?.name?.[0]?.toUpperCase() ?? 'U'}
            </div>
            <span className="hidden text-sm font-medium text-neutral-200 sm:block">{user?.name}</span>
          </Link>
          <button onClick={handleLogout} className="btn-ghost p-2" aria-label="Sair">
            <LogOut className="h-4 w-4" />
          </button>
          <button className="btn-ghost p-2 md:hidden" onClick={() => setOpen(true)} aria-label="Menu">
            <Menu className="h-5 w-5" />
          </button>
        </div>
      </div>

      {open && (
        <div className="fixed inset-0 z-50 bg-black/60 backdrop-blur-sm" onClick={() => setOpen(false)}>
          <div
            className="absolute right-0 top-0 flex h-full w-72 flex-col gap-2 bg-surface p-5"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="mb-4 flex items-center justify-between">
              <Logo />
              <button onClick={() => setOpen(false)} aria-label="Fechar">
                <X className="h-5 w-5" />
              </button>
            </div>
            {links.map((l) => (
              <Link
                key={l.to}
                to={l.to}
                onClick={() => setOpen(false)}
                className="flex items-center gap-3 rounded-lg px-3 py-3 text-sm font-medium text-neutral-200 hover:bg-white/10"
              >
                <l.icon className="h-5 w-5" />
                {l.label}
              </Link>
            ))}
            {user?.role === 'admin' && (
              <Link
                to="/admin"
                onClick={() => setOpen(false)}
                className="flex items-center gap-3 rounded-lg px-3 py-3 text-sm font-medium text-neutral-200 hover:bg-white/10"
              >
                <Shield className="h-5 w-5" />
                Admin
              </Link>
            )}
            <Link
              to="/settings"
              onClick={() => setOpen(false)}
              className="flex items-center gap-3 rounded-lg px-3 py-3 text-sm font-medium text-neutral-200 hover:bg-white/10"
            >
              <Settings className="h-5 w-5" />
              Configurações
            </Link>
            <button
              onClick={handleLogout}
              className="mt-auto flex items-center gap-3 rounded-lg px-3 py-3 text-sm font-medium text-red-400 hover:bg-white/10"
            >
              <LogOut className="h-5 w-5" />
              Sair
            </button>
          </div>
        </div>
      )}
    </header>
  )
}