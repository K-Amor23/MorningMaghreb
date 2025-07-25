import { NextApiRequest, NextApiResponse } from 'next';
import { createClient } from '@supabase/supabase-js';

// Initialize Supabase client
const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL!;
const supabaseServiceKey = process.env.SUPABASE_SERVICE_ROLE_KEY!;
const supabase = createClient(supabaseUrl, supabaseServiceKey);

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
    const { method } = req;
    const { id: watchlistId } = req.query;

    if (!watchlistId || typeof watchlistId !== 'string') {
        return res.status(400).json({ error: 'Watchlist ID is required' });
    }

    try {
        switch (method) {
            case 'GET':
                return await getWatchlistItems(req, res, watchlistId);
            case 'POST':
                return await addWatchlistItem(req, res, watchlistId);
            default:
                res.setHeader('Allow', ['GET', 'POST']);
                return res.status(405).json({ error: `Method ${method} Not Allowed` });
        }
    } catch (error) {
        console.error('Error in watchlist items endpoint:', error);
        return res.status(500).json({ error: 'Internal server error' });
    }
}

async function getWatchlistItems(req: NextApiRequest, res: NextApiResponse, watchlistId: string) {
    const { user_id } = req.query;

    if (!user_id || typeof user_id !== 'string') {
        return res.status(400).json({ error: 'User ID is required' });
    }

    try {
        // Verify user owns the watchlist
        const { data: watchlist, error: watchlistError } = await supabase
            .from('watchlists')
            .select('id')
            .eq('id', watchlistId)
            .eq('user_id', user_id)
            .single();

        if (watchlistError || !watchlist) {
            return res.status(404).json({ error: 'Watchlist not found' });
        }

        // Get watchlist items
        const { data: items, error: itemsError } = await supabase
            .from('user_watchlists_view')
            .select('*')
            .eq('watchlist_id', watchlistId)
            .not('ticker', 'is', null);

        if (itemsError) {
            console.error('Error fetching watchlist items:', itemsError);
            return res.status(500).json({ error: 'Failed to fetch watchlist items' });
        }

        const formattedItems = items?.map((item: any) => ({
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
        })) || [];

        const response = {
            items: formattedItems,
            total_items: formattedItems.length
        };

        res.status(200).json(response);

    } catch (error) {
        console.error('Error in getWatchlistItems:', error);
        res.status(500).json({ error: 'Internal server error' });
    }
}

async function addWatchlistItem(req: NextApiRequest, res: NextApiResponse, watchlistId: string) {
    const { user_id, ticker, notes, target_price } = req.body;

    if (!user_id || !ticker) {
        return res.status(400).json({ error: 'User ID and ticker are required' });
    }

    try {
        // Verify user owns the watchlist
        const { data: watchlist, error: watchlistError } = await supabase
            .from('watchlists')
            .select('id')
            .eq('id', watchlistId)
            .eq('user_id', user_id)
            .single();

        if (watchlistError || !watchlist) {
            return res.status(404).json({ error: 'Watchlist not found' });
        }

        // Get company ID from ticker
        const { data: company, error: companyError } = await supabase
            .from('companies')
            .select('id')
            .eq('ticker', ticker.toUpperCase())
            .single();

        if (companyError || !company) {
            return res.status(404).json({ error: 'Company not found' });
        }

        // Check if item already exists in watchlist
        const { data: existingItem, error: existingError } = await supabase
            .from('watchlist_items')
            .select('id')
            .eq('watchlist_id', watchlistId)
            .eq('company_id', company.id)
            .single();

        if (existingItem) {
            return res.status(409).json({ error: 'Company already in watchlist' });
        }

        // Add item to watchlist
        const { data: item, error: itemError } = await supabase
            .from('watchlist_items')
            .insert({
                watchlist_id: watchlistId,
                company_id: company.id,
                ticker: ticker.toUpperCase(),
                notes,
                target_price
            })
            .select()
            .single();

        if (itemError) {
            console.error('Error adding watchlist item:', itemError);
            return res.status(500).json({ error: 'Failed to add item to watchlist' });
        }

        const response = {
            item,
            message: 'Item added to watchlist successfully'
        };

        res.status(201).json(response);

    } catch (error) {
        console.error('Error in addWatchlistItem:', error);
        res.status(500).json({ error: 'Internal server error' });
    }
} 