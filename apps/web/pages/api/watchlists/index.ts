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
                return await getWatchlists(req, res);
            case 'POST':
                return await createWatchlist(req, res);
            default:
                res.setHeader('Allow', ['GET', 'POST']);
                return res.status(405).json({ error: `Method ${method} Not Allowed` });
        }
    } catch (error) {
        console.error('Error in watchlists endpoint:', error);
        return res.status(500).json({ error: 'Internal server error' });
    }
}

async function getWatchlists(req: NextApiRequest, res: NextApiResponse) {
    const { user_id } = req.query;

    if (!user_id || typeof user_id !== 'string') {
        return res.status(400).json({ error: 'User ID is required' });
    }

    try {
        // Get user's watchlists with items
        const { data: watchlists, error: watchlistsError } = await supabase
            .from('user_watchlists_view')
            .select('*')
            .eq('user_id', user_id);

        if (watchlistsError) {
            console.error('Error fetching watchlists:', watchlistsError);
            return res.status(500).json({ error: 'Failed to fetch watchlists' });
        }

        // Group watchlists by watchlist_id
        const groupedWatchlists = watchlists?.reduce((acc: any, item: any) => {
            const watchlistId = item.watchlist_id;

            if (!acc[watchlistId]) {
                acc[watchlistId] = {
                    id: watchlistId,
                    user_id: item.user_id,
                    name: item.watchlist_name,
                    description: item.description,
                    is_public: item.is_public,
                    created_at: item.watchlist_created_at,
                    items: []
                };
            }

            if (item.ticker) {
                acc[watchlistId].items.push({
                    id: item.item_id,
                    ticker: item.ticker,
                    company_name: item.company_name,
                    sector: item.sector,
                    market_cap_billion: item.market_cap_billion,
                    current_price: item.current_price,
                    price_change_percent: item.price_change_percent,
                    added_at: item.added_at,
                    notes: item.notes,
                    target_price: item.target_price
                });
            }

            return acc;
        }, {});

        const response = {
            watchlists: Object.values(groupedWatchlists || {}),
            total_watchlists: Object.keys(groupedWatchlists || {}).length,
            total_items: watchlists?.filter((item: any) => item.ticker).length || 0
        };

        res.status(200).json(response);

    } catch (error) {
        console.error('Error in getWatchlists:', error);
        res.status(500).json({ error: 'Internal server error' });
    }
}

async function createWatchlist(req: NextApiRequest, res: NextApiResponse) {
    const { user_id, name, description, is_public = false } = req.body;

    if (!user_id || !name) {
        return res.status(400).json({ error: 'User ID and name are required' });
    }

    try {
        // Create new watchlist
        const { data: watchlist, error: watchlistError } = await supabase
            .from('watchlists')
            .insert({
                user_id,
                name,
                description,
                is_public
            })
            .select()
            .single();

        if (watchlistError) {
            console.error('Error creating watchlist:', watchlistError);
            return res.status(500).json({ error: 'Failed to create watchlist' });
        }

        const response = {
            watchlist,
            message: 'Watchlist created successfully'
        };

        res.status(201).json(response);

    } catch (error) {
        console.error('Error in createWatchlist:', error);
        res.status(500).json({ error: 'Internal server error' });
    }
} 