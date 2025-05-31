import React, { useEffect, useState } from 'react'
import { View, Text, StyleSheet, ScrollView, TouchableOpacity, Image, Modal, ActivityIndicator } from 'react-native'
import { Ionicons } from '@expo/vector-icons'
import { Navbar } from '../components/Navbar'
import { useRouter } from 'expo-router'
import { useAuth } from '@clerk/clerk-expo'

const API_BASE_URL = 'http://192.168.82.141:8000' // Prob change for production

// Example categories for the feed
const CATEGORIES = ['All', 'Tech', 'Science', 'Art', 'Sports']

export default function FeedScreen() {
  const router = useRouter()
  const { isSignedIn, isLoaded, getToken } = useAuth()
  const [selectedCategory, setSelectedCategory] = useState('All')
  const [loading, setLoading] = useState(false)
  type FeedItem = {
    id: number
    category: string
    title: string
    image: string
    summary: string
    details: string
  }
  const [feedItems, setFeedItems] = useState<FeedItem[]>([])
  const [selectedItem, setSelectedItem] = useState<FeedItem | null>(null)

  useEffect(() => {
    if (isLoaded && !isSignedIn) {
      router.replace('/')
    }
  }, [isSignedIn, isLoaded, router])

  useEffect(() => {
    fetchFeed()
  }, [])

  const fetchFeed = async () => {
    try {
      setLoading(true)
      const token = await getToken()
      const res = await fetch(`${API_BASE_URL}/trends`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      })
      if (!res.ok) throw new Error('Failed to fetch trends')
      const data = await res.json()
      setFeedItems(data)
    } catch (e) {
      setFeedItems([])
    } finally {
      setLoading(false)
    }
  }

  const handleTabPress = (tab: string) => {
    if (tab === 'Feed') return
    if (tab === 'Analyze') router.replace('/(tabs)/analyze')
    if (tab === 'Profile') router.replace('/(tabs)/profile')
  }

  if (!isLoaded || !isSignedIn) {
    return null
  }

  const filteredItems =
    selectedCategory === 'All'
      ? feedItems
      : feedItems.filter(item => item.category === selectedCategory)

  return (
    <View style={styles.container}>
      <View style={styles.categoriesContainer}>
        <ScrollView horizontal showsHorizontalScrollIndicator={false}>
          {CATEGORIES.map(category => (
            <TouchableOpacity
              key={category}
              style={[
                styles.categoryTab,
                selectedCategory === category && styles.categoryTabActive,
              ]}
              onPress={() => setSelectedCategory(category)}
            >
              <Text
                style={[
                  styles.categoryTabText,
                  selectedCategory === category && styles.categoryTabTextActive,
                ]}
              >
                {category}
              </Text>
            </TouchableOpacity>
          ))}
        </ScrollView>
      </View>
      {loading ? (
        <View style={{ flex: 1, justifyContent: 'center', alignItems: 'center', marginTop: 40 }}>
          <ActivityIndicator size="large" color="#0a7ea4" />
        </View>
      ) : (
        <ScrollView contentContainerStyle={styles.content}>
          {filteredItems.map(item => (
            <TouchableOpacity
              key={item.id}
              style={styles.feedBlock}
              onPress={() => setSelectedItem(item)}
              activeOpacity={0.8}
            >
              <Image source={{ uri: item.image }} style={styles.feedImage} />
              <View style={styles.feedTextContainer}>
                <Text style={styles.feedTitle}>{item.title}</Text>
                <Text style={styles.feedSummary}>{item.summary}</Text>
              </View>
            </TouchableOpacity>
          ))}
          {filteredItems.length === 0 && !loading && (
            <Text style={styles.noItemsText}>No items in this category.</Text>
          )}
        </ScrollView>
      )}
      <Navbar onTabPress={handleTabPress} activeTab="Feed" />

      <Modal
        visible={!!selectedItem}
        transparent
        animationType="fade"
        onRequestClose={() => setSelectedItem(null)}
      >
        <View style={styles.modalOverlay}>
          <View style={styles.modalContent}>
            {selectedItem && (
              <>
                <Image source={{ uri: selectedItem.image }} style={styles.modalImage} />
                <Text style={styles.modalTitle}>{selectedItem.title}</Text>
                <Text style={styles.modalDetails}>{selectedItem.details}</Text>
                <TouchableOpacity
                  style={styles.closeButton}
                  onPress={() => setSelectedItem(null)}
                >
                  <Text style={styles.closeButtonText}>Close</Text>
                </TouchableOpacity>
              </>
            )}
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
  },
  categoriesContainer: {
    paddingTop: 32,
    paddingBottom: 12,
    backgroundColor: '#f7fafc',
    paddingHorizontal: 8,
  },
  categoryTab: {
    paddingVertical: 8,
    paddingHorizontal: 18,
    borderRadius: 20,
    backgroundColor: '#e0e7ef',
    marginRight: 10,
  },
  categoryTabActive: {
    backgroundColor: '#0a7ea4',
  },
  categoryTabText: {
    color: '#0a7ea4',
    fontWeight: '600',
    fontSize: 16,
  },
  categoryTabTextActive: {
    color: '#fff',
  },
  content: {
    padding: 16,
    paddingBottom: 80,
  },
  feedBlock: {
    flexDirection: 'row',
    backgroundColor: '#fff',
    borderRadius: 14,
    marginBottom: 18,
    overflow: 'hidden',
    elevation: 2,
    shadowColor: '#000',
    shadowOpacity: 0.06,
    shadowRadius: 6,
    shadowOffset: { width: 0, height: 2 },
  },
  feedImage: {
    width: 90,
    height: 90,
    borderTopLeftRadius: 14,
    borderBottomLeftRadius: 14,
  },
  feedTextContainer: {
    flex: 1,
    padding: 14,
    justifyContent: 'center',
  },
  feedTitle: {
    fontSize: 18,
    fontWeight: '700',
    color: '#0a7ea4',
    marginBottom: 4,
  },
  feedSummary: {
    fontSize: 15,
    color: '#444',
  },
  noItemsText: {
    textAlign: 'center',
    color: '#888',
    fontSize: 16,
    marginTop: 40,
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
    paddingVertical: 32,
    paddingHorizontal: 24,
    alignItems: 'center',
    width: 320,
    elevation: 8,
    shadowColor: '#0a7ea4',
    shadowOpacity: 0.15,
    shadowRadius: 12,
    shadowOffset: { width: 0, height: 4 },
  },
  modalImage: {
    width: 180,
    height: 120,
    borderRadius: 12,
    marginBottom: 16,
  },
  modalTitle: {
    fontSize: 22,
    fontWeight: '700',
    color: '#0a7ea4',
    marginBottom: 10,
    textAlign: 'center',
  },
  modalDetails: {
    fontSize: 16,
    color: '#444',
    marginBottom: 20,
    textAlign: 'center',
  },
  closeButton: {
    backgroundColor: '#0a7ea4',
    paddingVertical: 10,
    paddingHorizontal: 32,
    borderRadius: 8,
  },
  closeButtonText: {
    color: '#fff',
    fontWeight: '700',
    fontSize: 16,
  },
})