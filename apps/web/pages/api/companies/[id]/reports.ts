import { NextApiRequest, NextApiResponse } from 'next';
import { createClient } from '@supabase/supabase-js';

// Initialize Supabase client
const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL!;
const supabaseServiceKey = process.env.SUPABASE_SERVICE_ROLE_KEY!;
const supabase = createClient(supabaseUrl, supabaseServiceKey);

// Mock data for when database tables don't exist
const getMockReportsData = (ticker: string) => {
    const mockReports = [
        {
            id: '1',
            title: `${ticker.toUpperCase()} Annual Report 2023`,
            type: 'annual_report',
            date: '2023-12-31',
            year: '2023',
            quarter: null,
            url: '#',
            filename: `${ticker}_annual_2023.pdf`,
            scrapedAt: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString()
        },
        {
            id: '2',
            title: `${ticker.toUpperCase()} Q3 2023 Earnings Report`,
            type: 'earnings',
            date: '2023-10-15',
            year: '2023',
            quarter: 'Q3',
            url: '#',
            filename: `${ticker}_earnings_q3_2023.pdf`,
            scrapedAt: new Date(Date.now() - 60 * 24 * 60 * 60 * 1000).toISOString()
        },
        {
            id: '3',
            title: `${ticker.toUpperCase()} Q2 2023 Financial Statement`,
            type: 'financial_statement',
            date: '2023-07-15',
            year: '2023',
            quarter: 'Q2',
            url: '#',
            filename: `${ticker}_financial_q2_2023.pdf`,
            scrapedAt: new Date(Date.now() - 90 * 24 * 60 * 60 * 1000).toISOString()
        },
        {
            id: '4',
            title: `${ticker.toUpperCase()} Q1 2023 Quarterly Report`,
            type: 'quarterly_report',
            date: '2023-04-15',
            year: '2023',
            quarter: 'Q1',
            url: '#',
            filename: `${ticker}_quarterly_q1_2023.pdf`,
            scrapedAt: new Date(Date.now() - 120 * 24 * 60 * 60 * 1000).toISOString()
        },
        {
            id: '5',
            title: `${ticker.toUpperCase()} Annual Report 2022`,
            type: 'annual_report',
            date: '2022-12-31',
            year: '2022',
            quarter: null,
            url: '#',
            filename: `${ticker}_annual_2022.pdf`,
            scrapedAt: new Date(Date.now() - 150 * 24 * 60 * 60 * 1000).toISOString()
        }
    ];

    // Group reports by type
    const reportsByType = {
        annual_reports: mockReports.filter(r => r.type === 'annual_report'),
        quarterly_reports: mockReports.filter(r => r.type === 'quarterly_report'),
        financial_statements: mockReports.filter(r => r.type === 'financial_statement'),
        earnings: mockReports.filter(r => r.type === 'earnings'),
        other: mockReports.filter(r => !['annual_report', 'quarterly_report', 'financial_statement', 'earnings'].includes(r.type))
    };

    return {
        company: {
            ticker: ticker.toUpperCase(),
            name: `${ticker.toUpperCase()} Company`,
            sector: 'Technology',
            irUrl: '#'
        },
        reports: {
            all: mockReports,
            byType: reportsByType,
            totalCount: mockReports.length
        },
        metadata: {
            lastUpdated: new Date().toISOString(),
            sources: ['Mock Data'],
            dataQuality: 'mock'
        }
    };
};

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
    if (req.method !== 'GET') {
        return res.status(405).json({ error: 'Method not allowed' });
    }

    const { id: ticker } = req.query;

    if (!ticker || typeof ticker !== 'string') {
        return res.status(400).json({ error: 'Ticker is required' });
    }

    try {
        // Try to get data from database
        let company = null;
        let reports = null;

        try {
            // Get company information
            const { data: companyData, error: companyError } = await supabase
                .from('companies')
                .select('*')
                .eq('ticker', ticker.toUpperCase())
                .single();

            if (!companyError && companyData) {
                company = companyData;
            }

            // Get financial reports
            const { data: reportsData, error: reportsError } = await supabase
                .from('company_reports')
                .select('*')
                .eq('ticker', ticker.toUpperCase())
                .order('scraped_at', { ascending: false });

            if (!reportsError && reportsData) {
                reports = reportsData;
            }

        } catch (dbError) {
            console.log(`Database tables not available for ${ticker}, using mock data`);
        }

        // If we have real data, use it; otherwise use mock data
        if (company && reports) {
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
                    dataQuality: 'real'
                }
            };

            res.status(200).json(response);
        } else {
            // Use mock data when database tables don't exist
            const mockData = getMockReportsData(ticker);
            res.status(200).json(mockData);
        }

    } catch (error) {
        console.error('Error in reports endpoint:', error);
        // Fallback to mock data on any error
        const mockData = getMockReportsData(ticker);
        res.status(200).json(mockData);
    }
} 