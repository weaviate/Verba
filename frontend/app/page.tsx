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
import GettingStartedComponent from "./components/Login/GettingStarted";
import StatusMessengerComponent from "./components/Navigation/StatusMessenger";

// Types
import {
  Credentials,
  RAGConfig,
  Theme,
  StatusMessage,
  LightTheme,
  Themes,
  DarkTheme,
  DocumentFilter,
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
    default_deployment: "",
  });

  // RAG Config
  const [RAGConfig, setRAGConfig] = useState<null | RAGConfig>(null);

  const [documentFilter, setDocumentFilter] = useState<DocumentFilter[]>([]);

  const [statusMessages, setStatusMessages] = useState<StatusMessage[]>([]);

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
          default_deployment: health_data.default_deployment,
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

  const isValidTheme = (theme: Theme): boolean => {
    const requiredAttributes = [
      "primary_color",
      "secondary_color",
      "warning_color",
      "bg_color",
      "bg_alt_color",
      "text_color",
      "text_alt_color",
      "button_color",
      "button_hover_color",
      "button_text_color",
      "button_text_alt_color",
    ];
    return requiredAttributes.every(
      (attr) =>
        typeof theme[attr as keyof Theme] === "object" &&
        "color" in (theme[attr as keyof Theme] as object)
    );
  };

  const updateCSSVariables = useCallback(() => {
    const themeToUse = selectedTheme;
    const cssVars = {
      "--primary-verba":
        themeToUse.primary_color?.color || WeaviateTheme.primary_color.color,
      "--secondary-verba":
        themeToUse.secondary_color?.color ||
        WeaviateTheme.secondary_color.color,
      "--warning-verba":
        themeToUse.warning_color?.color || WeaviateTheme.warning_color.color,
      "--bg-verba": themeToUse.bg_color?.color || WeaviateTheme.bg_color.color,
      "--bg-alt-verba":
        themeToUse.bg_alt_color?.color || WeaviateTheme.bg_alt_color.color,
      "--text-verba":
        themeToUse.text_color?.color || WeaviateTheme.text_color.color,
      "--text-alt-verba":
        themeToUse.text_alt_color?.color || WeaviateTheme.text_alt_color.color,
      "--button-verba":
        themeToUse.button_color?.color || WeaviateTheme.button_color.color,
      "--button-hover-verba":
        themeToUse.button_hover_color?.color ||
        WeaviateTheme.button_hover_color.color,
      "--text-verba-button":
        themeToUse.button_text_color?.color ||
        WeaviateTheme.button_text_color.color,
      "--text-alt-verba-button":
        themeToUse.button_text_alt_color?.color ||
        WeaviateTheme.button_text_alt_color.color,
    };
    Object.entries(cssVars).forEach(([key, value]) => {
      document.documentElement.style.setProperty(key, value);
    });
  }, [selectedTheme, themes]);

  useEffect(updateCSSVariables, [selectedTheme]);

  const addStatusMessage = (
    message: string,
    type: "INFO" | "WARNING" | "SUCCESS" | "ERROR"
  ) => {
    setStatusMessages((prevMessages) => [
      ...prevMessages,
      { message, type, timestamp: new Date().toISOString() },
    ]);
  };

  return (
    <main
      className={`min-h-screen bg-bg-verba text-text-verba min-w-screen ${fontClassName}`}
      data-theme={selectedTheme.theme}
    >
      {gtag !== "" && <GoogleAnalytics gaId={gtag} />}

      <StatusMessengerComponent
        status_messages={statusMessages}
        set_status_messages={setStatusMessages}
      />

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
          <GettingStartedComponent addStatusMessage={addStatusMessage} />

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
                addStatusMessage={addStatusMessage}
                credentials={credentials}
                RAGConfig={RAGConfig}
                setRAGConfig={setRAGConfig}
                production={production}
                selectedTheme={selectedTheme}
                currentPage={currentPage}
                documentFilter={documentFilter}
                setDocumentFilter={setDocumentFilter}
              />
            </div>

            {currentPage === "DOCUMENTS" && (
              <DocumentView
                addStatusMessage={addStatusMessage}
                credentials={credentials}
                production={production}
                selectedTheme={selectedTheme}
                documentFilter={documentFilter}
                setDocumentFilter={setDocumentFilter}
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
                addStatusMessage={addStatusMessage}
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
                addStatusMessage={addStatusMessage}
                selectedTheme={selectedTheme}
                setSelectedTheme={setSelectedTheme}
                themes={themes}
                setThemes={setThemes}
              />
            </div>
          </div>

          <div
            className={`footer footer-center p-4 mt-8 bg-bg-verba text-text-alt-verba transition-all duration-1500 delay-1000`}
          >
            <aside>
              <p>Build with ♥ and Weaviate © 2024</p>
            </aside>
          </div>
        </div>
      )}

      <img
        referrerPolicy="no-referrer-when-downgrade"
        src="https://static.scarf.sh/a.png?x-pxid=ec666e70-aee5-4e87-bc62-0935afae63ac"
      />
    </main>
  );
}
