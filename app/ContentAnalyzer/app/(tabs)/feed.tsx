import React, { useEffect, useState } from 'react'
import { View, Text, StyleSheet, ScrollView, TouchableOpacity, Image, Modal, ActivityIndicator, TextInput } from 'react-native'
import { Ionicons, MaterialCommunityIcons } from '@expo/vector-icons'
import { Navbar } from '../components/Navbar'
import { useRouter } from 'expo-router'
import { useAuth } from '@clerk/clerk-expo'
import { LineChart } from 'react-native-chart-kit'

const API_BASE_URL = 'http://192.168.82.141:8000' // Prob change for production

// Example categories for the feed
const CATEGORIES = ['All', 'Tech', 'Science', 'Art', 'Sports']

export default function FeedScreen() {
  const router = useRouter()
  const { isSignedIn, isLoaded, getToken } = useAuth()
  const [selectedCategory, setSelectedCategory] = useState('All')
  const [loading, setLoading] = useState(false)
  const [chatVisible, setChatVisible] = useState(false)
  const [chatInput, setChatInput] = useState('')
  type ChatMessage =
    | { from: 'user'; text: string }
    | { from: 'ai'; text: string }
    | { from: 'ai-news'; news: { title: string; description: string }[] }

  const [chatMessages, setChatMessages] = useState<ChatMessage[]>([])
  const [chatLoading, setChatLoading] = useState(false)

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
  const [trendData, setTrendData] = useState<number[]>([])

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

  const sendChatMessage = async () => {
    if (!chatInput.trim()) return
    const userMsg: { from: 'user', text: string } = { from: 'user', text: chatInput }
    setChatMessages(msgs => [...msgs, userMsg])
    setChatInput('')
    setChatLoading(true)
    try {
      const token = await getToken()
      const res = await fetch(`${API_BASE_URL}/ai-news`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ question: userMsg.text }),
      })
      if (!res.ok) throw new Error('AI error')
      const data = await res.json()
      // Expect data.reply to be an array of {title, description}
      if (Array.isArray(data.reply) && data.reply[0]?.title) {
        setChatMessages(msgs => [
          ...msgs,
          { from: 'ai-news', news: data.reply }
        ])
      } else {
        setChatMessages(msgs => [
          ...msgs,
          { from: 'ai', text: 'Sorry, I could not fetch news right now.' }
        ])
      }
    } catch (e) {
      setChatMessages(msgs => [...msgs, { from: 'ai', text: 'Sorry, I could not fetch news right now.' }])
    } finally {
      setChatLoading(false)
    }
  }

  const handleFeedItemPress = async (item: FeedItem) => {
    setSelectedItem(item)
    // Fetch trend data for this item (simulate or call your backend)
    try {
      const token = await getToken()
      const res = await fetch(`${API_BASE_URL}/trend-growth?id=${item.id}`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      })
      if (res.ok) {
        const data = await res.json()
        setTrendData(data.growth) // e.g., [10, 20, 30, 50, 80]
      } else {
        setTrendData([])
      }
    } catch {
      setTrendData([])
    }
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
              onPress={() => handleFeedItemPress(item)}
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

      {/* Floating Chat Button */}
      <TouchableOpacity
        style={styles.chatButton}
        onPress={() => setChatVisible(true)}
        activeOpacity={0.8}
      >
        <MaterialCommunityIcons name="chat-question" size={32} color="#fff" />
      </TouchableOpacity>

      {/* Chat Modal */}
      <Modal
        visible={chatVisible}
        transparent
        animationType="slide"
        onRequestClose={() => setChatVisible(false)}
      >
        <View style={styles.chatModalOverlay}>
          <View style={styles.chatModalContent}>
            <Text style={styles.chatTitle}>Ask AI for News Suggestions</Text>
            <ScrollView style={styles.chatMessages} contentContainerStyle={{paddingBottom: 16}}>
              {chatMessages.map((msg, idx) => {
                if (msg.from === 'ai-news') {
                  return (
                    <View key={idx} style={styles.aiNewsContainer}>
                      {msg.news.map((item, nidx) => (
                        <View key={nidx} style={styles.aiNewsCard}>
                          <Text style={styles.aiNewsTitle}>{item.title}</Text>
                          <Text style={styles.aiNewsDesc}>{item.description}</Text>
                        </View>
                      ))}
                    </View>
                  )
                }
                return (
                  <View
                    key={idx}
                    style={[
                      styles.chatBubble,
                      msg.from === 'user' ? styles.chatBubbleUser : styles.chatBubbleAI,
                    ]}
                  >
                    <Text style={styles.chatBubbleText}>{msg.text}</Text>
                  </View>
                )
              })}
              {chatLoading && (
                <ActivityIndicator size="small" color="#0a7ea4" style={{marginTop: 8}} />
              )}
            </ScrollView>
            <View style={styles.chatInputRow}>
              <TextInput
                style={styles.chatInput}
                value={chatInput}
                onChangeText={setChatInput}
                placeholder="What news do you need?"
                editable={!chatLoading}
              />
              <TouchableOpacity
                style={styles.chatSendButton}
                onPress={sendChatMessage}
                disabled={chatLoading}
              >
                <Ionicons name="send" size={22} color="#fff" />
              </TouchableOpacity>
            </View>
            <TouchableOpacity
              style={styles.chatCloseButton}
              onPress={() => setChatVisible(false)}
            >
              <Text style={styles.closeButtonText}>Close</Text>
            </TouchableOpacity>
          </View>
        </View>
      </Modal>

      <Modal
        visible={!!selectedItem}
        transparent
        animationType="slide"
        onRequestClose={() => setSelectedItem(null)}
      >
        <View style={styles.modalOverlay}>
          <View style={styles.modalContent}>
            {selectedItem && (
              <ScrollView
                style={{ width: '100%', maxHeight: 440 }}
                contentContainerStyle={{ paddingBottom: 8, paddingTop: 8 }} // increased from 56 to 80
                showsVerticalScrollIndicator={true}
              >
                <Image source={{ uri: selectedItem.image }} style={styles.modalImage} />
                <Text style={styles.modalTitle}>{selectedItem.title}</Text>
                <Text style={styles.modalDetails}>{selectedItem.details}</Text>
                {/* Chart */}
                {trendData.length > 0 && (
                  <>
                    <Text style={{textAlign: 'center', color: '#888', marginBottom: 4, fontSize: 13}}>
                      Number of related news articles per day (last 5 days)
                    </Text>
                    <LineChart
                      data={{
                        labels: Array.from({length: trendData.length}, (_, i) => {
                          const d = new Date();
                          d.setDate(d.getDate() - (trendData.length - 1 - i));
                          return `${d.getMonth()+1}/${d.getDate()}`;
                        }),
                        datasets: [{ data: trendData }]
                      }}
                      width={288}
                      height={170}
                      chartConfig={{
                        backgroundColor: '#fff',
                        backgroundGradientFrom: '#fff',
                        backgroundGradientTo: '#fff',
                        decimalPlaces: 0,
                        color: (opacity = 1) => `rgba(10, 126, 164, ${opacity})`,
                        labelColor: () => '#888',
                        style: { borderRadius: 8 },
                        propsForDots: { r: "4", strokeWidth: "2", stroke: "#0a7ea4" }
                      }}
                      style={{
                        marginVertical: 8,
                        borderRadius: 8,
                        marginBottom: 8,
                        alignSelf: 'center',
                        zIndex: 100,
                      }}
                    />
                    {/* Add this spacer to make sure x-axis labels are visible */}
                    <View style={{ height: 28 }} />
                  </>
                )}
                <TouchableOpacity
                  style={styles.closeButton}
                  onPress={() => setSelectedItem(null)}
                >
                  <Text style={styles.closeButtonText}>Close</Text>
                </TouchableOpacity>
              </ScrollView>
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
    paddingVertical: 16,
    paddingHorizontal: 16,
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
  chatButton: {
    position: 'absolute',
    bottom: 90,
    right: 24,
    backgroundColor: '#0a7ea4',
    borderRadius: 32,
    width: 56,
    height: 56,
    justifyContent: 'center',
    alignItems: 'center',
    elevation: 6,
    shadowColor: '#000',
    shadowOpacity: 0.18,
    shadowRadius: 8,
    shadowOffset: { width: 0, height: 3 },
  },
  chatModalOverlay: {
    flex: 1,
    backgroundColor: 'rgba(0,0,0,0.18)',
    justifyContent: 'center',
    alignItems: 'center',
  },
  chatModalContent: {
    backgroundColor: '#fff',
    borderRadius: 18,
    paddingVertical: 24,
    paddingHorizontal: 16,
    alignItems: 'stretch',
    width: 340,
    maxHeight: '80%',
    elevation: 8,
  },
  chatTitle: {
    fontSize: 18,
    fontWeight: '700',
    color: '#0a7ea4',
    marginBottom: 10,
    textAlign: 'center',
  },
  chatMessages: {
    flexGrow: 0,
    maxHeight: 220,
    marginBottom: 10,
  },
  chatBubble: {
    marginVertical: 4,
    padding: 10,
    borderRadius: 12,
    maxWidth: '90%',
  },
  chatBubbleUser: {
    alignSelf: 'flex-end',
    backgroundColor: '#e0f7fa',
  },
  chatBubbleAI: {
    alignSelf: 'flex-start',
    backgroundColor: '#f1f8e9',
  },
  chatBubbleText: {
    fontSize: 15,
    color: '#222',
  },
  chatInputRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginTop: 8,
  },
  chatInput: {
    flex: 1,
    borderWidth: 1,
    borderColor: '#e0e7ef',
    borderRadius: 8,
    paddingHorizontal: 12,
    paddingVertical: 8,
    fontSize: 15,
    backgroundColor: '#f7fafc',
    marginRight: 8,
  },
  chatSendButton: {
    backgroundColor: '#0a7ea4',
    borderRadius: 8,
    padding: 10,
  },
  chatCloseButton: {
    marginTop: 12,
    alignSelf: 'center',
    backgroundColor: '#0a7ea4',
    paddingVertical: 8,
    paddingHorizontal: 32,
    borderRadius: 8,
  },
  aiNewsContainer: {
    marginVertical: 6,
  },
  aiNewsCard: {
    backgroundColor: '#fffbe7',
    borderRadius: 10,
    padding: 12,
    marginBottom: 8,
    borderWidth: 1,
    borderColor: '#ffe082',
    elevation: 2,
  },
  aiNewsTitle: {
    fontWeight: 'bold',
    fontSize: 16,
    color: '#e65100',
    marginBottom: 4,
  },
  aiNewsDesc: {
    fontSize: 14,
    color: '#444',
  },
})