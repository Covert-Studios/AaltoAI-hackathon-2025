import React, { useEffect, useState } from 'react'
import { View, Text, StyleSheet, ActivityIndicator, ScrollView, Alert } from 'react-native'
import { useLocalSearchParams, useRouter } from 'expo-router'
import { Ionicons } from '@expo/vector-icons'

export default function AnalyzeDetailScreen() {
  const { id } = useLocalSearchParams()
  const router = useRouter()
  const [detail, setDetail] = useState<any>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (!id) return
    fetchDetail()
  }, [id])

  const fetchDetail = async () => {
    setLoading(true)
    try {
      // TODO: Replace with your API call
      // Example: const res = await fetch(`https://your-api/analyze/${id}`)
      // const data = await res.json()
      // setDetail(data)
      // Mock data for now:
      setDetail({
        id,
        title: `Analysis ${id}`,
        date: new Date().toISOString().slice(0, 10),
        result: 'PLACEHOLDER: Analysis result will be displayed here.',
      })
    } catch (e) {
      Alert.alert('Error', 'Failed to fetch analysis details.')
    }
    setLoading(false)
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
      <Ionicons name="analytics-outline" size={48} color="#0a7ea4" style={{ marginBottom: 16 }} />
      <Text style={styles.title}>{detail.title}</Text>
      <Text style={styles.date}>{detail.date}</Text>
      <Text style={styles.result}>{detail.result}</Text>
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
    marginBottom: 8,
  },
  date: {
    fontSize: 14,
    color: '#888',
    marginBottom: 24,
  },
  result: {
    fontSize: 16,
    color: '#222',
    textAlign: 'center',
  },
})