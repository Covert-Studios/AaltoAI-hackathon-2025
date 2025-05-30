import { SignedIn, SignedOut, useUser } from '@clerk/clerk-expo'
import { Link, useRouter } from 'expo-router'
import { Text, View, StyleSheet, Animated, ActivityIndicator } from 'react-native'
import { SignOutButton } from '@/app/components/SignOutButton'
import React from 'react'

export default function Page() {
  const { user, isSignedIn } = useUser()
  const router = useRouter()
  const [showWelcome, setShowWelcome] = React.useState(false)
  const fadeAnim = React.useRef(new Animated.Value(0)).current

  React.useEffect(() => {
    if (isSignedIn) {
      router.replace('/(tabs)/feed')
    } else if (isSignedIn === false) {
      router.replace('/(auth)/sign-in')
    }
  }, [isSignedIn, router])

  if (isSignedIn === undefined) {
    return (
      <View style={styles.container}>
        <ActivityIndicator size="large" color="#0a7ea4" />
        <Text>Loading...</Text>
      </View>
    )
  }

  return null
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