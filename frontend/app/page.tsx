
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

  return (
    <main className="min-h-screen p-2 md:p-6 bg-bg-verba" data-theme="light">
      <Navbar title={settingsConfig.Customization.settings.title.text} subtitle={settingsConfig.Customization.settings.subtitle.text} imageSrc={settingsConfig.Customization.settings.image.encoding} version='v1.0.0' currentPage={currentPage} setCurrentPage={setCurrentPage} />

      {currentPage === "SETTINGS" && (
        <SettingsComponent settingsConfig={settingsConfig} setSettingsConfig={setSettingsConfig} />
      )}

    </main >
  );
}