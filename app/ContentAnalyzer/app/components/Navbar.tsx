import React from 'react'
import { View, TouchableOpacity, Text, StyleSheet } from 'react-native'
import { Ionicons } from '@expo/vector-icons'

type NavbarProps = {
  onTabPress?: (tab: 'Feed' | 'Analyze' | 'Profile') => void;
  activeTab?: 'Feed' | 'Analyze' | 'Profile';
};

export function Navbar({ onTabPress, activeTab = 'Feed' }: NavbarProps) {
  return (
    <View style={styles.navbar}>
      <TouchableOpacity style={styles.navItem} onPress={() => onTabPress?.('Feed')}>
        <Ionicons name="home-outline" size={28} color={activeTab === 'Feed' ? '#0a7ea4' : '#888'} />
        <Text style={[styles.navLabel, activeTab === 'Feed' && styles.activeLabel]}>Feed</Text>
      </TouchableOpacity>
      <TouchableOpacity style={styles.navItem} onPress={() => onTabPress?.('Analyze')}>
        <Ionicons name="analytics-outline" size={28} color={activeTab === 'Analyze' ? '#0a7ea4' : '#888'} />
        <Text style={[styles.navLabel, activeTab === 'Analyze' && styles.activeLabel]}>Analyze</Text>
      </TouchableOpacity>
      <TouchableOpacity style={styles.navItem} onPress={() => onTabPress?.('Profile')}>
        <Ionicons name="person-outline" size={28} color={activeTab === 'Profile' ? '#0a7ea4' : '#888'} />
        <Text style={[styles.navLabel, activeTab === 'Profile' && styles.activeLabel]}>Profile</Text>
      </TouchableOpacity>
    </View>
  )
}

const styles = StyleSheet.create({
  navbar: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    alignItems: 'center',
    paddingVertical: 12,
    backgroundColor: '#fff',
    borderTopWidth: 1,
    borderColor: '#e0e1dd',
    elevation: 8,
  },
  navItem: {
    alignItems: 'center',
    flex: 1,
  },
  navLabel: {
    fontSize: 13,
    color: '#888',
    marginTop: 2,
    fontWeight: '500',
  },
  activeLabel: {
    color: '#0a7ea4',
    fontWeight: '700',
  },
})