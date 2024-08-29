import * as THREE from "three";
import React, { useState, useRef, useEffect, useMemo, memo } from "react";
import { Canvas, useFrame } from "@react-three/fiber";
import { PresentationControls, useGLTF, Float } from "@react-three/drei";
import CustomShaderMaterial from "three-custom-shader-material/vanilla";
import GUI from "lil-gui";
import { RGBELoader } from "three/addons/loaders/RGBELoader.js";
import { mergeVertices } from "three/addons/utils/BufferGeometryUtils.js";
import { useThree } from "@react-three/fiber";

import wobbleVertexShader from "!raw-loader!../../../public/shaders/wobble/vertex.glsl";
import wobbleFragmentShader from "!raw-loader!../../../public/shaders/wobble/fragment.glsl";

import { FaDatabase } from "react-icons/fa";
import { FaDocker } from "react-icons/fa";
import { FaKey } from "react-icons/fa";
import { FaLaptopCode } from "react-icons/fa";
import { GrConnect } from "react-icons/gr";
import { CgWebsite } from "react-icons/cg";
import { FaBackspace } from "react-icons/fa";
import { HiMiniSparkles } from "react-icons/hi2";

import { connectToVerba } from "@/app/api";

import VerbaButton from "../Navigation/VerbaButton";

import { Credentials, RAGConfig, Theme, Themes } from "@/app/types";

let prefix = "";
if (process.env.NODE_ENV === "production") {
  prefix = "/static";
} else {
  prefix = "";
}

const VerbaThree = ({
  color,
  useMaterial,
  model_path,
}: {
  color: string;
  useMaterial: boolean;
  model_path: string;
}) => {
  const verba_model = useGLTF(prefix + model_path);

  const material = useMemo(
    () =>
      new THREE.MeshPhysicalMaterial({
        metalness: 1,
        roughness: 0.075,
        color: "#f1ff33",
        transmission: 1, // Set to 1 for glass-like transmission
        ior: 1,
        thickness: 1,
        transparent: false,
        wireframe: false,
        clearcoat: 1,
        clearcoatRoughness: 0.0,
      }),
    []
  );

  useEffect(() => {
    const enableGUI = false; // Set this to true to re-enable the GUI

    if (enableGUI) {
      const gui = new GUI();
      const materialFolder = gui.addFolder("Material");

      materialFolder.add(material, "roughness", 0, 1).name("roughness");
      materialFolder.add(material, "metalness", 0, 1).name("metalness");
      materialFolder.add(material, "clearcoat", 0, 1).name("clearcoat");
      materialFolder
        .add(material, "clearcoatRoughness", 0, 1)
        .name("clearcoatRoughness");
      materialFolder.addColor(material, "color").name("color");
      return () => {
        gui.destroy();
      };
    }
  }, [material]);

  // Apply the shiny material to all meshes in the model
  useEffect(() => {
    verba_model.scene.traverse((child) => {
      if (child instanceof THREE.Mesh) {
        console.log("Mesh:", child.name, "Material:", child.material);
        if (!useMaterial) {
          child.material = material;
        } else {
          child.material.roughness = 0.2;
          child.material.metalness = 0.6;
        }
      }
    });
  }, [verba_model, material]);

  return (
    <>
      <color args={[color]} attach="background" />
      <PresentationControls
        global
        rotation={[0.13, 0.1, 0]}
        polar={[-0.4, 0.2]}
        azimuth={[-1, 0.75]}
        config={{ mass: 2, tension: 400 }}
        snap={{ mass: 4, tension: 400 }}
      >
        <Float speed={1} rotationIntensity={0.4}>
          <primitive
            object={verba_model.scene}
            position-y={-0.1}
            position-x={0.15}
            position-z={-1}
            scale={0.6}
          />
        </Float>
      </PresentationControls>
    </>
  );
};

const CoolShape = memo(
  ({
    startPosition,
    endPosition,
    size,
    colorA,
    colorB,
  }: {
    startPosition: [number, number, number];
    endPosition: [number, number, number];
    size: number;
    colorA: string;
    colorB: string;
  }) => {
    const uniforms = useMemo(
      () => ({
        uTime: { value: 0 },
        uPositionFrequency: { value: 0.677 },
        uTimeFrequency: { value: 0.041 },
        uStrength: { value: 0.557 },

        uWarpPositionFrequency: { value: 0.267 },
        uWarpTimeFrequency: { value: 0.135 },
        uWarpStrength: { value: 0.238 },

        uColorA: { value: new THREE.Color(colorA) },
        uColorB: { value: new THREE.Color(colorB) },

        // New uniforms for glass effect
        uRefractionStrength: { value: 0.1 },
        uFresnelPower: { value: 2.0 },
        uTransparency: { value: 0.5 },
      }),
      []
    );

    const material = useMemo(
      () =>
        new CustomShaderMaterial({
          baseMaterial: THREE.MeshPhysicalMaterial,
          metalness: 1,
          roughness: 0.914,
          uniforms,
          color: "#ffffff",
          transmission: 1, // Set to 1 for glass-like transmission
          ior: 1.5,
          thickness: 1,
          silent: true,
          transparent: true,
          wireframe: false,
          clearcoat: 1,
          clearcoatRoughness: 0.0,
          vertexShader: wobbleVertexShader,
          fragmentShader: wobbleFragmentShader,
        }),
      []
    );

    const depth_material = useMemo(
      () =>
        new CustomShaderMaterial({
          baseMaterial: THREE.MeshDepthMaterial,
          silent: true,
          vertexShader: wobbleVertexShader,
          depthPacking: THREE.RGBADepthPacking,
        }),
      []
    );

    const meshRef = useRef<THREE.Mesh>(null);
    const initialPositionRef = useRef<THREE.Vector3 | null>(null);
    const targetPosition = new THREE.Vector3(...endPosition);

    useEffect(() => {
      if (meshRef.current) {
        initialPositionRef.current = new THREE.Vector3(...startPosition);
        meshRef.current.position.copy(initialPositionRef.current);
      }
    }, [startPosition]);

    useEffect(() => {
      const enableGUI = false; // Set this to true to re-enable the GUI

      if (enableGUI) {
        const gui = new GUI();
        const materialFolder = gui.addFolder("Material");

        materialFolder
          .add(uniforms.uPositionFrequency, "value", 0, 1)
          .name("uPositionFrequency");
        materialFolder
          .add(uniforms.uTimeFrequency, "value", 0, 1)
          .name("uTimeFrequency");
        materialFolder.add(uniforms.uStrength, "value", 0, 1).name("uStrength");
        materialFolder
          .add(uniforms.uWarpPositionFrequency, "value", 0, 1)
          .name("uWarpPositionFrequency");
        materialFolder
          .add(uniforms.uWarpTimeFrequency, "value", 0, 1)
          .name("uWarpTimeFrequency");
        materialFolder
          .add(uniforms.uWarpStrength, "value", 0, 1)
          .name("uWarpStrength");
        materialFolder
          .addColor(uniforms.uColorA, "value")
          .name("uColorA")
          .onChange((value: string | number[] | THREE.Color) => {
            if (value instanceof THREE.Color) {
              uniforms.uColorA.value.copy(value);
            } else if (Array.isArray(value)) {
              uniforms.uColorA.value.setRGB(value[0], value[1], value[2]);
            } else {
              uniforms.uColorA.value.set(value);
            }
          });
        materialFolder
          .addColor(uniforms.uColorB, "value")
          .name("uColorB")
          .onChange((value: string | number[] | THREE.Color) => {
            if (value instanceof THREE.Color) {
              uniforms.uColorB.value.copy(value);
            } else if (Array.isArray(value)) {
              uniforms.uColorB.value.setRGB(value[0], value[1], value[2]);
            } else {
              uniforms.uColorB.value.set(value);
            }
          });
        materialFolder.add(material, "roughness", 0, 1).name("roughness");
        materialFolder.add(material, "metalness", 0, 1).name("metalness");
        materialFolder.add(material, "clearcoat", 0, 1).name("clearcoat");
        materialFolder
          .add(material, "clearcoatRoughness", 0, 1)
          .name("clearcoatRoughness");

        // Add new GUI controls for glass effect
        materialFolder
          .add(uniforms.uRefractionStrength, "value", 0, 1)
          .name("Refraction Strength");
        materialFolder
          .add(uniforms.uFresnelPower, "value", 0, 10)
          .name("Fresnel Power");
        materialFolder
          .add(uniforms.uTransparency, "value", 0, 1)
          .name("Transparency");

        return () => {
          gui.destroy();
        };
      }
    }, [material]);

    useFrame((state, delta) => {
      uniforms.uTime.value = state.clock.elapsedTime;

      if (meshRef.current && initialPositionRef.current) {
        meshRef.current.position.lerp(targetPosition, 0.02);

        // Stop the animation when close enough to the target
        if (meshRef.current.position.distanceTo(targetPosition) < 0.01) {
          initialPositionRef.current = null;
        }
      }
    });

    const geometry = new THREE.IcosahedronGeometry(size, 30);
    const mergedGeometry = mergeVertices(geometry);
    mergedGeometry.computeTangents();
    return (
      <mesh
        ref={meshRef}
        material={material}
        receiveShadow={true}
        castShadow={true}
        customDepthMaterial={depth_material}
      >
        <bufferGeometry attach="geometry" {...mergedGeometry} />
      </mesh>
    );
  }
);

CoolShape.displayName = "CoolShape";

const EnvironmentMap = () => {
  const { scene } = useThree();

  useEffect(() => {
    const rgbeLoader = new RGBELoader();
    rgbeLoader.load(prefix + "/alps_field_1k.hdr", (environmentMap) => {
      environmentMap.mapping = THREE.EquirectangularReflectionMapping;
      scene.environment = environmentMap;
    });
  }, [scene]);

  return null;
};

interface LoginViewProps {
  credentials: Credentials;
  setCredentials: (c: Credentials) => void;
  setIsLoggedIn: (isLoggedIn: boolean) => void;
  setRAGConfig: (RAGConfig: RAGConfig | null) => void;
  setSelectedTheme: (theme: Theme) => void;
  setThemes: (themes: Themes) => void;
  production: "Local" | "Demo" | "Production";
}

const LoginView: React.FC<LoginViewProps> = ({
  credentials,
  setCredentials,
  setSelectedTheme,
  setThemes,
  setIsLoggedIn,
  production,
  setRAGConfig,
}) => {
  const [isLoading, setIsLoading] = useState(true);

  const [isConnecting, setIsConnecting] = useState(false);

  const [selectStage, setSelectStage] = useState(true);

  const [errorText, setErrorText] = useState("");

  const [selectedDeployment, setSelectedDeployment] = useState<
    "Weaviate" | "Docker" | "Local"
  >("Local");

  const [weaviateURL, setWeaviateURL] = useState(credentials.url);
  const [weaviateAPIKey, setWeaviateAPIKey] = useState(credentials.key);

  useEffect(() => {
    const timer = setTimeout(() => {
      setIsLoading(false);
    }, 300); // Adjust this delay as needed

    return () => clearTimeout(timer);
  }, []);

  const connect = async (deployment: "Local" | "Weaviate" | "Docker") => {
    setErrorText("");
    setIsConnecting(true);
    const response = await connectToVerba(
      deployment,
      weaviateURL,
      weaviateAPIKey
    );
    if (response) {
      if (response.error) {
        setIsLoggedIn(false);
        setErrorText(response.error);
      } else {
        setIsLoggedIn(true);
        setCredentials({
          deployment: deployment,
          key: weaviateAPIKey,
          url: weaviateURL,
        });
        setRAGConfig(response.rag_config);
        if (response.themes) {
          setThemes(response.themes);
        }
        if (response.theme) {
          setSelectedTheme(response.theme);
        }
      }
    }
    setIsConnecting(false);
  };

  const coolShapes = useMemo(
    () => (
      <>
        <CoolShape
          startPosition={[-3.3, -0.8, -1]}
          endPosition={[-1.3, -1, -4]}
          size={2}
          colorA="#00ffbf"
          colorB="#00ff01"
        />
        <CoolShape
          startPosition={[1.5, 10, -6]}
          endPosition={[1.5, 1, -5]}
          size={1}
          colorA="#00c0ff"
          colorB="#00c0ff"
        />
      </>
    ),
    []
  );

  return (
    <div className="w-screen h-screen bg-white">
      <div
        className={`flex w-full h-full transition-opacity duration-1000 ${
          isLoading ? "opacity-0" : "opacity-100"
        }`}
      >
        <div className="hidden md:flex md:w-1/2 lg:w-3/5 h-full">
          <Canvas
            camera={{ position: [0, -0.25, 3], fov: 50 }}
            className="w-full h-full touch-none"
          >
            <color attach="background" args={["#FAFAFA"]} />
            <EnvironmentMap />
            <ambientLight intensity={0.5} />
            <directionalLight position={[5, 5, 5]} intensity={1.5} />
            {/**coolShapes**/}
            <VerbaThree
              color="#FAFAFA"
              useMaterial={production == "Local" ? false : true}
              model_path={
                production == "Local" ? "/verba.glb" : "/weaviate.glb"
              }
            />
          </Canvas>
        </div>
        <div className="w-full md:flex md:w-1/2 lg:w-2/5 h-full flex justify-center items-center p-5">
          <div className="flex flex-col gap-8 items-start justify-center w-4/5">
            <div className="flex flex-col items-start gap-2">
              <div className="flex items-center gap-3">
                <p className="font-light text-2xl lg:text-4xl text-text-alt-verba">
                  Welcome to
                </p>
                <p className="font-light text-2xl lg:text-4xl text-text-verba">
                  Verba
                </p>
              </div>
              {production == "Local" && (
                <p className="text-text-verba text-base lg:text-lg ">
                  Choose your deployment
                </p>
              )}
            </div>
            {selectStage ? (
              <div className="flex flex-col justify-start gap-4 w-full">
                {production == "Local" && (
                  <div className="flex flex-col justify-start gap-2 w-full">
                    <VerbaButton
                      Icon={FaDatabase}
                      title="Weaviate"
                      disabled={isConnecting}
                      onClick={() => {
                        setSelectStage(false);
                        setSelectedDeployment("Weaviate");
                      }}
                    />
                    <VerbaButton
                      title="Docker"
                      Icon={FaDocker}
                      disabled={isConnecting}
                      onClick={() => {
                        setSelectedDeployment("Docker");
                        connect("Docker");
                      }}
                      loading={isConnecting && selectedDeployment == "Docker"}
                    />
                    <VerbaButton
                      title="Local"
                      Icon={FaLaptopCode}
                      disabled={isConnecting}
                      onClick={() => {
                        setSelectedDeployment("Local");
                        connect("Local");
                      }}
                      loading={isConnecting && selectedDeployment == "Local"}
                    />
                  </div>
                )}
                {production == "Demo" && (
                  <div className="flex flex-col justify-start gap-4 w-full">
                    <VerbaButton
                      Icon={HiMiniSparkles}
                      title="Start Demo"
                      disabled={isConnecting}
                      onClick={() => {
                        setSelectedDeployment("Weaviate");
                        connect("Weaviate");
                      }}
                      loading={isConnecting && selectedDeployment == "Weaviate"}
                    />
                  </div>
                )}
                {production == "Production" && (
                  <div className="flex flex-col justify-start gap-4 w-full">
                    <VerbaButton
                      Icon={HiMiniSparkles}
                      title="Start Verba"
                      onClick={() => {
                        setSelectStage(false);
                        setSelectedDeployment("Weaviate");
                      }}
                    />
                  </div>
                )}
              </div>
            ) : (
              <div className="flex flex-col justify-start gap-4 w-full">
                {production != "Demo" && (
                  <div className="flex flex-col justify-start gap-4 w-full">
                    <form
                      onSubmit={(e) => {
                        e.preventDefault();
                        connect(selectedDeployment);
                      }}
                    >
                      <label className="input flex items-center gap-2 border-none shadow-md bg-bg-verba">
                        <FaDatabase className="text-text-alt-verba" />
                        <input
                          type="text"
                          name="username"
                          value={weaviateURL}
                          onChange={(e) => setWeaviateURL(e.target.value)}
                          placeholder="Weaviate URL"
                          className="grow bg-button-verba text-text-alt-verba hover:text-text-verba w-full"
                          autoComplete="username"
                        />
                      </label>
                      <label className="input flex items-center gap-2 border-none shadow-md bg-bg-verba mt-4">
                        <FaKey className="text-text-alt-verba" />
                        <input
                          type="password"
                          name="current-password"
                          value={weaviateAPIKey}
                          onChange={(e) => setWeaviateAPIKey(e.target.value)}
                          placeholder="API Key"
                          className="grow bg-button-verba text-text-alt-verba hover:text-text-verba w-full"
                          autoComplete="current-password"
                        />
                      </label>
                      <div className="flex justify-between gap-4 mt-4">
                        <div className="flex flex-col w-full gap-2">
                          <div className="flex flex-col justify-start gap-2 w-full">
                            <VerbaButton
                              Icon={GrConnect}
                              title="Connect to Weaviate"
                              type="submit"
                              selected={true}
                              selected_color="bg-primary-verba"
                              loading={isConnecting}
                            />
                            <VerbaButton
                              Icon={CgWebsite}
                              title="Register"
                              type="button"
                              disabled={isConnecting}
                              onClick={() =>
                                window.open(
                                  "https://console.weaviate.cloud",
                                  "_blank"
                                )
                              }
                            />
                            <VerbaButton
                              Icon={FaBackspace}
                              title="Back to Deployments"
                              type="button"
                              button_size="btn-sm"
                              text_size="text-xs"
                              icon_size={12}
                              onClick={() => setSelectStage(true)}
                              disabled={isConnecting}
                            />
                          </div>
                        </div>
                      </div>
                    </form>
                  </div>
                )}
              </div>
            )}
            {errorText && (
              <div className="bg-warning-verba p-4 rounded w-full">
                <p className="flex w-full whitespace-pre-wrap">{errorText}</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default LoginView;
