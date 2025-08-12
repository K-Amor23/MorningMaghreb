import { NextRequest, NextResponse } from 'next/server'

// Lightweight cookie check; backend validation remains authoritative
export function middleware(req: NextRequest) {
  const { pathname } = req.nextUrl

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
  matcher: ['/admin/:path*'],
}


