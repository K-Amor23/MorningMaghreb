// Password protection configuration
export const PASSWORD_PROTECTION_CONFIG = {
  // Set your desired password here
  PASSWORD: process.env.NEXT_PUBLIC_SITE_PASSWORD || 'morningmaghreb2024',
  
  // Enable/disable password protection
  ENABLED: process.env.NEXT_PUBLIC_ENABLE_PASSWORD_PROTECTION === 'true',
  
  // Session storage key
  SESSION_KEY: 'morningmaghreb_authenticated',
  
  // Auto-logout after inactivity (in minutes)
  AUTO_LOGOUT_MINUTES: 60,
}

// Helper function to check if password protection is enabled
export const isPasswordProtectionEnabled = () => {
  return PASSWORD_PROTECTION_CONFIG.ENABLED
}

// Helper function to get the correct password
export const getCorrectPassword = () => {
  return PASSWORD_PROTECTION_CONFIG.PASSWORD
} 