import React from 'react';
import { AbsoluteFill, spring, useCurrentFrame, useVideoConfig, interpolate } from 'remotion';

// Bouncy, modern title card: letters spring in, soft glow, floating sparkles.
export const TitleCard: React.FC = () => {
  const f = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();
  const title = 'Pip & Pebble'.split('');
  const sub = spring({ frame: f - 22, fps, config: { damping: 12 } });
  const out = interpolate(f, [durationInFrames - 8, durationInFrames], [1, 0], { extrapolateLeft: 'clamp' });
  return (
    <AbsoluteFill style={{ background: 'radial-gradient(circle at 30% 25%, #fff6d6 0%, #9fdcff 45%, #5fb6ef 100%)', fontFamily: 'Inter, sans-serif', opacity: out }}>
      {Array.from({ length: 18 }).map((_, i) => {
        const x = (i * 137) % 1280, y = 720 - ((f * (2 + (i % 4)) + i * 60) % 820);
        return <div key={i} style={{ position: 'absolute', left: x, top: y, width: 14 + (i % 3) * 8, height: 14 + (i % 3) * 8, borderRadius: '50%', background: i % 2 ? 'rgba(255,255,255,.7)' : 'rgba(255,214,90,.75)', filter: 'blur(1px)' }} />;
      })}
      <div style={{ position: 'absolute', top: 210, width: '100%', textAlign: 'center' }}>
        {title.map((ch, i) => {
          const s = spring({ frame: f - i * 2, fps, config: { damping: 8, stiffness: 140 } });
          return (
            <span key={i} style={{ display: 'inline-block', fontSize: 150, fontWeight: 900, color: i < 3 ? '#ff6f3c' : i > 5 ? '#3fae47' : '#3d8bff',
              transform: `translateY(${(1 - s) * -260}px) scale(${0.4 + s * 0.6}) rotate(${(1 - s) * (i % 2 ? 20 : -20)}deg)`,
              textShadow: '0 10px 0 rgba(0,0,0,.08), 0 0 30px rgba(255,255,255,.9)', WebkitTextStroke: '6px white', paintOrder: 'stroke fill', whiteSpace: 'pre' }}>{ch}</span>
          );
        })}
      </div>
      <div style={{ position: 'absolute', top: 430, width: '100%', textAlign: 'center', transform: `scale(${sub})` }}>
        <span style={{ background: '#3d8bff', color: 'white', fontSize: 44, fontWeight: 800, padding: '14px 40px', borderRadius: 60, boxShadow: '0 12px 30px rgba(0,40,120,.25)' }}>Modern Cartoon Test</span>
      </div>
    </AbsoluteFill>
  );
};
