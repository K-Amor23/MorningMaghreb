import React, { useState, useEffect } from 'react'
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  ScrollView,
  Alert,
  StyleSheet,
  KeyboardAvoidingView,
  Platform,
} from 'react-native'
import { SafeAreaView } from 'react-native-safe-area-context'
import { useStore } from '../store/useStore'
import { authService } from '../services/auth'

type AuthMode = 'signin' | 'signup' | 'forgot'

const AuthScreen: React.FC = () => {
  const { setUser, setAuthenticated, setBiometricEnabled, authLoading } = useStore()
  const [mode, setMode] = useState<AuthMode>('signin')
  const [loading, setLoading] = useState(false)
  const [showPassword, setShowPassword] = useState(false)
  const [biometricSupported, setBiometricSupported] = useState(false)
  const [biometricEnrolled, setBiometricEnrolled] = useState(false)

  const [formData, setFormData] = useState({
    email: '',
    password: '',
    confirmPassword: '',
    name: '',
  })

  useEffect(() => {
    checkBiometricSupport()
  }, [])

  const checkBiometricSupport = async () => {
    try {
      const { hasHardware, isEnrolled } = await authService.checkBiometricSupport()
      setBiometricSupported(hasHardware)
      setBiometricEnrolled(isEnrolled)
    } catch (error) {
      console.error('Error checking biometric support:', error)
    }
  }

  const handleInputChange = (field: string, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }))
  }

  const handleSignIn = async () => {
    if (!formData.email || !formData.password) {
      Alert.alert('Error', 'Please fill in all fields')
      return
    }

    setLoading(true)
    try {
      const user = await authService.signInWithEmail(formData.email, formData.password)
      if (user) {
        setUser(user)
        setAuthenticated(true)
        
        // Check if biometric is enabled
        const biometricEnabled = await authService.isBiometricEnabled()
        setBiometricEnabled(biometricEnabled)
      }
    } catch (error: any) {
      Alert.alert('Sign In Error', error.message || 'Failed to sign in')
    } finally {
      setLoading(false)
    }
  }

  const handleSignUp = async () => {
    if (!formData.email || !formData.password || !formData.confirmPassword) {
      Alert.alert('Error', 'Please fill in all fields')
      return
    }

    if (formData.password !== formData.confirmPassword) {
      Alert.alert('Error', 'Passwords do not match')
      return
    }

    if (formData.password.length < 6) {
      Alert.alert('Error', 'Password must be at least 6 characters')
      return
    }

    setLoading(true)
    try {
      const user = await authService.signUpWithEmail(
        formData.email,
        formData.password,
        formData.name
      )
      if (user) {
        setUser(user)
        setAuthenticated(true)
      }
    } catch (error: any) {
      Alert.alert('Sign Up Error', error.message || 'Failed to sign up')
    } finally {
      setLoading(false)
    }
  }

  const handleBiometricSignIn = async () => {
    setLoading(true)
    try {
      const user = await authService.signInWithBiometric()
      if (user) {
        setUser(user)
        setAuthenticated(true)
      }
    } catch (error: any) {
      Alert.alert('Biometric Error', error.message || 'Biometric authentication failed')
    } finally {
      setLoading(false)
    }
  }

  const handleForgotPassword = async () => {
    if (!formData.email) {
      Alert.alert('Error', 'Please enter your email address')
      return
    }

    setLoading(true)
    try {
      await authService.resetPassword(formData.email)
      Alert.alert(
        'Password Reset',
        'If an account exists with this email, you will receive password reset instructions.',
        [{ text: 'OK', onPress: () => setMode('signin') }]
      )
    } catch (error: any) {
      Alert.alert('Error', error.message || 'Failed to send reset email')
    } finally {
      setLoading(false)
    }
  }

  const canUseBiometric = biometricSupported && biometricEnrolled

  return (
    <SafeAreaView style={styles.container}>
      <KeyboardAvoidingView
        behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
        style={styles.keyboardView}
      >
        <ScrollView contentContainerStyle={styles.scrollContent}>
          {/* Header */}
          <View style={styles.header}>
            <Text style={styles.logo}>📈</Text>
            <Text style={styles.title}>Casablanca Insight</Text>
            <Text style={styles.subtitle}>
              {mode === 'signin' ? 'Sign in to your account' :
               mode === 'signup' ? 'Create your account' :
               'Reset your password'}
            </Text>
          </View>

          {/* Biometric Sign In */}
          {mode === 'signin' && canUseBiometric && (
            <TouchableOpacity
              style={styles.biometricButton}
              onPress={handleBiometricSignIn}
              disabled={loading}
            >
              <Text style={styles.biometricIcon}>
                {authService.getBiometricType() === 'FaceID' ? '👁️' : '👆'}
              </Text>
              <Text style={styles.biometricText}>
                Sign in with {authService.getBiometricType()}
              </Text>
            </TouchableOpacity>
          )}

          {/* Divider */}
          {mode === 'signin' && canUseBiometric && (
            <View style={styles.divider}>
              <View style={styles.dividerLine} />
              <Text style={styles.dividerText}>or</Text>
              <View style={styles.dividerLine} />
            </View>
          )}

          {/* Form */}
          <View style={styles.form}>
            {mode === 'signup' && (
              <TextInput
                style={styles.input}
                placeholder="Full Name"
                value={formData.name}
                onChangeText={(value) => handleInputChange('name', value)}
                autoCapitalize="words"
                autoCorrect={false}
              />
            )}

            <TextInput
              style={styles.input}
              placeholder="Email Address"
              value={formData.email}
              onChangeText={(value) => handleInputChange('email', value)}
              keyboardType="email-address"
              autoCapitalize="none"
              autoCorrect={false}
            />

            {mode !== 'forgot' && (
              <View style={styles.passwordContainer}>
                <TextInput
                  style={[styles.input, styles.passwordInput]}
                  placeholder="Password"
                  value={formData.password}
                  onChangeText={(value) => handleInputChange('password', value)}
                  secureTextEntry={!showPassword}
                  autoCapitalize="none"
                  autoCorrect={false}
                />
                <TouchableOpacity
                  style={styles.eyeButton}
                  onPress={() => setShowPassword(!showPassword)}
                >
                  <Text style={styles.eyeIcon}>{showPassword ? '👁️' : '👁️‍🗨️'}</Text>
                </TouchableOpacity>
              </View>
            )}

            {mode === 'signup' && (
              <TextInput
                style={styles.input}
                placeholder="Confirm Password"
                value={formData.confirmPassword}
                onChangeText={(value) => handleInputChange('confirmPassword', value)}
                secureTextEntry={!showPassword}
                autoCapitalize="none"
                autoCorrect={false}
              />
            )}

            {/* Submit Button */}
            <TouchableOpacity
              style={[styles.submitButton, loading && styles.submitButtonDisabled]}
              onPress={
                mode === 'signin' ? handleSignIn :
                mode === 'signup' ? handleSignUp :
                handleForgotPassword
              }
              disabled={loading}
            >
              <Text style={styles.submitButtonText}>
                {loading ? 'Loading...' :
                 mode === 'signin' ? 'Sign In' :
                 mode === 'signup' ? 'Sign Up' :
                 'Send Reset Email'}
              </Text>
            </TouchableOpacity>

            {/* Mode Switcher */}
            <View style={styles.modeSwitcher}>
              {mode === 'signin' ? (
                <>
                  <TouchableOpacity onPress={() => setMode('forgot')}>
                    <Text style={styles.linkText}>Forgot Password?</Text>
                  </TouchableOpacity>
                  <TouchableOpacity onPress={() => setMode('signup')}>
                    <Text style={styles.linkText}>Don't have an account? Sign Up</Text>
                  </TouchableOpacity>
                </>
              ) : mode === 'signup' ? (
                <TouchableOpacity onPress={() => setMode('signin')}>
                  <Text style={styles.linkText}>Already have an account? Sign In</Text>
                </TouchableOpacity>
              ) : (
                <TouchableOpacity onPress={() => setMode('signin')}>
                  <Text style={styles.linkText}>Back to Sign In</Text>
                </TouchableOpacity>
              )}
            </View>
          </View>
        </ScrollView>
      </KeyboardAvoidingView>
    </SafeAreaView>
  )
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f8fafc',
  },
  keyboardView: {
    flex: 1,
  },
  scrollContent: {
    flexGrow: 1,
    justifyContent: 'center',
    padding: 20,
  },
  header: {
    alignItems: 'center',
    marginBottom: 40,
  },
  logo: {
    fontSize: 48,
    marginBottom: 16,
  },
  title: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#1e293b',
    marginBottom: 8,
  },
  subtitle: {
    fontSize: 16,
    color: '#64748b',
    textAlign: 'center',
  },
  biometricButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: '#1e3a8a',
    paddingVertical: 16,
    paddingHorizontal: 24,
    borderRadius: 12,
    marginBottom: 24,
  },
  biometricIcon: {
    fontSize: 20,
    marginRight: 8,
  },
  biometricText: {
    color: '#ffffff',
    fontSize: 16,
    fontWeight: '600',
  },
  divider: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 24,
  },
  dividerLine: {
    flex: 1,
    height: 1,
    backgroundColor: '#e2e8f0',
  },
  dividerText: {
    marginHorizontal: 16,
    color: '#64748b',
    fontSize: 14,
  },
  form: {
    gap: 16,
  },
  input: {
    backgroundColor: '#ffffff',
    borderWidth: 1,
    borderColor: '#e2e8f0',
    borderRadius: 12,
    paddingHorizontal: 16,
    paddingVertical: 16,
    fontSize: 16,
    color: '#1e293b',
  },
  passwordContainer: {
    position: 'relative',
  },
  passwordInput: {
    paddingRight: 50,
  },
  eyeButton: {
    position: 'absolute',
    right: 16,
    top: 16,
  },
  eyeIcon: {
    fontSize: 20,
  },
  submitButton: {
    backgroundColor: '#1e3a8a',
    paddingVertical: 16,
    borderRadius: 12,
    alignItems: 'center',
    marginTop: 8,
  },
  submitButtonDisabled: {
    backgroundColor: '#94a3b8',
  },
  submitButtonText: {
    color: '#ffffff',
    fontSize: 16,
    fontWeight: '600',
  },
  modeSwitcher: {
    alignItems: 'center',
    gap: 8,
    marginTop: 24,
  },
  linkText: {
    color: '#1e3a8a',
    fontSize: 14,
    textDecorationLine: 'underline',
  },
})

export default AuthScreen 