import { test, expect } from '@playwright/test';

// Test configuration
const BASE_URL = process.env.BASE_URL || 'http://localhost:3000';
const COMPANIES = ['IAM', 'ATW', 'BCP'];

test.describe('Company Pages E2E Tests', () => {
    test.beforeEach(async ({ page }) => {
        // Set viewport for consistent testing
        await page.setViewportSize({ width: 1280, height: 720 });
    });

    test.describe('Company Summary Pages', () => {
        for (const ticker of COMPANIES) {
            test(`should load company summary page for ${ticker}`, async ({ page }) => {
                const url = `${BASE_URL}/company/${ticker}`;

                // Navigate to company page
                await page.goto(url);

                // Wait for page to load
                await page.waitForLoadState('networkidle');

                // Verify page title contains company ticker
                await expect(page).toHaveTitle(new RegExp(ticker, 'i'));

                // Verify company header is present
                await expect(page.locator('[data-testid="company-header"]')).toBeVisible();

                // Verify company ticker is displayed
                await expect(page.locator(`text=${ticker}`)).toBeVisible();

                // Verify data quality badge is present
                await expect(page.locator('[data-testid="data-quality-badge"]')).toBeVisible();

                // Verify loading states are resolved
                await expect(page.locator('[data-testid="loading-spinner"]')).not.toBeVisible();

                // Verify error states are not present
                await expect(page.locator('[data-testid="error-message"]')).not.toBeVisible();
            });

            test(`should display company information for ${ticker}`, async ({ page }) => {
                const url = `${BASE_URL}/company/${ticker}`;

                await page.goto(url);
                await page.waitForLoadState('networkidle');

                // Verify company name is displayed
                await expect(page.locator('[data-testid="company-name"]')).toBeVisible();

                // Verify sector information is displayed
                await expect(page.locator('[data-testid="company-sector"]')).toBeVisible();

                // Verify current price is displayed
                await expect(page.locator('[data-testid="current-price"]')).toBeVisible();

                // Verify price change is displayed
                await expect(page.locator('[data-testid="price-change"]')).toBeVisible();

                // Verify market cap is displayed
                await expect(page.locator('[data-testid="market-cap"]')).toBeVisible();
            });

            test(`should display data quality badge for ${ticker}`, async ({ page }) => {
                const url = `${BASE_URL}/company/${ticker}`;

                await page.goto(url);
                await page.waitForLoadState('networkidle');

                // Verify data quality badge exists
                const qualityBadge = page.locator('[data-testid="data-quality-badge"]');
                await expect(qualityBadge).toBeVisible();

                // Verify badge shows either "Complete" or "Partial"
                const badgeText = await qualityBadge.textContent();
                expect(badgeText).toMatch(/^(Complete|Partial)$/);

                // Verify badge has appropriate styling
                if (badgeText?.includes('Complete')) {
                    await expect(qualityBadge).toHaveClass(/bg-green/);
                } else {
                    await expect(qualityBadge).toHaveClass(/bg-yellow/);
                }
            });
        }
    });

    test.describe('Trading Data Section', () => {
        for (const ticker of COMPANIES) {
            test(`should load trading data for ${ticker}`, async ({ page }) => {
                const url = `${BASE_URL}/company/${ticker}`;

                await page.goto(url);
                await page.waitForLoadState('networkidle');

                // Scroll to trading section
                await page.locator('[data-testid="trading-section"]').scrollIntoViewIfNeeded();

                // Verify trading chart is present
                await expect(page.locator('[data-testid="trading-chart"]')).toBeVisible();

                // Verify price data is loaded
                await expect(page.locator('[data-testid="price-data"]')).toBeVisible();

                // Verify volume data is displayed
                await expect(page.locator('[data-testid="volume-data"]')).toBeVisible();

                // Verify technical indicators are present (if available)
                const indicators = page.locator('[data-testid="technical-indicators"]');
                if (await indicators.isVisible()) {
                    await expect(indicators).toBeVisible();
                }
            });

            test(`should display price chart for ${ticker}`, async ({ page }) => {
                const url = `${BASE_URL}/company/${ticker}`;

                await page.goto(url);
                await page.waitForLoadState('networkidle');

                // Wait for chart to load
                await page.locator('[data-testid="trading-chart"]').waitFor({ state: 'visible' });

                // Verify chart container is present
                const chartContainer = page.locator('[data-testid="chart-container"]');
                await expect(chartContainer).toBeVisible();

                // Verify chart has content (not empty)
                const chartContent = await chartContainer.innerHTML();
                expect(chartContent.length).toBeGreaterThan(100);

                // Verify chart controls are present
                await expect(page.locator('[data-testid="chart-controls"]')).toBeVisible();
            });
        }
    });

    test.describe('Financial Reports Section', () => {
        for (const ticker of COMPANIES) {
            test(`should load financial reports for ${ticker}`, async ({ page }) => {
                const url = `${BASE_URL}/company/${ticker}`;

                await page.goto(url);
                await page.waitForLoadState('networkidle');

                // Scroll to reports section
                await page.locator('[data-testid="reports-section"]').scrollIntoViewIfNeeded();

                // Verify reports section is present
                await expect(page.locator('[data-testid="reports-section"]')).toBeVisible();

                // Verify reports list is displayed
                const reportsList = page.locator('[data-testid="reports-list"]');
                await expect(reportsList).toBeVisible();

                // Check if reports are available
                const reportItems = page.locator('[data-testid="report-item"]');
                const reportCount = await reportItems.count();

                if (reportCount > 0) {
                    // Verify at least one report is displayed
                    await expect(reportItems.first()).toBeVisible();

                    // Verify report title is present
                    await expect(page.locator('[data-testid="report-title"]').first()).toBeVisible();

                    // Verify report date is present
                    await expect(page.locator('[data-testid="report-date"]').first()).toBeVisible();

                    // Verify report type is displayed
                    await expect(page.locator('[data-testid="report-type"]').first()).toBeVisible();
                } else {
                    // Verify empty state is displayed
                    await expect(page.locator('[data-testid="no-reports-message"]')).toBeVisible();
                }
            });

            test(`should filter reports for ${ticker}`, async ({ page }) => {
                const url = `${BASE_URL}/company/${ticker}`;

                await page.goto(url);
                await page.waitForLoadState('networkidle');

                // Scroll to reports section
                await page.locator('[data-testid="reports-section"]').scrollIntoViewIfNeeded();

                // Check if filter controls are present
                const filterControls = page.locator('[data-testid="reports-filter"]');
                if (await filterControls.isVisible()) {
                    // Test report type filter
                    const typeFilter = page.locator('[data-testid="report-type-filter"]');
                    if (await typeFilter.isVisible()) {
                        await typeFilter.click();
                        await page.locator('text=Annual Report').click();

                        // Verify filter is applied
                        await expect(page.locator('[data-testid="active-filter"]')).toBeVisible();
                    }
                }
            });
        }
    });

    test.describe('News Section', () => {
        for (const ticker of COMPANIES) {
            test(`should load news for ${ticker}`, async ({ page }) => {
                const url = `${BASE_URL}/company/${ticker}`;

                await page.goto(url);
                await page.waitForLoadState('networkidle');

                // Scroll to news section
                await page.locator('[data-testid="news-section"]').scrollIntoViewIfNeeded();

                // Verify news section is present
                await expect(page.locator('[data-testid="news-section"]')).toBeVisible();

                // Verify news list is displayed
                const newsList = page.locator('[data-testid="news-list"]');
                await expect(newsList).toBeVisible();

                // Check if news articles are available
                const newsItems = page.locator('[data-testid="news-item"]');
                const newsCount = await newsItems.count();

                if (newsCount > 0) {
                    // Verify at least one news article is displayed
                    await expect(newsItems.first()).toBeVisible();

                    // Verify news headline is present
                    await expect(page.locator('[data-testid="news-headline"]').first()).toBeVisible();

                    // Verify news source is displayed
                    await expect(page.locator('[data-testid="news-source"]').first()).toBeVisible();

                    // Verify news date is present
                    await expect(page.locator('[data-testid="news-date"]').first()).toBeVisible();

                    // Verify sentiment indicator is present (if available)
                    const sentimentIndicator = page.locator('[data-testid="sentiment-indicator"]').first();
                    if (await sentimentIndicator.isVisible()) {
                        await expect(sentimentIndicator).toBeVisible();
                    }
                } else {
                    // Verify empty state is displayed
                    await expect(page.locator('[data-testid="no-news-message"]')).toBeVisible();
                }
            });

            test(`should filter news by sentiment for ${ticker}`, async ({ page }) => {
                const url = `${BASE_URL}/company/${ticker}`;

                await page.goto(url);
                await page.waitForLoadState('networkidle');

                // Scroll to news section
                await page.locator('[data-testid="news-section"]').scrollIntoViewIfNeeded();

                // Check if sentiment filter is present
                const sentimentFilter = page.locator('[data-testid="sentiment-filter"]');
                if (await sentimentFilter.isVisible()) {
                    // Test positive sentiment filter
                    await sentimentFilter.click();
                    await page.locator('text=Positive').click();

                    // Verify filter is applied
                    await expect(page.locator('[data-testid="active-sentiment-filter"]')).toBeVisible();
                }
            });
        }
    });

    test.describe('Error Handling', () => {
        test('should handle invalid company ticker', async ({ page }) => {
            const url = `${BASE_URL}/company/INVALID`;

            await page.goto(url);
            await page.waitForLoadState('networkidle');

            // Verify error message is displayed
            await expect(page.locator('[data-testid="error-message"]')).toBeVisible();

            // Verify error message contains appropriate text
            await expect(page.locator('[data-testid="error-message"]')).toContainText('not found');

            // Verify back to dashboard link is present
            await expect(page.locator('[data-testid="back-to-dashboard"]')).toBeVisible();
        });

        test('should handle network errors gracefully', async ({ page }) => {
            // Mock network error
            await page.route('**/api/companies/**', route => {
                route.abort('failed');
            });

            const url = `${BASE_URL}/company/IAM`;
            await page.goto(url);

            // Verify error state is displayed
            await expect(page.locator('[data-testid="error-message"]')).toBeVisible();

            // Verify retry button is present
            await expect(page.locator('[data-testid="retry-button"]')).toBeVisible();
        });
    });

    test.describe('Loading States', () => {
        test('should show loading states while data is being fetched', async ({ page }) => {
            // Slow down network requests to see loading states
            await page.route('**/api/companies/**', route => {
                setTimeout(() => route.continue(), 1000);
            });

            const url = `${BASE_URL}/company/IAM`;
            await page.goto(url);

            // Verify loading spinner is visible initially
            await expect(page.locator('[data-testid="loading-spinner"]')).toBeVisible();

            // Wait for data to load
            await page.waitForLoadState('networkidle');

            // Verify loading spinner is hidden after data loads
            await expect(page.locator('[data-testid="loading-spinner"]')).not.toBeVisible();
        });
    });

    test.describe('Responsive Design', () => {
        test('should work on mobile devices', async ({ page }) => {
            // Set mobile viewport
            await page.setViewportSize({ width: 375, height: 667 });

            const url = `${BASE_URL}/company/IAM`;
            await page.goto(url);
            await page.waitForLoadState('networkidle');

            // Verify page is responsive
            await expect(page.locator('[data-testid="company-header"]')).toBeVisible();

            // Verify navigation works on mobile
            await page.locator('[data-testid="mobile-menu-button"]').click();
            await expect(page.locator('[data-testid="mobile-menu"]')).toBeVisible();
        });

        test('should work on tablet devices', async ({ page }) => {
            // Set tablet viewport
            await page.setViewportSize({ width: 768, height: 1024 });

            const url = `${BASE_URL}/company/IAM`;
            await page.goto(url);
            await page.waitForLoadState('networkidle');

            // Verify page layout is appropriate for tablet
            await expect(page.locator('[data-testid="company-header"]')).toBeVisible();

            // Verify sidebar is visible on tablet
            await expect(page.locator('[data-testid="sidebar"]')).toBeVisible();
        });
    });

    test.describe('Accessibility', () => {
        test('should meet accessibility standards', async ({ page }) => {
            const url = `${BASE_URL}/company/IAM`;
            await page.goto(url);
            await page.waitForLoadState('networkidle');

            // Check for proper heading structure
            const headings = await page.locator('h1, h2, h3, h4, h5, h6').all();
            expect(headings.length).toBeGreaterThan(0);

            // Check for alt text on images
            const images = await page.locator('img').all();
            for (const img of images) {
                const alt = await img.getAttribute('alt');
                expect(alt).toBeTruthy();
            }

            // Check for proper ARIA labels
            const ariaLabels = await page.locator('[aria-label]').all();
            expect(ariaLabels.length).toBeGreaterThan(0);

            // Check for keyboard navigation
            await page.keyboard.press('Tab');
            await expect(page.locator(':focus')).toBeVisible();
        });
    });

    test.describe('Performance', () => {
        test('should load within performance budget', async ({ page }) => {
            const url = `${BASE_URL}/company/IAM`;

            // Start performance measurement
            const startTime = Date.now();

            await page.goto(url);
            await page.waitForLoadState('networkidle');

            const loadTime = Date.now() - startTime;

            // Verify page loads within 3 seconds
            expect(loadTime).toBeLessThan(3000);

            // Check for performance metrics
            const performanceMetrics = await page.evaluate(() => {
                const navigation = performance.getEntriesByType('navigation')[0] as PerformanceNavigationTiming;
                return {
                    domContentLoaded: navigation.domContentLoadedEventEnd - navigation.domContentLoadedEventStart,
                    loadComplete: navigation.loadEventEnd - navigation.loadEventStart,
                    firstContentfulPaint: performance.getEntriesByName('first-contentful-paint')[0]?.startTime || 0
                };
            });

            // Verify performance metrics are within acceptable ranges
            expect(performanceMetrics.domContentLoaded).toBeLessThan(1000);
            expect(performanceMetrics.loadComplete).toBeLessThan(2000);
        });
    });
}); 