import React, { useState } from 'react';

export default function FiltersSidebar({ onChange }: { onChange?: (f:any)=>void }) {
  const [priceMin, setPriceMin] = useState('');
  const [priceMax, setPriceMax] = useState('');
  const [beds, setBeds] = useState('');
  const [propertyType, setPropertyType] = useState('');
  const [location, setLocation] = useState('');
  const [lat, setLat] = useState('');
  const [lon, setLon] = useState('');
  const [radius, setRadius] = useState('');
  const [sortBy, setSortBy] = useState('');
  const [order, setOrder] = useState('asc');

  function apply() {
    const payload: any = {};
    if (priceMin) payload.price_min = priceMin;
    if (priceMax) payload.price_max = priceMax;
    if (beds) payload.beds = beds;
    if (propertyType) payload.property_type = propertyType;
    if (location) payload.location = location;
    if (lat) payload.lat = lat;
    if (lon) payload.lon = lon;
    if (radius) payload.radius_km = radius;
    if (sortBy) payload.sort_by = sortBy;
    if (order) payload.order = order;
    if (onChange) onChange(payload);
  }

  return (
    <aside className="w-full lg:w-80 bg-gradient-to-br from-accent-50 to-accent-100 rounded-xl p-6 shadow-card border border-accent-200">
      <h3 className="text-lg font-bold text-primary-900 mb-6 flex items-center gap-2">
        <span className="text-xl">⚙️</span>
        Filter Properties
      </h3>

      <div className="space-y-5">
        {/* Location Filter */}
        <div>
          <label className="text-sm font-semibold text-primary-700 block mb-2">Location</label>
          <input 
            value={location} 
            onChange={(e)=>setLocation(e.target.value)} 
            placeholder="City or neighborhood" 
            className="w-full rounded-lg px-4 py-2.5 bg-white border border-accent-300 focus:border-secondary-500 focus:ring-2 focus:ring-secondary-500/20 outline-none transition-all text-primary-900 placeholder-accent-600"
          />
        </div>

        {/* Coordinates Filter */}
        <div>
          <label className="text-sm font-semibold text-primary-700 block mb-2">Center Point (Lat, Lon)</label>
          <div className="flex gap-2">
            <input 
              value={lat} 
              onChange={(e)=>setLat(e.target.value)} 
              placeholder="Latitude" 
              className="w-1/2 rounded-lg px-3 py-2.5 bg-white border border-accent-300 focus:border-secondary-500 focus:ring-2 focus:ring-secondary-500/20 outline-none transition-all text-primary-900 placeholder-accent-600 text-sm"
            />
            <input 
              value={lon} 
              onChange={(e)=>setLon(e.target.value)} 
              placeholder="Longitude" 
              className="w-1/2 rounded-lg px-3 py-2.5 bg-white border border-accent-300 focus:border-secondary-500 focus:ring-2 focus:ring-secondary-500/20 outline-none transition-all text-primary-900 placeholder-accent-600 text-sm"
            />
          </div>
        </div>

        {/* Radius Filter */}
        <div>
          <label className="text-sm font-semibold text-primary-700 block mb-2">Search Radius (km)</label>
          <input 
            value={radius} 
            onChange={(e)=>setRadius(e.target.value)} 
            placeholder="e.g. 2" 
            type="number"
            className="w-full rounded-lg px-4 py-2.5 bg-white border border-accent-300 focus:border-secondary-500 focus:ring-2 focus:ring-secondary-500/20 outline-none transition-all text-primary-900 placeholder-accent-600"
          />
        </div>

        {/* Price Range Filter */}
        <div>
          <label className="text-sm font-semibold text-primary-700 block mb-2">Price Range (USD)</label>
          <div className="flex gap-2">
            <input 
              value={priceMin} 
              onChange={(e)=>setPriceMin(e.target.value)} 
              placeholder="Min" 
              type="number"
              className="w-1/2 rounded-lg px-3 py-2.5 bg-white border border-accent-300 focus:border-secondary-500 focus:ring-2 focus:ring-secondary-500/20 outline-none transition-all text-primary-900 placeholder-accent-600"
            />
            <input 
              value={priceMax} 
              onChange={(e)=>setPriceMax(e.target.value)} 
              placeholder="Max" 
              type="number"
              className="w-1/2 rounded-lg px-3 py-2.5 bg-white border border-accent-300 focus:border-secondary-500 focus:ring-2 focus:ring-secondary-500/20 outline-none transition-all text-primary-900 placeholder-accent-600"
            />
          </div>
        </div>

        {/* Bedrooms Filter */}
        <div>
          <label className="text-sm font-semibold text-primary-700 block mb-2">Bedrooms</label>
          <select 
            value={beds} 
            onChange={(e)=>setBeds(e.target.value)} 
            className="w-full rounded-lg px-4 py-2.5 bg-white border border-accent-300 focus:border-secondary-500 focus:ring-2 focus:ring-secondary-500/20 outline-none transition-all text-primary-900"
          >
            <option value="">Any</option>
            <option value="1">1+</option>
            <option value="2">2+</option>
            <option value="3">3+</option>
            <option value="4">4+</option>
            <option value="5">5+</option>
          </select>
        </div>

        {/* Property Type Filter */}
        <div>
          <label className="text-sm font-semibold text-primary-700 block mb-2">Property Type</label>
          <select 
            value={propertyType} 
            onChange={(e)=>setPropertyType(e.target.value)} 
            className="w-full rounded-lg px-4 py-2.5 bg-white border border-accent-300 focus:border-secondary-500 focus:ring-2 focus:ring-secondary-500/20 outline-none transition-all text-primary-900"
          >
            <option value="">All Types</option>
            <option value="Apartment">Apartment</option>
            <option value="House">House</option>
            <option value="Studio">Studio</option>
            <option value="Penthouse">Penthouse</option>
            <option value="Townhouse">Townhouse</option>
          </select>
        </div>

        {/* Sort Options */}
        <div>
          <label className="text-sm font-semibold text-primary-700 block mb-2">Sort By</label>
          <div className="flex gap-2">
            <select 
              value={sortBy} 
              onChange={(e)=>setSortBy(e.target.value)} 
              className="flex-1 rounded-lg px-3 py-2.5 bg-white border border-accent-300 focus:border-secondary-500 focus:ring-2 focus:ring-secondary-500/20 outline-none transition-all text-primary-900 text-sm"
            >
              <option value="">Relevance</option>
              <option value="price">Price</option>
              <option value="beds">Bedrooms</option>
              <option value="distance_km">Distance</option>
            </select>
            <select 
              value={order} 
              onChange={(e)=>setOrder(e.target.value)} 
              className="w-24 rounded-lg px-3 py-2.5 bg-white border border-accent-300 focus:border-secondary-500 focus:ring-2 focus:ring-secondary-500/20 outline-none transition-all text-primary-900 text-sm"
            >
              <option value="asc">↑ Low</option>
              <option value="desc">↓ High</option>
            </select>
          </div>
        </div>

        {/* Apply Button */}
        <div className="pt-4">
          <button 
            onClick={apply} 
            className="w-full px-6 py-3 bg-gradient-to-r from-secondary-500 to-secondary-700 hover:from-secondary-700 hover:to-secondary-500 text-white font-bold rounded-lg shadow-card hover:shadow-premium transition-all transform hover:scale-105"
          >
            Apply Filters
          </button>
        </div>
      </div>
    </aside>
  );
}
