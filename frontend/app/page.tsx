"use client";

import React, { useState, useEffect } from "react";
import Navbar from "./components/Navigation/NavbarComponent";
import SettingsComponent from "./components/Settings/SettingsComponent";
import ChatComponent from "./components/Chat/ChatComponent";
import DocumentViewerComponent from "./components/Document/DocumentViewerComponent";
import StatusComponent from "./components/Status/StatusComponent";
import { Settings, BaseSettings } from "./components/Settings/types";
import RAGComponent from "./components/RAG/RAGComponent";
import { HealthPayload } from "./components/Status/types";
import { RAGConfig, RAGResponse } from "./components/RAG/types";
import { detectHost } from "./api";
import { GoogleAnalytics } from "@next/third-parties/google";
import { fonts, FontKey } from "./info";
import PulseLoader from "react-spinners/PulseLoader";

export default function Home() {
  // Page States
  const [currentPage, setCurrentPage] = useState<
    "CHAT" | "DOCUMENTS" | "STATUS" | "ADD" | "SETTINGS" | "RAG"
  >("CHAT");

  const [production, setProduction] = useState(false);
  const [gtag, setGtag] = useState("");

  // Settings
  const [settingTemplate, setSettingTemplate] = useState("Default");
  const [baseSetting, setBaseSetting] = useState<Settings | null>(null);

  const fontKey = baseSetting
    ? (baseSetting[settingTemplate].Customization.settings.font
        .value as FontKey)
    : null; // Safely cast if you're sure, or use a check
  const fontClassName = fontKey ? fonts[fontKey]?.className || "" : "";

  // RAG Config
  const [RAGConfig, setRAGConfig] = useState<RAGConfig | null>(null);

  const [APIHost, setAPIHost] = useState<string | null>(null);

  const fetchHost = async () => {
    try {
      const host = await detectHost();
      setAPIHost(host);
      if (host === "" || host === "http://localhost:8000") {
        try {
          const health_response = await fetch(host + "/api/health", {
            method: "GET",
          });

          const health_data: HealthPayload = await health_response.json();

          if (health_data) {
            setProduction(health_data.production);
            setGtag(health_data.gtag);
          } else {
            console.warn("Could not retrieve health data");
          }

          const response = await fetch(host + "/api/config", {
            method: "GET",
          });
          const data: RAGResponse = await response.json();

          if (data) {
            if (data.error) {
              console.error(data.error);
            }

            if (data.data.RAG) {
              setRAGConfig(data.data.RAG);
            }
            if (data.data.SETTING.themes) {
              setBaseSetting(data.data.SETTING.themes);
              setSettingTemplate(data.data.SETTING.selectedTheme);
            } else {
              setBaseSetting(BaseSettings);
              setSettingTemplate("Default");
            }
          } else {
            console.warn("Configuration could not be retrieved");
          }
        } catch (error) {
          console.error("Failed to fetch configuration:", error);
          setRAGConfig(null);
        }
      }
    } catch (error) {
      console.error("Error detecting host:", error);
      setAPIHost(null); // Optionally handle the error by setting the state to an empty string or a specific error message
    }
  };

  useEffect(() => {
    fetchHost();
  }, []);

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

  useEffect(() => {
    importConfig();
  }, [baseSetting, settingTemplate]);

  useEffect(() => {
    if (baseSetting) {
      document.documentElement.style.setProperty(
        "--primary-verba",
        baseSetting[settingTemplate].Customization.settings.primary_color.color
      );
      document.documentElement.style.setProperty(
        "--secondary-verba",
        baseSetting[settingTemplate].Customization.settings.secondary_color
          .color
      );
      document.documentElement.style.setProperty(
        "--warning-verba",
        baseSetting[settingTemplate].Customization.settings.warning_color.color
      );
      document.documentElement.style.setProperty(
        "--bg-verba",
        baseSetting[settingTemplate].Customization.settings.bg_color.color
      );
      document.documentElement.style.setProperty(
        "--bg-alt-verba",
        baseSetting[settingTemplate].Customization.settings.bg_alt_color.color
      );
      document.documentElement.style.setProperty(
        "--text-verba",
        baseSetting[settingTemplate].Customization.settings.text_color.color
      );
      document.documentElement.style.setProperty(
        "--text-alt-verba",
        baseSetting[settingTemplate].Customization.settings.text_alt_color.color
      );
      document.documentElement.style.setProperty(
        "--button-verba",
        baseSetting[settingTemplate].Customization.settings.button_color.color
      );
      document.documentElement.style.setProperty(
        "--button-hover-verba",
        baseSetting[settingTemplate].Customization.settings.button_hover_color
          .color
      );
      document.documentElement.style.setProperty(
        "--bg-console-verba",
        baseSetting[settingTemplate].Customization.settings.bg_console.color
      );
      document.documentElement.style.setProperty(
        "--text-console-verba",
        baseSetting[settingTemplate].Customization.settings.text_console.color
      );
    }
  }, [baseSetting, settingTemplate]);

  return (
    <main
      className={`min-h-screen p-5 bg-bg-verba text-text-verba ${fontClassName}`}
      data-theme={
        baseSetting
          ? baseSetting[settingTemplate].Customization.settings.theme
          : "light"
      }
    >
      {gtag !== "" && <GoogleAnalytics gaId={gtag} />}

      {baseSetting ? (
        <div>
          <Navbar
            APIHost={APIHost}
            production={production}
            title={
              baseSetting[settingTemplate].Customization.settings.title.text
            }
            subtitle={
              baseSetting[settingTemplate].Customization.settings.subtitle.text
            }
            imageSrc={
              baseSetting[settingTemplate].Customization.settings.image.src
            }
            version="v1.0.1"
            currentPage={currentPage}
            setCurrentPage={setCurrentPage}
          />

          {currentPage === "CHAT" && (
            <ChatComponent
              production={production}
              settingConfig={baseSetting[settingTemplate]}
              APIHost={APIHost}
              RAGConfig={RAGConfig}
              setCurrentPage={setCurrentPage}
            />
          )}

          {currentPage === "DOCUMENTS" && (
            <DocumentViewerComponent
              RAGConfig={RAGConfig}
              production={production}
              setCurrentPage={setCurrentPage}
              settingConfig={baseSetting[settingTemplate]}
              APIHost={APIHost}
            />
          )}

          {currentPage === "STATUS" && !production && (
            <StatusComponent
              fetchHost={fetchHost}
              settingConfig={baseSetting[settingTemplate]}
              APIHost={APIHost}
            />
          )}

          {currentPage === "ADD" && !production && (
            <RAGComponent
              baseSetting={baseSetting}
              settingTemplate={settingTemplate}
              buttonTitle="Import"
              settingConfig={baseSetting[settingTemplate]}
              APIHost={APIHost}
              RAGConfig={RAGConfig}
              setRAGConfig={setRAGConfig}
              setCurrentPage={setCurrentPage}
              showComponents={["Reader", "Chunker", "Embedder"]}
            />
          )}

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
              settingTemplate={settingTemplate}
              setSettingTemplate={setSettingTemplate}
              baseSetting={baseSetting}
              setBaseSetting={setBaseSetting}
            />
          )}

          <footer className="footer footer-center p-4 mt-8 bg-bg-verba text-text-alt-verba">
            <aside>
              <p>Build with ♥ and Weaviate © 2024</p>
            </aside>
          </footer>
        </div>
      ) : (
        <div className="flex items-center justify-center h-screen gap-2">
          <PulseLoader loading={true} size={12} speedMultiplier={0.75} />
          <p>Loading Verba</p>
        </div>
      )}
    </main>
  );
}
