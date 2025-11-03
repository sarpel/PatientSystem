import React from 'react'
import { Link, useLocation } from 'react-router-dom'
import { useSystemStatus } from '../stores/useAppStore'

interface LayoutProps {
  children: React.ReactNode
}

const Layout: React.FC<LayoutProps> = ({ children }) => {
  const location = useLocation()
  const { databaseStatus, aiStatus } = useSystemStatus()

  const isActive = (path: string) => {
    return location.pathname === path
  }

  const statusColor = (status: string) => {
    switch (status) {
      case 'connected':
      case 'ready':
        return 'bg-green-500'
      case 'disconnected':
      case 'unavailable':
        return 'bg-red-500'
      default:
        return 'bg-gray-500'
    }
  }

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            {/* Logo and title */}
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <h1 className="text-xl font-bold text-blue-600">
                  Clinical AI Assistant
                </h1>
              </div>
            </div>

            {/* Status indicators */}
            <div className="flex items-center space-x-4">
              {/* Database status */}
              <div className="flex items-center space-x-2">
                <div className={`w-2 h-2 rounded-full ${statusColor(databaseStatus)}`}></div>
                <span className="text-sm text-gray-600">
                  Database: {databaseStatus}
                </span>
              </div>

              {/* AI status */}
              <div className="flex items-center space-x-2">
                <div className={`w-2 h-2 rounded-full ${statusColor(aiStatus)}`}></div>
                <span className="text-sm text-gray-600">
                  AI: {aiStatus}
                </span>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Navigation */}
      <nav className="bg-blue-600 text-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex space-x-8">
            <Link
              to="/"
              className={`px-3 py-4 text-sm font-medium hover:bg-blue-700 transition-colors ${
                isActive('/') ? 'bg-blue-700 border-b-2 border-white' : ''
              }`}
            >
              Dashboard
            </Link>
            <Link
              to="/search"
              className={`px-3 py-4 text-sm font-medium hover:bg-blue-700 transition-colors ${
                isActive('/search') ? 'bg-blue-700 border-b-2 border-white' : ''
              }`}
            >
              Patient Search
            </Link>
          </div>
        </div>
      </nav>

      {/* Main content */}
      <main className="flex-1 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 w-full">
        {children}
      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-gray-200 mt-auto">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="text-center text-sm text-gray-500">
            © 2024 Clinical AI Assistant. Built with React, FastAPI, and AI.
          </div>
        </div>
      </footer>
    </div>
  )
}

export default Layout
