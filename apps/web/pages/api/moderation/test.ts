import { NextApiRequest, NextApiResponse } from 'next'

interface ModerationRequest {
  text: string
  content_type: string
}

interface ModerationResponse {
  is_safe: boolean
  moderation_level: string
  moderated_text?: string
  sensitive_topics: string[]
  confidence_score: number
  flagged_phrases: string[]
  suggestions: string[]
  can_proceed: boolean
}

// Mock moderation service for demonstration
class MockModerationService {
  private sensitivePatterns = {
    monarchy: [
      /\bking\b/i, /\bmonarch\b/i, /\broyal\b/i, /\bpalace\b/i,
      /\bHM\b/i, /\bHis Majesty\b/i, /\bRoyal Family\b/i,
      /\bMohammed VI\b/i, /\bMohammed 6\b/i, /\bMohammed 6th\b/i
    ],
    government: [
      /\bgovernment\b/i, /\bministry\b/i, /\bminister\b/i,
      /\bparliament\b/i, /\bMP\b/i, /\bMember of Parliament\b/i,
      /\bPrime Minister\b/i, /\bPM\b/i
    ],
    religion: [
      /\bIslam\b/i, /\bMuslim\b/i, /\bmosque\b/i, /\bhalal\b/i,
      /\bharam\b/i, /\bIslamic\b/i, /\breligious\b/i
    ],
    politics: [
      /\bpolitical\b/i, /\bparty\b/i, /\belection\b/i, /\bvote\b/i,
      /\bopposition\b/i, /\bruling\b/i, /\bregime\b/i
    ]
  }

  private safeAlternatives = {
    'king': 'leadership',
    'monarch': 'leadership',
    'royal': 'official',
    'palace': 'institution',
    'government': 'authorities',
    'ministry': 'department',
    'minister': 'official',
    'parliament': 'legislative body',
    'Prime Minister': 'head of government',
    'PM': 'head of government',
    'regime': 'administration',
    'ruling': 'current',
    'opposition': 'other parties'
  }

  moderateContent(text: string, contentType: string): ModerationResponse {
    const sensitiveTopics: string[] = []
    const flaggedPhrases: string[] = []

    // Check for sensitive content
    for (const [topic, patterns] of Object.entries(this.sensitivePatterns)) {
      for (const pattern of patterns) {
        const matches = text.match(pattern)
        if (matches) {
          if (!sensitiveTopics.includes(topic)) {
            sensitiveTopics.push(topic)
          }
          flaggedPhrases.push(...matches)
        }
      }
    }

    // Determine moderation level
    let moderationLevel = 'safe'
    if (sensitiveTopics.includes('monarchy') || sensitiveTopics.includes('government')) {
      moderationLevel = 'blocked'
    } else if (sensitiveTopics.length >= 3 || flaggedPhrases.length >= 5) {
      moderationLevel = 'requires_review'
    } else if (sensitiveTopics.length > 0) {
      moderationLevel = 'flagged'
    }

    // Generate moderated text
    let moderatedText: string | undefined
    if (moderationLevel === 'flagged' || moderationLevel === 'requires_review') {
      moderatedText = this.generateSafeText(text, flaggedPhrases)
    }

    // Calculate confidence score
    const confidenceScore = Math.max(0, 1 - (sensitiveTopics.length * 0.2) - (flaggedPhrases.length * 0.1))

    // Generate suggestions
    const suggestions = this.generateSuggestions(contentType, sensitiveTopics)

    return {
      is_safe: moderationLevel === 'safe',
      moderation_level: moderationLevel,
      moderated_text: moderatedText,
      sensitive_topics: sensitiveTopics,
      confidence_score: confidenceScore,
      flagged_phrases: Array.from(new Set(flaggedPhrases)),
      suggestions,
      can_proceed: moderationLevel === 'safe' || moderationLevel === 'flagged'
    }
  }

  private generateSafeText(originalText: string, flaggedPhrases: string[]): string {
    let safeText = originalText

    for (const phrase of flaggedPhrases) {
      const lowerPhrase = phrase.toLowerCase()
      if (lowerPhrase in this.safeAlternatives) {
        const replacement = this.safeAlternatives[lowerPhrase as keyof typeof this.safeAlternatives]
        const regex = new RegExp(phrase, 'gi')
        safeText = safeText.replace(regex, replacement)
      }
    }

    return safeText
  }

  private generateSuggestions(contentType: string, sensitiveTopics: string[]): string[] {
    const suggestions: string[] = []

    if (sensitiveTopics.includes('monarchy')) {
      suggestions.push('Avoid references to monarchy or royal family')
    }
    if (sensitiveTopics.includes('government')) {
      suggestions.push('Focus on business and economic aspects rather than government')
    }
    if (sensitiveTopics.includes('religion')) {
      suggestions.push('Keep content secular and business-focused')
    }
    if (sensitiveTopics.includes('politics')) {
      suggestions.push('Avoid political commentary or analysis')
    }

    suggestions.push('Use a neutral, factual, and professional tone')
    suggestions.push('Focus on market performance, economic indicators, and business trends')

    return suggestions
  }
}

const moderationService = new MockModerationService()

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse
) {
  if (req.method !== 'POST') {
    return res.status(405).json({ message: 'Method not allowed' })
  }

  try {
    const { text, content_type }: ModerationRequest = req.body

    if (!text) {
      return res.status(400).json({ message: 'Text is required' })
    }

    // Perform moderation
    const moderationResult = moderationService.moderateContent(text, content_type)

    // Simulate processing delay
    await new Promise(resolve => setTimeout(resolve, 300))

    res.status(200).json({
      original_text: text,
      moderation_result: moderationResult,
      safe_alternatives: moderationService['safeAlternatives']
    })
  } catch (error) {
    console.error('Error in moderation test:', error)
    res.status(500).json({ message: 'Internal server error' })
  }
} 