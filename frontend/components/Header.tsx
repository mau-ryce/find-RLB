import React, { useState } from 'react';
import Link from 'next/link';

export default function Header() {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  return (
    <header className="w-full bg-gradient-to-b from-primary-900 via-primary-700 to-primary-700 border-b border-secondary-500/30 shadow-premium">
      <div className="container mx-auto px-4">
        {/* Main Header Bar */}
        <div className="flex items-center justify-between py-5">
          {/* Logo Section */}
          <Link href="/" className="flex items-center gap-4">
            <div className="w-12 h-12 bg-gradient-to-br from-secondary-500 to-secondary-700 rounded-lg flex items-center justify-center text-white font-bold text-lg shadow-lg">
              F
            </div>
            <div>
              <div className="text-xl font-bold text-white tracking-tight">FIND RLB</div>
              <div className="text-xs text-accent-500 font-medium">Rent. Save. Own.</div>
            </div>
          </Link>

          {/* Search Bar - Desktop */}
          <div className="flex-1 mx-8 hidden lg:block">
            <div className="relative group">
              <input 
                aria-label="Search properties" 
                placeholder="Search city, neighborhood, or property" 
                className="w-full rounded-lg py-3 px-5 bg-primary-500/20 placeholder:text-accent-500 text-white text-sm outline-none focus:ring-2 focus:ring-secondary-500/50 border border-accent-500/20 transition-all group-hover:bg-primary-500/30" 
              />
              <button className="absolute right-2 top-1/2 -translate-y-1/2 px-4 py-2 bg-gradient-to-r from-secondary-500 to-secondary-700 hover:from-secondary-700 hover:to-secondary-500 text-white rounded-md text-sm font-semibold transition-all shadow-lg">
                Search
              </button>
            </div>
          </div>

          {/* Navigation Links - Desktop */}
          <div className="hidden lg:flex items-center gap-8 mr-8">
            <Link href="/landlord" className="text-accent-500 hover:text-white text-sm font-medium transition-colors">Landlord</Link>
            <Link href="/tenant" className="text-accent-500 hover:text-white text-sm font-medium transition-colors">Tenant</Link>
            <Link href="/property" className="text-accent-500 hover:text-white text-sm font-medium transition-colors">Properties</Link>
          </div>

          {/* Auth Links & Mobile Menu */}
          <div className="flex items-center gap-4">
            <Link href="/login" className="hidden sm:block px-4 py-2 text-accent-500 hover:text-white text-sm font-medium transition-colors">
              Login
            </Link>
            <Link href="/register" className="px-6 py-2.5 bg-gradient-to-r from-secondary-500 to-secondary-700 hover:from-secondary-700 hover:to-secondary-500 text-white rounded-lg text-sm font-semibold transition-all shadow-lg">
              Get Started
            </Link>

            {/* Mobile Menu Button */}
            <button 
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="lg:hidden p-2 rounded-lg hover:bg-primary-600/50 transition-colors"
            >
              <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
              </svg>
            </button>
          </div>
        </div>

        {/* Mobile Menu */}
        {mobileMenuOpen && (
          <div className="lg:hidden pb-4 border-t border-primary-600">
            <nav className="flex flex-col gap-3 mt-4">
              <input 
                aria-label="Search properties" 
                placeholder="Search properties" 
                className="w-full rounded-lg py-3 px-4 bg-primary-500/20 placeholder:text-accent-500 text-white text-sm outline-none focus:ring-2 focus:ring-secondary-500/50 border border-accent-500/20" 
              />
              <Link href="/landlord" className="px-4 py-2 text-accent-500 hover:text-white hover:bg-primary-600/30 rounded-lg transition-colors">Landlord</Link>
              <Link href="/tenant" className="px-4 py-2 text-accent-500 hover:text-white hover:bg-primary-600/30 rounded-lg transition-colors">Tenant</Link>
              <Link href="/property" className="px-4 py-2 text-accent-500 hover:text-white hover:bg-primary-600/30 rounded-lg transition-colors">Properties</Link>
              <Link href="/login" className="px-4 py-2 text-accent-500 hover:text-white hover:bg-primary-600/30 rounded-lg transition-colors">Login</Link>
            </nav>
          </div>
        )}
      </div>
    </header>
  );
}
