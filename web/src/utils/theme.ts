export type ThemeMode = 'light' | 'dark'

const THEME_STORAGE_KEY = 'theme'

export function getInitialTheme(): ThemeMode {
  const saved = localStorage.getItem(THEME_STORAGE_KEY)
  if (saved === 'dark' || saved === 'light') return saved

  const prefersDark = window.matchMedia?.('(prefers-color-scheme: dark)')?.matches
  return prefersDark ? 'dark' : 'light'
}

export function applyTheme(theme: ThemeMode) {
  const root = document.documentElement

  // 1) 我们自有的 CSS 变量体系
  root.setAttribute('data-theme', theme)

  // 2) Element Plus 暗色变量体系：依赖 html 上的 .dark
  root.classList.toggle('dark', theme === 'dark')

  localStorage.setItem(THEME_STORAGE_KEY, theme)
}
