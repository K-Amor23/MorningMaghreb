import { NextApiRequest, NextApiResponse } from 'next';
import { createClient } from '@supabase/supabase-js';

// Initialize Supabase client
const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL!;
const supabaseServiceKey = process.env.SUPABASE_SERVICE_ROLE_KEY!;
const supabase = createClient(supabaseUrl, supabaseServiceKey);

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
    const { method } = req;

    try {
        switch (method) {
            case 'GET':
                return await getAlerts(req, res);
            case 'POST':
                return await createAlert(req, res);
            default:
                res.setHeader('Allow', ['GET', 'POST']);
                return res.status(405).json({ error: `Method ${method} Not Allowed` });
        }
    } catch (error) {
        console.error('Error in alerts endpoint:', error);
        return res.status(500).json({ error: 'Internal server error' });
    }
}

async function getAlerts(req: NextApiRequest, res: NextApiResponse) {
    const { user_id, status = 'all' } = req.query;

    if (!user_id || typeof user_id !== 'string') {
        return res.status(400).json({ error: 'User ID is required' });
    }

    try {
        let query = supabase
            .from('active_alerts_view')
            .select('*')
            .eq('user_id', user_id);

        // Filter by status
        if (status === 'active') {
            query = query.eq('is_triggered', false);
        } else if (status === 'triggered') {
            query = query.eq('is_triggered', true);
        }

        const { data: alerts, error: alertsError } = await query.order('created_at', { ascending: false });

        if (alertsError) {
            console.error('Error fetching alerts:', alertsError);
            return res.status(500).json({ error: 'Failed to fetch alerts' });
        }

        const response = {
            alerts: alerts || [],
            total_alerts: alerts?.length || 0,
            active_alerts: alerts?.filter((a: any) => !a.is_triggered).length || 0,
            triggered_alerts: alerts?.filter((a: any) => a.is_triggered).length || 0
        };

        res.status(200).json(response);

    } catch (error) {
        console.error('Error in getAlerts:', error);
        res.status(500).json({ error: 'Internal server error' });
    }
}

async function createAlert(req: NextApiRequest, res: NextApiResponse) {
    const {
        user_id,
        ticker,
        alert_type,
        condition_value,
        condition_operator = '=',
        notification_method = 'email',
        notification_url
    } = req.body;

    if (!user_id || !ticker || !alert_type || condition_value === undefined) {
        return res.status(400).json({
            error: 'User ID, ticker, alert type, and condition value are required'
        });
    }

    // Validate alert type
    const validAlertTypes = [
        'price_above', 'price_below', 'price_change_percent',
        'volume_above', 'rsi_above', 'rsi_below', 'macd_crossover',
        'moving_average_crossover', 'bollinger_breakout'
    ];

    if (!validAlertTypes.includes(alert_type)) {
        return res.status(400).json({
            error: `Invalid alert type. Must be one of: ${validAlertTypes.join(', ')}`
        });
    }

    // Validate condition operator
    const validOperators = ['=', '>', '<', '>=', '<='];
    if (!validOperators.includes(condition_operator)) {
        return res.status(400).json({
            error: `Invalid condition operator. Must be one of: ${validOperators.join(', ')}`
        });
    }

    // Validate notification method
    const validNotificationMethods = ['email', 'push', 'sms', 'webhook'];
    if (!validNotificationMethods.includes(notification_method)) {
        return res.status(400).json({
            error: `Invalid notification method. Must be one of: ${validNotificationMethods.join(', ')}`
        });
    }

    try {
        // Get company ID from ticker
        const { data: company, error: companyError } = await supabase
            .from('companies')
            .select('id')
            .eq('ticker', ticker.toUpperCase())
            .single();

        if (companyError || !company) {
            return res.status(404).json({ error: 'Company not found' });
        }

        // Create alert
        const { data: alert, error: alertError } = await supabase
            .from('alerts')
            .insert({
                user_id,
                company_id: company.id,
                ticker: ticker.toUpperCase(),
                alert_type,
                condition_value: parseFloat(condition_value),
                condition_operator,
                notification_method,
                notification_url
            })
            .select()
            .single();

        if (alertError) {
            console.error('Error creating alert:', alertError);
            return res.status(500).json({ error: 'Failed to create alert' });
        }

        const response = {
            alert,
            message: 'Alert created successfully'
        };

        res.status(201).json(response);

    } catch (error) {
        console.error('Error in createAlert:', error);
        res.status(500).json({ error: 'Internal server error' });
    }
} 