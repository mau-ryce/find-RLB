'use client';

import React, { useEffect } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { useAuth } from '../hooks/useAuth';

export default function Home() {
  const router = useRouter();
  const { user, isAuthenticated, isLoading, logout } = useAuth();

  useEffect(() => {
    // Redirect to login if not authenticated
    if (!isLoading && !isAuthenticated) {
      router.push('/login');
    }
  }, [isLoading, isAuthenticated, router]);

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-primary-900 to-primary-700 flex items-center justify-center">
        <div className="text-white text-2xl">Loading...</div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return null;
  }

  const handleLogout = async () => {
    await logout();
    router.push('/login');
  };

  const getRoleColor = (role: string) => {
    switch (role) {
      case 'tenant':
        return 'from-primary-500 to-primary-300';
      case 'landlord':
        return 'from-secondary-500 to-secondary-700';
      case 'service_provider':
        return 'from-accent-500 to-accent-700';
      default:
        return 'from-accent-700 to-accent-500';
    }
  };

  return (
    <main className="min-h-screen bg-gradient-to-br from-primary-900 via-primary-700 to-accent-700">
      {/* Hero Section - UEFA Inspired */}
      <section className="w-full bg-gradient-to-b from-primary-900 via-primary-700 to-primary-500/50 py-24 px-4 flex flex-col items-center justify-center text-center">
        <div className="mb-6 inline-block">
          <div className="text-7xl font-black tracking-tighter text-white drop-shadow-2xl">FIND-RLB</div>
        </div>
        <p className="text-2xl text-accent-500 mb-4 font-semibold">AI-Powered Real Estate Autonomous Economy</p>
        <p className="text-accent-300 text-lg max-w-2xl mb-12">Premium platform for rental discovery, property management, and wealth building</p>
        
        <div className="flex flex-col sm:flex-row gap-6 justify-center mb-12">
          <Link href="/tenant/search" className="px-10 py-4 rounded-lg font-bold text-lg bg-gradient-to-r from-secondary-500 to-secondary-700 hover:from-secondary-700 hover:to-secondary-500 text-white shadow-premium transition-all transform hover:scale-105">
            Find a Home
          </Link>
          <Link href="/landlord/listings" className="px-10 py-4 rounded-lg font-bold text-lg bg-gradient-to-r from-accent-500 to-accent-700 hover:from-accent-700 hover:to-accent-500 text-primary-900 shadow-premium transition-all transform hover:scale-105">
            List Your Property
          </Link>
        </div>
        
        <p className="text-accent-300 text-lg"><span className="font-semibold text-secondary-400">Transparent.</span> <span className="font-semibold text-accent-300">Automated.</span> <span className="font-semibold text-primary-300">Intelligent.</span></p>
      </section>

      {/* Featured Properties Section */}
      <section className="max-w-6xl mx-auto py-20 px-4">
        <div className="text-center mb-12">
          <h2 className="text-4xl font-bold text-white mb-2">Featured Properties</h2>
          <div className="h-1 w-24 bg-gradient-to-r from-secondary-500 to-secondary-700 mx-auto"></div>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {/* Featured Property 1 */}
          <div className="bg-gradient-to-br from-accent-50 to-accent-100 rounded-xl shadow-card hover:shadow-premium transition-all duration-300 overflow-hidden group">
            <div className="h-48 w-full bg-gradient-to-br from-primary-700 to-primary-500 flex items-center justify-center text-6xl group-hover:scale-110 transition-transform duration-300">🏠</div>
            <div className="p-6">
              <h3 className="text-2xl font-bold text-primary-900 mb-2">Oceanview Apartment</h3>
              <p className="text-secondary-600 font-semibold mb-2">$1,800/mo · For Rent</p>
              <p className="text-accent-700 mb-6 text-sm">Mombasa, Kenya</p>
              <Link href="/tenant/search" className="block w-full px-4 py-2.5 bg-gradient-to-r from-secondary-500 to-secondary-700 hover:from-secondary-700 hover:to-secondary-500 text-white rounded-lg font-semibold text-center transition-all shadow-card">View Details</Link>
            </div>
          </div>
          
          {/* Featured Property 2 */}
          <div className="bg-gradient-to-br from-accent-50 to-accent-100 rounded-xl shadow-card hover:shadow-premium transition-all duration-300 overflow-hidden group">
            <div className="h-48 w-full bg-gradient-to-br from-primary-500 to-primary-300 flex items-center justify-center text-6xl group-hover:scale-110 transition-transform duration-300">🏰</div>
            <div className="p-6">
              <h3 className="text-2xl font-bold text-primary-900 mb-2">Luxury Villa</h3>
              <p className="text-secondary-600 font-semibold mb-2">$250,000 · For Sale</p>
              <p className="text-accent-700 mb-6 text-sm">Karen, Nairobi</p>
              <Link href="/tenant/search" className="block w-full px-4 py-2.5 bg-gradient-to-r from-secondary-500 to-secondary-700 hover:from-secondary-700 hover:to-secondary-500 text-white rounded-lg font-semibold text-center transition-all shadow-card">View Details</Link>
            </div>
          </div>
          
          {/* Featured Property 3 */}
          <div className="bg-gradient-to-br from-accent-50 to-accent-100 rounded-xl shadow-card hover:shadow-premium transition-all duration-300 overflow-hidden group">
            <div className="h-48 w-full bg-gradient-to-br from-primary-300 to-accent-300 flex items-center justify-center text-6xl group-hover:scale-110 transition-transform duration-300">🏢</div>
            <div className="p-6">
              <h3 className="text-2xl font-bold text-primary-900 mb-2">Modern Studio</h3>
              <p className="text-secondary-600 font-semibold mb-2">$900/mo · For Rent</p>
              <p className="text-accent-700 mb-6 text-sm">Westlands, Nairobi</p>
              <Link href="/tenant/search" className="block w-full px-4 py-2.5 bg-gradient-to-r from-secondary-500 to-secondary-700 hover:from-secondary-700 hover:to-secondary-500 text-white rounded-lg font-semibold text-center transition-all shadow-card">View Details</Link>
            </div>
          </div>
        </div>
      </section>

      {/* Dashboard Section */}
      <section className="bg-gradient-to-r from-primary-800 to-primary-700/50 py-20 px-4 mt-12 mb-12">
        <div className="max-w-6xl mx-auto">
          <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-8 mb-12">
            <div>
              <h1 className="text-4xl font-bold text-white mb-2">Welcome, {user?.first_name}</h1>
              <p className="text-accent-300">Manage your properties and investments</p>
            </div>
            <div className="text-right">
              <div className="mb-4">
                <p className="text-accent-300 text-sm">Account Type</p>
                <span className={`inline-block px-4 py-2 rounded-lg text-sm font-semibold text-white bg-gradient-to-r ${getRoleColor(user?.role || '')} mt-2`}>
                  {user?.role.replace('_', ' ').toUpperCase()}
                </span>
              </div>
              <div className="flex gap-2 justify-end">
                {user?.role === 'admin' && (
                  <Link href="/admin/dashboard" className="px-5 py-2.5 bg-gradient-to-r from-primary-600 to-primary-500 hover:from-primary-500 hover:to-primary-600 text-white rounded-lg text-sm font-semibold transition shadow-card inline-block">
                    Admin Panel
                  </Link>
                )}
                <button
                  onClick={handleLogout}
                  className="px-5 py-2.5 bg-gradient-to-r from-secondary-600 to-secondary-700 hover:from-secondary-700 hover:to-secondary-600 text-white rounded-lg text-sm font-semibold transition shadow-card"
                >
                  Sign Out
                </button>
              </div>
            </div>
          </div>

          {/* Main Navigation Cards */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {/* Tenant App Card */}
            <Link href="/tenant" className="group">
              <div className="bg-gradient-to-br from-primary-600 to-primary-500 rounded-xl shadow-card hover:shadow-premium transition-all duration-300 p-8 text-white cursor-pointer transform hover:scale-105 h-full">
                <div className="mb-4 text-6xl group-hover:scale-125 transition-transform duration-300">👤</div>
                <h2 className="text-3xl font-bold mb-3">Tenant App</h2>
                <p className="text-primary-100 mb-6 text-sm leading-relaxed">Discover premium properties, manage payments, and build wealth through intelligent savings.</p>
                <div className="flex items-center justify-between">
                  <span className="text-xs font-semibold bg-white/20 px-3 py-1.5 rounded-full">8 Features</span>
                  <span className="text-2xl group-hover:translate-x-2 transition-transform">→</span>
                </div>
              </div>
            </Link>

            {/* Landlord Dashboard Card */}
            <Link href="/landlord" className="group">
              <div className="bg-gradient-to-br from-secondary-600 to-secondary-500 rounded-xl shadow-card hover:shadow-premium transition-all duration-300 p-8 text-white cursor-pointer transform hover:scale-105 h-full">
                <div className="mb-4 text-6xl group-hover:scale-125 transition-transform duration-300">🏢</div>
                <h2 className="text-3xl font-bold mb-3">Landlord Dashboard</h2>
                <p className="text-secondary-100 mb-6 text-sm leading-relaxed">Manage properties, track analytics, set pricing, and optimize your rental portfolio with AI.</p>
                <div className="flex items-center justify-between">
                  <span className="text-xs font-semibold bg-white/20 px-3 py-1.5 rounded-full">5 Features</span>
                  <span className="text-2xl group-hover:translate-x-2 transition-transform">→</span>
                </div>
              </div>
            </Link>

            {/* Service Provider Portal Card */}
            <Link href="/service" className="group">
              <div className="bg-gradient-to-br from-accent-600 to-accent-500 rounded-xl shadow-card hover:shadow-premium transition-all duration-300 p-8 text-primary-900 cursor-pointer transform hover:scale-105 h-full">
                <div className="mb-4 text-6xl group-hover:scale-125 transition-transform duration-300">🔧</div>
                <h2 className="text-3xl font-bold mb-3 text-primary-900">Service Portal</h2>
                <p className="text-primary-800 mb-6 text-sm leading-relaxed">Browse premium services, manage bookings, coordinate maintenance efficiently.</p>
                <div className="flex items-center justify-between">
                  <span className="text-xs font-semibold bg-black/10 px-3 py-1.5 rounded-full text-primary-900">3 Services</span>
                  <span className="text-2xl group-hover:translate-x-2 transition-transform text-primary-900">→</span>
                </div>
              </div>
            </Link>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="max-w-6xl mx-auto py-20 px-4">
        <div className="text-center mb-12">
          <h3 className="text-4xl font-bold text-white mb-2">Platform Highlights</h3>
          <div className="h-1 w-24 bg-gradient-to-r from-secondary-500 to-secondary-700 mx-auto"></div>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <div className="bg-gradient-to-br from-primary-700 to-primary-600 rounded-xl p-6 border border-primary-500/30 hover:border-secondary-500/50 transition-all group">
            <div className="text-4xl mb-3 group-hover:scale-125 transition-transform duration-300">🤖</div>
            <h4 className="font-bold text-white mb-2 text-lg">AI Agents</h4>
            <p className="text-primary-200 text-sm leading-relaxed">Smart recommendations powered by advanced machine learning</p>
          </div>
          <div className="bg-gradient-to-br from-primary-700 to-primary-600 rounded-xl p-6 border border-primary-500/30 hover:border-secondary-500/50 transition-all group">
            <div className="text-4xl mb-3 group-hover:scale-125 transition-transform duration-300">⛓️</div>
            <h4 className="font-bold text-white mb-2 text-lg">On-Chain</h4>
            <p className="text-primary-200 text-sm leading-relaxed">Secure Hedera blockchain transactions and smart contracts</p>
          </div>
          <div className="bg-gradient-to-br from-primary-700 to-primary-600 rounded-xl p-6 border border-primary-500/30 hover:border-secondary-500/50 transition-all group">
            <div className="text-4xl mb-3 group-hover:scale-125 transition-transform duration-300">💰</div>
            <h4 className="font-bold text-white mb-2 text-lg">FIND Token</h4>
            <p className="text-primary-200 text-sm leading-relaxed">Native cryptocurrency for platform rewards and governance</p>
          </div>
          <div className="bg-gradient-to-br from-primary-700 to-primary-600 rounded-xl p-6 border border-primary-500/30 hover:border-secondary-500/50 transition-all group">
            <div className="text-4xl mb-3 group-hover:scale-125 transition-transform duration-300">📊</div>
            <h4 className="font-bold text-white mb-2 text-lg">Analytics</h4>
            <p className="text-primary-200 text-sm leading-relaxed">Real-time market insights and comprehensive data analytics</p>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="max-w-4xl mx-auto py-16 px-4 text-center">
        <h3 className="text-3xl font-bold text-white mb-4">Ready to Transform Your Real Estate Journey?</h3>
        <p className="text-accent-300 mb-8 text-lg">Join thousands of users leveraging AI and blockchain for smarter decisions</p>
        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <Link href="/tenant/search" className="px-10 py-3.5 bg-gradient-to-r from-secondary-500 to-secondary-700 hover:from-secondary-700 hover:to-secondary-500 text-white rounded-lg font-semibold shadow-premium transition-all transform hover:scale-105">
            Start Searching
          </Link>
          <Link href="/landlord" className="px-10 py-3.5 border-2 border-accent-500 text-accent-300 hover:bg-accent-500/10 rounded-lg font-semibold transition-all">
            Become a Landlord
          </Link>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-primary-900/80 border-t border-primary-700/50 mt-20 py-8 px-4">
        <div className="max-w-6xl mx-auto text-center text-accent-400 text-sm">
          <p> © 2026 FIND-RLB. Premium real estate platform powered by AI and blockchain.</p>
        </div>
      </footer>
    </main>
  );
}
