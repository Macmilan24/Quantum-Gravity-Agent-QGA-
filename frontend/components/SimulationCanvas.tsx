"use client";
import { Canvas, useFrame } from "@react-three/fiber";
import { OrbitControls, Stars } from "@react-three/drei";
import { useRef, useMemo } from "react";
import * as THREE from "three";

// The data structure we expect from Python
interface PointData {
  x: number;
  y: number;
  z: number;
  intensity?: number;
}

interface SimulationProps {
  data: PointData[];
  status: string;
}

function ParticleSystem({ data }: { data: PointData[] }) {
  const meshRef = useRef<THREE.Points>(null);

  // Convert JSON data to Three.js BufferGeometry
  const particles = useMemo(() => {
    if (!data || data.length === 0) return null;
    
    const count = data.length;
    const positions = new Float32Array(count * 3);
    const colors = new Float32Array(count * 3);
    const colorObj = new THREE.Color();

    data.forEach((p, i) => {
      positions[i * 3] = p.x;
      positions[i * 3 + 1] = p.y;
      positions[i * 3 + 2] = p.z;

      // Color based on "intensity" or position
      // Cyan to Purple gradient
      const intensity = p.intensity || Math.abs(p.y); 
      colorObj.setHSL(0.5 + intensity * 0.2, 1.0, 0.6);
      colors[i * 3] = colorObj.r;
      colors[i * 3 + 1] = colorObj.g;
      colors[i * 3 + 2] = colorObj.b;
    });

    return { positions, colors };
  }, [data]);

  useFrame((state) => {
    if (meshRef.current) {
      // Slow rotation for cinematic effect
      meshRef.current.rotation.y += 0.002;
      meshRef.current.rotation.z += 0.001;
    }
  });

  if (!particles) return null;

  return (
    <points ref={meshRef}>
      <bufferGeometry>
        <bufferAttribute
          attach="attributes-position"
          count={data.length}
          array={particles.positions}
          itemSize={3}
        />
        <bufferAttribute
          attach="attributes-color"
          count={data.length}
          array={particles.colors}
          itemSize={3}
        />
      </bufferGeometry>
      <pointsMaterial
        size={0.15}
        vertexColors
        transparent
        opacity={0.8}
        sizeAttenuation
        blending={THREE.AdditiveBlending}
      />
    </points>
  );
}

export default function SimulationCanvas({ data, status }: SimulationProps) {
  return (
    <div className="w-full h-full bg-black relative">
      {/* Overlay Status */}
      <div className="absolute top-4 left-4 z-10 text-xs text-cyan-400 font-bold uppercase tracking-widest">
        VISUALIZATION_ENGINE: {status === "SIMULATED" ? "ONLINE" : "STANDBY"}
      </div>

      <Canvas camera={{ position: [5, 5, 5], fov: 60 }}>
        <ambientLight intensity={0.5} />
        <Stars radius={100} depth={50} count={5000} factor={4} saturation={0} fade speed={1} />
        <OrbitControls autoRotate autoRotateSpeed={0.5} />
        
        {data.length > 0 ? (
           <ParticleSystem data={data} />
        ) : (
           // Placeholder Spinning Grid when no data
           <gridHelper args={[10, 10, 0x222222, 0x111111]} />
        )}
      </Canvas>
    </div>
  );
}