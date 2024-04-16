
'use client'

import React, { useState, useEffect } from 'react';
import Navbar from './components/Navigation/navbar'
import SettingsComponent from "./components/Settings/settings_component"
import { SettingsConfiguration, BaseSettings } from "./components/Settings/types"

export default function Home() {

  // Page States
  const [currentPage, setCurrentPage] = useState<"CHAT" | "DOCUMENTS" | "STATUS" | "ADD" | "SETTINGS" | "RAG">("CHAT")

  // Settings
  const [settingsConfig, setSettingsConfig] = useState<SettingsConfiguration>(BaseSettings)

  useEffect(() => {
    document.documentElement.style.setProperty("--primary-verba", settingsConfig.Customization.settings.primary_color.color);
    document.documentElement.style.setProperty("--secondary-verba", settingsConfig.Customization.settings.secondary_color.color);
    document.documentElement.style.setProperty("--warning-verba", settingsConfig.Customization.settings.warning_color.color);
    document.documentElement.style.setProperty("--bg-verba", settingsConfig.Customization.settings.bg_color.color);
    document.documentElement.style.setProperty("--bg-alt-verba", settingsConfig.Customization.settings.bg_alt_color.color);
    document.documentElement.style.setProperty("--text-verba", settingsConfig.Customization.settings.text_color.color);
    document.documentElement.style.setProperty("--text-alt-verba", settingsConfig.Customization.settings.text_alt_color.color);
    document.documentElement.style.setProperty("--button-verba", settingsConfig.Customization.settings.button_color.color);
    document.documentElement.style.setProperty("--button-hover-verba", settingsConfig.Customization.settings.button_hover_color.color);
  }, [settingsConfig]);

  return (
    <main className="min-h-screen p-5 bg-bg-verba text-text-verba" data-theme="light">
      <Navbar title={settingsConfig.Customization.settings.title.text} subtitle={settingsConfig.Customization.settings.subtitle.text} imageSrc={settingsConfig.Customization.settings.image.src} version='v1.0.0' currentPage={currentPage} setCurrentPage={setCurrentPage} />

      {currentPage === "SETTINGS" && (
        <SettingsComponent settingsConfig={settingsConfig} setSettingsConfig={setSettingsConfig} />
      )}

      <footer className="footer footer-center p-4 mt-8 bg-bg-verba text-text-alt-verba">
        <aside>
          <p>Build with ♥ and Weaviate © 2024</p>
        </aside>
      </footer>

    </main >
  );
}