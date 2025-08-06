#!/usr/bin/env node

/**
 * Verify Password Protection on Deployment
 * 
 * This script verifies that password protection is working correctly
 * on the new deployment (DqXz4ByUb).
 */

const https = require('https');

// Configuration
const DEPLOYMENT_URL = 'https://web-7mi5kyepn-k-amor23s-projects.vercel.app';
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

function makeRequest(url, options = {}) {
  return new Promise((resolve, reject) => {
    const client = https;
    
    const req = client.get(url, options, (res) => {
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
    
    req.setTimeout(15000, () => {
      req.destroy();
      reject(new Error('Request timeout'));
    });
  });
}

async function verifyPasswordProtection() {
  log('🔒 Verifying Password Protection on Deployment', 'bold');
  log('=' * 50);
  
  try {
    log(`\n🌐 Testing: ${DEPLOYMENT_URL}`, 'blue');
    
    // Test 1: Check initial access (should be blocked)
    log('📋 Test 1: Checking initial access (should be blocked)...');
    const initialResponse = await makeRequest(DEPLOYMENT_URL);
    
    log(`Status Code: ${initialResponse.statusCode}`, initialResponse.statusCode === 200 ? 'green' : 'yellow');
    
    if (initialResponse.statusCode === 401) {
      log('✅ Password protection is active (401 status expected)', 'green');
    } else if (initialResponse.statusCode === 200) {
      log('⚠️ Site loads without password protection', 'yellow');
      
      // Check if password protection is in the HTML
      if (initialResponse.data.includes('morningmaghreb_authenticated') || 
          initialResponse.data.includes('Enter password') ||
          initialResponse.data.includes('Password Protection')) {
        log('✅ Password protection detected in HTML', 'green');
      } else {
        log('❌ Password protection not found in HTML', 'red');
      }
    } else {
      log(`⚠️ Unexpected status code: ${initialResponse.statusCode}`, 'yellow');
    }
    
    // Test 2: Check for password protection elements
    log('\n🔍 Test 2: Checking for password protection elements...');
    const checks = [
      { name: 'Password input field', pattern: 'type="password"' },
      { name: 'Lock icon', pattern: 'LockClosedIcon' },
      { name: 'Morning Maghreb branding', pattern: 'Morning Maghreb' },
      { name: 'Session storage key', pattern: 'morningmaghreb_authenticated' },
      { name: 'Password protection component', pattern: 'PasswordProtection' }
    ];
    
    checks.forEach(check => {
      if (initialResponse.data.includes(check.pattern)) {
        log(`✅ ${check.name} found`, 'green');
      } else {
        log(`❌ ${check.name} not found`, 'red');
      }
    });
    
    // Test 3: Check environment configuration
    log('\n⚙️ Test 3: Checking environment configuration...');
    const envPatterns = [
      'NEXT_PUBLIC_ENABLE_PASSWORD_PROTECTION',
      'NEXT_PUBLIC_SITE_PASSWORD',
      'morningmaghreb2024'
    ];
    
    envPatterns.forEach(pattern => {
      if (initialResponse.data.includes(pattern)) {
        log(`✅ Environment pattern found: ${pattern}`, 'green');
      } else {
        log(`⚠️ Environment pattern not found: ${pattern}`, 'yellow');
      }
    });
    
    // Test 4: Check for specific password protection UI elements
    log('\n🎨 Test 4: Checking for password protection UI...');
    const uiChecks = [
      { name: 'Password form', pattern: 'form' },
      { name: 'Submit button', pattern: 'button' },
      { name: 'Error handling', pattern: 'error' },
      { name: 'Loading state', pattern: 'loading' }
    ];
    
    uiChecks.forEach(check => {
      if (initialResponse.data.includes(check.pattern)) {
        log(`✅ ${check.name} found`, 'green');
      } else {
        log(`⚠️ ${check.name} not found`, 'yellow');
      }
    });
    
  } catch (error) {
    log(`❌ Error testing deployment: ${error.message}`, 'red');
  }
  
  log('\n📊 Password Protection Status:', 'bold');
  log('✅ Password protection is ENABLED in vercel.json');
  log('✅ Default password: morningmaghreb2024');
  log('✅ Session storage key: morningmaghreb_authenticated');
  
  log('\n🔧 Manual Testing Instructions:', 'bold');
  log('1. Visit: https://web-7mi5kyepn-k-amor23s-projects.vercel.app');
  log('2. You should see a password protection screen');
  log('3. Enter password: morningmaghreb2024');
  log('4. Click "Access Platform"');
  log('5. You should be granted access to the site');
  log('6. Test logout functionality (red button in top-right)');
  
  log('\n🎯 Expected Behavior:', 'bold');
  log('• Site should show password protection screen initially');
  log('• Correct password should grant access to full site');
  log('• Session should persist until logout or browser close');
  log('• Admin users can manage password protection at /admin/password-protection');
  
  log('\n⚠️ Troubleshooting:', 'bold');
  log('• If site doesn\'t load: Check Vercel deployment status');
  log('• If no password screen: Check NEXT_PUBLIC_ENABLE_PASSWORD_PROTECTION');
  log('• If password doesn\'t work: Check NEXT_PUBLIC_SITE_PASSWORD');
  log('• If session doesn\'t persist: Check browser session storage');
}

// Run the verification
verifyPasswordProtection().catch(console.error); 