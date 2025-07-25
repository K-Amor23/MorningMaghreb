import { NextApiRequest, NextApiResponse } from 'next';
import { createClient } from '@supabase/supabase-js';

// Initialize Supabase client
const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL!;
const supabaseServiceKey = process.env.SUPABASE_SERVICE_ROLE_KEY!;
const supabase = createClient(supabaseUrl, supabaseServiceKey);

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
    if (req.method !== 'GET') {
        return res.status(405).json({ error: 'Method not allowed' });
    }

    const { id: ticker } = req.query;

    if (!ticker || typeof ticker !== 'string') {
        return res.status(400).json({ error: 'Ticker is required' });
    }

    try {
        // Get company information
        const { data: company, error: companyError } = await supabase
            .from('companies')
            .select('*')
            .eq('ticker', ticker.toUpperCase())
            .single();

        if (companyError || !company) {
            return res.status(404).json({ error: 'Company not found' });
        }

        // Get financial reports
        const { data: reports, error: reportsError } = await supabase
            .from('company_reports')
            .select('*')
            .eq('ticker', ticker.toUpperCase())
            .order('scraped_at', { ascending: false });

        if (reportsError) {
            console.error('Error fetching reports:', reportsError);
            return res.status(500).json({ error: 'Failed to fetch reports data' });
        }

        // Group reports by type
        const reportsByType = {
            annual_reports: reports?.filter(r => r.report_type === 'annual_report') || [],
            quarterly_reports: reports?.filter(r => r.report_type === 'quarterly_report') || [],
            financial_statements: reports?.filter(r => r.report_type === 'financial_statement') || [],
            earnings: reports?.filter(r => r.report_type === 'earnings') || [],
            other: reports?.filter(r => !['annual_report', 'quarterly_report', 'financial_statement', 'earnings'].includes(r.report_type)) || []
        };

        // Format reports for frontend
        const formattedReports = reports?.map(report => ({
            id: report.id,
            title: report.title,
            type: report.report_type,
            date: report.report_date,
            year: report.report_year,
            quarter: report.report_quarter,
            url: report.url,
            filename: report.filename,
            scrapedAt: report.scraped_at
        })) || [];

        const response = {
            company: {
                ticker: company.ticker,
                name: company.name,
                sector: company.sector,
                irUrl: company.ir_url
            },
            reports: {
                all: formattedReports,
                byType: reportsByType,
                totalCount: reports?.length || 0
            },
            metadata: {
                lastUpdated: new Date().toISOString(),
                sources: ['Supabase Database'],
                dataQuality: reports && reports.length > 0 ? 'real' : 'none'
            }
        };

        res.status(200).json(response);

    } catch (error) {
        console.error('Error in reports endpoint:', error);
        res.status(500).json({ error: 'Internal server error' });
    }
} 