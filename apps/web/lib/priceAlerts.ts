import { supabase } from './supabase'

export interface PriceAlert {
  id: string
  user_id: string
  symbol: string
  target_price: number
  condition: 'above' | 'below'
  is_active: boolean
  created_at: string
  triggered_at?: string
}

export interface CreatePriceAlertData {
  symbol: string
  target_price: number
  condition: 'above' | 'below'
}

// Create a new price alert
export async function createPriceAlert(data: CreatePriceAlertData): Promise<PriceAlert | null> {
  try {
    if (!supabase) return null

    const { data: { user } } = await supabase.auth.getUser()
    if (!user) throw new Error('User not authenticated')

    const { data: alert, error } = await supabase
      .from('price_alerts')
      .insert([
        {
          user_id: user.id,
          symbol: data.symbol,
          target_price: data.target_price,
          condition: data.condition,
          is_active: true
        }
      ])
      .select()
      .single()

    if (error) throw error
    return alert
  } catch (error) {
    console.error('Error creating price alert:', error)
    return null
  }
}

// Get user's price alerts
export async function getUserPriceAlerts(): Promise<PriceAlert[]> {
  try {
    if (!supabase) return []

    const { data: { user } } = await supabase.auth.getUser()
    if (!user) return []

    const { data: alerts, error } = await supabase
      .from('price_alerts')
      .select('*')
      .eq('user_id', user.id)
      .order('created_at', { ascending: false })

    if (error) throw error
    return alerts || []
  } catch (error) {
    console.error('Error fetching price alerts:', error)
    return []
  }
}

// Delete a price alert
export async function deletePriceAlert(alertId: string): Promise<boolean> {
  try {
    if (!supabase) return false

    const { error } = await supabase
      .from('price_alerts')
      .delete()
      .eq('id', alertId)

    if (error) throw error
    return true
  } catch (error) {
    console.error('Error deleting price alert:', error)
    return false
  }
}

// Update a price alert
export async function updatePriceAlert(
  alertId: string, 
  updates: Partial<PriceAlert>
): Promise<PriceAlert | null> {
  try {
    if (!supabase) return null

    const { data: alert, error } = await supabase
      .from('price_alerts')
      .update(updates)
      .eq('id', alertId)
      .select()
      .single()

    if (error) throw error
    return alert
  } catch (error) {
    console.error('Error updating price alert:', error)
    return null
  }
}

// Check if price alerts should be triggered
export async function checkPriceAlerts(currentPrice: number, symbol: string): Promise<void> {
  try {
    if (!supabase) return

    const { data: alerts, error } = await supabase
      .from('price_alerts')
      .select('*')
      .eq('symbol', symbol)
      .eq('is_active', true)

    if (error) throw error

    for (const alert of alerts || []) {
      let shouldTrigger = false

      if (alert.condition === 'above' && currentPrice >= alert.target_price) {
        shouldTrigger = true
      } else if (alert.condition === 'below' && currentPrice <= alert.target_price) {
        shouldTrigger = true
      }

      if (shouldTrigger) {
        // Mark alert as triggered
        await updatePriceAlert(alert.id, {
          is_active: false,
          triggered_at: new Date().toISOString()
        })

        // Here you would typically send a notification
        console.log(`Price alert triggered for ${symbol}: ${alert.condition} ${alert.target_price}`)
      }
    }
  } catch (error) {
    console.error('Error checking price alerts:', error)
  }
} 