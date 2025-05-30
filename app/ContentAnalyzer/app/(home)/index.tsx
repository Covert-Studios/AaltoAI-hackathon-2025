import { SignedIn, SignedOut, useUser } from '@clerk/clerk-expo'
import { Link } from 'expo-router'
import { Text, View, StyleSheet, TouchableOpacity } from 'react-native'
import { SignOutButton } from '@/app/components/SignOutButton'
import { Ionicons } from '@expo/vector-icons'

export default function Page() {
  const { user } = useUser()

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
        {/* Dummy Navbar */}
        <View style={styles.navbar}>
          <TouchableOpacity style={styles.navItem}>
            <Ionicons name="home-outline" size={28} color="#0a7ea4" />
            <Text style={styles.navLabel}>Feed</Text>
          </TouchableOpacity>
          <TouchableOpacity style={styles.navItem}>
            <Ionicons name="analytics-outline" size={28} color="#888" />
            <Text style={styles.navLabel}>Analyze</Text>
          </TouchableOpacity>
          <TouchableOpacity style={styles.navItem}>
            <Ionicons name="person-outline" size={28} color="#888" />
            <Text style={styles.navLabel}>Profile</Text>
          </TouchableOpacity>
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
  navbar: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    alignItems: 'center',
    backgroundColor: '#fff',
    paddingVertical: 14,
    borderTopWidth: 1,
    borderColor: '#eee',
    elevation: 8,
  },
  navItem: {
    alignItems: 'center',
    flex: 1,
  },
  navLabel: {
    fontSize: 13,
    color: '#0a7ea4',
    marginTop: 2,
    fontWeight: '600',
  },
})