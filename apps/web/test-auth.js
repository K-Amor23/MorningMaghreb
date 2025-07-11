// Simple test script to verify authentication and watchlist functionality
// Run this in the browser console on the dashboard page

console.log('🧪 Testing Casablanca Insights Authentication & Watchlist');

// Test 1: Check if Supabase is available
if (typeof window !== 'undefined' && window.supabase) {
  console.log('✅ Supabase client is available');
} else {
  console.log('❌ Supabase client not found');
}

// Test 2: Check if user is authenticated
async function testAuth() {
  try {
    const { data: { session } } = await supabase.auth.getSession();
    if (session) {
      console.log('✅ User is authenticated:', session.user.email);
      return session.user.id;
    } else {
      console.log('❌ No active session found');
      return null;
    }
  } catch (error) {
    console.log('❌ Auth test failed:', error);
    return null;
  }
}

// Test 3: Test watchlist operations
async function testWatchlist(userId) {
  if (!userId) {
    console.log('❌ Cannot test watchlist without user ID');
    return;
  }

  try {
    // Test adding a ticker
    const { data: addData, error: addError } = await supabase
      .from('watchlists')
      .insert([
        {
          user_id: userId,
          ticker: 'TEST',
        }
      ]);

    if (addError) {
      console.log('❌ Failed to add ticker:', addError);
    } else {
      console.log('✅ Successfully added test ticker');
    }

    // Test fetching watchlist
    const { data: fetchData, error: fetchError } = await supabase
      .from('watchlists')
      .select('*')
      .eq('user_id', userId);

    if (fetchError) {
      console.log('❌ Failed to fetch watchlist:', fetchError);
    } else {
      console.log('✅ Successfully fetched watchlist:', fetchData);
    }

    // Test removing test ticker
    const { error: deleteError } = await supabase
      .from('watchlists')
      .delete()
      .eq('user_id', userId)
      .eq('ticker', 'TEST');

    if (deleteError) {
      console.log('❌ Failed to remove test ticker:', deleteError);
    } else {
      console.log('✅ Successfully removed test ticker');
    }

  } catch (error) {
    console.log('❌ Watchlist test failed:', error);
  }
}

// Run tests
async function runTests() {
  console.log('🚀 Starting tests...');
  const userId = await testAuth();
  await testWatchlist(userId);
  console.log('🏁 Tests completed!');
}

// Export for manual testing
window.testCasablancaInsights = runTests; 