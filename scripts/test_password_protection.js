#!/usr/bin/env node

/**
 * Test Password Protection on New Deployment
 * 
 * This script tests if password protection is working correctly
 * on the new deployment (DqXz4ByUb).
 */

const https = require('https');
const http = require('http');

// Configuration
const DEPLOYMENT_URL = 'https://web-7mi5kyepn-k-amor23s-projects.vercel.app';
const PRODUCTION_URL = 'https://morningmaghreb.com';
const TEST_PASSWORD = 'morningmaghreb2024';

// Colors for console output
const colors = {
  green: '\x1b[32m',
  red: '\x1b[31m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  reset: '\x1b[0m',
  bold: '\x1b[1m'
};

function log(message, color = 'reset') {
  console.log(`${colors[color]}${message}${colors.reset}`);
}

function makeRequest(url) {
  return new Promise((resolve, reject) => {
    const client = url.startsWith('https') ? https : http;
    
    const req = client.get(url, (res) => {
      let data = '';
      
      res.on('data', (chunk) => {
        data += chunk;
      });
      
      res.on('end', () => {
        resolve({
          statusCode: res.statusCode,
          headers: res.headers,
          data: data
        });
      });
    });
    
    req.on('error', (error) => {
      reject(error);
    });
    
    req.setTimeout(10000, () => {
      req.destroy();
      reject(new Error('Request timeout'));
    });
  });
}

async function testPasswordProtection() {
  log('🔒 Testing Password Protection on New Deployment', 'bold');
  log('=' * 50);
  
  const urls = [
    DEPLOYMENT_URL,
    PRODUCTION_URL
  ];
  
  for (const baseUrl of urls) {
    log(`\n🌐 Testing: ${baseUrl}`, 'blue');
    
    try {
      // Test 1: Check if site loads
      log('📋 Test 1: Checking if site loads...');
      const response = await makeRequest(baseUrl);
      
      if (response.statusCode === 200) {
        log('✅ Site loads successfully', 'green');
      } else {
        log(`❌ Site returned status ${response.statusCode}`, 'red');
        continue;
      }
      
      // Test 2: Check if password protection is present
      log('🔐 Test 2: Checking for password protection...');
      const hasPasswordProtection = response.data.includes('morningmaghreb_authenticated') ||
                                   response.data.includes('Enter password') ||
                                   response.data.includes('Password Protection');
      
      if (hasPasswordProtection) {
        log('✅ Password protection detected', 'green');
      } else {
        log('⚠️ Password protection not detected (may be disabled)', 'yellow');
      }
      
      // Test 3: Check for specific password protection elements
      log('🔍 Test 3: Checking for password protection elements...');
      const checks = [
        { name: 'Password input field', pattern: 'type="password"' },
        { name: 'Lock icon', pattern: 'LockClosedIcon' },
        { name: 'Morning Maghreb branding', pattern: 'Morning Maghreb' },
        { name: 'Session storage key', pattern: 'morningmaghreb_authenticated' }
      ];
      
      checks.forEach(check => {
        if (response.data.includes(check.pattern)) {
          log(`✅ ${check.name} found`, 'green');
        } else {
          log(`❌ ${check.name} not found`, 'red');
        }
      });
      
      // Test 4: Check environment variables
      log('⚙️ Test 4: Checking environment configuration...');
      const envChecks = [
        { name: 'Password protection enabled', pattern: 'NEXT_PUBLIC_ENABLE_PASSWORD_PROTECTION' },
        { name: 'Site password configured', pattern: 'NEXT_PUBLIC_SITE_PASSWORD' }
      ];
      
      envChecks.forEach(check => {
        if (response.data.includes(check.pattern)) {
          log(`✅ ${check.name}`, 'green');
        } else {
          log(`⚠️ ${check.name} not found in response`, 'yellow');
        }
      });
      
    } catch (error) {
      log(`❌ Error testing ${baseUrl}: ${error.message}`, 'red');
    }
  }
  
  log('\n📊 Summary:', 'bold');
  log('1. Check if the site loads without errors');
  log('2. Verify password protection is active');
  log('3. Test with correct password: morningmaghreb2024');
  log('4. Check admin panel for password management');
  
  log('\n🔧 Manual Testing Steps:', 'bold');
  log('1. Visit the site');
  log('2. Enter password: morningmaghreb2024');
  log('3. Verify access is granted');
  log('4. Check logout functionality');
  log('5. Test session persistence');
  
  log('\n🎯 Expected Behavior:', 'bold');
  log('• Site should show password protection screen');
  log('• Correct password should grant access');
  log('• Session should persist until logout');
  log('• Admin users can manage password protection');
}

// Run the test
testPasswordProtection().catch(console.error); 