import { NextApiRequest, NextApiResponse } from 'next';
import { SendGridService } from '../../lib/sendgrid';

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  if (req.method !== 'POST') {
    return res.status(405).json({ message: 'Method not allowed' });
  }

  try {
    const { to, subject, html, type } = req.body;

    if (!to || !subject) {
      return res.status(400).json({ 
        error: 'Missing required fields: to, subject' 
      });
    }

    let success = false;

    switch (type) {
      case 'newsletter':
        // Send newsletter format
        success = await SendGridService.sendNewsletter({
          to,
          subject,
          marketMovers: [
            { symbol: 'ATW', name: 'Attijariwafa Bank', change: 2.5, price: 45.20 },
            { symbol: 'BMCE', name: 'BMCE Bank', change: -1.2, price: 23.80 },
            { symbol: 'CIH', name: 'CIH Bank', change: 3.1, price: 12.45 }
          ],
          corporateActions: [
            { company: 'Attijariwafa Bank', action: 'Dividend Payment', date: '2024-01-15' },
            { company: 'BMCE Bank', action: 'Annual General Meeting', date: '2024-01-20' }
          ],
          macroHighlights: [
            { indicator: 'MASI Index', value: '12,450.25', change: '+1.2%' },
            { indicator: 'Inflation Rate', value: '2.8%', change: '-0.1%' },
            { indicator: 'Policy Rate', value: '3.0%', change: 'No change' }
          ],
          aiCommentary: 'The Moroccan market showed resilience today with banking stocks leading gains. The MASI index reached new highs supported by strong corporate earnings and positive economic indicators.'
        });
        break;

      case 'price-alert':
        // Send price alert
        success = await SendGridService.sendPriceAlert(
          to,
          'ATW',
          45.20,
          44.00,
          'above'
        );
        break;

      case 'contest':
        // Send contest notification
        success = await SendGridService.sendContestNotification(
          to,
          'January Trading Challenge',
          'Congratulations! You\'ve moved up to 3rd place in the January Trading Challenge. Keep up the great performance!',
          'https://casablancainsights.com/contest'
        );
        break;

      default:
        // Send basic email
        success = await SendGridService.sendEmail({
          to,
          subject,
          html: html || '<p>This is a test email from Casablanca Insights.</p>'
        });
    }

    if (success) {
      res.status(200).json({ 
        message: 'Email sent successfully',
        type: type || 'basic'
      });
    } else {
      res.status(500).json({ 
        error: 'Failed to send email' 
      });
    }

  } catch (error) {
    console.error('Email API error:', error);
    res.status(500).json({ 
      error: 'Internal server error',
      details: error instanceof Error ? error.message : 'Unknown error'
    });
  }
} 