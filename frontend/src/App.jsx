import { App } from './app/App'
import { PWAInstallPrompt } from './components/PWAInstallPrompt'

function AppWrapper() {
  return (
    <>
      <App />
      <PWAInstallPrompt />
    </>
  )
}

export { AppWrapper as App }
