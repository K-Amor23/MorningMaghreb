export function getBaseUrl(): string {
  if (typeof window !== 'undefined' && window.location) {
    return window.location.origin
  }

  const siteUrl = process.env.NEXT_PUBLIC_SITE_URL || process.env.VERCEL_URL
  if (siteUrl) {
    return siteUrl.startsWith('http') ? siteUrl : `https://${siteUrl}`
  }

  const port = process.env.PORT || 3000
  return `http://localhost:${port}`
}

export function makeApiUrl(path: string): string {
  const base = getBaseUrl()
  if (path.startsWith('http')) return path
  if (path.startsWith('/')) return `${base}${path}`
  return `${base}/${path}`
}

