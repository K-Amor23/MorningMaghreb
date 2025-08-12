import type { NextApiRequest, NextApiResponse } from 'next'

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  if (req.method !== 'POST') return res.status(405).end()

  try {
    // In preview mode, simply set a cookie flag. Do not store plaintext passwords server-side.
    // If you need real verification, back it by a persistent backend service.
    res.setHeader('Set-Cookie', `mm_gate=ok; Path=/; SameSite=Lax`)
    return res.status(200).json({ ok: true })
  } catch (e) {
    return res.status(500).json({ error: 'Failed to set password' })
  }
}


