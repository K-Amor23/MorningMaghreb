import React, { useState } from 'react';

interface EmailTestData {
  to: string;
  subject: string;
  type: 'basic' | 'newsletter' | 'price-alert' | 'contest';
}

export default function SendGridTest() {
  const [emailData, setEmailData] = useState<EmailTestData>({
    to: '',
    subject: 'Test Email from Casablanca Insights',
    type: 'basic'
  });
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<{ success: boolean; message: string } | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setResult(null);

    try {
      const response = await fetch('/api/send-email', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(emailData),
      });

      const data = await response.json();

      if (response.ok) {
        setResult({ success: true, message: data.message });
      } else {
        setResult({ success: false, message: data.error || 'Failed to send email' });
      }
    } catch (error) {
      setResult({ success: false, message: 'Network error occurred' });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-md mx-auto p-6 bg-white rounded-lg shadow-md">
      <h2 className="text-2xl font-bold mb-4 text-gray-800">SendGrid Email Test</h2>
      
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label htmlFor="to" className="block text-sm font-medium text-gray-700 mb-1">
            To Email
          </label>
          <input
            type="email"
            id="to"
            value={emailData.to}
            onChange={(e) => setEmailData({ ...emailData, to: e.target.value })}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="recipient@example.com"
            required
          />
        </div>

        <div>
          <label htmlFor="subject" className="block text-sm font-medium text-gray-700 mb-1">
            Subject
          </label>
          <input
            type="text"
            id="subject"
            value={emailData.subject}
            onChange={(e) => setEmailData({ ...emailData, subject: e.target.value })}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            required
          />
        </div>

        <div>
          <label htmlFor="type" className="block text-sm font-medium text-gray-700 mb-1">
            Email Type
          </label>
          <select
            id="type"
            value={emailData.type}
            onChange={(e) => setEmailData({ ...emailData, type: e.target.value as any })}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="basic">Basic Email</option>
            <option value="newsletter">Morning Maghreb Newsletter</option>
            <option value="price-alert">Price Alert</option>
            <option value="contest">Contest Notification</option>
          </select>
        </div>

        <button
          type="submit"
          disabled={loading}
          className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {loading ? 'Sending...' : 'Send Test Email'}
        </button>
      </form>

      {result && (
        <div className={`mt-4 p-3 rounded-md ${
          result.success 
            ? 'bg-green-100 text-green-800 border border-green-200' 
            : 'bg-red-100 text-red-800 border border-red-200'
        }`}>
          <p className="font-medium">
            {result.success ? '✅ Success!' : '❌ Error!'}
          </p>
          <p className="text-sm">{result.message}</p>
        </div>
      )}

      <div className="mt-6 p-4 bg-gray-50 rounded-md">
        <h3 className="font-medium text-gray-800 mb-2">Test Email Types:</h3>
        <ul className="text-sm text-gray-600 space-y-1">
          <li>• <strong>Basic Email:</strong> Simple test email</li>
          <li>• <strong>Newsletter:</strong> Morning Maghreb format with market data</li>
          <li>• <strong>Price Alert:</strong> Stock price alert notification</li>
          <li>• <strong>Contest:</strong> Trading contest update notification</li>
        </ul>
      </div>
    </div>
  );
} 