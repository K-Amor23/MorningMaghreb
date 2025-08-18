import { NextRequest } from 'next/server'
import { spawn } from 'child_process'

export async function POST(_req: NextRequest) {
    try {
        // Fire-and-wait: run the script once (idempotent)
        const cwd = process.cwd().replace(/apps\/web$/, '') || process.cwd()
        const proc = spawn('python', ['scripts/scrape_news.py'], { cwd })

        const out: Buffer[] = []
        const err: Buffer[] = []
        proc.stdout.on('data', (d) => out.push(Buffer.from(d)))
        proc.stderr.on('data', (d) => err.push(Buffer.from(d)))

        const code: number = await new Promise((resolve) => proc.on('close', resolve))
        if (code !== 0) {
            return new Response(JSON.stringify({ ok: false, error: Buffer.concat(err).toString() }), { status: 500 })
        }
        return new Response(JSON.stringify({ ok: true, output: Buffer.concat(out).toString() }), { status: 200 })
    } catch (e: any) {
        return new Response(JSON.stringify({ ok: false, error: e?.message || 'failed' }), { status: 500 })
    }
}






