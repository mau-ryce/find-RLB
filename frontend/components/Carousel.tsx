import React, { useState, useEffect } from 'react';

export default function Carousel({ images }: { images: string[] }) {
  const [index, setIndex] = useState(0);

  useEffect(() => {
    const t = setInterval(() => setIndex(i => (i + 1) % images.length), 4000);
    return () => clearInterval(t);
  }, [images.length]);

  if (!images || images.length === 0) return null;

  return (
    <div className="relative rounded-2xl overflow-hidden shadow-premium">
      <div className="h-64 md:h-96 bg-gradient-to-br from-primary-700 to-primary-500">
        {images.map((src, i) => (
          <img
            key={i}
            src={src}
            alt={`slide-${i}`}
            className={`w-full h-full object-cover absolute inset-0 transition-opacity duration-700 ${i === index ? 'opacity-100' : 'opacity-0'}`}
          />
        ))}
      </div>

      {/* Navigation Buttons */}
      <div className="absolute left-4 top-1/2 transform -translate-y-1/2">
        <button 
          onClick={() => setIndex((index-1+images.length)%images.length)} 
          className="px-3 py-2 rounded-full bg-secondary-500/80 hover:bg-secondary-700 text-white font-bold transition-all transform hover:scale-110 shadow-lg"
        >
          ◀
        </button>
      </div>
      <div className="absolute right-4 top-1/2 transform -translate-y-1/2">
        <button 
          onClick={() => setIndex((index+1)%images.length)} 
          className="px-3 py-2 rounded-full bg-secondary-500/80 hover:bg-secondary-700 text-white font-bold transition-all transform hover:scale-110 shadow-lg"
        >
          ▶
        </button>
      </div>

      {/* Indicators */}
      <div className="absolute bottom-4 left-1/2 transform -translate-x-1/2 flex gap-2">
        {images.map((_, i) => (
          <button
            key={i}
            onClick={() => setIndex(i)}
            className={`h-2 rounded-full transition-all ${
              i === index 
                ? 'w-6 bg-secondary-500' 
                : 'w-2 bg-accent-500/50 hover:bg-accent-500'
            }`}
          />
        ))}
      </div>
    </div>
  );
}
