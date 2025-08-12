import i18n from 'i18next'
import { initReactI18next } from 'react-i18next'

// Import translations
const resources = {
  en: {
    translation: {
      // Common
      'common.loading': 'Loading...',
      'common.error': 'An error occurred',
      'common.success': 'Success',
      'common.save': 'Save',
      'common.cancel': 'Cancel',
      'common.edit': 'Edit',
      'common.delete': 'Delete',
      'common.back': 'Back',
      'common.next': 'Next',
      'common.previous': 'Previous',

      // Navigation
      'nav.home': 'Home',
      'nav.markets': 'Markets',
      'nav.portfolio': 'Portfolio',
      'nav.news': 'News',
      'nav.newsletter': 'Newsletter',
      'nav.compliance': 'Market Guide',
      'nav.advanced': 'Advanced',
      'nav.premium': 'Premium',
      'nav.admin': 'Admin',

      // Markets
      'markets.stocks': 'Stocks',
      'markets.bonds': 'Bonds',
      'markets.etfs': 'ETFs',
      'markets.macro': 'Macro Data',
      'markets.gdp': 'GDP',
      'markets.interest_rates': 'Interest Rates',
      'markets.inflation': 'Inflation',
      'markets.exchange_rates': 'Exchange Rates',
      'markets.trade_balance': 'Trade Balance',

      // Portfolio
      'portfolio.title': 'Portfolio',
      'portfolio.add_holding': 'Add Holding',
      'portfolio.total_value': 'Total Value',
      'portfolio.daily_change': 'Daily Change',
      'portfolio.ytd_return': 'YTD Return',

      // News
      'news.title': 'News',
      'news.latest': 'Latest News',
      'news.trending': 'Trending',
      'news.market_news': 'Market News',
      'news.economic_news': 'Economic News',

      // Newsletter
      'newsletter.title': 'Newsletter',
      'newsletter.subscribe': 'Subscribe',
      'newsletter.unsubscribe': 'Unsubscribe',
      'newsletter.email': 'Email Address',

      // Auth
      'auth.sign_in': 'Sign In',
      'auth.sign_up': 'Sign Up',
      'auth.sign_out': 'Sign Out',
      'auth.email': 'Email',
      'auth.password': 'Password',
      'auth.confirm_password': 'Confirm Password',
      'auth.forgot_password': 'Forgot Password?',
      'auth.remember_me': 'Remember me',

      // Dashboard
      'dashboard.title': 'Dashboard',
      'dashboard.welcome': 'Welcome to Morning Maghreb',
      'dashboard.quick_actions': 'Quick Actions',
      'dashboard.recent_activity': 'Recent Activity',

      // Settings
      'settings.title': 'Settings',
      'settings.profile': 'Profile',
      'settings.notifications': 'Notifications',
      'settings.security': 'Security',
      'settings.language': 'Language',

      // Language names
      'language.english': 'English',
      'language.french': 'Français',
      'language.arabic': 'العربية',

      // Theme
      'theme.light': 'Light',
      'theme.dark': 'Dark',
      'theme.auto': 'Auto',

      // Notifications
      'notifications.title': 'Notifications',
      'notifications.mark_all_read': 'Mark all as read',
      'notifications.no_notifications': 'No notifications',

      // Search
      'search.placeholder': 'Search companies, markets...',
      'search.no_results': 'No results found',
      'search.recent_searches': 'Recent searches',

      // Footer
      'footer.about': 'About',
      'footer.contact': 'Contact',
      'footer.privacy': 'Privacy',
      'footer.terms': 'Terms',
      'footer.copyright': '© 2024 Morning Maghreb. All rights reserved.',
    }
  },
  fr: {
    translation: {
      // Common
      'common.loading': 'Chargement...',
      'common.error': 'Une erreur s\'est produite',
      'common.success': 'Succès',
      'common.save': 'Enregistrer',
      'common.cancel': 'Annuler',
      'common.edit': 'Modifier',
      'common.delete': 'Supprimer',
      'common.back': 'Retour',
      'common.next': 'Suivant',
      'common.previous': 'Précédent',

      // Navigation
      'nav.home': 'Accueil',
      'nav.markets': 'Marchés',
      'nav.portfolio': 'Portefeuille',
      'nav.news': 'Actualités',
      'nav.newsletter': 'Newsletter',
      'nav.compliance': 'Guide du Marché',
      'nav.advanced': 'Avancé',
      'nav.premium': 'Premium',
      'nav.admin': 'Admin',

      // Markets
      'markets.stocks': 'Actions',
      'markets.bonds': 'Obligations',
      'markets.etfs': 'ETF',
      'markets.macro': 'Données Macro',
      'markets.gdp': 'PIB',
      'markets.interest_rates': 'Taux d\'Intérêt',
      'markets.inflation': 'Inflation',
      'markets.exchange_rates': 'Taux de Change',
      'markets.trade_balance': 'Balance Commerciale',

      // Portfolio
      'portfolio.title': 'Portefeuille',
      'portfolio.add_holding': 'Ajouter un Titre',
      'portfolio.total_value': 'Valeur Totale',
      'portfolio.daily_change': 'Variation Quotidienne',
      'portfolio.ytd_return': 'Rendement YTD',

      // News
      'news.title': 'Actualités',
      'news.latest': 'Dernières Actualités',
      'news.trending': 'Tendances',
      'news.market_news': 'Actualités du Marché',
      'news.economic_news': 'Actualités Économiques',

      // Newsletter
      'newsletter.title': 'Newsletter',
      'newsletter.subscribe': 'S\'abonner',
      'newsletter.unsubscribe': 'Se désabonner',
      'newsletter.email': 'Adresse Email',

      // Auth
      'auth.sign_in': 'Se Connecter',
      'auth.sign_up': 'S\'Inscrire',
      'auth.sign_out': 'Se Déconnecter',
      'auth.email': 'Email',
      'auth.password': 'Mot de Passe',
      'auth.confirm_password': 'Confirmer le Mot de Passe',
      'auth.forgot_password': 'Mot de Passe Oublié?',
      'auth.remember_me': 'Se souvenir de moi',

      // Dashboard
      'dashboard.title': 'Tableau de Bord',
      'dashboard.welcome': 'Bienvenue sur Morning Maghreb',
      'dashboard.quick_actions': 'Actions Rapides',
      'dashboard.recent_activity': 'Activité Récente',

      // Settings
      'settings.title': 'Paramètres',
      'settings.profile': 'Profil',
      'settings.notifications': 'Notifications',
      'settings.security': 'Sécurité',
      'settings.language': 'Langue',

      // Language names
      'language.english': 'English',
      'language.french': 'Français',
      'language.arabic': 'العربية',

      // Theme
      'theme.light': 'Clair',
      'theme.dark': 'Sombre',
      'theme.auto': 'Auto',

      // Notifications
      'notifications.title': 'Notifications',
      'notifications.mark_all_read': 'Marquer tout comme lu',
      'notifications.no_notifications': 'Aucune notification',

      // Search
      'search.placeholder': 'Rechercher des entreprises, marchés...',
      'search.no_results': 'Aucun résultat trouvé',
      'search.recent_searches': 'Recherches récentes',

      // Footer
      'footer.about': 'À Propos',
      'footer.contact': 'Contact',
      'footer.privacy': 'Confidentialité',
      'footer.terms': 'Conditions',
      'footer.copyright': '© 2024 Morning Maghreb. Tous droits réservés.',
    }
  },
  ar: {
    translation: {
      // Common
      'common.loading': 'جاري التحميل...',
      'common.error': 'حدث خطأ',
      'common.success': 'نجح',
      'common.save': 'حفظ',
      'common.cancel': 'إلغاء',
      'common.edit': 'تعديل',
      'common.delete': 'حذف',
      'common.back': 'رجوع',
      'common.next': 'التالي',
      'common.previous': 'السابق',

      // Navigation
      'nav.home': 'الرئيسية',
      'nav.markets': 'الأسواق',
      'nav.portfolio': 'المحفظة',
      'nav.news': 'الأخبار',
      'nav.newsletter': 'النشرة الإخبارية',
      'nav.compliance': 'دليل السوق',
      'nav.advanced': 'متقدم',
      'nav.premium': 'بريميوم',
      'nav.admin': 'المدير',

      // Markets
      'markets.stocks': 'الأسهم',
      'markets.bonds': 'السندات',
      'markets.etfs': 'صناديق الاستثمار',
      'markets.macro': 'البيانات الاقتصادية',
      'markets.gdp': 'الناتج المحلي الإجمالي',
      'markets.interest_rates': 'أسعار الفائدة',
      'markets.inflation': 'التضخم',
      'markets.exchange_rates': 'أسعار الصرف',
      'markets.trade_balance': 'الميزان التجاري',

      // Portfolio
      'portfolio.title': 'المحفظة',
      'portfolio.add_holding': 'إضافة حيازة',
      'portfolio.total_value': 'القيمة الإجمالية',
      'portfolio.daily_change': 'التغيير اليومي',
      'portfolio.ytd_return': 'العائد منذ بداية العام',

      // News
      'news.title': 'الأخبار',
      'news.latest': 'آخر الأخبار',
      'news.trending': 'رائج',
      'news.market_news': 'أخبار السوق',
      'news.economic_news': 'الأخبار الاقتصادية',

      // Newsletter
      'newsletter.title': 'النشرة الإخبارية',
      'newsletter.subscribe': 'اشتراك',
      'newsletter.unsubscribe': 'إلغاء الاشتراك',
      'newsletter.email': 'البريد الإلكتروني',

      // Auth
      'auth.sign_in': 'تسجيل الدخول',
      'auth.sign_up': 'إنشاء حساب',
      'auth.sign_out': 'تسجيل الخروج',
      'auth.email': 'البريد الإلكتروني',
      'auth.password': 'كلمة المرور',
      'auth.confirm_password': 'تأكيد كلمة المرور',
      'auth.forgot_password': 'نسيت كلمة المرور؟',
      'auth.remember_me': 'تذكرني',

      // Dashboard
      'dashboard.title': 'لوحة التحكم',
      'dashboard.welcome': 'مرحباً بك في مورنينغ مغرب',
      'dashboard.quick_actions': 'الإجراءات السريعة',
      'dashboard.recent_activity': 'النشاط الأخير',

      // Settings
      'settings.title': 'الإعدادات',
      'settings.profile': 'الملف الشخصي',
      'settings.notifications': 'الإشعارات',
      'settings.security': 'الأمان',
      'settings.language': 'اللغة',

      // Language names
      'language.english': 'English',
      'language.french': 'Français',
      'language.arabic': 'العربية',

      // Theme
      'theme.light': 'فاتح',
      'theme.dark': 'داكن',
      'theme.auto': 'تلقائي',

      // Notifications
      'notifications.title': 'الإشعارات',
      'notifications.mark_all_read': 'تحديد الكل كمقروء',
      'notifications.no_notifications': 'لا توجد إشعارات',

      // Search
      'search.placeholder': 'البحث عن الشركات والأسواق...',
      'search.no_results': 'لم يتم العثور على نتائج',
      'search.recent_searches': 'البحث الأخير',

      // Footer
      'footer.about': 'حول',
      'footer.contact': 'اتصل بنا',
      'footer.privacy': 'الخصوصية',
      'footer.terms': 'الشروط',
      'footer.copyright': '© 2024 مورنينغ مغرب. جميع الحقوق محفوظة.',
    }
  }
}

i18n
  .use(initReactI18next)
  .init({
    resources,
    lng: 'en', // default language
    fallbackLng: 'en',
    interpolation: {
      escapeValue: false, // React already escapes values
    },
    detection: {
      order: ['localStorage', 'navigator'],
      caches: ['localStorage'],
    },
  })

export default i18n 