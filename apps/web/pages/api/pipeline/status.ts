import type { NextApiRequest, NextApiResponse } from 'next'
import { createClient } from '@supabase/supabase-js'

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL as string
const supabaseServiceKey = process.env.SUPABASE_SERVICE_ROLE_KEY as string
const supabase = createClient(supabaseUrl, supabaseServiceKey)

type StatusResponse = {
    ok: boolean
    market_status: any | null
    counts: {
        comprehensive_market_data: number
        company_news: number
    }
    timestamp: string
}

export default async function handler(req: NextApiRequest, res: NextApiResponse<StatusResponse | { ok: false; error: string }>) {
    if (req.method !== 'GET') return res.status(405).json({ ok: false, error: 'Method not allowed' })
    try {
        const midnightUtc = new Date()
        midnightUtc.setUTCHours(0, 0, 0, 0)

        // Latest market_status
        const { data: marketStatus } = await supabase
            .from('market_status')
            .select('*')
            .order('created_at', { ascending: false })
            .limit(1)
            .maybeSingle()

        // Counts since 00:00Z
        const { count: cmdCount } = await supabase
            .from('comprehensive_market_data')
            .select('id', { count: 'exact', head: true })
            .gte('created_at', midnightUtc.toISOString())

        const { count: newsCount } = await supabase
            .from('company_news')
            .select('id', { count: 'exact', head: true })
            .gte('created_at', midnightUtc.toISOString())

        return res.status(200).json({
            ok: true,
            market_status: marketStatus || null,
            counts: {
                comprehensive_market_data: cmdCount ?? 0,
                company_news: newsCount ?? 0,
            },
            timestamp: new Date().toISOString(),
        })
    } catch (e: any) {
        return res.status(500).json({ ok: false, error: e?.message || 'failed' })
    }
}


