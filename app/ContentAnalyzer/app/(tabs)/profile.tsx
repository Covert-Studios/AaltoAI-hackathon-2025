import React from 'react'
import { View, Text, StyleSheet } from 'react-native'
import { Ionicons } from '@expo/vector-icons'
import { Navbar } from '../components/Navbar'
import { useRouter } from 'expo-router'

export default function ProfileScreen() {
  const router = useRouter()

  const handleTabPress = (tab: string) => {
    if (tab === 'Profile') return
    if (tab === 'Feed') router.replace('/(tabs)/feed')
    if (tab === 'Analyze') router.replace('/(tabs)/analyze')
  }

  return (
    <View style={styles.container}>
      <View style={styles.content}>
        <Ionicons name="person-outline" size={48} color="#0a7ea4" style={{ marginBottom: 16 }} />
        <Text style={styles.title}>Profile</Text>
        <Text style={styles.subtitle}>Your profile details will appear here.</Text>
      </View>
      <Navbar onTabPress={handleTabPress} activeTab="Profile" />
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