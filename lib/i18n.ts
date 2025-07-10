import i18n from 'i18next'
import { initReactI18next } from 'react-i18next'

const resources = {
  en: {
    translation: {
      // Navigation
      home: 'Home',
      dashboard: 'Dashboard',
      markets: 'Markets',
      portfolio: 'Portfolio',
      newsletter: 'Newsletter',
      settings: 'Settings',
      login: 'Login',
      signup: 'Sign Up',
      logout: 'Logout',
      
      // Common
      loading: 'Loading...',
      error: 'Error',
      success: 'Success',
      save: 'Save',
      cancel: 'Cancel',
      delete: 'Delete',
      edit: 'Edit',
      view: 'View',
      
      // Market Data
      price: 'Price',
      change: 'Change',
      volume: 'Volume',
      marketCap: 'Market Cap',
      peRatio: 'P/E Ratio',
      lastUpdate: 'Last Update',
      
      // Portfolio
      holdings: 'Holdings',
      performance: 'Performance',
      unrealizedPnL: 'Unrealized P&L',
      totalValue: 'Total Value',
      
      // Newsletter
      morningMaghreb: 'Morning Maghreb',
      subscribeNewsletter: 'Subscribe to Newsletter',
      unsubscribe: 'Unsubscribe',
      
      // Plans
      freePlan: 'Free Plan',
      proPlan: 'Pro Plan',
      upgrade: 'Upgrade',
      manageBilling: 'Manage Billing',
      
      // Time periods
      today: 'Today',
      week: '1W',
      month: '1M',
      year: '1Y',
      all: 'All',
    },
  },
  fr: {
    translation: {
      // Navigation
      home: 'Accueil',
      dashboard: 'Tableau de bord',
      markets: 'Marchés',
      portfolio: 'Portefeuille',
      newsletter: 'Newsletter',
      settings: 'Paramètres',
      login: 'Connexion',
      signup: 'S\'inscrire',
      logout: 'Déconnexion',
      
      // Common
      loading: 'Chargement...',
      error: 'Erreur',
      success: 'Succès',
      save: 'Enregistrer',
      cancel: 'Annuler',
      delete: 'Supprimer',
      edit: 'Modifier',
      view: 'Voir',
      
      // Market Data
      price: 'Prix',
      change: 'Variation',
      volume: 'Volume',
      marketCap: 'Capitalisation',
      peRatio: 'P/E Ratio',
      lastUpdate: 'Dernière MAJ',
      
      // Portfolio
      holdings: 'Positions',
      performance: 'Performance',
      unrealizedPnL: 'P&L Latents',
      totalValue: 'Valeur Totale',
      
      // Newsletter
      morningMaghreb: 'Morning Maghreb',
      subscribeNewsletter: 'S\'abonner à la Newsletter',
      unsubscribe: 'Se désabonner',
      
      // Plans
      freePlan: 'Plan Gratuit',
      proPlan: 'Plan Pro',
      upgrade: 'Mettre à niveau',
      manageBilling: 'Gérer la facturation',
      
      // Time periods
      today: 'Aujourd\'hui',
      week: '1S',
      month: '1M',
      year: '1A',
      all: 'Tout',
    },
  },
  ar: {
    translation: {
      // Navigation
      home: 'الرئيسية',
      dashboard: 'لوحة التحكم',
      markets: 'الأسواق',
      portfolio: 'المحفظة',
      newsletter: 'النشرة الإخبارية',
      settings: 'الإعدادات',
      login: 'تسجيل الدخول',
      signup: 'التسجيل',
      logout: 'تسجيل الخروج',
      
      // Common
      loading: 'جاري التحميل...',
      error: 'خطأ',
      success: 'نجح',
      save: 'حفظ',
      cancel: 'إلغاء',
      delete: 'حذف',
      edit: 'تعديل',
      view: 'عرض',
      
      // Market Data
      price: 'السعر',
      change: 'التغيير',
      volume: 'الحجم',
      marketCap: 'القيمة السوقية',
      peRatio: 'نسبة السعر للأرباح',
      lastUpdate: 'آخر تحديث',
      
      // Portfolio
      holdings: 'الحيازات',
      performance: 'الأداء',
      unrealizedPnL: 'الأرباح غير المحققة',
      totalValue: 'القيمة الإجمالية',
      
      // Newsletter
      morningMaghreb: 'صباح المغرب',
      subscribeNewsletter: 'اشترك في النشرة الإخبارية',
      unsubscribe: 'إلغاء الاشتراك',
      
      // Plans
      freePlan: 'الخطة المجانية',
      proPlan: 'الخطة المميزة',
      upgrade: 'ترقية',
      manageBilling: 'إدارة الفواتير',
      
      // Time periods
      today: 'اليوم',
      week: '1أ',
      month: '1ش',
      year: '1س',
      all: 'الكل',
    },
  },
}

i18n
  .use(initReactI18next)
  .init({
    resources,
    lng: 'en',
    fallbackLng: 'en',
    interpolation: {
      escapeValue: false,
    },
  })

export default i18n