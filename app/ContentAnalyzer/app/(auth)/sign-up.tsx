import * as React from 'react'
import { Text, TextInput, TouchableOpacity, View, StyleSheet, Modal, Animated, ActivityIndicator } from 'react-native' // <-- add ActivityIndicator
import { useSignUp } from '@clerk/clerk-expo'
import { Link, useRouter } from 'expo-router'
import { HeaderTitle } from '@react-navigation/elements'

export default function SignUpScreen() {
  const { isLoaded, signUp, setActive } = useSignUp()
  const router = useRouter()

  const [emailAddress, setEmailAddress] = React.useState('')
  const [password, setPassword] = React.useState('')
  const [pendingVerification, setPendingVerification] = React.useState(false)
  const [code, setCode] = React.useState('')
  const [error, setError] = React.useState<string | null>(null)
  const [showError, setShowError] = React.useState(false)
  const fadeAnim = React.useRef(new Animated.Value(0)).current

  const [loading, setLoading] = React.useState(false)

  const onSignUpPress = async () => {
    if (!isLoaded) return
    setLoading(true)
    try {
      await signUp.create({
        emailAddress,
        password,
      })
      await signUp.prepareEmailAddressVerification({ strategy: 'email_code' })
      setPendingVerification(true)
    } catch (err: any) {
      let message = 'Unknown error'
      if (err && err.errors && err.errors[0] && err.errors[0].message) {
        message = err.errors[0].message
      } else if (err && err.message) {
        message = err.message
      }
      setError(message)
      setShowError(true)
      Animated.timing(fadeAnim, {
        toValue: 1,
        duration: 300,
        useNativeDriver: true,
      }).start()
      console.error(JSON.stringify(err, null, 2))
    } finally {
      setLoading(false)
    }
  }

  const onVerifyPress = async () => {
    if (!isLoaded) return
    setLoading(true)
    try {
      const signUpAttempt = await signUp.attemptEmailAddressVerification({
        code,
      })
      if (signUpAttempt.status === 'complete') {
        await setActive({ session: signUpAttempt.createdSessionId })
        router.replace('/')
      } else {
        setError('Verification not complete. Please check your code.')
        setShowError(true)
        Animated.timing(fadeAnim, {
          toValue: 1,
          duration: 300,
          useNativeDriver: true,
        }).start()
        console.error(JSON.stringify(signUpAttempt, null, 2))
      }
    } catch (err: any) {
      let message = 'Unknown error'
      if (err && err.errors && err.errors[0] && err.errors[0].message) {
        message = err.errors[0].message
      } else if (err && err.message) {
        message = err.message
      }
      setError(message)
      setShowError(true)
      Animated.timing(fadeAnim, {
        toValue: 1,
        duration: 300,
        useNativeDriver: true,
      }).start()
      console.error(JSON.stringify(err, null, 2))
    } finally {
      setLoading(false)
    }
  }

  const handleCloseError = () => {
    Animated.timing(fadeAnim, {
      toValue: 0,
      duration: 200,
      useNativeDriver: true,
    }).start(() => {
      setShowError(false)
      setError(null)
    })
  }

  if (loading) {
    return (
      <View style={styles.container}>
        <ActivityIndicator size="large" color="#3a86ff" />
        <Text style={{ marginTop: 18, color: '#3a86ff', fontSize: 18 }}>Please wait...</Text>
      </View>
    )
  }

  if (pendingVerification) {
    return (
      <View style={styles.container}>
        {/* Error Popup */}
        <Modal visible={showError} transparent animationType="none">
          <View style={styles.modalOverlay}>
            <Animated.View style={[styles.errorPopup, { opacity: fadeAnim }]}>
              <Text style={styles.errorTitle}>Verification Error</Text>
              <Text style={styles.errorMessage}>{error}</Text>
              <TouchableOpacity style={styles.errorButton} onPress={handleCloseError}>
                <Text style={styles.errorButtonText}>Close</Text>
              </TouchableOpacity>
            </Animated.View>
          </View>
        </Modal>
        <Text style={styles.title}>Verify your email</Text>
        <Text style={styles.subtitle}>
          Enter the verification code sent to your email.
        </Text>
        <TextInput
          value={code}
          placeholder="Verification code"
          placeholderTextColor="#888"
          onChangeText={setCode}
          style={styles.input}
          keyboardType="number-pad"
        />
        <TouchableOpacity style={styles.button} onPress={onVerifyPress}>
          <Text style={styles.buttonText}>Verify</Text>
        </TouchableOpacity>
      </View>
    )
  }

  return (
    <View style={styles.container}>
      {/* Error Popup */}
      <Modal visible={showError} transparent animationType="none">
        <View style={styles.modalOverlay}>
          <Animated.View style={[styles.errorPopup, { opacity: fadeAnim }]}>
            <Text style={styles.errorTitle}>Sign Up Error</Text>
            <Text style={styles.errorMessage}>{error}</Text>
            <TouchableOpacity style={styles.errorButton} onPress={handleCloseError}>
              <Text style={styles.errorButtonText}>Close</Text>
            </TouchableOpacity>
          </Animated.View>
        </View>
      </Modal>
      <HeaderTitle>Sign Up</HeaderTitle>
      <Text style={{ color: '#444', fontSize: 16, marginBottom: 24 }}>
        Please enter your email and password to create a new account.
      </Text>
      <TextInput
        autoCapitalize="none"
        value={emailAddress}
        placeholder="Email"
        placeholderTextColor="#888"
        onChangeText={setEmailAddress}
        style={styles.input}
        keyboardType="email-address"
      />
      <TextInput
        value={password}
        placeholder="Password"
        placeholderTextColor="#888"
        secureTextEntry={true}
        onChangeText={setPassword}
        style={styles.input}
      />
      <TouchableOpacity style={styles.button} onPress={onSignUpPress}>
        <Text style={styles.buttonText}>Continue</Text>
      </TouchableOpacity>
      <View style={styles.footer}>
        <Text style={styles.footerText}>Already have an account?</Text>
        <Link href="./sign-in" asChild>
          <TouchableOpacity>
            <Text style={styles.linkText}>Sign in</Text>
          </TouchableOpacity>
        </Link>
      </View>
    </View>
  )
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    padding: 28,
    backgroundColor: '#f8f9fa',
  },
  title: {
    fontSize: 32,
    fontWeight: '700',
    marginBottom: 18,
    color: '#22223b',
    alignSelf: 'center',
  },
  subtitle: {
    fontSize: 16,
    color: '#444',
    marginBottom: 18,
    textAlign: 'center',
  },
  input: {
    backgroundColor: '#fff',
    paddingHorizontal: 16,
    paddingVertical: 14,
    borderRadius: 10,
    fontSize: 16,
    marginBottom: 18,
    borderWidth: 1,
    borderColor: '#e0e1dd',
  },
  button: {
    backgroundColor: '#3a86ff',
    paddingVertical: 14,
    borderRadius: 10,
    alignItems: 'center',
    marginTop: 8,
    marginBottom: 18,
    shadowColor: '#3a86ff',
    shadowOpacity: 0.15,
    shadowRadius: 8,
    shadowOffset: { width: 0, height: 2 },
    elevation: 2,
  },
  buttonText: {
    color: '#fff',
    fontWeight: '600',
    fontSize: 18,
  },
  footer: {
    flexDirection: 'row',
    justifyContent: 'center',
    gap: 6,
  },
  footerText: {
    color: '#444',
    fontSize: 15,
  },
  linkText: {
    color: '#3a86ff',
    fontWeight: '600',
    fontSize: 15,
    marginLeft: 4,
  },
  // Error popup styles
  modalOverlay: {
    flex: 1,
    backgroundColor: 'rgba(0,0,0,0.18)',
    justifyContent: 'center',
    alignItems: 'center',
  },
  errorPopup: {
    backgroundColor: '#fff',
    borderRadius: 18,
    paddingVertical: 28,
    paddingHorizontal: 28,
    alignItems: 'center',
    elevation: 8,
    shadowColor: '#ff3a3a',
    shadowOpacity: 0.18,
    shadowRadius: 12,
    shadowOffset: { width: 0, height: 4 },
    minWidth: 260,
    maxWidth: 320,
  },
  errorTitle: {
    fontSize: 20,
    fontWeight: '700',
    color: '#ff3a3a',
    marginBottom: 8,
    textAlign: 'center',
  },
  errorMessage: {
    fontSize: 16,
    color: '#444',
    marginBottom: 18,
    textAlign: 'center',
  },
  errorButton: {
    backgroundColor: '#ff3a3a',
    borderRadius: 8,
    paddingVertical: 8,
    paddingHorizontal: 24,
  },
  errorButtonText: {
    color: '#fff',
    fontWeight: '600',
    fontSize: 16,
  },
})