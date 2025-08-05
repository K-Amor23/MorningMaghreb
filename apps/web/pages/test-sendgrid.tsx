import React from 'react';
import Head from 'next/head';
import SendGridTest from '../components/SendGridTest';

export default function TestSendGridPage() {
  return (
    <>
      <Head>
        <title>SendGrid Test - Casablanca Insights</title>
        <meta name="description" content="Test SendGrid email integration" />
      </Head>
      
      <div className="min-h-screen bg-gray-50 py-8">
        <div className="max-w-4xl mx-auto px-4">
          <div className="text-center mb-8">
            <h1 className="text-3xl font-bold text-gray-900 mb-2">
              SendGrid Integration Test
            </h1>
            <p className="text-gray-600">
              Test the SendGrid email functionality for Casablanca Insights
            </p>
          </div>
          
          <SendGridTest />
          
          <div className="mt-8 p-6 bg-white rounded-lg shadow-md">
            <h2 className="text-xl font-semibold text-gray-800 mb-4">
              Integration Details
            </h2>
            <div className="space-y-3 text-sm text-gray-600">
              <p><strong>API Key:</strong> Configured in environment variables</p>
              <p><strong>From Email:</strong> Set to default or configured email</p>
              <p><strong>Package:</strong> @sendgrid/mail installed</p>
              <p><strong>Service:</strong> SendGridService class implemented</p>
              <p><strong>Endpoints:</strong> /api/send-email for testing</p>
            </div>
          </div>
        </div>
      </div>
    </>
  );
} 