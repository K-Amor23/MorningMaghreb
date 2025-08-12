import type { NextApiRequest, NextApiResponse } from 'next'

export default function handler(req: NextApiRequest, res: NextApiResponse) {
  if (req.method !== 'POST') return res.status(405).end()
  // This endpoint exists just to confirm action in UI. Actual gating reads NEXT_PUBLIC_ENABLE_PASSWORD_PROTECTION
  return res.status(200).json({ ok: true })
}


