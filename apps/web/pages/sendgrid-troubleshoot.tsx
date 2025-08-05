import { useState, useEffect } from 'react';
import { useRouter } from 'next/router';

interface TroubleshootingData {
  currentConfig: {
    apiKey: string;
    fromEmail: string;
    apiKeyLength: number;
  };
  commonIssues: Array<{
    issue: string;
    cause: string;
    solution: string;
  }>;
  stepsToFix: string[];
  alternativeSolution: {
    description: string;
    steps: string[];
  };
}

export default function SendGridTroubleshoot() {
  const [data, setData] = useState<TroubleshootingData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();

  useEffect(() => {
    fetch('/api/sendgrid-troubleshoot')
      .then(res => res.json())
      .then(setData)
      .catch(err => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="p-8">Loading troubleshooting data...</div>;
  if (error) return <div className="p-8 text-red-600">Error: {error}</div>;
  if (!data) return <div className="p-8">No data available</div>;

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-4xl mx-auto px-4">
        <div className="bg-white rounded-lg shadow-lg p-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-6">
            SendGrid Troubleshooting Guide
          </h1>

          {/* Current Configuration */}
          <div className="mb-8">
            <h2 className="text-xl font-semibold text-gray-800 mb-4">
              Current Configuration
            </h2>
            <div className="bg-gray-50 p-4 rounded-lg">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <span className="font-medium">API Key:</span> {data.currentConfig.apiKey}
                </div>
                <div>
                  <span className="font-medium">From Email:</span> {data.currentConfig.fromEmail}
                </div>
                <div>
                  <span className="font-medium">API Key Length:</span> {data.currentConfig.apiKeyLength}
                </div>
              </div>
            </div>
          </div>

          {/* Common Issues */}
          <div className="mb-8">
            <h2 className="text-xl font-semibold text-gray-800 mb-4">
              Common Issues & Solutions
            </h2>
            <div className="space-y-4">
              {data.commonIssues.map((issue, index) => (
                <div key={index} className="border border-gray-200 rounded-lg p-4">
                  <h3 className="font-semibold text-red-600 mb-2">{issue.issue}</h3>
                  <p className="text-gray-600 mb-2"><strong>Cause:</strong> {issue.cause}</p>
                  <p className="text-gray-800"><strong>Solution:</strong> {issue.solution}</p>
                </div>
              ))}
            </div>
          </div>

          {/* Steps to Fix */}
          <div className="mb-8">
            <h2 className="text-xl font-semibold text-gray-800 mb-4">
              Steps to Fix the Issue
            </h2>
            <div className="bg-blue-50 p-4 rounded-lg">
              <ol className="list-decimal list-inside space-y-2">
                {data.stepsToFix.map((step, index) => (
                  <li key={index} className="text-gray-800">{step}</li>
                ))}
              </ol>
            </div>
          </div>

          {/* Alternative Solution */}
          <div className="mb-8">
            <h2 className="text-xl font-semibold text-gray-800 mb-4">
              Alternative Solution
            </h2>
            <div className="bg-green-50 p-4 rounded-lg">
              <p className="font-medium text-gray-800 mb-3">{data.alternativeSolution.description}</p>
              <ol className="list-decimal list-inside space-y-2">
                {data.alternativeSolution.steps.map((step, index) => (
                  <li key={index} className="text-gray-800">{step}</li>
                ))}
              </ol>
            </div>
          </div>

          {/* Action Buttons */}
          <div className="flex space-x-4">
            <button
              onClick={() => router.push('/test-sendgrid')}
              className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 transition-colors"
            >
              Test SendGrid Again
            </button>
            <button
              onClick={() => router.push('/')}
              className="bg-gray-600 text-white px-6 py-2 rounded-lg hover:bg-gray-700 transition-colors"
            >
              Back to Home
            </button>
          </div>
        </div>
      </div>
    </div>
  );
} 