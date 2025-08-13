import { createClient } from '@supabase/supabase-js'

export const getAdminClient = () => {
    const url = process.env.NEXT_PUBLIC_SUPABASE_URL as string
    const key = process.env.SUPABASE_SERVICE_ROLE_KEY as string
    if (!url || !key) throw new Error('Supabase admin env missing')
    return createClient(url, key, { auth: { persistSession: false } })
}


