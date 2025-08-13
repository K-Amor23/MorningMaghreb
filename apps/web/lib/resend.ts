import { Resend } from 'resend'

export const isResendConfigured = (): boolean => {
    return Boolean(process.env.RESEND_API_KEY && process.env.RESEND_FROM)
}

export const getResendClient = () => {
    const apiKey = process.env.RESEND_API_KEY
    if (!apiKey) throw new Error('RESEND_API_KEY is not set')
    return new Resend(apiKey)
}

export const getFromEmail = (): string => {
    return process.env.RESEND_FROM || 'no-reply@casablancainsights.com'
}

export const getReplyToEmail = (): string | undefined => {
    return process.env.RESEND_REPLY_TO || undefined
}


