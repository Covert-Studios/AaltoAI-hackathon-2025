import { useSignIn } from '@clerk/clerk-expo'
import { Link, useRouter } from 'expo-router'
import { Text, TextInput, TouchableOpacity, View, StyleSheet, Modal, Animated } from 'react-native'
import React from 'react'
import { HeaderTitle } from '@react-navigation/elements'

export default function Page() {
  const { signIn, setActive, isLoaded } = useSignIn()
  const router = useRouter()

  const [emailAddress, setEmailAddress] = React.useState('')
  const [password, setPassword] = React.useState('')
  const [error, setError] = React.useState<string | null>(null)
  const [showError, setShowError] = React.useState(false)
  const fadeAnim = React.useRef(new Animated.Value(0)).current

  // Handle the submission of the sign-in form
  const onSignInPress = async () => {
    if (!isLoaded) return

    try {
      const signInAttempt = await signIn.create({
        identifier: emailAddress,
        password,
      })

      if (signInAttempt.status === 'complete') {
        await setActive({ session: signInAttempt.createdSessionId })
        router.replace('/')
      } else {
        // Show error if status isn't complete
        setError('Sign-in not complete. Please check your credentials or complete any required steps.')
        setShowError(true)
        Animated.timing(fadeAnim, {
          toValue: 1,
          duration: 300,
          useNativeDriver: true,
        }).start()
        console.error(JSON.stringify(signInAttempt, null, 2))
      }
    } catch (err: any) {
      // Show error popup with Clerk error message
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

  return (
    <View style={styles.container}>
      {/* Error Popup */}
      <Modal visible={showError} transparent animationType="none">
        <View style={styles.modalOverlay}>
          <Animated.View style={[styles.errorPopup, { opacity: fadeAnim }]}>
            <Text style={styles.errorTitle}>Sign In Error</Text>
            <Text style={styles.errorMessage}>{error}</Text>
            <TouchableOpacity style={styles.errorButton} onPress={handleCloseError}>
              <Text style={styles.errorButtonText}>Close</Text>
            </TouchableOpacity>
          </Animated.View>
        </View>
      </Modal>
      <HeaderTitle>Sign In</HeaderTitle>
      <Text style={{ color: '#444', fontSize: 16, marginBottom: 24 }}>
        Please enter your email and password to sign in to your account.
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
        secureTextEntry
        onChangeText={setPassword}
        style={styles.input}
      />
      <TouchableOpacity style={styles.button} onPress={onSignInPress}>
        <Text style={styles.buttonText}>Continue</Text>
      </TouchableOpacity>
      <View style={styles.footer}>
        <Text style={styles.footerText}>Don&apos;t have an account?</Text>
        <Link href="./sign-up" asChild>
          <TouchableOpacity>
            <Text style={styles.linkText}>Sign up</Text>
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