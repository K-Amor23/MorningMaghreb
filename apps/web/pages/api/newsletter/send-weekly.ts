import type { NextApiRequest, NextApiResponse } from 'next'
import OpenAI from 'openai'
import { getResendClient, isResendConfigured, getFromEmail } from '@/lib/resend'
import { supabase } from '@/lib/supabase'

export default async function handler(
    req: NextApiRequest,
    res: NextApiResponse
) {
    if (req.method !== 'POST') {
        return res.status(405).json({ error: 'Method not allowed' })
    }

    try {
        // Check prerequisites
        if (!process.env.OPENAI_API_KEY) {
            return res.status(400).json({ error: 'OPENAI_API_KEY is not configured' })
        }
        if (!isResendConfigured()) {
            return res.status(400).json({ error: 'Resend is not configured (RESEND_API_KEY/RESEND_FROM)' })
        }

        const language = (req.body?.language as string) || 'en'

        // Build newsletter content using OpenAI
        const openai = new OpenAI({ apiKey: process.env.OPENAI_API_KEY })
        const systemPrompt = `You are an assistant that writes concise ${language.toUpperCase()} market newsletters for Moroccan equities. Tone is professional, clear, and friendly. Include: macro snapshot, top sector moves, 3-5 notable company highlights. Keep under 250 words.`

        const { data: companies } = await supabase!
            .from('companies')
            .select('ticker,name,sector,price,change_1d_percent')
            .limit(50)

        const userPrompt = `Use the following recent data (may be partial):\n${JSON.stringify(companies || []).slice(0, 4000)}\nWrite the newsletter now.`

        const completion = await openai.chat.completions.create({
            model: 'gpt-4o-mini',
            messages: [
                { role: 'system', content: systemPrompt },
                { role: 'user', content: userPrompt },
            ],
            temperature: 0.7,
            max_tokens: 600,
        })

        const content = completion.choices[0]?.message?.content || 'Weekly market recap.'
        const subject = `Casablanca Insights — Weekly Recap`

        // Fetch subscribers
        const { data: subs, error: subsErr } = await supabase!
            .from('newsletter_subscribers')
            .select('email,status')
            .eq('status', 'active')

        if (subsErr) {
            return res.status(500).json({ error: 'Failed to load subscribers', details: subsErr.message })
        }

        const toList = (subs || []).map((s: any) => s.email).filter(Boolean)
        if (toList.length === 0) {
            return res.status(200).json({ success: true, message: 'No active subscribers to send to', subject, preview: content.slice(0, 200) })
        }

        const resend = getResendClient()
        const from = getFromEmail()

        // Send in batches of 50 to avoid rate limits
        const batchSize = 50
        for (let i = 0; i < toList.length; i += batchSize) {
            const batch = toList.slice(i, i + batchSize)
            await resend.emails.send({
                from,
                to: batch,
                subject,
                html: `<div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; white-space: pre-wrap;">${content}</div>`
            } as any)
        }

        return res.status(200).json({ success: true, sent: toList.length, subject })
    } catch (err: any) {
        console.error('send-weekly error:', err)
        return res.status(500).json({ error: 'Failed to send weekly newsletter', details: err?.message || String(err) })
    }
}




