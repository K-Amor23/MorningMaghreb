import { NextRequest, NextResponse } from 'next/server'

// Lightweight cookie check; backend validation remains authoritative
export function middleware(req: NextRequest) {
  const { pathname } = req.nextUrl

  // Global preview password gate (skip for public assets and auth)
  const isPasswordEnabled = process.env.NEXT_PUBLIC_ENABLE_PASSWORD_PROTECTION === 'true'
  const isPublic =
    pathname.startsWith('/_next') ||
    pathname.startsWith('/api') ||
    pathname.startsWith('/auth') ||
    pathname.startsWith('/login') ||
    pathname.startsWith('/signup') ||
    pathname.startsWith('/public') ||
    pathname.startsWith('/icons') ||
    pathname === '/'

  if (isPasswordEnabled && !isPublic) {
    const hasGate = req.cookies.get('mm_gate')?.value === 'ok'
    if (!hasGate) {
      const url = req.nextUrl.clone()
      url.pathname = '/admin/password-protection'
      url.searchParams.set('redirect', pathname)
      return NextResponse.redirect(url)
    }
  }

  // Admin area gate
  if (pathname.startsWith('/admin')) {
    const tier = req.cookies.get('mm_tier')?.value || ''
    if (tier !== 'admin') {
      const url = req.nextUrl.clone()
      url.pathname = '/login'
      url.searchParams.set('redirect', pathname)
      return NextResponse.redirect(url)
    }
  }

  return NextResponse.next()
}

export const config = {
  matcher: ['/:path*'],
}


