import type { AppProps } from "next/app";
import Navbar from "../components/Navbar";
import { useState, useEffect } from "react";
import Head from 'next/head';
import Script from "next/script";

import { getApiHost } from "@/pages";

import { PT_Mono } from "next/font/google";

const pt_mono = PT_Mono({ weight: "400", subsets: ["latin"] });

import "../app/globals.css";

const bgUrl = process.env.NODE_ENV === 'production'
  ? 'static/'
  : '/';

const apiHost = getApiHost()

function MyApp({ Component, pageProps }: AppProps) {

  const [googleTag, setGoogleTag] = useState<string>("");

  useEffect(() => {
    document.body.style.backgroundImage = `url('${bgUrl + 'background.png'}')`;
    document.body.style.backgroundPosition = "center";
    document.body.style.backgroundSize = "cover";
    document.body.style.backgroundRepeat = "no-repeat";
  }, []);

  useEffect(() => {
    const fetchEnvironment = async () => {
      try {
        const response = await fetch(apiHost + "/api/get_google_tag", {
          method: "GET",
          headers: {
            "Content-Type": "application/json",
          },
        });
        const response_data = await response.json();

        if (response_data.tag) {
          console.log("Google Tag Set!")
        } else {
          console.log("No Google Tag found.")
        }

        // Update the document title and text
        setGoogleTag(response_data.tag);
      } catch (error) {
        console.error("Failed to fetch document:", error);
      }
    }

    fetchEnvironment();
  }, []);

  return (
    <div className={pt_mono.className}>
      {googleTag && (
        <>
          <Script
            strategy="lazyOnload"
            src={`https://www.googletagmanager.com/gtag/js?id=${googleTag}`}
          />
          <Script strategy="lazyOnload">
            {`
            window.dataLayer = window.dataLayer || [];
            function gtag(){dataLayer.push(arguments);}
            gtag('js', new Date());
            gtag('config', '${googleTag}', {
              page_path: window.location.pathname,
            });
          `}
          </Script>
        </>
      )}
      <Head>
        <link rel="icon" type="image/png" href={`${bgUrl}favicon.png`} />
      </Head>
      <Navbar />
      <Component {...pageProps} />
    </div>
  );
}

export default MyApp;
