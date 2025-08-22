import { useEffect, useState } from 'react';
import { createClient } from '@supabase/supabase-js';

export default function TestDBConnection() {
    const [status, setStatus] = useState<string>('Testing...');
    const [error, setError] = useState<string | null>(null);
    const [tables, setTables] = useState<string[]>([]);

    useEffect(() => {
        async function testConnection() {
            try {
                setStatus('Testing database connection...');

                const url = process.env.NEXT_PUBLIC_SUPABASE_URL
                const key = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY
                if (!url || !key) {
                    throw new Error('supabaseUrl is required.')
                }

                const supabase = createClient(url, key)

                // Test basic connection
                const { data, error } = await supabase
                    .from('profiles')
                    .select('*')
                    .limit(1);

                if (error) {
                    if (error.code === 'PGRST205') {
                        setError('Database schema not set up. Tables do not exist.');
                        setStatus('Schema not found');
                    } else {
                        setError(`Database error: ${error.message}`);
                        setStatus('Connection failed');
                    }
                } else {
                    setStatus('Database connection successful!');
                    setTables(['profiles']);
                }

            } catch (err) {
                setError(`Connection error: ${err instanceof Error ? err.message : 'Unknown error'}`);
                setStatus('Connection failed');
            }
        }

        testConnection();
    }, []);

    return (
        <div style={{ padding: '20px', fontFamily: 'Arial, sans-serif' }}>
            <h1>🔍 Morning Maghreb Database Test</h1>

            <div style={{ margin: '20px 0', padding: '15px', border: '1px solid #ccc', borderRadius: '5px' }}>
                <h3>Database Status: {status}</h3>

                {error && (
                    <div style={{ color: 'red', margin: '10px 0' }}>
                        <strong>Error:</strong> {error}
                    </div>
                )}

                {tables.length > 0 && (
                    <div style={{ color: 'green', margin: '10px 0' }}>
                        <strong>Available Tables:</strong> {tables.join(', ')}
                    </div>
                )}
            </div>

            <div style={{ margin: '20px 0' }}>
                <h3>Environment Variables:</h3>
                <ul>
                    <li><strong>SUPABASE_URL:</strong> {process.env.NEXT_PUBLIC_SUPABASE_URL ? '✅ Set' : '❌ Missing'}</li>
                    <li><strong>SUPABASE_ANON_KEY:</strong> {process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY ? '✅ Set' : '❌ Missing'}</li>
                </ul>
            </div>

            <div style={{ margin: '20px 0', padding: '15px', backgroundColor: '#f0f0f0', borderRadius: '5px' }}>
                <h3>Next Steps:</h3>
                <ol>
                    <li>If you see "Schema not found", you need to set up the database schema manually</li>
                    <li>Go to Supabase Dashboard → SQL Editor</li>
                    <li>Copy and paste the contents of <code>database/complete_supabase_schema.sql</code></li>
                    <li>Click "Run" to create all tables</li>
                    <li>Refresh this page to test again</li>
                </ol>
            </div>
        </div>
    );
} 