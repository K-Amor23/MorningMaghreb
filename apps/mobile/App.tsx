import React from 'react'
import { NavigationContainer } from '@react-navigation/native'
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs'
import { SafeAreaProvider } from 'react-native-safe-area-context'
import { Text } from 'react-native'

// Import screens
import HomeScreen from './src/screens/HomeScreen'
import MarketsScreen from './src/screens/MarketsScreen'
import NewsScreen from './src/screens/NewsScreen'
import SettingsScreen from './src/screens/SettingsScreen'

const Tab = createBottomTabNavigator()

export default function App() {
  return (
    <SafeAreaProvider>
      <NavigationContainer>
        <Tab.Navigator
          screenOptions={({ route }) => ({
            tabBarIcon: ({ focused, color, size }) => {
              let iconName

              if (route.name === 'Home') {
                iconName = focused ? '🏠' : '🏠'
              } else if (route.name === 'Markets') {
                iconName = focused ? '📈' : '📈'
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
      </NavigationContainer>
    </SafeAreaProvider>
  )
}
