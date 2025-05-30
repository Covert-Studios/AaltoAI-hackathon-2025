import { SignedIn, SignedOut, useUser } from '@clerk/clerk-expo'
import { Link, useRouter } from 'expo-router'
import { Text, View, StyleSheet, Animated } from 'react-native'
import { SignOutButton } from '@/app/components/SignOutButton'
import React from 'react'

export default function Page() {
  const { user, isSignedIn } = useUser()
  const router = useRouter()
  const [showWelcome, setShowWelcome] = React.useState(false)
  const fadeAnim = React.useRef(new Animated.Value(0)).current

  React.useEffect(() => {
    if (isSignedIn) {
      setShowWelcome(true)
      Animated.timing(fadeAnim, {
        toValue: 1,
        duration: 400,
        useNativeDriver: true,
      }).start()
      setTimeout(() => {
        Animated.timing(fadeAnim, {
          toValue: 0,
          duration: 400,
          useNativeDriver: true,
        }).start(() => {
          setShowWelcome(false)
          router.replace('/(tabs)/feed')
        })
      }, 1800)
    }
  }, [isSignedIn])

  return (
    <View style={styles.container}>
      <SignedIn>
        <View style={styles.tabContent}>
          <Text style={styles.greeting}>
            👋 Hello, {user?.emailAddresses[0].emailAddress}
          </Text>
          <Text style={styles.subtitle}>Welcome to Content Analyzer!</Text>
          <SignOutButton />
        </View>
      </SignedIn>
      <SignedOut>
        <View style={styles.signedOut}>
          <Text style={styles.signedOutText}>You are not signed in.</Text>
          <Link href="../(auth)/sign-in" style={styles.link}>
            <Text style={styles.linkText}>Sign in</Text>
          </Link>
          <Link href="../(auth)/sign-up" style={styles.link}>
            <Text style={styles.linkText}>Sign up</Text>
          </Link>
        </View>
      </SignedOut>
    </View>
  )
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f7fafc',
    paddingTop: 40,
    justifyContent: 'space-between',
  },
  tabContent: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
    gap: 16,
  },
  greeting: {
    fontSize: 22,
    fontWeight: 'bold',
    color: '#0a7ea4',
  },
  subtitle: {
    fontSize: 18,
    color: '#333',
    marginBottom: 16,
  },
  signedOut: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
    gap: 12,
  },
  signedOutText: {
    fontSize: 18,
    color: '#888',
    marginBottom: 12,
  },
  link: {
    marginVertical: 4,
  },
  linkText: {
    color: '#0a7ea4',
    fontWeight: 'bold',
    fontSize: 16,
  },
  modalOverlay: {
    flex: 1,
    backgroundColor: 'rgba(0,0,0,0.18)',
    justifyContent: 'center',
    alignItems: 'center',
  },
  welcomePopup: {
    backgroundColor: '#fff',
    borderRadius: 18,
    paddingVertical: 36,
    paddingHorizontal: 36,
    alignItems: 'center',
    elevation: 8,
    shadowColor: '#0a7ea4',
    shadowOpacity: 0.15,
    shadowRadius: 12,
    shadowOffset: { width: 0, height: 4 },
  },
  welcomeEmoji: {
    fontSize: 48,
    marginBottom: 8,
  },
  welcomeText: {
    fontSize: 22,
    fontWeight: '700',
    color: '#0a7ea4',
    textAlign: 'center',
  },
})