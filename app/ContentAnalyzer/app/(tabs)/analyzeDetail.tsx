import React, { useEffect, useState } from 'react'
import { View, Text, StyleSheet, ActivityIndicator, ScrollView, Alert, TouchableOpacity, Modal, TextInput } from 'react-native'
import { Ionicons } from '@expo/vector-icons'
import { useRouter, useLocalSearchParams } from 'expo-router'
import { useAuth } from '@clerk/clerk-expo'

const API_BASE_URL = 'http://192.168.82.141:8000' // Prob change for production

export default function AnalyzeDetailScreen() {
  const router = useRouter()
  const params = useLocalSearchParams()
  const { getToken } = useAuth()
  const [detail, setDetail] = useState<any>(null)
  const [loading, setLoading] = useState(true)
  const [newTitle, setNewTitle] = useState('')
  const [renameModalVisible, setRenameModalVisible] = useState(false)

  const id = params?.id

  useEffect(() => { 
    if (!id) return
    fetchDetail()
  }, [id])

  const fetchDetail = async () => {
    setLoading(true)
    try {
      const token = await getToken()
      const res = await fetch(`${API_BASE_URL}/analyze/${id}`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      })
      if (!res.ok) throw new Error('Failed to fetch analysis details')
      const data = await res.json()
      setDetail(data)
    } catch (e) {
      Alert.alert('Error', 'Failed to fetch analysis details.')
      setDetail(null)
    }
    setLoading(false)
  }

  const handleRename = async () => {
    if (!newTitle.trim()) {
      Alert.alert('Please enter a new name.')
      return
    }
    try {
      const token = await getToken()
      await fetch(`${API_BASE_URL}/rename_analysis`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({
          user_id: detail.user_id,
          analysis_id: detail.id,
          new_title: newTitle,
        }),
      })
      setDetail({ ...detail, title: newTitle })
      setRenameModalVisible(false)
      setNewTitle('')
      Alert.alert('Success', 'Analysis renamed.')
    } catch (e) {
      Alert.alert('Error', 'Failed to rename analysis.')
    }
  }

  function renderRichResult(result: string) {
    const lines = result.split('\n');
    return lines.map((line, idx) => {
      // Headings
      if (line.startsWith('### ')) {
        return (
          <Text key={idx} style={{ fontSize: 20, fontWeight: 'bold', marginTop: 18, marginBottom: 6, color: '#0a7ea4' }}>
            {line.replace('### ', '')}
          </Text>
        );
      }
      // Sub-bold (e.g. **Label:** value or **Label**: value)
      const subBoldMatch = line.match(/^\*\*([^*]+)\*\*:? ?(.*)/);
      if (subBoldMatch && subBoldMatch[1] && subBoldMatch[2] !== undefined) {
        return (
          <Text key={idx} style={{ marginLeft: 8, marginBottom: 4 }}>
            <Text style={{ fontWeight: 'bold' }}>{subBoldMatch[1]}{line.includes(':') ? ':' : ''}</Text>
            {subBoldMatch[2] ? ` ${subBoldMatch[2]}` : ''}
          </Text>
        );
      }
      // Bold (only if not sub-bold)
      if (line.startsWith('**') && line.endsWith('**') && !line.includes(':')) {
        return (
          <Text key={idx} style={{ fontWeight: 'bold', marginTop: 10, marginBottom: 4 }}>
            {line.replace(/\*\*/g, '')}
          </Text>
        );
      }
      // Numbered list
      if (/^\d+\./.test(line.trim())) {
        return (
          <Text key={idx} style={{ marginLeft: 16, marginBottom: 4 }}>
            <Text style={{ fontWeight: 'bold' }}>{line.trim().split('.')[0]}.</Text>
            {line.trim().substring(line.trim().indexOf('.') + 1)}
          </Text>
        );
      }
      // Bulleted list
      if (line.trim().startsWith('- ')) {
        return (
          <Text key={idx} style={{ marginLeft: 16, marginBottom: 4 }}>
            <Text style={{ fontWeight: 'bold' }}>• </Text>
            {line.trim().substring(2)}
          </Text>
        );
      }
      // Default
      return (
        <Text key={idx} style={{ marginBottom: 4 }}>
          {line}
        </Text>
      );
    });
  }

  if (loading) {
    return (
      <View style={styles.centered}>
        <ActivityIndicator size="large" color="#0a7ea4" />
      </View>
    )
  }

  if (!detail) {
    return (
      <View style={styles.centered}>
        <Text>Analysis not found.</Text>
      </View>
    )
  }

  return (
    <ScrollView contentContainerStyle={styles.container}>
      {/* Back Button */}
      <TouchableOpacity
        style={{ position: 'absolute', top: 24, left: 16, zIndex: 10 }}
        onPress={() => router.back()}
      >
        <Ionicons name="arrow-back" size={28} color="#0a7ea4" />
      </TouchableOpacity>

      <Ionicons name="analytics-outline" size={48} color="#0a7ea4" style={{ marginBottom: 16, marginTop: 32 }} />
      <Text style={styles.title}>{detail.title}</Text>
      <Text style={styles.date}>{detail.date}</Text>
      <Text style={{ color: '#888', fontSize: 14, marginBottom: 8 }}>ID: {detail.id}</Text>
      <View style={styles.result}>
        {renderRichResult(detail.result)}
      </View>

      <TouchableOpacity
        style={{
          backgroundColor: '#0a7ea4',
          paddingVertical: 8,
          paddingHorizontal: 16,
          borderRadius: 8,
          marginTop: 16,
          alignSelf: 'center',
        }}
        onPress={() => setRenameModalVisible(true)}
      >
        <Text style={{ color: '#fff', fontWeight: '600' }}>Change Name</Text>
      </TouchableOpacity>

      <Modal
        visible={renameModalVisible}
        transparent
        animationType="fade"
        onRequestClose={() => setRenameModalVisible(false)}
      >
        <View style={{
          flex: 1,
          backgroundColor: 'rgba(0,0,0,0.18)',
          justifyContent: 'center',
          alignItems: 'center',
        }}>
          <View style={{
            backgroundColor: '#fff',
            borderRadius: 18,
            padding: 24,
            alignItems: 'center',
            width: 300,
          }}>
            <Text style={{ fontSize: 18, fontWeight: '700', color: '#0a7ea4', marginBottom: 12 }}>Rename Analysis</Text>
            <TextInput
              style={{
                borderWidth: 1,
                borderColor: '#ccc',
                borderRadius: 8,
                padding: 8,
                width: '100%',
                marginBottom: 16,
              }}
              placeholder="New name"
              value={newTitle}
              onChangeText={setNewTitle}
            />
            <TouchableOpacity
              style={{ backgroundColor: '#0a7ea4', padding: 10, borderRadius: 8, marginBottom: 8, width: '100%' }}
              onPress={handleRename}
            >
              <Text style={{ color: '#fff', textAlign: 'center', fontWeight: '600' }}>Save</Text>
            </TouchableOpacity>
            <TouchableOpacity
              style={{ backgroundColor: '#ccc', padding: 10, borderRadius: 8, width: '100%' }}
              onPress={() => setRenameModalVisible(false)}
            >
              <Text style={{ color: '#222', textAlign: 'center', fontWeight: '600' }}>Cancel</Text>
            </TouchableOpacity>
          </View>
        </View>
      </Modal>
    </ScrollView>
  )
}

const styles = StyleSheet.create({
  container: {
    flexGrow: 1,
    alignItems: 'center',
    justifyContent: 'center',
    padding: 24,
    backgroundColor: '#f7fafc',
  },
  centered: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: '#f7fafc',
  },
  title: {
    fontSize: 24,
    fontWeight: '700',
    color: '#0a7ea4',
    marginBottom: 4,
    marginTop: 24,
  },
  date: {
    fontSize: 16,
    color: '#444',
    marginBottom: 2,
  },
  result: {
    width: '100%',
    marginBottom: 16,
  },
})