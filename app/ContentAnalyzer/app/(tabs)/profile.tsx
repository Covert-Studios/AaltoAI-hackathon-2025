import React, { useEffect, useState } from 'react'
import { View, Text, StyleSheet, TouchableOpacity, Modal, Linking } from 'react-native'
import { Ionicons } from '@expo/vector-icons'
import { Navbar } from '../components/Navbar'
import { useRouter } from 'expo-router'
import { useAuth, useUser } from '@clerk/clerk-expo'

export default function ProfileScreen() {
  const router = useRouter()
  const { isSignedIn, isLoaded, signOut } = useAuth()
  const { user } = useUser()
  const [modalVisible, setModalVisible] = useState(false)

  useEffect(() => {
    if (isLoaded && !isSignedIn) {
      router.replace('/')
    }
  }, [isSignedIn, isLoaded, router])

  const handleTabPress = (tab: string) => {
    if (tab === 'Profile') return
    if (tab === 'Feed') router.replace('/(tabs)/feed')
    if (tab === 'Analyze') router.replace('/(tabs)/analyze')
  }

  const handleManageAccount = () => {
    // Open Clerk's hosted account portal in browser
    Linking.openURL('https://YOUR-CLERK-INSTANCE.clerk.accounts.dev/user') // Replace with your Clerk instance URL
    setModalVisible(false)
  }

  const handleSignOut = async () => {
    await signOut()
    router.replace('/')
  }

  if (!isLoaded || !isSignedIn) {
    return null
  }

  return (
    <View style={styles.container}>
      <View style={styles.content}>
        <Ionicons name="person-outline" size={48} color="#0a7ea4" style={{ marginBottom: 16 }} />
        <Text style={styles.title}>Profile</Text>
        <Text style={styles.subtitle}>Your profile details will appear here.</Text>
        <View style={styles.infoBox}>
          <Text style={styles.label}>Email:</Text>
          <Text style={styles.value}>{user?.emailAddresses[0]?.emailAddress}</Text>
          <TouchableOpacity style={styles.button} onPress={() => setModalVisible(true)}>
            <Text style={styles.buttonText}>Manage Account</Text>
          </TouchableOpacity>
        </View>
        <View style={styles.infoBox}>
          <Text style={styles.label}>Password:</Text>
          <Text style={styles.value}>********</Text>
          <TouchableOpacity style={styles.button} onPress={() => setModalVisible(true)}>
            <Text style={styles.buttonText}>Change Password</Text>
          </TouchableOpacity>
        </View>
        <TouchableOpacity style={styles.signOutButton} onPress={handleSignOut}>
          <Text style={styles.signOutText}>Sign Out</Text>
        </TouchableOpacity>
      </View>
      <Navbar onTabPress={handleTabPress} activeTab="Profile" />

      <Modal
        visible={modalVisible}
        transparent
        animationType="fade"
        onRequestClose={() => setModalVisible(false)}
      >
        <View style={styles.modalOverlay}>
          <View style={styles.modalContent}>
            <Text style={styles.modalTitle}>Manage Account</Text>
            <Text style={styles.modalText}>
              To change your email or password, you&apos;ll be redirected to the secure Clerk account portal.
            </Text>
            <TouchableOpacity style={styles.button} onPress={handleManageAccount}>
              <Text style={styles.buttonText}>Open Account Portal</Text>
            </TouchableOpacity>
            <TouchableOpacity style={[styles.button, { backgroundColor: '#ccc', marginTop: 10 }]} onPress={() => setModalVisible(false)}>
              <Text style={[styles.buttonText, { color: '#222' }]}>Cancel</Text>
            </TouchableOpacity>
          </View>
        </View>
      </Modal>
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
    marginBottom: 24,
  },
  infoBox: {
    width: '100%',
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 16,
    marginBottom: 16,
    alignItems: 'flex-start',
    shadowColor: '#000',
    shadowOpacity: 0.05,
    shadowRadius: 4,
    shadowOffset: { width: 0, height: 2 },
    elevation: 2,
  },
  label: {
    fontSize: 16,
    color: '#0a7ea4',
    fontWeight: '600',
    marginBottom: 4,
  },
  value: {
    fontSize: 16,
    color: '#222',
    marginBottom: 8,
  },
  button: {
    backgroundColor: '#0a7ea4',
    paddingVertical: 8,
    paddingHorizontal: 16,
    borderRadius: 8,
    alignSelf: 'flex-start',
  },
  buttonText: {
    color: '#fff',
    fontWeight: '600',
    fontSize: 15,
  },
  signOutButton: {
    marginTop: 24,
    backgroundColor: '#e74c3c',
    paddingVertical: 10,
    paddingHorizontal: 24,
    borderRadius: 8,
  },
  signOutText: {
    color: '#fff',
    fontWeight: '700',
    fontSize: 16,
  },
  modalOverlay: {
    flex: 1,
    backgroundColor: 'rgba(0,0,0,0.18)',
    justifyContent: 'center',
    alignItems: 'center',
  },
  modalContent: {
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
  modalTitle: {
    fontSize: 22,
    fontWeight: '700',
    color: '#0a7ea4',
    marginBottom: 12,
    textAlign: 'center',
  },
  modalText: {
    fontSize: 16,
    color: '#444',
    marginBottom: 24,
    textAlign: 'center',
  },
})