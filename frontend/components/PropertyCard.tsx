import React from 'react';
import Link from 'next/link';

type Props = {
  title: string;
  price?: string;
  location?: string;
  image?: string;
  href?: string;
}

export default function PropertyCard({ title, price, location, image, href }: Props) {
  const img = image || 'https://images.unsplash.com/photo-1560185127-6ae1b9d6f2c4?auto=format&fit=crop&w=1200&q=80';

  return (
    <Link href={href || '#'} className="group block h-full overflow-hidden rounded-xl bg-gradient-to-br from-accent-50 to-accent-100 shadow-card hover:shadow-premium transition-all duration-300 transform hover:scale-105">
      <div className="h-48 rounded-t-xl bg-cover bg-center group-hover:scale-110 transition-transform duration-300 overflow-hidden" style={{ backgroundImage: `url('${img}')` }}>
        <div className="w-full h-full bg-gradient-to-t from-primary-900/60 to-transparent"></div>
      </div>
      <div className="p-6">
        <div className="flex items-start justify-between mb-3">
          <div className="flex-1">
            <h3 className="text-lg font-bold text-primary-900 group-hover:text-secondary-600 transition-colors">{title}</h3>
            <p className="text-sm text-accent-600 mt-1">{location}</p>
          </div>
        </div>
        <div className="pt-4 border-t border-accent-200 flex items-end justify-between">
          <div>
            <p className="text-2xl font-bold text-secondary-600">{price || '—'}</p>
            <p className="text-xs text-accent-600 font-medium">/month</p>
          </div>
          <div className="text-3xl text-secondary-500 group-hover:translate-x-1 transition-transform">→</div>
        </div>
      </div>
    </Link>
  );
}
