import { NextApiRequest, NextApiResponse } from 'next';
import sgMail from '@sendgrid/mail';

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  if (req.method !== 'GET') {
    return res.status(405).json({ message: 'Method not allowed' });
  }

  try {
    // Check environment variables
    const apiKey = process.env.SENDGRID_API_KEY;
    const fromEmail = process.env.SENDGRID_FROM_EMAIL;

    const config: any = {
      apiKeyExists: !!apiKey,
      apiKeyLength: apiKey ? apiKey.length : 0,
      fromEmailExists: !!fromEmail,
      fromEmail: fromEmail,
      nodeEnv: process.env.NODE_ENV
    };

    // Test SendGrid connection
    if (apiKey) {
      sgMail.setApiKey(apiKey);

      try {
        // Test with a simple email to yourself
        const testMsg = {
          to: 'test@example.com', // This will fail but we can see the error
          from: fromEmail || 'test@example.com',
          subject: 'SendGrid Test',
          text: 'This is a test email to verify SendGrid configuration.',
          html: '<p>This is a test email to verify SendGrid configuration.</p>'
        };

        // Don't actually send, just test the configuration
        const response = await fetch('https://api.sendgrid.com/v3/mail/send', {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${apiKey}`,
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            personalizations: [{
              to: [{ email: 'test@example.com' }]
            }],
            from: { email: fromEmail || 'test@example.com' },
            subject: 'SendGrid Test',
            content: [{
              type: 'text/plain',
              value: 'This is a test email to verify SendGrid configuration.'
            }]
          })
        });

        config.sendGridTest = {
          status: response.status,
          statusText: response.statusText,
          headers: Object.fromEntries(response.headers.entries())
        };

        if (response.status === 401) {
          config.error = 'API key is invalid or expired';
        } else if (response.status === 403) {
          config.error = 'API key lacks permissions or sender not verified';
        } else if (response.status === 400) {
          config.error = 'Request format is incorrect';
        }

      } catch (error) {
        config.sendGridError = error instanceof Error ? error.message : 'Unknown error';
      }
    } else {
      config.error = 'SENDGRID_API_KEY not found in environment variables';
    }

    res.status(200).json(config);

  } catch (error) {
    console.error('SendGrid config test error:', error);
    res.status(500).json({
      error: 'Internal server error',
      details: error instanceof Error ? error.message : 'Unknown error'
    });
  }
} 