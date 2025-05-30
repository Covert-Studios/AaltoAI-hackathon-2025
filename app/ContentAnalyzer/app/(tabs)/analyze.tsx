import React, { useEffect } from 'react'
import { View, Text, StyleSheet } from 'react-native'
import { Ionicons } from '@expo/vector-icons'
import { Navbar } from '../components/Navbar'
import { useRouter } from 'expo-router'
import { useAuth } from '@clerk/clerk-expo'

export default function AnalyzeScreen() {
  const router = useRouter()
  const { isSignedIn, isLoaded } = useAuth()

  useEffect(() => {
    if (isLoaded && !isSignedIn) {
      router.replace('/')
    }
  }, [isSignedIn, isLoaded, router])

  const handleTabPress = (tab: string) => {
    if (tab === 'Analyze') return
    if (tab === 'Feed') router.replace('/(tabs)/feed')
    if (tab === 'Profile') router.replace('/(tabs)/profile')
  }

  if (!isLoaded || !isSignedIn) {
    return null
  }

  return (
    <View style={styles.container}>
      <View style={styles.content}>
        <Ionicons name="analytics-outline" size={48} color="#0a7ea4" style={{ marginBottom: 16 }} />
        <Text style={styles.title}>Analyze</Text>
        <Text style={styles.subtitle}>Your content analysis tools will appear here.</Text>
      </View>
      <Navbar onTabPress={handleTabPress} activeTab="Analyze" />
    </View>
  )
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f7fafc',
    justifyContent: 'space-between',
  },
  content: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
    padding: 24,
  },
  title: {
    fontSize: 28,
    fontWeight: '700',
    color: '#0a7ea4',
    marginBottom: 8,
  },
  subtitle: {
    fontSize: 16,
    color: '#444',
    textAlign: 'center',
  },
})