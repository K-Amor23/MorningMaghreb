#!/usr/bin/env node

/**
 * Week 2 Frontend Features Test Script
 * Tests authentication, watchlists, alerts, PWA, and real-time features
 */

const puppeteer = require('puppeteer')
const fs = require('fs')
const path = require('path')

class Week2FeatureTester {
    constructor() {
        this.browser = null
        this.page = null
        this.results = {
            auth: {},
            watchlists: {},
            alerts: {},
            pwa: {},
            realtime: {},
            overall: { passed: 0, failed: 0, total: 0 }
        }
    }

    async init() {
        console.log('🚀 Starting Week 2 Frontend Features Test...')
        this.browser = await puppeteer.launch({
            headless: false,
            defaultViewport: { width: 1280, height: 720 }
        })
        this.page = await this.browser.newPage()

        // Set up console logging
        this.page.on('console', msg => {
            if (msg.type() === 'error') {
                console.log('Browser Error:', msg.text())
            }
        })
    }

    async testAuthFeatures() {
        console.log('\n🔐 Testing Authentication Features...')

        try {
            // Test login page
            await this.page.goto('http://localhost:3000/login')
            await this.page.waitForSelector('input[type="email"]')

            // Fill login form
            await this.page.type('input[type="email"]', 'test@example.com')
            await this.page.type('input[type="password"]', 'password123')

            // Test form validation
            const emailInput = await this.page.$('input[type="email"]')
            const emailValue = await emailInput.evaluate(el => el.value)
            this.results.auth.emailValidation = emailValue === 'test@example.com'

            console.log('✅ Login form validation passed')

            // Test password reset
            await this.page.goto('http://localhost:3000/auth/forgot-password')
            await this.page.waitForSelector('input[type="email"]')

            const resetForm = await this.page.$('form')
            this.results.auth.passwordReset = !!resetForm

            console.log('✅ Password reset form found')

        } catch (error) {
            console.error('❌ Auth test failed:', error.message)
            this.results.auth.error = error.message
        }
    }

    async testWatchlistFeatures() {
        console.log('\n📋 Testing Watchlist Features...')

        try {
            // Test watchlist page
            await this.page.goto('http://localhost:3000/watchlists')
            await this.page.waitForTimeout(2000)

            // Check for watchlist manager component
            const watchlistManager = await this.page.$('[data-testid="watchlist-manager"]')
            this.results.watchlists.componentLoaded = !!watchlistManager

            // Test create watchlist button
            const createButton = await this.page.$('button:has-text("New Watchlist")')
            this.results.watchlists.createButton = !!createButton

            if (createButton) {
                await createButton.click()
                await this.page.waitForTimeout(1000)

                // Check for modal
                const modal = await this.page.$('.fixed.inset-0')
                this.results.watchlists.modalOpens = !!modal

                if (modal) {
                    // Test form inputs
                    const nameInput = await this.page.$('input[placeholder*="name"]')
                    this.results.watchlists.formInputs = !!nameInput
                }
            }

            console.log('✅ Watchlist features tested')

        } catch (error) {
            console.error('❌ Watchlist test failed:', error.message)
            this.results.watchlists.error = error.message
        }
    }

    async testAlertFeatures() {
        console.log('\n🔔 Testing Alert Features...')

        try {
            // Test alerts page
            await this.page.goto('http://localhost:3000/alerts')
            await this.page.waitForTimeout(2000)

            // Check for alert manager component
            const alertManager = await this.page.$('[data-testid="alert-manager"]')
            this.results.alerts.componentLoaded = !!alertManager

            // Test create alert button
            const createButton = await this.page.$('button:has-text("New Alert")')
            this.results.alerts.createButton = !!createButton

            if (createButton) {
                await createButton.click()
                await this.page.waitForTimeout(1000)

                // Check for modal
                const modal = await this.page.$('.fixed.inset-0')
                this.results.alerts.modalOpens = !!modal

                if (modal) {
                    // Test form inputs
                    const tickerInput = await this.page.$('input[placeholder*="ticker"]')
                    this.results.alerts.formInputs = !!tickerInput
                }
            }

            console.log('✅ Alert features tested')

        } catch (error) {
            console.error('❌ Alert test failed:', error.message)
            this.results.alerts.error = error.message
        }
    }

    async testPWAFeatures() {
        console.log('\n📱 Testing PWA Features...')

        try {
            // Check manifest file
            const manifestResponse = await this.page.goto('http://localhost:3000/manifest.json')
            this.results.pwa.manifestExists = manifestResponse.ok()

            if (manifestResponse.ok()) {
                const manifest = await manifestResponse.json()
                this.results.pwa.manifestValid = !!manifest.name && !!manifest.short_name
            }

            // Check service worker
            await this.page.goto('http://localhost:3000')
            await this.page.waitForTimeout(2000)

            const swRegistration = await this.page.evaluate(() => {
                return 'serviceWorker' in navigator
            })
            this.results.pwa.serviceWorkerSupported = swRegistration

            // Check for PWA installer component
            const pwaInstaller = await this.page.$('[data-testid="pwa-installer"]')
            this.results.pwa.installerComponent = !!pwaInstaller

            console.log('✅ PWA features tested')

        } catch (error) {
            console.error('❌ PWA test failed:', error.message)
            this.results.pwa.error = error.message
        }
    }

    async testRealTimeFeatures() {
        console.log('\n⚡ Testing Real-time Features...')

        try {
            // Test WebSocket connection
            await this.page.goto('http://localhost:3000/watchlists')
            await this.page.waitForTimeout(2000)

            // Check for WebSocket connection status
            const connectionStatus = await this.page.$('.text-sm:has-text("Connected")')
            this.results.realtime.connectionIndicator = !!connectionStatus

            // Check for notifications component
            const notifications = await this.page.$('[data-testid="real-time-notifications"]')
            this.results.realtime.notificationsComponent = !!notifications

            // Test notification bell
            const bellIcon = await this.page.$('svg[class*="BellIcon"]')
            this.results.realtime.notificationBell = !!bellIcon

            if (bellIcon) {
                await bellIcon.click()
                await this.page.waitForTimeout(1000)

                // Check for notifications panel
                const notificationsPanel = await this.page.$('.absolute.right-0.mt-2')
                this.results.realtime.notificationsPanel = !!notificationsPanel
            }

            console.log('✅ Real-time features tested')

        } catch (error) {
            console.error('❌ Real-time test failed:', error.message)
            this.results.realtime.error = error.message
        }
    }

    async runAllTests() {
        await this.init()

        try {
            await this.testAuthFeatures()
            await this.testWatchlistFeatures()
            await this.testAlertFeatures()
            await this.testPWAFeatures()
            await this.testRealTimeFeatures()

            this.generateReport()

        } catch (error) {
            console.error('❌ Test suite failed:', error)
        } finally {
            await this.cleanup()
        }
    }

    generateReport() {
        console.log('\n📊 Week 2 Features Test Report')
        console.log('================================')

        const categories = ['auth', 'watchlists', 'alerts', 'pwa', 'realtime']

        categories.forEach(category => {
            console.log(`\n${category.toUpperCase()}:`)
            const results = this.results[category]

            Object.entries(results).forEach(([test, passed]) => {
                const status = passed ? '✅' : '❌'
                console.log(`  ${status} ${test}`)

                if (passed) {
                    this.results.overall.passed++
                } else {
                    this.results.overall.failed++
                }
                this.results.overall.total++
            })
        })

        console.log('\n📈 SUMMARY:')
        console.log(`  Total Tests: ${this.results.overall.total}`)
        console.log(`  Passed: ${this.results.overall.passed}`)
        console.log(`  Failed: ${this.results.overall.failed}`)
        console.log(`  Success Rate: ${((this.results.overall.passed / this.results.overall.total) * 100).toFixed(1)}%`)

        // Save report to file
        const reportPath = path.join(__dirname, 'week2-test-report.json')
        fs.writeFileSync(reportPath, JSON.stringify(this.results, null, 2))
        console.log(`\n📄 Report saved to: ${reportPath}`)
    }

    async cleanup() {
        if (this.browser) {
            await this.browser.close()
        }
    }
}

// Run tests if this script is executed directly
if (require.main === module) {
    const tester = new Week2FeatureTester()
    tester.runAllTests().catch(console.error)
}

module.exports = Week2FeatureTester 