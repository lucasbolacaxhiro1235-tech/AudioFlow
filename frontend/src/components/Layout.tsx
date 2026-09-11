import { Outlet } from 'react-router-dom'
import { Navbar } from './Navbar'
import { PlayerBar } from './PlayerBar'
import { usePlayer } from '../lib/player'

export function Layout() {
  const { current } = usePlayer()
  return (
    <div className="min-h-screen bg-base">
      <Navbar />
      <main className={`mx-auto max-w-7xl px-4 py-6 sm:px-6 ${current ? 'pb-28' : 'pb-8'}`}>
        <Outlet />
      </main>
      <PlayerBar />
    </div>
  )
}