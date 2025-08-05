import type { NextApiRequest, NextApiResponse } from 'next'

export default async function handler(
    req: NextApiRequest,
    res: NextApiResponse
) {
    if (req.method !== 'POST') {
        return res.status(405).json({ error: 'Method not allowed' })
    }

    try {
        const { include_macro, include_sectors, include_top_movers, language } = req.body

        // Mock newsletter content generation
        const mockNewsletterContent = {
            en: {
                subject: 'Weekly Market Recap - July 29, 2025',
                content: `# Weekly Market Recap - July 29, 2025

## Market Overview
The Casablanca Stock Exchange (CSE) showed mixed performance this week, with the MASI index closing at 12,450 points, up 0.8% from last week.

## Top Performers
- ATW (Attijariwafa Bank): +5.2% - Strong Q2 earnings beat expectations
- IAM (Maroc Telecom): +3.8% - Dividend announcement boosts shares
- BCP (Banque Centrale Populaire): +2.1% - Positive analyst coverage

## Top Decliners
- CMT (Ciments du Maroc): -2.3% - Cement demand concerns
- LAFA (Lafarge Ciments): -1.8% - Sector-wide pressure
- BMCE (BMCE Bank): -1.2% - Profit taking after recent gains

## Macro Economic Updates
- Bank Al-Maghrib maintains key rate at 3%
- Inflation rate stable at 2.1% year-over-year
- Foreign exchange reserves at $35.2 billion

## Sector Performance
- Banking: +2.1% - Strong earnings season
- Telecom: +1.8% - Stable growth outlook
- Materials: -0.9% - Construction slowdown concerns

## Looking Ahead
Next week's key events:
- ATW earnings call (Tuesday)
- IAM dividend payment (Wednesday)
- Macro data release (Friday)

Stay informed with Casablanca Insights!`
            },
            fr: {
                subject: 'Récapitulatif Hebdomadaire - 29 Juillet 2025',
                content: `# Récapitulatif Hebdomadaire - 29 Juillet 2025

## Aperçu du Marché
La Bourse de Casablanca (CSE) a affiché des performances mitigées cette semaine, avec l'indice MASI clôturant à 12 450 points, en hausse de 0,8% par rapport à la semaine dernière.

## Meilleurs Performeurs
- ATW (Attijariwafa Bank): +5,2% - Résultats Q2 solides dépassent les attentes
- IAM (Maroc Telecom): +3,8% - Annonce de dividende booste les actions
- BCP (Banque Centrale Populaire): +2,1% - Couverture analyste positive

## Principaux Déclins
- CMT (Ciments du Maroc): -2,3% - Préoccupations sur la demande de ciment
- LAFA (Lafarge Ciments): -1,8% - Pression sectorielle
- BMCE (BMCE Bank): -1,2% - Prise de bénéfices après les gains récents

## Mises à Jour Macro-économiques
- Bank Al-Maghrib maintient le taux directeur à 3%
- Taux d'inflation stable à 2,1% en glissement annuel
- Réserves de change à 35,2 milliards de dollars

## Performance Sectorielle
- Banque: +2,1% - Saison des résultats solide
- Télécom: +1,8% - Perspectives de croissance stables
- Matériaux: -0,9% - Préoccupations de ralentissement de la construction

## Perspectives
Événements clés de la semaine prochaine:
- Conférence téléphonique ATW (mardi)
- Paiement de dividende IAM (mercredi)
- Publication des données macro (vendredi)

Restez informé avec Casablanca Insights!`
            },
            ar: {
                subject: 'تقرير السوق الأسبوعي - 29 يوليو 2025',
                content: `# تقرير السوق الأسبوعي - 29 يوليو 2025

## نظرة عامة على السوق
أظهرت بورصة الدار البيضاء (CSE) أداءً مختلطاً هذا الأسبوع، حيث أغلق مؤشر MASI عند 12,450 نقطة، مرتفعاً بنسبة 0.8% مقارنة بالأسبوع الماضي.

## أفضل الأداء
- ATW (بنك التجاري وفا بنك): +5.2% - أرباح Q2 قوية تتجاوز التوقعات
- IAM (المغرب للاتصالات): +3.8% - إعلان الأرباح يعزز الأسهم
- BCP (البنك المركزي الشعبي): +2.1% - تغطية محلل إيجابية

## أكبر الانخفاضات
- CMT (إسمنت المغرب): -2.3% - مخاوف الطلب على الإسمنت
- LAFA (لافارج إسمنت): -1.8% - ضغط قطاعي
- BMCE (بنك BMCE): -1.2% - جني الأرباح بعد المكاسب الأخيرة

## تحديثات الاقتصاد الكلي
- بنك المغرب يحافظ على سعر الفائدة الرئيسي عند 3%
- معدل التضخم مستقر عند 2.1% سنوياً
- احتياطيات العملة الأجنبية عند 35.2 مليار دولار

## أداء القطاعات
- البنوك: +2.1% - موسم أرباح قوي
- الاتصالات: +1.8% - آفاق نمو مستقرة
- المواد: -0.9% - مخاوف تباطؤ البناء

## النظرة المستقبلية
الأحداث الرئيسية للأسبوع القادم:
- مكالمة أرباح ATW (الثلاثاء)
- دفع أرباح IAM (الأربعاء)
- إصدار البيانات الاقتصادية (الجمعة)

ابق على اطلاع مع رؤى الدار البيضاء!`
            }
        }

        const content = mockNewsletterContent[language as keyof typeof mockNewsletterContent] || mockNewsletterContent.en

        res.status(200).json({
            subject: content.subject,
            content: content.content,
            language: language,
            generated_at: new Date().toISOString()
        })
    } catch (error) {
        console.error('Error generating newsletter preview:', error)
        res.status(500).json({
            error: 'Internal server error',
            message: 'Failed to generate newsletter preview'
        })
    }
} 