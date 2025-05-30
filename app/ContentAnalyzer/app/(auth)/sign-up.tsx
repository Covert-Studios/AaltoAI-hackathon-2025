import * as React from 'react'
import { Text, TextInput, TouchableOpacity, View, StyleSheet } from 'react-native'
import { useSignUp } from '@clerk/clerk-expo'
import { Link, useRouter } from 'expo-router'

export default function SignUpScreen() {
  const { isLoaded, signUp, setActive } = useSignUp()
  const router = useRouter()

  const [emailAddress, setEmailAddress] = React.useState('')
  const [password, setPassword] = React.useState('')
  const [pendingVerification, setPendingVerification] = React.useState(false)
  const [code, setCode] = React.useState('')

  const onSignUpPress = async () => {
    if (!isLoaded) return
    try {
      await signUp.create({
        emailAddress,
        password,
      })
      await signUp.prepareEmailAddressVerification({ strategy: 'email_code' })
      setPendingVerification(true)
    } catch (err) {
      console.error(JSON.stringify(err, null, 2))
    }
  }

  const onVerifyPress = async () => {
    if (!isLoaded) return
    try {
      const signUpAttempt = await signUp.attemptEmailAddressVerification({
        code,
      })
      if (signUpAttempt.status === 'complete') {
        await setActive({ session: signUpAttempt.createdSessionId })
        router.replace('/')
      } else {
        console.error(JSON.stringify(signUpAttempt, null, 2))
      }
    } catch (err) {
      console.error(JSON.stringify(err, null, 2))
    }
  }

  if (pendingVerification) {
    return (
      <View style={styles.container}>
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
      <Text style={styles.title}>Sign up</Text>
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
})