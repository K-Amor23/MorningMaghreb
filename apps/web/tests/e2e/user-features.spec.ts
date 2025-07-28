import { test, expect } from '@playwright/test';

test.describe('User Features E2E Tests', () => {
    const baseUrl = 'http://localhost:3000';
    const apiUrl = 'http://localhost:8000';

    test.describe('Authentication', () => {
        test('should register a new user', async ({ request }) => {
            const response = await request.post(`${apiUrl}/api/auth/register`, {
                data: {
                    email: 'test@example.com',
                    password: 'TestPassword123',
                    full_name: 'Test User',
                    language_preference: 'en'
                }
            });

            expect(response.status()).toBe(200);
            const data = await response.json();
            expect(data.user).toBeDefined();
            expect(data.access_token).toBeDefined();
            expect(data.refresh_token).toBeDefined();
            expect(data.user.email).toBe('test@example.com');
            expect(data.user.full_name).toBe('Test User');
        });

        test('should login an existing user', async ({ request }) => {
            const response = await request.post(`${apiUrl}/api/auth/login`, {
                data: {
                    email: 'test@example.com',
                    password: 'TestPassword123'
                }
            });

            expect(response.status()).toBe(200);
            const data = await response.json();
            expect(data.user).toBeDefined();
            expect(data.access_token).toBeDefined();
            expect(data.refresh_token).toBeDefined();
        });

        test('should get user profile', async ({ request }) => {
            // First login to get token
            const loginResponse = await request.post(`${apiUrl}/api/auth/login`, {
                data: {
                    email: 'test@example.com',
                    password: 'TestPassword123'
                }
            });

            const loginData = await loginResponse.json();
            const token = loginData.access_token;

            // Get profile
            const response = await request.get(`${apiUrl}/api/auth/profile`, {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });

            expect(response.status()).toBe(200);
            const data = await response.json();
            expect(data.email).toBe('test@example.com');
            expect(data.full_name).toBe('Test User');
        });

        test('should update user profile', async ({ request }) => {
            // First login to get token
            const loginResponse = await request.post(`${apiUrl}/api/auth/login`, {
                data: {
                    email: 'test@example.com',
                    password: 'TestPassword123'
                }
            });

            const loginData = await loginResponse.json();
            const token = loginData.access_token;

            // Update profile
            const response = await request.put(`${apiUrl}/api/auth/profile`, {
                headers: {
                    'Authorization': `Bearer ${token}`
                },
                data: {
                    full_name: 'Updated Test User',
                    language_preference: 'fr'
                }
            });

            expect(response.status()).toBe(200);
            const data = await response.json();
            expect(data.full_name).toBe('Updated Test User');
            expect(data.language_preference).toBe('fr');
        });

        test('should check auth status', async ({ request }) => {
            // First login to get token
            const loginResponse = await request.post(`${apiUrl}/api/auth/login`, {
                data: {
                    email: 'test@example.com',
                    password: 'TestPassword123'
                }
            });

            const loginData = await loginResponse.json();
            const token = loginData.access_token;

            // Check auth status
            const response = await request.get(`${apiUrl}/api/auth/status`, {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });

            expect(response.status()).toBe(200);
            const data = await response.json();
            expect(data.is_authenticated).toBe(true);
            expect(data.user).toBeDefined();
        });
    });

    test.describe('Watchlists', () => {
        let authToken: string;

        test.beforeEach(async ({ request }) => {
            // Login to get token
            const loginResponse = await request.post(`${apiUrl}/api/auth/login`, {
                data: {
                    email: 'test@example.com',
                    password: 'TestPassword123'
                }
            });

            const loginData = await loginResponse.json();
            authToken = loginData.access_token;
        });

        test('should create a new watchlist', async ({ request }) => {
            const response = await request.post(`${apiUrl}/api/watchlists`, {
                headers: {
                    'Authorization': `Bearer ${authToken}`
                },
                data: {
                    name: 'My Watchlist',
                    description: 'Test watchlist',
                    is_default: true
                }
            });

            expect(response.status()).toBe(200);
            const data = await response.json();
            expect(data.watchlist.name).toBe('My Watchlist');
            expect(data.watchlist.description).toBe('Test watchlist');
            expect(data.watchlist.is_default).toBe(true);
        });

        test('should get user watchlists', async ({ request }) => {
            const response = await request.get(`${apiUrl}/api/watchlists`, {
                headers: {
                    'Authorization': `Bearer ${authToken}`
                }
            });

            expect(response.status()).toBe(200);
            const data = await response.json();
            expect(data.watchlists).toBeDefined();
            expect(Array.isArray(data.watchlists)).toBe(true);
            expect(data.total_count).toBeGreaterThanOrEqual(0);
        });

        test('should get specific watchlist', async ({ request }) => {
            // First create a watchlist
            const createResponse = await request.post(`${apiUrl}/api/watchlists`, {
                headers: {
                    'Authorization': `Bearer ${authToken}`
                },
                data: {
                    name: 'Test Watchlist',
                    description: 'Test description'
                }
            });

            const createData = await createResponse.json();
            const watchlistId = createData.watchlist.id;

            // Get the watchlist
            const response = await request.get(`${apiUrl}/api/watchlists/${watchlistId}`, {
                headers: {
                    'Authorization': `Bearer ${authToken}`
                }
            });

            expect(response.status()).toBe(200);
            const data = await response.json();
            expect(data.watchlist.id).toBe(watchlistId);
            expect(data.watchlist.name).toBe('Test Watchlist');
        });

        test('should add item to watchlist', async ({ request }) => {
            // First create a watchlist
            const createResponse = await request.post(`${apiUrl}/api/watchlists`, {
                headers: {
                    'Authorization': `Bearer ${authToken}`
                },
                data: {
                    name: 'Test Watchlist',
                    description: 'Test description'
                }
            });

            const createData = await createResponse.json();
            const watchlistId = createData.watchlist.id;

            // Add item to watchlist
            const response = await request.post(`${apiUrl}/api/watchlists/${watchlistId}/items`, {
                headers: {
                    'Authorization': `Bearer ${authToken}`
                },
                data: {
                    ticker: 'IAM',
                    notes: 'Test note'
                }
            });

            expect(response.status()).toBe(200);
            const data = await response.json();
            expect(data.item.ticker).toBe('IAM');
            expect(data.item.notes).toBe('Test note');
        });

        test('should get watchlist items', async ({ request }) => {
            // First create a watchlist and add an item
            const createResponse = await request.post(`${apiUrl}/api/watchlists`, {
                headers: {
                    'Authorization': `Bearer ${authToken}`
                },
                data: {
                    name: 'Test Watchlist',
                    description: 'Test description'
                }
            });

            const createData = await createResponse.json();
            const watchlistId = createData.watchlist.id;

            await request.post(`${apiUrl}/api/watchlists/${watchlistId}/items`, {
                headers: {
                    'Authorization': `Bearer ${authToken}`
                },
                data: {
                    ticker: 'ATW',
                    notes: 'Test note'
                }
            });

            // Get watchlist items
            const response = await request.get(`${apiUrl}/api/watchlists/${watchlistId}/items`, {
                headers: {
                    'Authorization': `Bearer ${authToken}`
                }
            });

            expect(response.status()).toBe(200);
            const data = await response.json();
            expect(data.items).toBeDefined();
            expect(Array.isArray(data.items)).toBe(true);
            expect(data.total_count).toBeGreaterThan(0);
        });

        test('should update watchlist item', async ({ request }) => {
            // First create a watchlist and add an item
            const createResponse = await request.post(`${apiUrl}/api/watchlists`, {
                headers: {
                    'Authorization': `Bearer ${authToken}`
                },
                data: {
                    name: 'Test Watchlist',
                    description: 'Test description'
                }
            });

            const createData = await createResponse.json();
            const watchlistId = createData.watchlist.id;

            await request.post(`${apiUrl}/api/watchlists/${watchlistId}/items`, {
                headers: {
                    'Authorization': `Bearer ${authToken}`
                },
                data: {
                    ticker: 'BCP',
                    notes: 'Original note'
                }
            });

            // Update the item
            const response = await request.put(`${apiUrl}/api/watchlists/${watchlistId}/items/BCP`, {
                headers: {
                    'Authorization': `Bearer ${authToken}`
                },
                data: {
                    notes: 'Updated note'
                }
            });

            expect(response.status()).toBe(200);
            const data = await response.json();
            expect(data.item.ticker).toBe('BCP');
            expect(data.item.notes).toBe('Updated note');
        });

        test('should remove item from watchlist', async ({ request }) => {
            // First create a watchlist and add an item
            const createResponse = await request.post(`${apiUrl}/api/watchlists`, {
                headers: {
                    'Authorization': `Bearer ${authToken}`
                },
                data: {
                    name: 'Test Watchlist',
                    description: 'Test description'
                }
            });

            const createData = await createResponse.json();
            const watchlistId = createData.watchlist.id;

            await request.post(`${apiUrl}/api/watchlists/${watchlistId}/items`, {
                headers: {
                    'Authorization': `Bearer ${authToken}`
                },
                data: {
                    ticker: 'BMCE',
                    notes: 'Test note'
                }
            });

            // Remove the item
            const response = await request.delete(`${apiUrl}/api/watchlists/${watchlistId}/items/BMCE`, {
                headers: {
                    'Authorization': `Bearer ${authToken}`
                }
            });

            expect(response.status()).toBe(200);
            const data = await response.json();
            expect(data.message).toBe('Watchlist item removed successfully');
        });

        test('should update watchlist', async ({ request }) => {
            // First create a watchlist
            const createResponse = await request.post(`${apiUrl}/api/watchlists`, {
                headers: {
                    'Authorization': `Bearer ${authToken}`
                },
                data: {
                    name: 'Original Name',
                    description: 'Original description'
                }
            });

            const createData = await createResponse.json();
            const watchlistId = createData.watchlist.id;

            // Update the watchlist
            const response = await request.put(`${apiUrl}/api/watchlists/${watchlistId}`, {
                headers: {
                    'Authorization': `Bearer ${authToken}`
                },
                data: {
                    name: 'Updated Name',
                    description: 'Updated description'
                }
            });

            expect(response.status()).toBe(200);
            const data = await response.json();
            expect(data.watchlist.name).toBe('Updated Name');
            expect(data.watchlist.description).toBe('Updated description');
        });

        test('should delete watchlist', async ({ request }) => {
            // First create a watchlist
            const createResponse = await request.post(`${apiUrl}/api/watchlists`, {
                headers: {
                    'Authorization': `Bearer ${authToken}`
                },
                data: {
                    name: 'Test Watchlist',
                    description: 'Test description'
                }
            });

            const createData = await createResponse.json();
            const watchlistId = createData.watchlist.id;

            // Delete the watchlist
            const response = await request.delete(`${apiUrl}/api/watchlists/${watchlistId}`, {
                headers: {
                    'Authorization': `Bearer ${authToken}`
                }
            });

            expect(response.status()).toBe(200);
            const data = await response.json();
            expect(data.message).toBe('Watchlist deleted successfully');
        });
    });

    test.describe('Alerts', () => {
        let authToken: string;

        test.beforeEach(async ({ request }) => {
            // Login to get token
            const loginResponse = await request.post(`${apiUrl}/api/auth/login`, {
                data: {
                    email: 'test@example.com',
                    password: 'TestPassword123'
                }
            });

            const loginData = await loginResponse.json();
            authToken = loginData.access_token;
        });

        test('should create a new price alert', async ({ request }) => {
            const response = await request.post(`${apiUrl}/api/alerts`, {
                headers: {
                    'Authorization': `Bearer ${authToken}`
                },
                data: {
                    ticker: 'IAM',
                    alert_type: 'above',
                    target_value: 15.0,
                    notes: 'Test alert'
                }
            });

            expect(response.status()).toBe(200);
            const data = await response.json();
            expect(data.alert.ticker).toBe('IAM');
            expect(data.alert.alert_type).toBe('above');
            expect(data.alert.target_value).toBe(15.0);
            expect(data.alert.notes).toBe('Test alert');
            expect(data.alert.is_active).toBe(true);
        });

        test('should get user alerts', async ({ request }) => {
            const response = await request.get(`${apiUrl}/api/alerts`, {
                headers: {
                    'Authorization': `Bearer ${authToken}`
                }
            });

            expect(response.status()).toBe(200);
            const data = await response.json();
            expect(data.alerts).toBeDefined();
            expect(Array.isArray(data.alerts)).toBe(true);
            expect(data.total_count).toBeGreaterThanOrEqual(0);
        });

        test('should get specific alert', async ({ request }) => {
            // First create an alert
            const createResponse = await request.post(`${apiUrl}/api/alerts`, {
                headers: {
                    'Authorization': `Bearer ${authToken}`
                },
                data: {
                    ticker: 'ATW',
                    alert_type: 'below',
                    target_value: 40.0,
                    notes: 'Test alert'
                }
            });

            const createData = await createResponse.json();
            const alertId = createData.alert.id;

            // Get the alert
            const response = await request.get(`${apiUrl}/api/alerts/${alertId}`, {
                headers: {
                    'Authorization': `Bearer ${authToken}`
                }
            });

            expect(response.status()).toBe(200);
            const data = await response.json();
            expect(data.alert.id).toBe(alertId);
            expect(data.alert.ticker).toBe('ATW');
            expect(data.alert.alert_type).toBe('below');
        });

        test('should update alert', async ({ request }) => {
            // First create an alert
            const createResponse = await request.post(`${apiUrl}/api/alerts`, {
                headers: {
                    'Authorization': `Bearer ${authToken}`
                },
                data: {
                    ticker: 'BCP',
                    alert_type: 'above',
                    target_value: 20.0,
                    notes: 'Original note'
                }
            });

            const createData = await createResponse.json();
            const alertId = createData.alert.id;

            // Update the alert
            const response = await request.put(`${apiUrl}/api/alerts/${alertId}`, {
                headers: {
                    'Authorization': `Bearer ${authToken}`
                },
                data: {
                    target_value: 25.0,
                    notes: 'Updated note',
                    is_active: false
                }
            });

            expect(response.status()).toBe(200);
            const data = await response.json();
            expect(data.alert.target_value).toBe(25.0);
            expect(data.alert.notes).toBe('Updated note');
            expect(data.alert.is_active).toBe(false);
        });

        test('should delete alert', async ({ request }) => {
            // First create an alert
            const createResponse = await request.post(`${apiUrl}/api/alerts`, {
                headers: {
                    'Authorization': `Bearer ${authToken}`
                },
                data: {
                    ticker: 'BMCE',
                    alert_type: 'above',
                    target_value: 25.0,
                    notes: 'Test alert'
                }
            });

            const createData = await createResponse.json();
            const alertId = createData.alert.id;

            // Delete the alert
            const response = await request.delete(`${apiUrl}/api/alerts/${alertId}`, {
                headers: {
                    'Authorization': `Bearer ${authToken}`
                }
            });

            expect(response.status()).toBe(200);
            const data = await response.json();
            expect(data.message).toBe('Alert deleted successfully');
        });

        test('should trigger alerts check', async ({ request }) => {
            const response = await request.post(`${apiUrl}/api/alerts/trigger`, {
                headers: {
                    'Authorization': `Bearer ${authToken}`
                }
            });

            expect(response.status()).toBe(200);
            const data = await response.json();
            expect(data.triggered_alerts).toBeDefined();
            expect(Array.isArray(data.triggered_alerts)).toBe(true);
            expect(data.total_triggered).toBeGreaterThanOrEqual(0);
        });
    });

    test.describe('Error Handling', () => {
        test('should handle invalid authentication', async ({ request }) => {
            const response = await request.get(`${apiUrl}/api/auth/profile`, {
                headers: {
                    'Authorization': 'Bearer invalid_token'
                }
            });

            expect(response.status()).toBe(401);
        });

        test('should handle missing authentication', async ({ request }) => {
            const response = await request.get(`${apiUrl}/api/watchlists`);

            expect(response.status()).toBe(401);
        });

        test('should handle invalid watchlist ID', async ({ request }) => {
            // Login to get token
            const loginResponse = await request.post(`${apiUrl}/api/auth/login`, {
                data: {
                    email: 'test@example.com',
                    password: 'TestPassword123'
                }
            });

            const loginData = await loginResponse.json();
            const token = loginData.access_token;

            const response = await request.get(`${apiUrl}/api/watchlists/invalid-id`, {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });

            expect(response.status()).toBe(404);
        });

        test('should handle invalid alert ID', async ({ request }) => {
            // Login to get token
            const loginResponse = await request.post(`${apiUrl}/api/auth/login`, {
                data: {
                    email: 'test@example.com',
                    password: 'TestPassword123'
                }
            });

            const loginData = await loginResponse.json();
            const token = loginData.access_token;

            const response = await request.get(`${apiUrl}/api/alerts/invalid-id`, {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });

            expect(response.status()).toBe(404);
        });
    });
}); 