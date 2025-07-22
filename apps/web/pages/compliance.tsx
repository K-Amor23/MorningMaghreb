import React from 'react'
import MoroccanMarketInfo from '@/components/MoroccanMarketInfo'
import Header from '@/components/Header'
import Footer from '@/components/Footer'

export default function MoroccanMarketPage() {
  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <Header />
      <MoroccanMarketInfo />
      <Footer />
    </div>
  )
} 