"use client";

import React, { useState, useEffect, useCallback } from "react";
import { GoogleAnalytics } from "@next/third-parties/google";

// Components
import Navbar from "./components/Navigation/NavbarComponent";
import DocumentView from "./components/Document/DocumentView";
import IngestionView from "./components/Ingestion/IngestionView";
import LoginView from "./components/Login/LoginView";
import ChatView from "./components/Chat/ChatView";
import SettingsView from "./components/Settings/SettingsView";

// Types
import {
  Credentials,
  RAGConfig,
  Theme,
  LightTheme,
  Themes,
  DarkTheme,
  WCDTheme,
  WeaviateTheme,
} from "./types";

// Utilities
import { fetchHealth } from "./api";
import { fonts, FontKey } from "./util";

export default function Home() {
  // Page States
  const [currentPage, setCurrentPage] = useState("CHAT");
  const [production, setProduction] = useState<"Local" | "Demo" | "Production">(
    "Local"
  );
  const [gtag, setGtag] = useState("");

  // Settings
  const [themes, setThemes] = useState<Themes>({
    Light: LightTheme,
    Dark: DarkTheme,
    Weaviate: WeaviateTheme,
    WCD: WCDTheme,
  });
  const [selectedTheme, setSelectedTheme] = useState<Theme>(themes["Weaviate"]);

  const fontKey = selectedTheme.font.value as FontKey; // Safely cast if you're sure, or use a check
  const fontClassName = fontKey ? fonts[fontKey]?.className || "" : "";

  // Login States
  const [isHealthy, setIsHealthy] = useState(false);
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [isLoaded, setIsLoaded] = useState(false);
  const [credentials, setCredentials] = useState<Credentials>({
    deployment: "Local",
    url: "",
    key: "",
  });

  // RAG Config
  const [RAGConfig, setRAGConfig] = useState<null | RAGConfig>(null);

  const initialFetch = useCallback(async () => {
    try {
      const [health_data] = await Promise.all([fetchHealth()]);

      if (health_data) {
        setProduction(health_data.production);
        setGtag(health_data.gtag);
        setIsHealthy(true);
        setCredentials({
          deployment: "Local",
          url: health_data.deployments.WEAVIATE_URL_VERBA,
          key: health_data.deployments.WEAVIATE_API_KEY_VERBA,
        });
      } else {
        console.warn("Could not retrieve health data");
        setIsHealthy(false);
        setIsLoggedIn(false);
      }
    } catch (error) {
      console.error("Error during initial fetch:", error);
      setIsHealthy(false);
      setIsLoggedIn(false);
    }
  }, []);

  useEffect(() => {
    initialFetch();
  }, []);

  useEffect(() => {
    if (isLoggedIn) {
      const timer = setTimeout(() => {
        setIsLoaded(true);
      }, 1000);

      return () => clearTimeout(timer);
    }
  }, [isLoggedIn]);

  const updateCSSVariables = useCallback(() => {
    const cssVars = {
      "--primary-verba": selectedTheme.primary_color.color,
      "--secondary-verba": selectedTheme.secondary_color.color,
      "--warning-verba": selectedTheme.warning_color.color,
      "--bg-verba": selectedTheme.bg_color.color,
      "--bg-alt-verba": selectedTheme.bg_alt_color.color,
      "--text-verba": selectedTheme.text_color.color,
      "--text-alt-verba": selectedTheme.text_alt_color.color,
      "--button-verba": selectedTheme.button_color.color,
      "--button-hover-verba": selectedTheme.button_hover_color.color,
    };
    Object.entries(cssVars).forEach(([key, value]) => {
      document.documentElement.style.setProperty(key, value);
    });
  }, [selectedTheme]);

  useEffect(updateCSSVariables, [selectedTheme]);

  return (
    <main
      className={`min-h-screen bg-bg-verba text-text-verba ${fontClassName}`}
      data-theme={selectedTheme.theme}
    >
      {gtag !== "" && <GoogleAnalytics gaId={gtag} />}

      {!isLoggedIn && isHealthy && (
        <LoginView
          production={production}
          setSelectedTheme={setSelectedTheme}
          setThemes={setThemes}
          credentials={credentials}
          setIsLoggedIn={setIsLoggedIn}
          setRAGConfig={setRAGConfig}
          setCredentials={setCredentials}
        />
      )}

      {isLoggedIn && isHealthy && (
        <div
          className={`transition-opacity duration-1000 ${
            isLoaded ? "opacity-100" : "opacity-0"
          } flex flex-col gap-2 p-5`}
        >
          <div>
            <Navbar
              production={production}
              title={selectedTheme.title.text}
              subtitle={selectedTheme.subtitle.text}
              imageSrc={selectedTheme.image.src}
              version="v2.0.0"
              currentPage={currentPage}
              setCurrentPage={setCurrentPage}
            />

            <div className={`${currentPage === "CHAT" ? "" : "hidden"}`}>
              <ChatView
                credentials={credentials}
                RAGConfig={RAGConfig}
                setRAGConfig={setRAGConfig}
                production={production}
                selectedTheme={selectedTheme}
                currentPage={currentPage}
              />
            </div>

            {currentPage === "DOCUMENTS" && (
              <DocumentView
                credentials={credentials}
                production={production}
                selectedTheme={selectedTheme}
              />
            )}

            <div
              className={`${
                currentPage === "ADD" && production != "Demo" ? "" : "hidden"
              }`}
            >
              <IngestionView
                RAGConfig={RAGConfig}
                setRAGConfig={setRAGConfig}
                credentials={credentials}
              />
            </div>

            <div
              className={`${
                currentPage === "SETTINGS" && production != "Demo"
                  ? ""
                  : "hidden"
              }`}
            >
              <SettingsView
                credentials={credentials}
                selectedTheme={selectedTheme}
                setSelectedTheme={setSelectedTheme}
                themes={themes}
                setThemes={setThemes}
              />
            </div>
          </div>

          <footer
            className={`footer footer-center p-4 mt-8 bg-bg-verba text-text-alt-verba transition-all duration-1500 delay-1000 ${
              isLoggedIn
                ? "opacity-100 translate-y-0"
                : "opacity-0 translate-y-4"
            }`}
          >
            <aside>
              <p>Build with ♥ and Weaviate © 2024</p>
            </aside>
          </footer>
        </div>
      )}

      <img
        referrerPolicy="no-referrer-when-downgrade"
        src="https://static.scarf.sh/a.png?x-pxid=ec666e70-aee5-4e87-bc62-0935afae63ac"
      />
    </main>
  );
}
