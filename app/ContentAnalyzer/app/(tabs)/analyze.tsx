import React, { useEffect, useState } from 'react'
import { View, Text, StyleSheet, Button, FlatList, TouchableOpacity, Alert, ActivityIndicator } from 'react-native'
import { Ionicons } from '@expo/vector-icons'
import { Navbar } from '../components/Navbar'
import { useRouter } from 'expo-router'
import { useAuth } from '@clerk/clerk-expo'
import * as ImagePicker from 'expo-image-picker'

export default function AnalyzeScreen() {
  const router = useRouter()
  const { isSignedIn, isLoaded } = useAuth()
  const [history, setHistory] = useState<any[]>([])
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    if (isLoaded && !isSignedIn) {
      router.replace('/')
    }
    if (isLoaded && isSignedIn) {
      fetchHistory()
    }
  }, [isSignedIn, isLoaded, router])

  const fetchHistory = async () => {
    // TODO: Replace with your API call
    // Example: const res = await fetch('https://your-api/analyze/history')
    // setHistory(await res.json())
    setHistory([]) // Empty for now
  }

  const handleTabPress = (tab: string) => {
    if (tab === 'Analyze') return
    if (tab === 'Feed') router.replace('/(tabs)/feed')
    if (tab === 'Profile') router.replace('/(tabs)/profile')
  }

  const handleScan = async () => {
    const result = await ImagePicker.launchImageLibraryAsync({
      mediaTypes: ImagePicker.MediaTypeOptions.Videos,
      allowsEditing: false,
      quality: 1,
    });

    if (!result.canceled && result.assets && result.assets.length > 0) {
      setLoading(true);
      try {
        // Upload video to API
        const videoUri = result.assets[0].uri;
        const formData = new FormData();
        formData.append("video", {
          uri: videoUri,
          name: "uploaded_video.mp4",
          type: "video/mp4",
        });

        const response = await fetch("http://<your-server-ip>:5000/upload", {
          method: "POST",
          headers: {
            "Content-Type": "multipart/form-data",
            "x-api-key": "prohackerschmacker6969",
          },
          body: formData,
        });

        if (!response.ok) {
          throw new Error("Failed to upload video");
        }

        const data = await response.json();
        console.log("Upload successful:", data);

        // Add to history
        const historyData = {
          id: String(Date.now()),
          title: `Analysis ${history.length + 1}`,
          date: new Date().toISOString().slice(0, 10),
        };
        setHistory([historyData, ...history]);
        router.push({ pathname: "/(tabs)/analyzeDetail", params: { id: historyData.id } });
      } catch (e) {
        Alert.alert("Error", "Failed to upload video.");
      }
      setLoading(false);
    }
  };

  const handleHistoryPress = (item: { id: string }) => {
    router.push({ pathname: '/(tabs)/analyzeDetail', params: { id: item.id } })
  }

  if (!isLoaded || !isSignedIn) {
    return null
  }

  return (
    <View style={styles.container}>
      <View style={styles.content}>
        <Ionicons name="analytics-outline" size={48} color="#0a7ea4" style={{ marginBottom: 16 }} />
        <Text style={styles.title}>Analyze</Text>
        <Button title="Scan (Pick Video)" onPress={handleScan} />
        <Text style={styles.subtitle}>History</Text>
        {loading && <ActivityIndicator size="large" color="#0a7ea4" style={{ marginVertical: 16 }} />}
        <FlatList
          data={history}
          keyExtractor={item => item.id}
          renderItem={({ item }) => (
            <TouchableOpacity onPress={() => handleHistoryPress(item)} style={styles.historyItem}>
              <Text style={styles.historyTitle}>{item.title}</Text>
              <Text style={styles.historyDate}>{item.date}</Text>
            </TouchableOpacity>
          )}
          ListEmptyComponent={<Text style={{ color: '#888', marginTop: 16 }}>No analyzes yet.</Text>}
        />
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
    width: '100%',
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
    marginTop: 24,
    marginBottom: 8,
  },
  historyItem: {
    backgroundColor: '#fff',
    padding: 16,
    borderRadius: 8,
    marginBottom: 8,
    width: '100%',
    shadowColor: '#000',
    shadowOpacity: 0.05,
    shadowRadius: 4,
    elevation: 2,
  },
  historyTitle: {
    fontSize: 16,
    fontWeight: '600',
  },
  historyDate: {
    fontSize: 12,
    color: '#888',
  },
})