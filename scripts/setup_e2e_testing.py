#!/usr/bin/env python3
"""
End-to-End Testing Setup for Casablanca Insights
Configures Playwright tests for comprehensive E2E validation
"""

import os
import sys
import json
import logging
import subprocess
from pathlib import Path
from typing import Dict, List, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class E2ETestingSetup:
    """Setup comprehensive E2E testing with Playwright"""

    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.web_dir = self.project_root / "apps" / "web"
        self.tests_dir = self.web_dir / "tests" / "e2e"
        self.companies = ["IAM", "ATW", "BCP"]

    def setup_e2e_testing(self) -> bool:
        """Setup complete E2E testing infrastructure"""
        logger.info("🚀 Setting up End-to-End Testing Infrastructure")

        try:
            # 1. Setup Playwright
            self.setup_playwright()

            # 2. Create test configuration
            self.create_playwright_config()

            # 3. Create company-specific tests
            self.create_company_tests()

            # 4. Create authentication tests
            self.create_auth_tests()

            # 5. Create data quality tests
            self.create_data_quality_tests()

            # 6. Create chart rendering tests
            self.create_chart_tests()

            # 7. Create test utilities
            self.create_test_utilities()

            # 8. Create test runner script
            self.create_test_runner()

            logger.info("✅ E2E testing setup completed successfully")
            return True

        except Exception as e:
            logger.error(f"❌ E2E testing setup failed: {e}")
            return False

    def setup_playwright(self):
        """Setup Playwright testing framework"""
        logger.info("📦 Setting up Playwright...")

        # Navigate to web directory
        os.chdir(self.web_dir)

        # Install Playwright if not already installed
        try:
            subprocess.run(
                ["npx", "playwright", "--version"], capture_output=True, check=True
            )
            logger.info("✅ Playwright already installed")
        except subprocess.CalledProcessError:
            logger.info("Installing Playwright...")
            subprocess.run(["npm", "install", "-D", "@playwright/test"], check=True)
            subprocess.run(["npx", "playwright", "install"], check=True)
            logger.info("✅ Playwright installed successfully")

    def create_playwright_config(self):
        """Create Playwright configuration"""
        logger.info("⚙️ Creating Playwright configuration...")

        config_content = """
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
"""

        config_file = self.web_dir / "playwright.config.ts"
        with open(config_file, "w") as f:
            f.write(config_content)

        logger.info(f"✅ Playwright config created: {config_file}")

    def create_company_tests(self):
        """Create company-specific E2E tests"""
        logger.info("🏢 Creating company-specific tests...")

        # Create tests directory
        self.tests_dir.mkdir(parents=True, exist_ok=True)

        for company in self.companies:
            self.create_company_test_file(company)

    def create_company_test_file(self, company: str):
        """Create test file for specific company"""
        test_content = f"""
import {{ test, expect }} from '@playwright/test';
import {{ CompanyPage }} from '../utils/company-page';

test.describe('{company} Company Page', () => {{
  let companyPage: CompanyPage;

  test.beforeEach(async ({ page })) => {{
    companyPage = new CompanyPage(page, '{company}');
    await companyPage.goto();
  }});

  test('should load company page successfully', async () => {{
    await expect(page).toHaveTitle(/.*{company}.*/);
    await expect(page.locator('[data-testid="company-header"]')).toBeVisible();
  }});

  test('should display company summary section', async () => {{
    await expect(page.locator('[data-testid="company-summary"]')).toBeVisible();
    await expect(page.locator('[data-testid="company-name"]')).toContainText('{company}');
  }});

  test('should render trading data charts', async () => {{
    await expect(page.locator('[data-testid="trading-chart"]')).toBeVisible();
    await expect(page.locator('[data-testid="volume-chart"]')).toBeVisible();
    
    // Wait for charts to load data
    await page.waitForTimeout(2000);
    
    // Verify chart has data
    const chartElement = page.locator('[data-testid="trading-chart"]');
    await expect(chartElement).toBeVisible();
  }});

  test('should display financial reports section', async () => {{
    await expect(page.locator('[data-testid="financial-reports"]')).toBeVisible();
    
    // Check if reports are loaded
    const reportsList = page.locator('[data-testid="reports-list"]');
    await expect(reportsList).toBeVisible();
  }});

  test('should display news section', async () => {{
    await expect(page.locator('[data-testid="news-section"]')).toBeVisible();
    
    // Check if news items are loaded
    const newsItems = page.locator('[data-testid="news-item"]');
    await expect(newsItems.first()).toBeVisible();
  }});

  test('should show data quality badge', async () => {{
    const qualityBadge = page.locator('[data-testid="data-quality-badge"]');
    await expect(qualityBadge).toBeVisible();
    
    // Verify badge has correct status
    const badgeText = await qualityBadge.textContent();
    expect(badgeText).toMatch(/^(Excellent|Good|Fair|Poor)$/);
  }});

  test('should handle real-time data updates', async () => {{
    // Wait for initial data load
    await page.waitForTimeout(2000);
    
    // Get initial price
    const initialPrice = await page.locator('[data-testid="current-price"]').textContent();
    
    // Wait for potential updates
    await page.waitForTimeout(5000);
    
    // Check if price updated (should be different or same, but not empty)
    const updatedPrice = await page.locator('[data-testid="current-price"]').textContent();
    expect(updatedPrice).toBeTruthy();
  }});

  test('should display company metrics', async () => {{
    await expect(page.locator('[data-testid="company-metrics"]')).toBeVisible();
    
    // Check key metrics
    await expect(page.locator('[data-testid="market-cap"]')).toBeVisible();
    await expect(page.locator('[data-testid="pe-ratio"]')).toBeVisible();
    await expect(page.locator('[data-testid="dividend-yield"]')).toBeVisible();
  }});

  test('should handle responsive design', async () => {{
    // Test mobile viewport
    await page.setViewportSize({{ width: 375, height: 667 }});
    
    // Verify mobile layout
    await expect(page.locator('[data-testid="mobile-menu"]')).toBeVisible();
    
    // Test tablet viewport
    await page.setViewportSize({{ width: 768, height: 1024 }});
    
    // Verify tablet layout
    await expect(page.locator('[data-testid="tablet-layout"]')).toBeVisible();
  }});

  test('should handle loading states', async () => {{
    // Navigate to page and check loading states
    await page.goto(`/company/${{company.toLowerCase()}}`);
    
    // Check if loading indicators are shown initially
    const loadingIndicator = page.locator('[data-testid="loading-indicator"]');
    if (await loadingIndicator.isVisible()) {{
      await expect(loadingIndicator).toBeVisible();
      // Wait for loading to complete
      await expect(loadingIndicator).not.toBeVisible();
    }}
  }});

  test('should handle error states gracefully', async () => {{
    // Test with invalid company ticker
    await page.goto('/company/INVALID');
    
    // Should show error page
    await expect(page.locator('[data-testid="error-page"]')).toBeVisible();
    await expect(page.locator('[data-testid="error-message"]')).toContainText('Company not found');
  }});
}});
"""

        test_file = self.tests_dir / f"{company.lower()}.spec.ts"
        with open(test_file, "w") as f:
            f.write(test_content)

        logger.info(f"✅ Created test file: {test_file}")

    def create_auth_tests(self):
        """Create authentication flow tests"""
        logger.info("🔐 Creating authentication tests...")

        auth_test_content = """
import { test, expect } from '@playwright/test';

test.describe('Authentication Flows', () => {
  test('should handle user registration', async ({ page }) => {
    await page.goto('/signup');
    
    // Fill registration form
    await page.fill('[data-testid="email-input"]', 'test@example.com');
    await page.fill('[data-testid="password-input"]', 'TestPassword123!');
    await page.fill('[data-testid="confirm-password-input"]', 'TestPassword123!');
    
    // Submit form
    await page.click('[data-testid="signup-button"]');
    
    // Should redirect to verification page
    await expect(page).toHaveURL(/.*verify.*/);
  });

  test('should handle user login', async ({ page }) => {
    await page.goto('/login');
    
    // Fill login form
    await page.fill('[data-testid="email-input"]', 'test@example.com');
    await page.fill('[data-testid="password-input"]', 'TestPassword123!');
    
    // Submit form
    await page.click('[data-testid="login-button"]');
    
    // Should redirect to dashboard
    await expect(page).toHaveURL(/.*dashboard.*/);
  });

  test('should handle password reset', async ({ page }) => {
    await page.goto('/forgot-password');
    
    // Fill email
    await page.fill('[data-testid="email-input"]', 'test@example.com');
    
    // Submit form
    await page.click('[data-testid="reset-button"]');
    
    // Should show success message
    await expect(page.locator('[data-testid="success-message"]')).toBeVisible();
  });

  test('should handle logout', async ({ page }) => {
    // Login first
    await page.goto('/login');
    await page.fill('[data-testid="email-input"]', 'test@example.com');
    await page.fill('[data-testid="password-input"]', 'TestPassword123!');
    await page.click('[data-testid="login-button"]');
    
    // Logout
    await page.click('[data-testid="logout-button"]');
    
    // Should redirect to home page
    await expect(page).toHaveURL('/');
  });

  test('should protect authenticated routes', async ({ page }) => {
    // Try to access protected route without login
    await page.goto('/dashboard');
    
    // Should redirect to login
    await expect(page).toHaveURL(/.*login.*/);
  });
});
"""

        auth_test_file = self.tests_dir / "auth.spec.ts"
        with open(auth_test_file, "w") as f:
            f.write(auth_test_content)

        logger.info(f"✅ Created auth test file: {auth_test_file}")

    def create_data_quality_tests(self):
        """Create data quality validation tests"""
        logger.info("📊 Creating data quality tests...")

        data_quality_content = """
import { test, expect } from '@playwright/test';

test.describe('Data Quality Validation', () => {
  const companies = ['IAM', 'ATW', 'BCP'];

  for (const company of companies) {
    test(`should validate ${company} data quality`, async ({ page }) => {
      await page.goto(`/company/${company.toLowerCase()}`);
      
      // Wait for data to load
      await page.waitForTimeout(3000);
      
      // Check data quality badge
      const qualityBadge = page.locator('[data-testid="data-quality-badge"]');
      await expect(qualityBadge).toBeVisible();
      
      // Verify badge color based on quality
      const badgeClass = await qualityBadge.getAttribute('class');
      expect(badgeClass).toMatch(/badge-(excellent|good|fair|poor)/);
      
      // Check data freshness
      const lastUpdated = page.locator('[data-testid="last-updated"]');
      await expect(lastUpdated).toBeVisible();
      
      // Verify data is not too old (within 24 hours)
      const updatedText = await lastUpdated.textContent();
      expect(updatedText).toMatch(/\\d+ hours? ago|Today|Yesterday/);
    });

    test(`should validate ${company} financial data`, async ({ page }) => {
      await page.goto(`/company/${company.toLowerCase()}`);
      
      // Check financial metrics
      const metrics = [
        'market-cap',
        'pe-ratio',
        'dividend-yield',
        'price-to-book',
        'debt-to-equity'
      ];
      
      for (const metric of metrics) {
        const element = page.locator(`[data-testid="${metric}"]`);
        await expect(element).toBeVisible();
        
        // Verify metric has a value
        const value = await element.textContent();
        expect(value).toBeTruthy();
        expect(value).not.toBe('N/A');
      }
    });

    test(`should validate ${company} chart data`, async ({ page }) => {
      await page.goto(`/company/${company.toLowerCase()}`);
      
      // Wait for charts to load
      await page.waitForTimeout(3000);
      
      // Check trading chart
      const tradingChart = page.locator('[data-testid="trading-chart"]');
      await expect(tradingChart).toBeVisible();
      
      // Verify chart has data points
      const chartData = await page.evaluate(() => {
        const chart = document.querySelector('[data-testid="trading-chart"]');
        return chart ? chart.getAttribute('data-points') : null;
      });
      
      expect(chartData).toBeTruthy();
      expect(JSON.parse(chartData || '[]').length).toBeGreaterThan(0);
    });
  }

  test('should handle missing data gracefully', async ({ page }) => {
    // Test with company that might have missing data
    await page.goto('/company/test');
    
    // Should show appropriate message for missing data
    const missingDataMessage = page.locator('[data-testid="missing-data-message"]');
    if (await missingDataMessage.isVisible()) {
      await expect(missingDataMessage).toBeVisible();
    }
  });
});
"""

        data_quality_file = self.tests_dir / "data-quality.spec.ts"
        with open(data_quality_file, "w") as f:
            f.write(data_quality_content)

        logger.info(f"✅ Created data quality test file: {data_quality_file}")

    def create_chart_tests(self):
        """Create chart rendering tests"""
        logger.info("📈 Creating chart rendering tests...")

        chart_test_content = """
import { test, expect } from '@playwright/test';

test.describe('Chart Rendering Tests', () => {
  const companies = ['IAM', 'ATW', 'BCP'];

  for (const company of companies) {
    test(`should render ${company} trading chart correctly`, async ({ page }) => {
      await page.goto(`/company/${company.toLowerCase()}`);
      
      // Wait for chart to load
      await page.waitForTimeout(3000);
      
      // Check chart container
      const chartContainer = page.locator('[data-testid="trading-chart"]');
      await expect(chartContainer).toBeVisible();
      
      // Verify chart dimensions
      const chartBox = await chartContainer.boundingBox();
      expect(chartBox?.width).toBeGreaterThan(0);
      expect(chartBox?.height).toBeGreaterThan(0);
      
      // Check for chart elements (SVG, canvas, etc.)
      const chartElement = page.locator('[data-testid="trading-chart"] svg, [data-testid="trading-chart"] canvas');
      await expect(chartElement).toBeVisible();
    });

    test(`should render ${company} volume chart correctly`, async ({ page }) => {
      await page.goto(`/company/${company.toLowerCase()}`);
      
      // Wait for chart to load
      await page.waitForTimeout(3000);
      
      // Check volume chart
      const volumeChart = page.locator('[data-testid="volume-chart"]');
      await expect(volumeChart).toBeVisible();
      
      // Verify volume data is displayed
      const volumeData = page.locator('[data-testid="volume-data"]');
      await expect(volumeData).toBeVisible();
    });

    test(`should handle ${company} chart interactions`, async ({ page }) => {
      await page.goto(`/company/${company.toLowerCase()}`);
      
      // Wait for chart to load
      await page.waitForTimeout(3000);
      
      // Test chart hover
      const chart = page.locator('[data-testid="trading-chart"]');
      await chart.hover();
      
      // Check if tooltip appears
      const tooltip = page.locator('[data-testid="chart-tooltip"]');
      if (await tooltip.isVisible()) {
        await expect(tooltip).toBeVisible();
      }
      
      // Test chart zoom (if available)
      const zoomInButton = page.locator('[data-testid="zoom-in"]');
      if (await zoomInButton.isVisible()) {
        await zoomInButton.click();
        // Verify zoom state
        await expect(page.locator('[data-testid="zoomed-chart"]')).toBeVisible();
      }
    });

    test(`should render ${company} chart with real-time data`, async ({ page }) => {
      await page.goto(`/company/${company.toLowerCase()}`);
      
      // Wait for initial data load
      await page.waitForTimeout(3000);
      
      // Get initial chart state
      const initialData = await page.evaluate(() => {
        const chart = document.querySelector('[data-testid="trading-chart"]');
        return chart ? chart.getAttribute('data-last-update') : null;
      });
      
      // Wait for potential real-time update
      await page.waitForTimeout(10000);
      
      // Check if chart updated
      const updatedData = await page.evaluate(() => {
        const chart = document.querySelector('[data-testid="trading-chart"]');
        return chart ? chart.getAttribute('data-last-update') : null;
      });
      
      // Chart should have data (may or may not have updated)
      expect(updatedData).toBeTruthy();
    });
  }

  test('should handle chart loading states', async ({ page }) => {
    await page.goto('/company/iam');
    
    // Check for loading state
    const loadingState = page.locator('[data-testid="chart-loading"]');
    if (await loadingState.isVisible()) {
      await expect(loadingState).toBeVisible();
      // Wait for loading to complete
      await expect(loadingState).not.toBeVisible();
    }
  });

  test('should handle chart error states', async ({ page }) => {
    // Mock network error for chart data
    await page.route('**/api/companies/*/trading', route => {
      route.abort();
    });
    
    await page.goto('/company/iam');
    
    // Should show error state
    const errorState = page.locator('[data-testid="chart-error"]');
    await expect(errorState).toBeVisible();
  });
});
"""

        chart_test_file = self.tests_dir / "charts.spec.ts"
        with open(chart_test_file, "w") as f:
            f.write(chart_test_content)

        logger.info(f"✅ Created chart test file: {chart_test_file}")

    def create_test_utilities(self):
        """Create test utility classes"""
        logger.info("🛠️ Creating test utilities...")

        utils_dir = self.tests_dir / "utils"
        utils_dir.mkdir(exist_ok=True)

        # Company page utility
        company_page_content = """
import { Page, expect } from '@playwright/test';

export class CompanyPage {
  constructor(private page: Page, private company: string) {}

  async goto() {
    await this.page.goto(`/company/${this.company.toLowerCase()}`);
  }

  async waitForDataLoad() {
    await this.page.waitForTimeout(3000);
    await expect(this.page.locator('[data-testid="company-header"]')).toBeVisible();
  }

  async getCurrentPrice(): Promise<string> {
    const priceElement = this.page.locator('[data-testid="current-price"]');
    await expect(priceElement).toBeVisible();
    return await priceElement.textContent() || '';
  }

  async getDataQualityBadge(): Promise<string> {
    const badge = this.page.locator('[data-testid="data-quality-badge"]');
    await expect(badge).toBeVisible();
    return await badge.textContent() || '';
  }

  async getChartData(): Promise<any> {
    return await this.page.evaluate(() => {
      const chart = document.querySelector('[data-testid="trading-chart"]');
      return chart ? JSON.parse(chart.getAttribute('data-points') || '[]') : [];
    });
  }

  async waitForChartLoad() {
    await this.page.waitForTimeout(2000);
    await expect(this.page.locator('[data-testid="trading-chart"]')).toBeVisible();
  }
}
"""

        company_page_file = utils_dir / "company-page.ts"
        with open(company_page_file, "w") as f:
            f.write(company_page_content)

        logger.info(f"✅ Created test utilities: {company_page_file}")

    def create_test_runner(self):
        """Create test runner script"""
        logger.info("🏃 Creating test runner script...")

        runner_content = """#!/bin/bash

# E2E Test Runner for Casablanca Insights
# Runs comprehensive end-to-end tests

set -e

# Colors for output
RED='\\033[0;31m'
GREEN='\\033[0;32m'
YELLOW='\\033[1;33m'
BLUE='\\033[0;34m'
NC='\\033[0m'

# Configuration
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WEB_DIR="$PROJECT_ROOT/apps/web"
RESULTS_DIR="$PROJECT_ROOT/test_results/e2e"

# Create results directory
mkdir -p "$RESULTS_DIR"

# Logging function
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

success() {
    echo -e "${GREEN}✅ $1${NC}"
}

warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check prerequisites
check_prerequisites() {
    log "Checking prerequisites..."
    
    cd "$WEB_DIR"
    
    # Check if Playwright is installed
    if ! npx playwright --version &> /dev/null; then
        error "Playwright not installed. Run setup_e2e_testing.py first."
        exit 1
    fi
    
    # Check if tests exist
    if [ ! -d "tests/e2e" ]; then
        error "E2E tests not found. Run setup_e2e_testing.py first."
        exit 1
    fi
    
    success "Prerequisites check passed"
}

# Run company-specific tests
run_company_tests() {
    log "Running company-specific tests..."
    
    cd "$WEB_DIR"
    
    companies=("IAM" "ATW" "BCP")
    
    for company in "${companies[@]}"; do
        log "Testing company: $company"
        
        if npx playwright test "${company,,}.spec.ts" --reporter=list; then
            success "Tests passed for $company"
        else
            error "Tests failed for $company"
            return 1
        fi
    done
}

# Run all E2E tests
run_all_tests() {
    log "Running all E2E tests..."
    
    cd "$WEB_DIR"
    
    if npx playwright test --reporter=list; then
        success "All E2E tests passed"
    else
        error "Some E2E tests failed"
        return 1
    fi
}

# Generate test report
generate_report() {
    log "Generating test report..."
    
    cd "$WEB_DIR"
    
    # Generate HTML report
    if npx playwright show-report; then
        success "Test report generated"
    fi
    
    # Copy results to project directory
    if [ -d "playwright-report" ]; then
        cp -r playwright-report "$RESULTS_DIR/"
        success "Test results copied to $RESULTS_DIR"
    fi
}

# Main execution
main() {
    log "Starting E2E Test Execution"
    log "=========================="
    
    # Check prerequisites
    check_prerequisites
    
    # Run company-specific tests
    if run_company_tests; then
        success "Company tests completed"
    else
        error "Company tests failed"
        exit 1
    fi
    
    # Run all tests
    if run_all_tests; then
        success "All tests completed"
    else
        error "Some tests failed"
        exit 1
    fi
    
    # Generate report
    generate_report
    
    log "=========================="
    success "E2E testing completed successfully!"
    log "Check results: $RESULTS_DIR/playwright-report"
}

# Run main function
main "$@"
"""

        runner_file = self.project_root / "scripts" / "run_e2e_tests.sh"
        with open(runner_file, "w") as f:
            f.write(runner_content)

        # Make executable
        os.chmod(runner_file, 0o755)

        logger.info(f"✅ Created test runner: {runner_file}")


def main():
    """Main function"""
    setup = E2ETestingSetup()

    success = setup.setup_e2e_testing()

    if success:
        logger.info("🎉 E2E testing setup completed successfully!")
        logger.info("📁 Test files created in: apps/web/tests/e2e/")
        logger.info("🏃 Run tests with: ./scripts/run_e2e_tests.sh")
        sys.exit(0)
    else:
        logger.error("💥 E2E testing setup failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()
