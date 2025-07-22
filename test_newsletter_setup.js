#!/usr/bin/env node
/**
 * Test Newsletter Setup for Casablanca Insights
 * 
 * This script tests the Supabase configuration and newsletter functionality
 * to ensure everything is working properly.
 */

const { createClient } = require('@supabase/supabase-js')

// Get environment variables
const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY

console.log('🧪 Testing Newsletter Setup for Casablanca Insights')
console.log('=' * 60)

// Test 1: Environment Variables
console.log('\n📋 Test 1: Environment Variables')
console.log('-'.repeat(30))

if (!supabaseUrl || supabaseUrl === 'your_supabase_url') {
  console.log('❌ NEXT_PUBLIC_SUPABASE_URL not set or using default value')
  console.log('   Please set NEXT_PUBLIC_SUPABASE_URL in your .env.local file')
} else {
  console.log('✅ NEXT_PUBLIC_SUPABASE_URL is configured')
  console.log(`   URL: ${supabaseUrl}`)
}

if (!supabaseAnonKey || supabaseAnonKey === 'your_supabase_anon_key') {
  console.log('❌ NEXT_PUBLIC_SUPABASE_ANON_KEY not set or using default value')
  console.log('   Please set NEXT_PUBLIC_SUPABASE_ANON_KEY in your .env.local file')
} else {
  console.log('✅ NEXT_PUBLIC_SUPABASE_ANON_KEY is configured')
  console.log(`   Key: ${supabaseAnonKey.substring(0, 20)}...`)
}

// Test 2: Supabase Connection
console.log('\n🔌 Test 2: Supabase Connection')
console.log('-'.repeat(30))

if (!supabaseUrl || !supabaseAnonKey || 
    supabaseUrl === 'your_supabase_url' || 
    supabaseAnonKey === 'your_supabase_anon_key') {
  console.log('⚠️  Skipping connection test - environment variables not configured')
} else {
  try {
    const supabase = createClient(supabaseUrl, supabaseAnonKey)
    console.log('✅ Supabase client created successfully')
    
    // Test connection by querying a simple table
    const { data, error } = await supabase
      .from('newsletter_subscribers')
      .select('count')
      .limit(1)
    
    if (error) {
      console.log('❌ Database connection failed:')
      console.log(`   Error: ${error.message}`)
      
      if (error.message.includes('relation "newsletter_subscribers" does not exist')) {
        console.log('   💡 The newsletter_subscribers table does not exist')
        console.log('   Please run the database schema setup first')
      }
    } else {
      console.log('✅ Database connection successful')
      console.log('✅ newsletter_subscribers table exists')
    }
    
  } catch (error) {
    console.log('❌ Failed to create Supabase client:')
    console.log(`   Error: ${error.message}`)
  }
}

// Test 3: API Endpoint
console.log('\n🌐 Test 3: API Endpoint')
console.log('-'.repeat(30))

async function testNewsletterAPI() {
  try {
    const response = await fetch('http://localhost:3000/api/newsletter/signup', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        email: 'test@example.com',
        name: 'Test User',
        preferences: {
          language: 'en',
          delivery_time: '08:00',
          frequency: 'daily',
        }
      }),
    })

    const data = await response.json()
    
    if (response.ok) {
      console.log('✅ Newsletter API endpoint is working')
      console.log(`   Response: ${data.message}`)
    } else {
      console.log('❌ Newsletter API endpoint returned an error:')
      console.log(`   Status: ${response.status}`)
      console.log(`   Error: ${data.error}`)
    }
    
  } catch (error) {
    console.log('❌ Newsletter API endpoint test failed:')
    console.log(`   Error: ${error.message}`)
    console.log('   Make sure your Next.js development server is running on port 3000')
  }
}

// Only test API if we have a local server
testNewsletterAPI()

// Test 4: Database Schema
console.log('\n🗄️ Test 4: Database Schema')
console.log('-'.repeat(30))

if (!supabaseUrl || !supabaseAnonKey || 
    supabaseUrl === 'your_supabase_url' || 
    supabaseAnonKey === 'your_supabase_anon_key') {
  console.log('⚠️  Skipping schema test - environment variables not configured')
} else {
  try {
    const supabase = createClient(supabaseUrl, supabaseAnonKey)
    
    // Check if required tables exist
    const tables = [
      'newsletter_subscribers',
      'newsletter_campaigns', 
      'newsletter_logs',
      'profiles'
    ]
    
    for (const table of tables) {
      const { error } = await supabase
        .from(table)
        .select('count')
        .limit(1)
      
      if (error && error.message.includes('does not exist')) {
        console.log(`❌ Table '${table}' does not exist`)
      } else {
        console.log(`✅ Table '${table}' exists`)
      }
    }
    
  } catch (error) {
    console.log('❌ Schema test failed:')
    console.log(`   Error: ${error.message}`)
  }
}

// Summary and Next Steps
console.log('\n📋 Summary and Next Steps')
console.log('-'.repeat(30))

console.log('\n🔧 To fix newsletter subscription issues:')
console.log('1. Set up Supabase environment variables in .env.local:')
console.log('   NEXT_PUBLIC_SUPABASE_URL=your_supabase_url')
console.log('   NEXT_PUBLIC_SUPABASE_ANON_KEY=your_supabase_anon_key')
console.log('')
console.log('2. Run the database schema setup:')
console.log('   - Go to your Supabase dashboard')
console.log('   - Run the SQL from database/schema.sql')
console.log('   - Or use the setup script: setup_supabase_integration.sh')
console.log('')
console.log('3. Start your development server:')
console.log('   npm run dev')
console.log('')
console.log('4. Test the newsletter signup:')
console.log('   - Go to your website')
console.log('   - Try subscribing to the newsletter')
console.log('   - Check the browser console for errors')

console.log('\n🎉 Newsletter setup test completed!') 