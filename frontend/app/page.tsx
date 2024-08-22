"use client";

import React, { useState, useEffect, useCallback } from "react";
import { GoogleAnalytics } from "@next/third-parties/google";

// Components
import Navbar from "./components/Navigation/NavbarComponent";
import DocumentView from "./components/Document/DocumentView";
import IngestionView from "./components/Ingestion/IngestionView";
import LoginView from "./components/Login/LoginView";
import ChatView from "./components/Chat/ChatView";

// Types
import { Settings, BaseSettings } from "./components/Settings/types";
import { Credentials, RAGConfig } from "./api_types";

// Utilities
import { fetchHealth, fetchRAGConfig } from "./api";
import { fonts, FontKey } from "./util";

export default function Home() {
  // Page States
  const [currentPage, setCurrentPage] = useState("CHAT");
  const [production, setProduction] = useState(false);
  const [gtag, setGtag] = useState("");

  // Settings
  const [settingTemplate, setSettingTemplate] = useState("Default");
  const [baseSetting, setBaseSetting] = useState<Settings>(BaseSettings);

  const fontKey = baseSetting
    ? (baseSetting[settingTemplate].Customization.settings.font
        .value as FontKey)
    : null; // Safely cast if you're sure, or use a check
  const fontClassName = fontKey ? fonts[fontKey]?.className || "" : "";

  // Login States
  const [isHealthy, setIsHealthy] = useState(false);
  const [isLoggedIn, setIsLoggedIn] = useState(false);
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

  const updateCSSVariables = useCallback(() => {
    if (baseSetting) {
      const settings = baseSetting[settingTemplate].Customization.settings;
      const cssVars = {
        "--primary-verba": settings.primary_color.color,
        "--secondary-verba": settings.secondary_color.color,
        "--warning-verba": settings.warning_color.color,
        "--bg-verba": settings.bg_color.color,
        "--bg-alt-verba": settings.bg_alt_color.color,
        "--text-verba": settings.text_color.color,
        "--text-alt-verba": settings.text_alt_color.color,
        "--button-verba": settings.button_color.color,
        "--button-hover-verba": settings.button_hover_color.color,
        "--bg-console-verba": settings.bg_console.color,
        "--text-console-verba": settings.text_console.color,
      };

      Object.entries(cssVars).forEach(([key, value]) => {
        document.documentElement.style.setProperty(key, value);
      });
    }
  }, [baseSetting, settingTemplate]);

  useEffect(updateCSSVariables, [updateCSSVariables]);

  return (
    <main
      className={`min-h-screen bg-bg-verba text-text-verba ${fontClassName}`}
      data-theme={
        baseSetting
          ? baseSetting[settingTemplate].Customization.settings.theme
          : "light"
      }
    >
      {gtag !== "" && <GoogleAnalytics gaId={gtag} />}

      {!isLoggedIn && isHealthy && (
        <LoginView
          credentials={credentials}
          setIsLoggedIn={setIsLoggedIn}
          setRAGConfig={setRAGConfig}
          setBaseSetting={setBaseSetting}
          setSettingTemplate={setSettingTemplate}
          setCredentials={setCredentials}
        />
      )}

      {isLoggedIn && isHealthy && (
        <div className="flex flex-col gap-2 p-5">
          <div
            className={`transition-all duration-1500 delay-500 ${
              isLoggedIn
                ? "opacity-100 translate-y-0"
                : "opacity-0 translate-y-4"
            }`}
          >
            {baseSetting && isLoggedIn && (
              <div>
                <Navbar
                  production={production}
                  title={
                    baseSetting[settingTemplate].Customization.settings.title
                      .text
                  }
                  subtitle={
                    baseSetting[settingTemplate].Customization.settings.subtitle
                      .text
                  }
                  imageSrc={
                    baseSetting[settingTemplate].Customization.settings.image
                      .src
                  }
                  version="v2.0.0"
                  currentPage={currentPage}
                  setCurrentPage={setCurrentPage}
                />

                <div
                  className={`${
                    currentPage === "CHAT" && !production ? "" : "hidden"
                  }`}
                >
                  <ChatView
                    credentials={credentials}
                    RAGConfig={RAGConfig}
                    setRAGConfig={setRAGConfig}
                    production={production}
                    settingConfig={baseSetting[settingTemplate]}
                    currentPage={currentPage}
                  />
                </div>

                {currentPage === "DOCUMENTS" && !production && (
                  <DocumentView
                    credentials={credentials}
                    production={production}
                    settingConfig={baseSetting[settingTemplate]}
                  />
                )}

                <div
                  className={`${
                    currentPage === "ADD" && !production ? "" : "hidden"
                  }`}
                >
                  <IngestionView
                    RAGConfig={RAGConfig}
                    setRAGConfig={setRAGConfig}
                    settingConfig={baseSetting[settingTemplate]}
                    credentials={credentials}
                  />
                </div>

                {/* {currentPage === "SETTINGS" && !production && (
                  <SettingsComponent
                    importConfig={updateRAGConfig}
                    settingTemplate={settingTemplate}
                    setSettingTemplate={setSettingTemplate}
                    baseSetting={baseSetting}
                    setBaseSetting={setBaseSetting}
                  />
                )} */}

                {/* {currentPage === "STATUS" && !production && (
                  <StatusComponent
                    fetchHost={() => {}}
                    settingConfig={baseSetting[settingTemplate]}
                  />
                )} */}
              </div>
            )}
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
