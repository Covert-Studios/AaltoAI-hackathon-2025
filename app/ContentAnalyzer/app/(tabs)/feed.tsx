import React, { useEffect, useState } from 'react'
import { View, Text, StyleSheet, ScrollView, TouchableOpacity, Image, Modal } from 'react-native'
import { Ionicons } from '@expo/vector-icons'
import { Navbar } from '../components/Navbar'
import { useRouter } from 'expo-router'
import { useAuth } from '@clerk/clerk-expo'

// Example categories for the feed
const CATEGORIES = ['All', 'Tech', 'Science', 'Art', 'Sports']

const FEED_ITEMS = [
  // Example feed items 
  // other stuff will be added from the api 
  {
    id: 1,
    category: 'Tech',
    title: 'AI Revolutionizes Coding',
    image: 'https://images.unsplash.com/photo-1519389950473-47ba0277781c',
    summary: 'AI tools are changing how developers write code.',
    details: 'AI-powered code assistants are making development faster and more efficient by providing real-time suggestions and automating repetitive tasks.',
  },
  {
    id: 2,
    category: 'Science',
    title: 'New Planet Discovered',
    image: 'https://images.unsplash.com/photo-1465101046530-73398c7f28ca',
    summary: 'Astronomers have found a new Earth-like planet.',
    details: 'The planet, located in the habitable zone, could potentially support life. Scientists are excited about future research opportunities.',
  },
  {
    id: 3,
    category: 'Art',
    title: 'Modern Art Exhibition',
    image: 'https://images.unsplash.com/photo-1506744038136-46273834b3fb',
    summary: 'A new exhibition showcases modern art from around the world.',
    details: 'The exhibition features works from over 50 artists and explores themes of identity, technology, and society.',
  },
  {
    id: 4,
    category: 'Sports',
    title: 'Championship Finals',
    image: 'https://images.unsplash.com/photo-1517649763962-0c623066013b',
    summary: 'The finals were full of surprises and upsets.',
    details: 'Fans witnessed an intense battle as underdogs took the lead and secured a historic victory.',
  },
]

export default function FeedScreen() {
  const router = useRouter()
  const { isSignedIn, isLoaded } = useAuth()
  const [selectedCategory, setSelectedCategory] = useState('All')
  type FeedItem = {
    id: number
    category: string
    title: string
    image: string
    summary: string
    details: string
  }
  const [selectedItem, setSelectedItem] = useState<FeedItem | null>(null)

  useEffect(() => {
    if (isLoaded && !isSignedIn) {
      router.replace('/')
    }
  }, [isSignedIn, isLoaded, router])

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
      ? FEED_ITEMS
      : FEED_ITEMS.filter(item => item.category === selectedCategory)

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
        {filteredItems.length === 0 && (
          <Text style={styles.noItemsText}>No items in this category.</Text>
        )}
      </ScrollView>
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