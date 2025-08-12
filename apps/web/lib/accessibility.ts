// ARIA labels for better accessibility
export const ARIA_LABELS = {
  SEARCH_INPUT: 'Search companies and tickers',
  THEME_TOGGLE: 'Toggle dark mode',
  ACCOUNT_MENU: 'Account menu',
  CLOSE_MODAL: 'Close modal',
  LOADING: 'Loading content',
  ERROR: 'Error occurred',
}

// Keyboard shortcuts configuration
export const KEYBOARD_SHORTCUTS = {
  SEARCH: {
    key: 'k',
    description: 'Open search',
    action: () => {
      const searchInput = document.querySelector('[data-testid="search-input"]') as HTMLInputElement
      if (searchInput) {
        searchInput.focus()
      }
    }
  },
  THEME_TOGGLE: {
    key: 't',
    description: 'Toggle theme',
    action: () => {
      // This will be handled by the theme context
      const event = new CustomEvent('toggle-theme')
      window.dispatchEvent(event)
    }
  },
  HELP: {
    key: '?',
    description: 'Show keyboard shortcuts',
    action: () => {
      // This will be handled by the help component
      const event = new CustomEvent('show-help')
      window.dispatchEvent(event)
    }
  }
} 