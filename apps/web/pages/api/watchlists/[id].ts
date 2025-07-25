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
                return await getWatchlist(req, res, watchlistId);
            case 'PUT':
                return await updateWatchlist(req, res, watchlistId);
            case 'DELETE':
                return await deleteWatchlist(req, res, watchlistId);
            default:
                res.setHeader('Allow', ['GET', 'PUT', 'DELETE']);
                return res.status(405).json({ error: `Method ${method} Not Allowed` });
        }
    } catch (error) {
        console.error('Error in watchlist endpoint:', error);
        return res.status(500).json({ error: 'Internal server error' });
    }
}

async function getWatchlist(req: NextApiRequest, res: NextApiResponse, watchlistId: string) {
    const { user_id } = req.query;

    if (!user_id || typeof user_id !== 'string') {
        return res.status(400).json({ error: 'User ID is required' });
    }

    try {
        // Get watchlist details
        const { data: watchlist, error: watchlistError } = await supabase
            .from('watchlists')
            .select('*')
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
            watchlist: {
                ...watchlist,
                items: formattedItems,
                item_count: formattedItems.length
            }
        };

        res.status(200).json(response);

    } catch (error) {
        console.error('Error in getWatchlist:', error);
        res.status(500).json({ error: 'Internal server error' });
    }
}

async function updateWatchlist(req: NextApiRequest, res: NextApiResponse, watchlistId: string) {
    const { user_id, name, description, is_public } = req.body;

    if (!user_id) {
        return res.status(400).json({ error: 'User ID is required' });
    }

    try {
        // Update watchlist
        const updateData: any = {};
        if (name !== undefined) updateData.name = name;
        if (description !== undefined) updateData.description = description;
        if (is_public !== undefined) updateData.is_public = is_public;

        const { data: watchlist, error: watchlistError } = await supabase
            .from('watchlists')
            .update(updateData)
            .eq('id', watchlistId)
            .eq('user_id', user_id)
            .select()
            .single();

        if (watchlistError || !watchlist) {
            return res.status(404).json({ error: 'Watchlist not found' });
        }

        const response = {
            watchlist,
            message: 'Watchlist updated successfully'
        };

        res.status(200).json(response);

    } catch (error) {
        console.error('Error in updateWatchlist:', error);
        res.status(500).json({ error: 'Internal server error' });
    }
}

async function deleteWatchlist(req: NextApiRequest, res: NextApiResponse, watchlistId: string) {
    const { user_id } = req.query;

    if (!user_id || typeof user_id !== 'string') {
        return res.status(400).json({ error: 'User ID is required' });
    }

    try {
        // Delete watchlist (cascade will delete items)
        const { error: deleteError } = await supabase
            .from('watchlists')
            .delete()
            .eq('id', watchlistId)
            .eq('user_id', user_id);

        if (deleteError) {
            console.error('Error deleting watchlist:', deleteError);
            return res.status(500).json({ error: 'Failed to delete watchlist' });
        }

        const response = {
            message: 'Watchlist deleted successfully'
        };

        res.status(200).json(response);

    } catch (error) {
        console.error('Error in deleteWatchlist:', error);
        res.status(500).json({ error: 'Internal server error' });
    }
} 