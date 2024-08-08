"use client";

import React, { useState, useEffect, useCallback } from "react";
import Navbar from "./components/Navigation/NavbarComponent";
import SettingsComponent from "./components/Settings/SettingsComponent";
import DocumentView from "./components/Document/DocumentView";
import StatusComponent from "./components/Status/StatusComponent";
import { Settings, BaseSettings } from "./components/Settings/types";
import RAGComponent from "./components/RAG/RAGComponent";
import { RAGConfig } from "./components/RAG/types";
import { detectHost, fetchConfig, fetchHealth } from "./api";
import IngestionView from "./components/Ingestion/IngestionView";
import { GoogleAnalytics } from "@next/third-parties/google";
import { fonts, FontKey } from "./info";
import PulseLoader from "react-spinners/PulseLoader";

import LoginView from "./components/Login/LoginView";

import ChatView from "./components/Chat/ChatView";

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

  // RAG Config
  const [RAGConfig, setRAGConfig] = useState<RAGConfig | null>(null);
  const [reconnect, setReconnect] = useState(false);

  const [APIHost, setAPIHost] = useState<string | null>(null);

  const [isLoaded, setIsLoaded] = useState(false);
  const [isHealthy, setIsHealthy] = useState(false);
  const [isLoggedIn, setIsLoggedIn] = useState(false);

  const [deployments, setDeployments] = useState<{
    WEAVIATE_URL_VERBA: string;
    WEAVIATE_API_KEY_VERBA: boolean;
  }>({ WEAVIATE_URL_VERBA: "", WEAVIATE_API_KEY_VERBA: false });

  const initialFetch = useCallback(async () => {
    try {
      const host = await detectHost();
      setAPIHost(host);

      const [health_data] = await Promise.all([fetchHealth()]);

      if (health_data) {
        setProduction(health_data.production);
        setGtag(health_data.gtag);
        setIsHealthy(true);
        setDeployments(health_data.deployments);
      } else {
        console.warn("Could not retrieve health data");
        setIsHealthy(false);
      }
    } catch (error) {
      console.error("Error during initial fetch:", error);
      setAPIHost(null);
    }
  }, []);

  useEffect(() => {
    initialFetch();
  }, [initialFetch, reconnect]);

  const importConfig = async () => {
    if (!APIHost || !baseSetting) {
      return;
    }

    try {
      const payload = {
        config: {
          RAG: RAGConfig,
          SETTING: { selectedTheme: settingTemplate, themes: baseSetting },
        },
      };

      const response = await fetch(APIHost + "/api/set_config", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(payload),
      });
    } catch (error) {
      console.error("Failed to update config:", error);
    }
  };

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
          deployments={deployments}
          setIsLoggedIn={setIsLoggedIn}
          setRAGConfig={setRAGConfig}
          setBaseSetting={setBaseSetting}
          setSettingTemplate={setSettingTemplate}
          setIsLoaded={setIsLoaded}
        />
      )}

      {isLoggedIn && isHealthy && isLoaded && (
        <div className="flex flex-col gap-2 p-5">
          <div
            className={`transition-all duration-1500 delay-500 ${
              isLoaded ? "opacity-100 translate-y-0" : "opacity-0 translate-y-4"
            }`}
          >
            {baseSetting && isLoaded && (
              <div>
                <Navbar
                  APIHost={APIHost}
                  production={production}
                  handleViewChange={setCurrentPage}
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
                    RAGConfig={RAGConfig}
                    setRAGConfig={setRAGConfig}
                    production={production}
                    setCurrentPage={setCurrentPage}
                    settingConfig={baseSetting[settingTemplate]}
                    APIHost={APIHost}
                    currentPage={currentPage}
                  />
                </div>

                {currentPage === "DOCUMENTS" && !production && (
                  <DocumentView
                    RAGConfig={RAGConfig}
                    production={production}
                    setCurrentPage={setCurrentPage}
                    settingConfig={baseSetting[settingTemplate]}
                    APIHost={APIHost}
                  />
                )}

                {currentPage === "STATUS" && !production && (
                  <StatusComponent
                    fetchHost={() => {}}
                    settingConfig={baseSetting[settingTemplate]}
                    APIHost={APIHost}
                  />
                )}

                <div
                  className={`${
                    currentPage === "ADD" && !production ? "" : "hidden"
                  }`}
                >
                  <IngestionView
                    settingConfig={baseSetting[settingTemplate]}
                    RAGConfig={RAGConfig}
                    setRAGConfig={setRAGConfig}
                    APIHost={APIHost}
                    setReconnectMain={setReconnect}
                  />
                </div>

                {currentPage === "RAG" && !production && (
                  <RAGComponent
                    baseSetting={baseSetting}
                    settingTemplate={settingTemplate}
                    buttonTitle="Save"
                    settingConfig={baseSetting[settingTemplate]}
                    APIHost={APIHost}
                    RAGConfig={RAGConfig}
                    setRAGConfig={setRAGConfig}
                    setCurrentPage={setCurrentPage}
                    showComponents={["Embedder", "Retriever", "Generator"]}
                  />
                )}

                {currentPage === "SETTINGS" && !production && (
                  <SettingsComponent
                    importConfig={importConfig}
                    settingTemplate={settingTemplate}
                    setSettingTemplate={setSettingTemplate}
                    baseSetting={baseSetting}
                    setBaseSetting={setBaseSetting}
                  />
                )}
              </div>
            )}
          </div>

          <footer
            className={`footer footer-center p-4 mt-8 bg-bg-verba text-text-alt-verba transition-all duration-1500 delay-1000 ${
              isLoaded ? "opacity-100 translate-y-0" : "opacity-0 translate-y-4"
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
