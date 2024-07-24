import React, { useState, useRef, useEffect } from "react";
import { Canvas, useFrame } from "@react-three/fiber";
import { extend } from "@react-three/fiber";
import { OrbitControls, Float, PerspectiveCamera } from "@react-three/drei";
import { AxesHelper, GridHelper } from "three";
import * as THREE from "three";
import { GoTriangleDown } from "react-icons/go";

import { VerbaVector } from "./types";

import { SettingsConfiguration } from "../Settings/types";

import { VerbaDocument, VectorsPayload, VectorGroup } from "./types";

import { colors } from "./util";

extend({ OrbitControls: OrbitControls });

const Sphere: React.FC<{
  vector: VerbaVector;
  index: number;
  color: string;
  setHoverTitle: (t: string) => void;
  documentTitle: string;
  multiplication: number;
  showAll: boolean;
  minX: number;
  maxX: number;
  minY: number;
  maxY: number;
  minZ: number;
  maxZ: number;
}> = ({
  vector,
  index,
  color,
  setHoverTitle,
  documentTitle,
  multiplication,
  showAll,
  minX,
  maxX,
  minY,
  maxY,
  minZ,
  maxZ,
}) => {
  const ref = useRef<THREE.Mesh>(null!);
  const [hover, setHover] = useState(false);

  function normalize(value: number, min: number, max: number): number {
    if (max === min) return 0; // Avoid division by zero
    return (value - min) / (max - min);
  }

  function vectorToColor(
    vector: VerbaVector,
    minX: number,
    maxX: number,
    minY: number,
    maxY: number,
    minZ: number,
    maxZ: number
  ): THREE.Color {
    // Normalize vector components to be within the range of 0 to 1 based on min and max
    const normalizedX = normalize(vector.x, minX, maxX);
    const normalizedY = normalize(vector.y, minY, maxY);
    const normalizedZ = normalize(vector.z, minZ, maxZ);

    // Scale normalized values to 0-255
    const r = Math.floor(normalizedZ * 255); // Red from Z axis
    const g = Math.floor(normalizedX * 255); // Green from X axis
    const b = Math.floor(normalizedY * 255); // Blue from Y axis

    return new THREE.Color(`rgb(${g},${b},${r})`);
  }

  const sphereColor = showAll
    ? new THREE.Color(color)
    : vectorToColor(vector, minX, maxX, minY, maxY, minZ, maxZ);

  useFrame(() => {
    if (ref.current) {
      ref.current.position.lerp(
        new THREE.Vector3(
          vector.x * multiplication,
          vector.y * multiplication,
          vector.z * multiplication
        ),
        0.02
      );
    }
  });

  return (
    <Float rotationIntensity={0.2}>
      <mesh
        ref={ref}
        position={[0, 0, 0]}
        onPointerEnter={() => {
          setHover(true);
          setHoverTitle(documentTitle);
        }}
        onPointerLeave={() => {
          setHover(false);
        }}
      >
        <sphereGeometry />
        <meshBasicMaterial
          color={sphereColor}
          opacity={0.5}
          transparent={true}
        />
      </mesh>
    </Float>
  );
};

interface VectorViewProps {
  APIHost: string | null;
  selectedDocument: string | null;
  settingConfig: SettingsConfiguration;
}

const VectorView: React.FC<VectorViewProps> = ({
  APIHost,
  selectedDocument,
  settingConfig,
}) => {
  const refs = useRef<(THREE.Mesh | null)[]>([]);
  const [isFetching, setIsFetching] = useState(false);
  const [vectors, setVectors] = useState<VectorGroup[]>([]);
  const [embedder, setEmbedder] = useState("");
  const [showAll, setShowAll] = useState(false);
  const [hoverTitle, setHoverTitle] = useState("");
  const [viewMultiplication, setViewMultiplication] = useState(200);

  const [minX, setMinX] = useState(-1);
  const [maxX, setMaxX] = useState(1);

  const [minY, setMinY] = useState(-1);
  const [maxY, setMaxY] = useState(1);

  const [minZ, setMinZ] = useState(-1);
  const [maxZ, setMaxZ] = useState(1);

  useEffect(() => {
    if (selectedDocument) {
      fetchVectors();
    } else {
      setVectors([]);
    }
  }, [selectedDocument, showAll]);

  function calculateMinMax(values: number[]): { min: number; max: number } {
    const min = Math.min(...values);
    const max = Math.max(...values);
    return { min, max };
  }

  const getVectorCount = () => {
    let vector_count = 0;
    for (const vector_group of vectors) {
      vector_count += vector_group.vectors.length;
    }
    return vector_count;
  };

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
          showAll: showAll,
        }),
      });

      const data: VectorsPayload = await response.json();

      if (data) {
        if (data.error !== "") {
          console.error(data.error);
          setIsFetching(false);
          setVectors([]);
          setEmbedder("None");
        } else {
          setVectors(data.payload.vectors);
          setEmbedder(data.payload.embedder);
          setIsFetching(false);

          if (!showAll) {
            const xValues = data.payload.vectors[0].vectors.map((v) => v.x);
            const yValues = data.payload.vectors[0].vectors.map((v) => v.y);
            const zValues = data.payload.vectors[0].vectors.map((v) => v.z);

            const { min: _minX, max: _maxX } = calculateMinMax(xValues);
            setMinX(_minX);
            setMaxX(_maxX);

            const { min: _minY, max: _maxY } = calculateMinMax(yValues);
            setMinY(_minY);
            setMaxY(_maxY);

            const { min: _minZ, max: _maxZ } = calculateMinMax(zValues);
            setMinZ(_minZ);
            setMaxZ(_maxZ);
          }
        }
      }
    } catch (error) {
      console.error("Failed to fetch document:", error);
      setIsFetching(false);
    }
  };

  function selectColor(index: number): string {
    if (index >= colors.length) {
      const randomIndex = Math.floor(Math.random() * colors.length);
      return colors[randomIndex];
    } else {
      return colors[index];
    }
  }

  return (
    <div className="flex flex-col gap-2 h-full w-full">
      <div className="flex justify-end w-full gap-2 items-center">
        <div className="flex w-full justify-between">
          <div className="flex flex-col gap-2">
            <div className="flex gap-1 items-center">
              {isFetching && (
                <div className="flex items-center justify-center text-text-alt-verba gap-2 h-full">
                  <span className="loading loading-spinner loading-sm"></span>
                </div>
              )}
              <p className="text-text-alt-verba text-sm font-bold">
                Embedding Model:
              </p>
              <p className="text-text-alt-verba text-sm">{embedder}</p>
            </div>
            <div className="flex gap-1 items-center">
              <p className="text-text-alt-verba text-sm font-bold">Hover:</p>
              <p className="text-sm text-text-alt-verba">{hoverTitle}</p>
            </div>
            <div className="flex gap-1 items-center">
              <p className="text-text-alt-verba text-sm font-bold">Vectors:</p>
              <p className="text-sm text-text-alt-verba">{getVectorCount()}</p>
            </div>
          </div>
          <div className="flex gap-2 items-center min-w-[20vw]">
            <div className="flex gap-2 items-center min-w-[10vw]">
              <p className="text-xs text-text-alt-verba">Show All Documents</p>
              <input
                type="checkbox"
                className="toggle"
                checked={showAll}
                onChange={(e) => {
                  setShowAll(e.target.checked);
                }}
              />
            </div>

            <label className="input flex input-sm items-center gap-2 w-full bg-bg-verba">
              <input
                type="number"
                className="grow w-full"
                value={viewMultiplication}
                onChange={(e) => {
                  setViewMultiplication(Number(e.target.value));
                }}
              />
            </label>

            <div className="dropdown dropdown-bottom flex w-full justify-start items-center">
              <button
                tabIndex={0}
                role="button"
                className="btn btn-sm bg-button-verba hover:bg-button-hover-verba text-text-verba w-full flex justify-start border-none"
              >
                <GoTriangleDown size={15} />
                <p>PCA</p>
              </button>
              <ul
                tabIndex={0}
                className="dropdown-content menu bg-base-100 rounded-box z-[1] w-full p-2 shadow"
              ></ul>
            </div>
          </div>
        </div>
      </div>
      <div className="flex flex-grow h-full w-full">
        <Canvas>
          <ambientLight intensity={0.5} />
          <OrbitControls></OrbitControls>
          <PerspectiveCamera makeDefault position={[0, 0, 0 + 150]} />
          <axesHelper args={[50]} />
          {vectors.map((vector_group, index) =>
            vector_group.vectors.map((vector, v_index) => (
              <Sphere
                showAll={showAll}
                multiplication={viewMultiplication}
                key={"Sphere_" + v_index + vector_group.name}
                vector={vector}
                index={v_index}
                color={selectColor(index)}
                setHoverTitle={setHoverTitle}
                documentTitle={vector_group.name}
                minX={minX}
                minY={minY}
                minZ={minZ}
                maxX={maxX}
                maxY={maxY}
                maxZ={maxZ}
              />
            ))
          )}
        </Canvas>
      </div>
    </div>
  );
};

export default VectorView;
