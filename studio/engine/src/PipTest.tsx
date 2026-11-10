import React from 'react';
import { ThreeCanvas } from '@remotion/three';
import { AbsoluteFill, useCurrentFrame, useVideoConfig, interpolate } from 'remotion';
import { RoundedBox } from '@react-three/drei';

// A soft, toy-like 3D Pip built from simple shapes.
const Pip: React.FC<{ t: number }> = ({ t }) => {
  const hop = Math.abs(Math.sin(t * 5)) * 0.35;
  const fur = '#f7e6d4', pink = '#ffb3c6';
  return (
    <group position={[0, hop, 0]} rotation={[0, Math.sin(t * 1.5) * 0.4, 0]}>
      <mesh position={[0, 0.9, 0]} castShadow><sphereGeometry args={[0.75, 48, 48]} /><meshStandardMaterial color={fur} roughness={0.85} /></mesh>
      <mesh position={[0, 0.85, 0.42]} castShadow><sphereGeometry args={[0.45, 32, 32]} /><meshStandardMaterial color="#fffaf2" roughness={0.9} /></mesh>
      <mesh position={[0, 2.05, 0]} castShadow><sphereGeometry args={[0.72, 48, 48]} /><meshStandardMaterial color={fur} roughness={0.85} /></mesh>
      {[-1, 1].map((s) => (
        <group key={s} position={[s * 0.3, 2.7, 0]} rotation={[0, 0, -s * (0.15 + Math.sin(t * 4 + s) * 0.05)]}>
          <mesh position={[0, 0.55, 0]} scale={[0.22, 0.75, 0.14]} castShadow><sphereGeometry args={[1, 32, 32]} /><meshStandardMaterial color={fur} roughness={0.85} /></mesh>
          <mesh position={[0, 0.55, 0.08]} scale={[0.11, 0.55, 0.07]}><sphereGeometry args={[1, 24, 24]} /><meshStandardMaterial color={pink} roughness={0.9} /></mesh>
        </group>
      ))}
      {[-1, 1].map((s) => (
        <group key={'e' + s}>
          <mesh position={[s * 0.25, 2.15, 0.6]}><sphereGeometry args={[0.13, 32, 32]} /><meshStandardMaterial color="#1a100c" roughness={0.15} metalness={0.1} /></mesh>
          <mesh position={[s * 0.25 - 0.04, 2.2, 0.72]}><sphereGeometry args={[0.04, 16, 16]} /><meshBasicMaterial color="#ffffff" /></mesh>
          <mesh position={[s * 0.45, 1.95, 0.5]} scale={[1, 0.6, 0.4]}><sphereGeometry args={[0.1, 16, 16]} /><meshStandardMaterial color="#ff8fa8" transparent opacity={0.6} /></mesh>
        </group>
      ))}
      <mesh position={[0, 2.0, 0.71]}><sphereGeometry args={[0.07, 16, 16]} /><meshStandardMaterial color="#ff7f9e" /></mesh>
      <mesh position={[0, 1.45, 0]} rotation={[Math.PI / 2, 0, 0]} castShadow><torusGeometry args={[0.55, 0.12, 16, 48]} /><meshStandardMaterial color="#3d8bff" roughness={0.6} /></mesh>
      {[-1, 1].map((s) => (
        <mesh key={'f' + s} position={[s * 0.35, 0.12, 0.2]} scale={[1, 0.5, 1.4]} castShadow><sphereGeometry args={[0.22, 24, 24]} /><meshStandardMaterial color={fur} roughness={0.85} /></mesh>
      ))}
      <mesh position={[0, 0.8, -0.72]} castShadow><sphereGeometry args={[0.25, 24, 24]} /><meshStandardMaterial color="#ffffff" roughness={1} /></mesh>
    </group>
  );
};

export const PipTest: React.FC = () => {
  const frame = useCurrentFrame();
  const { width, height, fps } = useVideoConfig();
  const t = frame / fps;
  const camZ = interpolate(frame, [0, 72], [8, 6.5]);
  return (
    <AbsoluteFill style={{ background: 'linear-gradient(#8fd3ff, #e6f6ff)' }}>
      <ThreeCanvas width={width} height={height} shadows camera={{ position: [0, 2.2, camZ], fov: 40 }}>
        <ambientLight intensity={0.55} />
        <hemisphereLight args={['#dff4ff', '#7fc95a', 0.6]} />
        <directionalLight position={[4, 8, 5]} intensity={1.6} castShadow shadow-mapSize={[2048, 2048]} shadow-radius={6} />
        <mesh rotation={[-Math.PI / 2, 0, 0]} receiveShadow><circleGeometry args={[12, 64]} /><meshStandardMaterial color="#79c95a" roughness={1} /></mesh>
        {[[-2.5, -3], [2.8, -2.5], [-4, -5]].map(([x, z], i) => (
          <group key={i} position={[x, 0, z]}>
            <mesh position={[0, 0.8, 0]} castShadow><cylinderGeometry args={[0.15, 0.2, 1.6, 16]} /><meshStandardMaterial color="#8a5a3b" /></mesh>
            <mesh position={[0, 2.0, 0]} castShadow><sphereGeometry args={[0.9, 32, 32]} /><meshStandardMaterial color="#4fae4f" roughness={0.9} /></mesh>
          </group>
        ))}
        <RoundedBox args={[1.2, 0.5, 0.6]} radius={0.15} position={[1.6, 0.25, 0.8]} castShadow><meshStandardMaterial color="#e8473f" /></RoundedBox>
        <Pip t={t} />
      </ThreeCanvas>
    </AbsoluteFill>
  );
};
