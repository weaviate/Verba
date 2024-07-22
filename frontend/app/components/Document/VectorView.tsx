import React, { useState, useRef, useEffect } from "react";
import { Canvas, useFrame } from "@react-three/fiber";
import { extend } from "@react-three/fiber";
import { OrbitControls, Float, PerspectiveCamera } from "@react-three/drei";
import { AxesHelper, GridHelper } from "three";
import * as THREE from "three";

import { VerbaVector } from "./types";

import { VerbaDocument, VectorsPayload } from "./types";

extend({ OrbitControls: OrbitControls });

const Sphere: React.FC<{ vector: VerbaVector; index: number }> = ({
  vector,
  index,
}) => {
  const ref = useRef<THREE.Mesh>(null!);

  useFrame(() => {
    if (ref.current) {
      ref.current.position.lerp(
        new THREE.Vector3(vector.x, vector.y, vector.z),
        0.02
      );
    }
  });

  return (
    <Float rotationIntensity={0.2}>
      <mesh ref={ref} position={[0, 0, 0]} onPointerOver={() => {}}>
        <sphereGeometry />
        <meshBasicMaterial color="green" opacity={0.5} transparent={true} />
      </mesh>
    </Float>
  );
};

interface VectorViewProps {
  APIHost: string | null;
  selectedDocument: string | null;
}

const VectorView: React.FC<VectorViewProps> = ({
  APIHost,
  selectedDocument,
}) => {
  const refs = useRef<(THREE.Mesh | null)[]>([]);
  const [isFetching, setIsFetching] = useState(false);
  const [vectors, setVectors] = useState<VerbaVector[]>([]);
  const [showAll, setShowAll] = useState(false);

  useEffect(() => {
    if (selectedDocument) {
      fetchVectors();
    } else {
      setVectors([]);
    }
  }, [selectedDocument, showAll]);

  const fetchVectors = async () => {
    try {
      setIsFetching(true);

      const response = await fetch(APIHost + "/api/get_vectors", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          uuid: selectedDocument,
        }),
      });

      const data: VectorsPayload = await response.json();

      if (data) {
        if (data.error !== "") {
          console.error(data.error);
          setIsFetching(false);
          setVectors([]);
        } else {
          setVectors(data.vectors);
          setIsFetching(false);
        }
      }
    } catch (error) {
      console.error("Failed to fetch document:", error);
      setIsFetching(false);
    }
  };

  const generateRandomVectors = (numVectors: number) => {
    const vectors = [];
    for (let i = 0; i < numVectors; i++) {
      const vector: VerbaVector = {
        x: Math.random() * 100,
        y: Math.random() * 100,
        z: Math.random() * 100,
      };
      vectors.push(vector);
    }
    return vectors;
  };

  const onHover = () => {};

  const onClick = () => {};

  const averagePoint: VerbaVector = vectors.reduce(
    (avg, vector) => {
      avg.x += vector.x / vectors.length;
      avg.y += vector.y / vectors.length;
      avg.z += vector.z / vectors.length;
      return avg;
    },
    { x: 0, y: 0, z: 0 }
  );

  return (
    <div className="flex flex-col gap-2 h-full w-full">
      <div className="flex justify-end w-full gap-2 items-center">
        <p className="text-xs text-text-alt-verba">Show All Chunks</p>
        <input
          type="checkbox"
          className="toggle"
          checked={showAll}
          onChange={(e) => {
            setShowAll(e.target.checked);
          }}
        />
      </div>
      <div className="flex h-full w-full">
        <Canvas>
          <ambientLight intensity={0.5} />
          <OrbitControls></OrbitControls>
          <PerspectiveCamera makeDefault position={[0, 0, 0 + 150]} />
          <axesHelper args={[50]} />
          {vectors.map((vector, index) => (
            <Sphere key={index} vector={vector} index={index} />
          ))}
        </Canvas>
      </div>
    </div>
  );
};

export default VectorView;
