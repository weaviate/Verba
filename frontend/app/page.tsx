
'use client'

import React, { useState, useEffect } from 'react';
import Navbar from './components/Navigation/navbar'
import SettingsComponent from "./components/Settings/settings_component"
import { Settings, BaseSettings } from "./components/Settings/types"
import { Inter, Plus_Jakarta_Sans, Open_Sans, PT_Mono } from "next/font/google";

// Fonts
const inter = Inter({ subsets: ["latin"] });
const plus_jakarta_sans = Plus_Jakarta_Sans({ subsets: ["latin"] });
const open_sans = Open_Sans({ subsets: ["latin"] });
const pt_mono = PT_Mono({ subsets: ["latin"], weight: "400" });

type FontKey = "Inter" | "Plus_Jakarta_Sans" | "Open_Sans" | "PT_Mono";

const fonts: Record<FontKey, typeof inter> = {
  "Inter": inter,
  "Plus_Jakarta_Sans": plus_jakarta_sans,
  "Open_Sans": open_sans,
  "PT_Mono": pt_mono
}

export default function Home() {

  // Page States
  const [currentPage, setCurrentPage] = useState<"CHAT" | "DOCUMENTS" | "STATUS" | "ADD" | "SETTINGS" | "RAG">("CHAT")

  // Settings
  const [settingTemplate, setSettingTemplate] = useState("Default")
  const [baseSetting, setBaseSetting] = useState<Settings>(BaseSettings)

  const fontKey = baseSetting[settingTemplate].Customization.settings.font.value as FontKey; // Safely cast if you're sure, or use a check
  const fontClassName = fonts[fontKey]?.className || "";

  return (
    <main className={`min-h-screen p-5 bg-bg-verba text-text-verba ${fontClassName}`} data-theme={baseSetting[settingTemplate].Customization.settings.theme}>
      <Navbar title={baseSetting[settingTemplate].Customization.settings.title.text} subtitle={baseSetting[settingTemplate].Customization.settings.subtitle.text} imageSrc={baseSetting[settingTemplate].Customization.settings.image.src} version='v1.0.0' currentPage={currentPage} setCurrentPage={setCurrentPage} />

      {currentPage === "SETTINGS" && (
        <SettingsComponent settingTemplate={settingTemplate} setSettingTemplate={setSettingTemplate} baseSetting={baseSetting} setBaseSetting={setBaseSetting} />
      )}

      <footer className="footer footer-center p-4 mt-8 bg-bg-verba text-text-alt-verba">
        <aside>
          <p>Build with ♥ and Weaviate © 2024</p>
        </aside>
      </footer>

    </main >
  );
}