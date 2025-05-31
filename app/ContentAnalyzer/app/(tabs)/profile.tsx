import React, { useEffect, useState } from 'react'
import { View, Text, StyleSheet, TouchableOpacity, Modal, Linking, Alert, TextInput, ScrollView } from 'react-native'
import { Ionicons } from '@expo/vector-icons'
import { Navbar } from '../components/Navbar'
import { useRouter } from 'expo-router'
import { useAuth, useUser } from '@clerk/clerk-expo'

const API_BASE_URL = 'http://192.168.82.141:8000' // Prob change for production

export default function ProfileScreen() {
  const router = useRouter()
  const { isSignedIn, isLoaded, signOut } = useAuth()
  const { user } = useUser()
  const [modalVisible, setModalVisible] = useState(false)
  const [manageAnalysesModal, setManageAnalysesModal] = useState(false)
  const [deleteId, setDeleteId] = useState('')
  const [analysesCount, setAnalysesCount] = useState<number | null>(null)

  useEffect(() => {
    if (isLoaded && !isSignedIn) {
      router.replace('/')
    }
  }, [isSignedIn, isLoaded, router])

  useEffect(() => {
    if (isLoaded && isSignedIn && user) {
      /*fetch(`${API_BASE_URL}/analyses_count?user_id=${user.id}`)
        .then(res => res.json())
        .then(data => setAnalysesCount(data.count))
        .catch(() => setAnalysesCount(null))*/
    }
  }, [isLoaded, isSignedIn, user])

  const handleTabPress = (tab: string) => {
    if (tab === 'Profile') return
    if (tab === 'Feed') router.replace('/(tabs)/feed')
    if (tab === 'Analyze') router.replace('/(tabs)/analyze')
  }

  const handleManageAccount = () => {
    Linking.openURL('https://YOUR-CLERK-INSTANCE.clerk.accounts.dev/user') 
    setModalVisible(false)
  }

  const handleSignOut = async () => {
    await signOut()
    router.replace('/')
  }

  const deleteAllAnalyses = async () => {
    if (!user) {
      Alert.alert('User not found')
      return
    }
    try {
      await fetch(`${API_BASE_URL}/delete_all_analyses`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_id: user.id })
      })
      Alert.alert('All analyses deleted!')
      setManageAnalysesModal(false)
    } catch (e) {
      Alert.alert('Error deleting all analyses')
    }
  }

  const deleteOneAnalysis = async () => {
    if (!deleteId) {
      Alert.alert('Please enter an analysis ID')
      return
    }
    if (!user) {
      Alert.alert('User not found')
      return
    }
    try {
      await fetch(`${API_BASE_URL}/delete_analysis`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_id: user.id, analysis_id: deleteId })
      })
      Alert.alert(`Analysis ${deleteId} deleted!`)
      setDeleteId('')
      setManageAnalysesModal(false)
    } catch (e) {
      Alert.alert('Error deleting analysis')
    }
  }

  if (!isLoaded || !isSignedIn) {
    return null
  }

  return (
    <View style={styles.container}>
      <ScrollView contentContainerStyle={styles.content} keyboardShouldPersistTaps="handled">
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
        <View style={styles.infoBox}>
          <Text style={styles.label}>Analyses:</Text>
          <Text style={styles.value}>
            {analysesCount === null ? 'Loading...' : `${analysesCount} analyses`}
          </Text>
          <TouchableOpacity style={styles.button} onPress={() => setManageAnalysesModal(true)}>
            <Text style={styles.buttonText}>Manage Analyses</Text>
          </TouchableOpacity>
        </View>
        <TouchableOpacity style={styles.signOutButton} onPress={handleSignOut}>
          <Text style={styles.signOutText}>Sign Out</Text>
        </TouchableOpacity>
      </ScrollView>
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

      {/* Analyses Management Modal */}
      <Modal
        visible={manageAnalysesModal}
        transparent
        animationType="fade"
        onRequestClose={() => setManageAnalysesModal(false)}
      >
        <View style={styles.modalOverlay}>
          <View style={styles.modalContent}>
            <Text style={styles.modalTitle}>Manage Analyses</Text>
            <TouchableOpacity
              style={[styles.button, { backgroundColor: '#e74c3c', marginBottom: 12 }]}
              onPress={deleteAllAnalyses}
            >
              <Text style={styles.buttonText}>Delete All Analyses</Text>
            </TouchableOpacity>
            <Text style={{ marginBottom: 8, color: '#444' }}>Delete by Analysis ID:</Text>
            <TextInput
              style={{
                borderWidth: 1,
                borderColor: '#ccc',
                borderRadius: 8,
                padding: 8,
                marginBottom: 12,
                width: 180,
                backgroundColor: '#f7fafc',
                color: '#222'
              }}
              placeholder="Enter Analysis ID"
              value={deleteId}
              onChangeText={setDeleteId}
              placeholderTextColor="#aaa"
            />
            <TouchableOpacity
              style={[styles.button, { backgroundColor: '#e74c3c' }]}
              onPress={deleteOneAnalysis}
            >
              <Text style={styles.buttonText}>Delete One Analysis</Text>
            </TouchableOpacity>
            <TouchableOpacity
              style={[styles.button, { backgroundColor: '#ccc', marginTop: 16 }]}
              onPress={() => setManageAnalysesModal(false)}
            >
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