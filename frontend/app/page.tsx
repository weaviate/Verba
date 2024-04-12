
'use client'

import React, { useState, useEffect } from 'react';
import Navbar from './components/Navigation/navbar'

export default function Home() {

  // Page States
  const [currentPage, setCurrentPage] = useState<"CHAT" | "DOCUMENTS" | "STATUS" | "ADD" | "SETTINGS">("CHAT")

  return (
    <main className="min-h-screen p-2 md:p-6" data-theme="light">
      <Navbar title='Verba' subtitle='The Golden RAGtriever' imageSrc='favicon.png' version='v1.0.0' currentPage={currentPage} setCurrentPage={setCurrentPage} />

    </main >
  );
}