import React, { useEffect } from 'react'
import { NavigationContainer } from '@react-navigation/native'
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs'
import { createStackNavigator } from '@react-navigation/stack'
import { SafeAreaProvider } from 'react-native-safe-area-context'
import { Text, View, StyleSheet } from 'react-native'
import { useStore } from './src/store/useStore'

// Import screens
import HomeScreen from './src/screens/HomeScreen'
import MarketsScreen from './src/screens/MarketsScreen'
import NewsScreen from './src/screens/NewsScreen'
import SettingsScreen from './src/screens/SettingsScreen'
import AuthScreen from './src/screens/AuthScreen'
import PortfolioScreen from './src/screens/PortfolioScreen'

const Tab = createBottomTabNavigator()
const Stack = createStackNavigator()

function TabNavigator() {
  return (
    <Tab.Navigator
      screenOptions={({ route }) => ({
        tabBarIcon: ({ focused, color, size }) => {
          let iconName

          if (route.name === 'Home') {
            iconName = focused ? '🏠' : '🏠'
          } else if (route.name === 'Markets') {
            iconName = focused ? '📈' : '📈'
          } else if (route.name === 'Portfolio') {
            iconName = focused ? '💼' : '💼'
          } else if (route.name === 'News') {
            iconName = focused ? '📰' : '📰'
          } else if (route.name === 'Settings') {
            iconName = focused ? '⚙️' : '⚙️'
          }

          return <Text style={{ fontSize: size, color }}>{iconName}</Text>
        },
        tabBarActiveTintColor: '#1e3a8a',
        tabBarInactiveTintColor: '#6b7280',
        tabBarStyle: {
          backgroundColor: 'white',
          borderTopWidth: 1,
          borderTopColor: '#e5e7eb',
          paddingBottom: 5,
          paddingTop: 5,
          height: 60,
        },
        tabBarLabelStyle: {
          fontSize: 12,
          fontWeight: '500',
        },
        headerShown: false,
      })}
    >
      <Tab.Screen 
        name="Home" 
        component={HomeScreen}
        options={{
          title: 'Home',
        }}
      />
      <Tab.Screen 
        name="Markets" 
        component={MarketsScreen}
        options={{
          title: 'Markets',
        }}
      />
      <Tab.Screen 
        name="Portfolio" 
        component={PortfolioScreen}
        options={{
          title: 'Portfolio',
        }}
      />
      <Tab.Screen 
        name="News" 
        component={NewsScreen}
        options={{
          title: 'News',
        }}
      />
      <Tab.Screen 
        name="Settings" 
        component={SettingsScreen}
        options={{
          title: 'Settings',
        }}
      />
    </Tab.Navigator>
  )
}

function LoadingScreen() {
  return (
    <View style={styles.loadingContainer}>
      <Text style={styles.loadingIcon}>📈</Text>
      <Text style={styles.loadingText}>Casablanca Insight</Text>
      <Text style={styles.loadingSubtext}>Loading...</Text>
    </View>
  )
}

export default function App() {
  const { 
    isAuthenticated, 
    authLoading, 
    initializeApp,
    syncData,
    isOnline 
  } = useStore()

  useEffect(() => {
    // Initialize app on startup
    initializeApp()
  }, [])

  useEffect(() => {
    // Sync data when online status changes
    if (isOnline) {
      syncData()
    }
  }, [isOnline])

  // Show loading screen while initializing
  if (authLoading) {
    return (
      <SafeAreaProvider>
        <LoadingScreen />
      </SafeAreaProvider>
    )
  }

  return (
    <SafeAreaProvider>
      <NavigationContainer>
        <Stack.Navigator screenOptions={{ headerShown: false }}>
          {isAuthenticated ? (
            <Stack.Screen name="Main" component={TabNavigator} />
          ) : (
            <Stack.Screen name="Auth" component={AuthScreen} />
          )}
        </Stack.Navigator>
      </NavigationContainer>
    </SafeAreaProvider>
  )
}

const styles = StyleSheet.create({
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#f8fafc',
  },
  loadingIcon: {
    fontSize: 64,
    marginBottom: 16,
  },
  loadingText: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#1e293b',
    marginBottom: 8,
  },
  loadingSubtext: {
    fontSize: 16,
    color: '#64748b',
  },
})
