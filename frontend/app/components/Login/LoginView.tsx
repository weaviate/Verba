import React, {
  useState,
  useRef,
  useEffect,
  useMemo,
  useCallback,
} from "react";
import { Canvas, useFrame } from "@react-three/fiber";
import {
  PresentationControls,
  useGLTF,
  ContactShadows,
  Environment,
  Float,
  Text,
} from "@react-three/drei";

const VerbaThree = ({ color }: { color: string }) => {
  const verba_model = useGLTF("/verba.gltf");
  const book = useGLTF(
    "https://vazxmixjsiawhamofees.supabase.co/storage/v1/object/public/models/open-book/model.gltf"
  );
  const keyboard = useGLTF(
    "https://vazxmixjsiawhamofees.supabase.co/storage/v1/object/public/models/mechanical-keyboard/model.gltf"
  );

  return (
    <>
      <color args={[color]} attach="background" />
      <Environment preset="city" />
      <PresentationControls
        global
        rotation={[0.13, 0.1, 0]}
        polar={[-0.4, 0.2]}
        azimuth={[-1, 0.75]}
        config={{ mass: 2, tension: 400 }}
        snap={{ mass: 4, tension: 400 }}
      >
        <Float speed={1} rotationIntensity={0.4}>
          <rectAreaLight
            width={2.5}
            height={1.65}
            intensity={65}
            color={"#ff6900"}
            rotation={[-0.1, Math.PI, 0]}
            position={[0, 0.55, -1.15]}
          />
          <primitive
            object={book.scene}
            position-y={-0.3}
            position-x={0}
            position-z={-0.5}
            rotation-x={0.5}
            scale={3}
          />
          <primitive
            object={keyboard.scene}
            position-y={-1.2}
            position-x={0}
            position-z={0}
            scale={1}
          />
          <Text
            fontSize={0.5}
            position={[2, 0.75, 0.75]}
            rotation-y={-1.25}
            maxWidth={3}
          >
            Verba
          </Text>
        </Float>
      </PresentationControls>

      <ContactShadows position-y={-1.4} opacity={0.4} scale={5} blur={2.4} />
    </>
  );
};

interface LoginViewProps {
  color: string;
}

const LoginView: React.FC<LoginViewProps> = ({ color }) => {
  return (
    <Canvas
      style={{
        width: "100%",
        height: "100%",
        top: "0",
        left: "0",
        position: "fixed",
        touchAction: "none",
      }}
      camera={{
        fov: 45,
        near: 0.1,
        far: 2000,
        position: [-3, 1.5, 4],
      }}
    >
      <VerbaThree color={color} />
    </Canvas>
  );
};

export default LoginView;
