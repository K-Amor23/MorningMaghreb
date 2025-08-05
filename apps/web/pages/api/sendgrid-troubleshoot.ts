import { NextApiRequest, NextApiResponse } from 'next';

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  if (req.method !== 'GET') {
    return res.status(405).json({ message: 'Method not allowed' });
  }

  const troubleshooting = {
    currentConfig: {
      apiKey: process.env.SENDGRID_API_KEY ? '✅ Set' : '❌ Missing',
      fromEmail: process.env.SENDGRID_FROM_EMAIL || '❌ Not set',
      apiKeyLength: process.env.SENDGRID_API_KEY?.length || 0
    },
    commonIssues: [
      {
        issue: '403 Forbidden Error',
        cause: 'Sender email not verified in SendGrid',
        solution: 'Verify admin@morningmaghreb.com in SendGrid dashboard'
      },
      {
        issue: '401 Unauthorized',
        cause: 'Invalid or expired API key',
        solution: 'Generate new API key in SendGrid dashboard'
      },
      {
        issue: '400 Bad Request',
        cause: 'Invalid email format or missing required fields',
        solution: 'Check email format and required fields'
      }
    ],
    stepsToFix: [
      '1. Go to https://app.sendgrid.com/',
      '2. Navigate to Settings → Sender Authentication',
      '3. Click "Single Sender Verification"',
      '4. Add admin@morningmaghreb.com',
      '5. Check your email for verification link',
      '6. Click the verification link',
      '7. Test sending again'
    ],
    alternativeSolution: {
      description: 'Use a verified email temporarily',
      steps: [
        '1. Use your personal Gmail (if verified)',
        '2. Update SENDGRID_FROM_EMAIL in .env',
        '3. Restart the development server'
      ]
    }
  };

  res.status(200).json(troubleshooting);
} 