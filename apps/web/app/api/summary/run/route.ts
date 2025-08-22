import { NextRequest } from 'next/server'
import OpenAI from 'openai'
import { getAdminClient } from '@/lib/supabaseAdmin'

export async function POST(_req: NextRequest) {
    try {
        const supa = getAdminClient()
        const openaiKey = process.env.OPENAI_API_KEY
        if (!openaiKey) throw new Error('OPENAI_API_KEY missing')
        const openai = new OpenAI({ apiKey: openaiKey })

        // Pull last 7 days headlines for target tickers
        const { data: news } = await supa
            .from('company_news')
            .select('ticker,headline,source,published_at')
            .gte('published_at', new Date(Date.now() - 7 * 864e5).toISOString())
            .in('ticker', ['ATW', 'IAM', 'BCP'])
            .order('published_at', { ascending: false })
            .limit(50)

        const headBlob = (news || [])
            .slice(0, 50)
            .map(n => `- ${n.ticker}: ${n.headline} (${n.source})`)
            .join('\n')

        const system = 'You are a careful financial editor for Moroccan markets. Write a concise weekly recap in Markdown (<= 250 words), neutral and factual.'
        const user = `Recent headlines (subset):\n${headBlob}`

        const resp = await openai.chat.completions.create({
            model: 'gpt-4o-mini',
            messages: [
                { role: 'system', content: system },
                { role: 'user', content: user },
            ],
            temperature: 0.4,
            max_tokens: 600,
        })
        const content = resp.choices[0]?.message?.content || '# Weekly Moroccan Business Recap\n\n(no content)'
        const subject = `Moroccan Markets Weekly Recap — ${new Date().toISOString().slice(0, 10)}`

        // Upsert into newsletter_summaries
        const { data, error } = await supa
            .from('newsletter_summaries')
            .upsert({
                summary_date: new Date().toISOString().slice(0, 10),
                language: 'en',
                subject,
                content,
            }, { onConflict: 'summary_date,language' })
            .select()
            .limit(1)

        if (error) throw error
        return new Response(JSON.stringify({ ok: true, summaryId: data?.[0]?.id || null }), { status: 200 })
    } catch (e: any) {
        return new Response(JSON.stringify({ ok: false, error: e?.message || 'failed' }), { status: 500 })
    }
}








