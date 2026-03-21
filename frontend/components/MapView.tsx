"use client";

import React, { useEffect, useRef } from 'react';

export default function MapView({ properties }: { properties: any[] }){
  const mapRef = useRef<any>(null);
  const containerRef = useRef<HTMLDivElement | null>(null);

  useEffect(()=>{
    // Load Leaflet CSS and JS from CDN if not present
    const LCSS = 'https://unpkg.com/leaflet@1.9.4/dist/leaflet.css';
    const LJS = 'https://unpkg.com/leaflet@1.9.4/dist/leaflet.js';

    function addLink(){
      if (!document.querySelector(`link[href="${LCSS}"]`)){
        const link = document.createElement('link');
        link.rel = 'stylesheet';
        link.href = LCSS;
        document.head.appendChild(link);
      }
    }

    function addScript(cb:any){
      if ((window as any).L) return cb();
      if (document.querySelector(`script[src="${LJS}"]`)) return document.querySelector(`script[src="${LJS}"]`)?.addEventListener('load', cb);
      const s = document.createElement('script');
      s.src = LJS;
      s.async = true;
      s.onload = cb;
      document.body.appendChild(s);
    }

    addLink();
    addScript(()=>{
      const L = (window as any).L;
      if (!containerRef.current) return;
      if (mapRef.current) {
        mapRef.current.remove();
        mapRef.current = null;
      }
      const center = properties && properties.length>0 ? [properties[0].lat || -4.0435, properties[0].lon || 39.6636] : [-4.0435,39.6636];
      mapRef.current = L.map(containerRef.current).setView(center, 13);
      L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 19,
      }).addTo(mapRef.current);

      // Add markers
      properties.forEach(p=>{
        if (p.lat && p.lon){
          const marker = L.marker([p.lat, p.lon]).addTo(mapRef.current);
          marker.bindPopup(`<strong>${p.title}</strong><br/>${p.location}<br/>$${p.price}`);
        }
      });
    });

    return ()=>{
      if (mapRef.current) { mapRef.current.remove(); mapRef.current = null; }
    }
  }, [properties]);

  return (
    <div className="w-full h-80 rounded-xl overflow-hidden shadow-premium border-2 border-secondary-500/30 bg-gradient-to-br from-primary-700 to-primary-600">
      <div ref={containerRef} style={{ width: '100%', height: '100%' }} />
    </div>
  );
}
