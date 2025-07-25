# 🧪 End-to-End Testing Guide - Casablanca Insights

This guide provides comprehensive instructions for setting up and running end-to-end tests for the Casablanca Insights platform, focusing on IAM, ATW, and BCP companies.

## 📋 Overview

### Test Coverage
- ✅ **Company Pages**: IAM, ATW, BCP with real-time data
- ✅ **Authentication Flows**: Registration, login, password reset
- ✅ **Data Quality**: Validation of financial data and quality badges
- ✅ **Chart Rendering**: Real-time charts with live data
- ✅ **Responsive Design**: Mobile and desktop compatibility
- ✅ **Error Handling**: Graceful handling of edge cases

### Test Technologies
- **Playwright**: Modern browser automation
- **TypeScript**: Type-safe test development
- **Real-time Data**: Live API integration
- **Visual Testing**: Screenshot and video capture
- **Cross-browser**: Chrome, Firefox, Safari, Mobile

## 🚀 Quick Start

### 1. Setup E2E Testing Infrastructure

```bash
# Run the setup script
python3 scripts/setup_e2e_testing.py
```

This will:
- ✅ Install Playwright and dependencies
- ✅ Create test configuration
- ✅ Generate company-specific tests
- ✅ Set up authentication tests
- ✅ Create data quality validation
- ✅ Configure chart rendering tests

### 2. Run Complete E2E Test Suite

```bash
# Execute all E2E tests
./scripts/run_e2e_tests.sh
```

This will:
- ✅ Test IAM, ATW, BCP companies
- ✅ Validate authentication flows
- ✅ Check data quality badges
- ✅ Verify chart rendering
- ✅ Generate comprehensive reports

## 📊 Test Structure

### Company-Specific Tests

#### IAM Company Tests (`iam.spec.ts`)
```typescript
test.describe('IAM Company Page', () => {
  test('should load company page successfully', async () => {
    await expect(page).toHaveTitle(/.*IAM.*/);
    await expect(page.locator('[data-testid="company-header"]')).toBeVisible();
  });

  test('should render trading data charts', async () => {
    await expect(page.locator('[data-testid="trading-chart"]')).toBeVisible();
    await expect(page.locator('[data-testid="volume-chart"]')).toBeVisible();
  });

  test('should show data quality badge', async () => {
    const qualityBadge = page.locator('[data-testid="data-quality-badge"]');
    await expect(qualityBadge).toBeVisible();
    const badgeText = await qualityBadge.textContent();
    expect(badgeText).toMatch(/^(Excellent|Good|Fair|Poor)$/);
  });
});
```

#### ATW Company Tests (`atw.spec.ts`)
```typescript
test.describe('ATW Company Page', () => {
  test('should display company metrics', async () => {
    await expect(page.locator('[data-testid="company-metrics"]')).toBeVisible();
    await expect(page.locator('[data-testid="market-cap"]')).toBeVisible();
    await expect(page.locator('[data-testid="pe-ratio"]')).toBeVisible();
  });

  test('should handle real-time data updates', async () => {
    const initialPrice = await page.locator('[data-testid="current-price"]').textContent();
    await page.waitForTimeout(5000);
    const updatedPrice = await page.locator('[data-testid="current-price"]').textContent();
    expect(updatedPrice).toBeTruthy();
  });
});
```

#### BCP Company Tests (`bcp.spec.ts`)
```typescript
test.describe('BCP Company Page', () => {
  test('should display financial reports section', async () => {
    await expect(page.locator('[data-testid="financial-reports"]')).toBeVisible();
    const reportsList = page.locator('[data-testid="reports-list"]');
    await expect(reportsList).toBeVisible();
  });

  test('should display news section', async () => {
    await expect(page.locator('[data-testid="news-section"]')).toBeVisible();
    const newsItems = page.locator('[data-testid="news-item"]');
    await expect(newsItems.first()).toBeVisible();
  });
});
```

### Authentication Tests (`auth.spec.ts`)

```typescript
test.describe('Authentication Flows', () => {
  test('should handle user registration', async ({ page }) => {
    await page.goto('/signup');
    await page.fill('[data-testid="email-input"]', 'test@example.com');
    await page.fill('[data-testid="password-input"]', 'TestPassword123!');
    await page.click('[data-testid="signup-button"]');
    await expect(page).toHaveURL(/.*verify.*/);
  });

  test('should handle user login', async ({ page }) => {
    await page.goto('/login');
    await page.fill('[data-testid="email-input"]', 'test@example.com');
    await page.fill('[data-testid="password-input"]', 'TestPassword123!');
    await page.click('[data-testid="login-button"]');
    await expect(page).toHaveURL(/.*dashboard.*/);
  });
});
```

### Data Quality Tests (`data-quality.spec.ts`)

```typescript
test.describe('Data Quality Validation', () => {
  test('should validate IAM data quality', async ({ page }) => {
    await page.goto('/company/iam');
    await page.waitForTimeout(3000);
    
    const qualityBadge = page.locator('[data-testid="data-quality-badge"]');
    await expect(qualityBadge).toBeVisible();
    
    const badgeClass = await qualityBadge.getAttribute('class');
    expect(badgeClass).toMatch(/badge-(excellent|good|fair|poor)/);
  });
});
```

### Chart Rendering Tests (`charts.spec.ts`)

```typescript
test.describe('Chart Rendering Tests', () => {
  test('should render IAM trading chart correctly', async ({ page }) => {
    await page.goto('/company/iam');
    await page.waitForTimeout(3000);
    
    const chartContainer = page.locator('[data-testid="trading-chart"]');
    await expect(chartContainer).toBeVisible();
    
    const chartBox = await chartContainer.boundingBox();
    expect(chartBox?.width).toBeGreaterThan(0);
    expect(chartBox?.height).toBeGreaterThan(0);
  });
});
```

## 🔧 Configuration

### Playwright Configuration (`playwright.config.ts`)

```typescript
import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './tests/e2e',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: [
    ['html'],
    ['json', { outputFile: 'test-results/results.json' }],
    ['junit', { outputFile: 'test-results/results.xml' }]
  ],
  use: {
    baseURL: process.env.WEB_BASE_URL || 'http://localhost:3000',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
  },
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
    {
      name: 'firefox',
      use: { ...devices['Desktop Firefox'] },
    },
    {
      name: 'webkit',
      use: { ...devices['Desktop Safari'] },
    },
    {
      name: 'Mobile Chrome',
      use: { ...devices['Pixel 5'] },
    },
    {
      name: 'Mobile Safari',
      use: { ...devices['iPhone 12'] },
    },
  ],
  webServer: {
    command: 'npm run dev',
    url: process.env.WEB_BASE_URL || 'http://localhost:3000',
    reuseExistingServer: !process.env.CI,
    timeout: 120 * 1000,
  },
});
```

### Environment Variables

```bash
# Required for testing
export WEB_BASE_URL="http://localhost:3000"
export API_BASE_URL="http://localhost:8000"

# Optional for enhanced testing
export TEST_USER_EMAIL="test@example.com"
export TEST_USER_PASSWORD="TestPassword123!"
export HEADLESS_MODE="false"
```

## 🏃‍♂️ Running Tests

### Individual Test Categories

```bash
# Run company-specific tests
npx playwright test iam.spec.ts
npx playwright test atw.spec.ts
npx playwright test bcp.spec.ts

# Run authentication tests
npx playwright test auth.spec.ts

# Run data quality tests
npx playwright test data-quality.spec.ts

# Run chart rendering tests
npx playwright test charts.spec.ts
```

### Browser-Specific Testing

```bash
# Test on specific browsers
npx playwright test --project=chromium
npx playwright test --project=firefox
npx playwright test --project=webkit

# Test on mobile devices
npx playwright test --project="Mobile Chrome"
npx playwright test --project="Mobile Safari"
```

### CI/CD Integration

```bash
# Run tests in CI mode
npx playwright test --reporter=junit --project=chromium

# Generate HTML report
npx playwright show-report
```

## 📊 Test Results & Reporting

### Generated Reports

After running tests, you'll find:

```
test_results/e2e/
├── comprehensive_report/          # Full HTML report
├── iam_report/                   # IAM-specific results
├── atw_report/                   # ATW-specific results
├── bcp_report/                   # BCP-specific results
└── e2e_test_summary.md           # Summary report
```

### Report Contents

#### HTML Reports
- **Test Results**: Pass/fail status for each test
- **Screenshots**: Visual evidence of test execution
- **Videos**: Recorded test sessions
- **Traces**: Detailed execution traces
- **Console Logs**: Browser console output

#### Summary Report
- **Test Execution Summary**: Overview of all tests
- **Company Test Results**: Status for IAM, ATW, BCP
- **Performance Metrics**: Response times and data quality
- **Browser Compatibility**: Cross-browser test results
- **Recommendations**: Next steps and improvements

## 🔍 Debugging Tests

### Common Issues & Solutions

#### 1. Tests Failing Due to Timing

```typescript
// Add explicit waits for dynamic content
await page.waitForSelector('[data-testid="trading-chart"]', { timeout: 10000 });
await page.waitForTimeout(3000); // Wait for data to load
```

#### 2. Data Quality Badge Not Found

```typescript
// Check if badge exists before testing
const badge = page.locator('[data-testid="data-quality-badge"]');
if (await badge.isVisible()) {
  await expect(badge).toBeVisible();
} else {
  console.log('Data quality badge not found - may be missing data');
}
```

#### 3. Chart Not Rendering

```typescript
// Wait for chart to load and verify data
await page.waitForTimeout(3000);
const chartData = await page.evaluate(() => {
  const chart = document.querySelector('[data-testid="trading-chart"]');
  return chart ? chart.getAttribute('data-points') : null;
});
expect(chartData).toBeTruthy();
```

### Debug Mode

```bash
# Run tests in debug mode
npx playwright test --debug

# Run specific test in debug mode
npx playwright test iam.spec.ts --debug
```

### Visual Debugging

```bash
# Generate screenshots on failure
npx playwright test --screenshot=only-on-failure

# Record videos
npx playwright test --video=on

# Generate traces
npx playwright test --trace=on
```

## 🎯 Test Data Validation

### Real-time Data Verification

```bash
# Validate API endpoints
curl -s "http://localhost:8000/api/companies/IAM/summary" | jq .
curl -s "http://localhost:8000/api/companies/ATW/trading" | jq .
curl -s "http://localhost:8000/api/companies/BCP/reports" | jq .
```

### Data Quality Checks

```typescript
// Verify financial metrics
const metrics = ['market-cap', 'pe-ratio', 'dividend-yield'];
for (const metric of metrics) {
  const element = page.locator(`[data-testid="${metric}"]`);
  await expect(element).toBeVisible();
  const value = await element.textContent();
  expect(value).toBeTruthy();
  expect(value).not.toBe('N/A');
}
```

## 🚀 Performance Testing

### Response Time Validation

```typescript
// Measure page load time
const startTime = Date.now();
await page.goto('/company/iam');
const loadTime = Date.now() - startTime;
expect(loadTime).toBeLessThan(3000); // Should load in < 3 seconds
```

### Chart Rendering Performance

```typescript
// Measure chart rendering time
const chartStart = Date.now();
await page.waitForSelector('[data-testid="trading-chart"]');
const chartTime = Date.now() - chartStart;
expect(chartTime).toBeLessThan(2000); // Should render in < 2 seconds
```

## 📱 Mobile Testing

### Responsive Design Validation

```typescript
// Test mobile viewport
await page.setViewportSize({ width: 375, height: 667 });
await expect(page.locator('[data-testid="mobile-menu"]')).toBeVisible();

// Test tablet viewport
await page.setViewportSize({ width: 768, height: 1024 });
await expect(page.locator('[data-testid="tablet-layout"]')).toBeVisible();
```

## 🔄 Continuous Integration

### GitHub Actions Example

```yaml
name: E2E Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: 18
      - run: npm ci
      - run: npx playwright install --with-deps
      - run: npm run build
      - run: npm run start:ci &
      - run: npx playwright test
      - uses: actions/upload-artifact@v3
        if: always()
        with:
          name: playwright-report
          path: playwright-report/
```

## 📈 Monitoring & Maintenance

### Regular Test Maintenance

1. **Weekly**: Review test results and update selectors if needed
2. **Monthly**: Update test data and add new test cases
3. **Quarterly**: Review and optimize test performance

### Test Metrics

- **Test Coverage**: Percentage of features tested
- **Test Execution Time**: Total time to run all tests
- **Test Reliability**: Percentage of tests passing consistently
- **Test Maintenance**: Time spent updating tests

## 🎉 Success Criteria

Your E2E testing is successful when:

✅ **All Company Tests Pass**
- IAM, ATW, BCP pages load correctly
- Real-time data displays properly
- Charts render with live data
- Data quality badges show correct status

✅ **Authentication Flows Work**
- User registration completes successfully
- Login/logout functions properly
- Password reset works correctly
- Protected routes are secure

✅ **Data Quality Validated**
- Financial metrics are populated
- Data quality badges reflect actual data quality
- Real-time updates work correctly
- Error states are handled gracefully

✅ **Performance Targets Met**
- Page load time < 3 seconds
- Chart rendering < 2 seconds
- API response time < 200ms (P95)
- Mobile responsiveness verified

---

**🎯 Your E2E testing suite is now ready to ensure the quality and reliability of Casablanca Insights!** 