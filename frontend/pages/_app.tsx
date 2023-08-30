import type { AppProps } from "next/app";
import Navbar from "../components/Navbar";
import { useEffect } from "react";
import Head from 'next/head';

import { PT_Mono } from "next/font/google";

const pt_mono = PT_Mono({ weight: "400", subsets: ["latin"] });

import "../app/globals.css";

const bgUrl = process.env.NODE_ENV === 'production'
  ? 'static/'
  : '/';

function MyApp({ Component, pageProps }: AppProps) {
  useEffect(() => {
    document.body.style.backgroundImage = `url('${bgUrl + 'background.png'}')`;
    document.body.style.backgroundPosition = "center";
    document.body.style.backgroundSize = "cover";
    document.body.style.backgroundRepeat = "no-repeat";
  }, []);

  return (
    <div className={pt_mono.className}>
      <Head>
        <link rel="icon" type="image/png" href={`${bgUrl}favicon.png`} />
      </Head>
      <Navbar />
      <Component {...pageProps} />
    </div>
  );
}

export default MyApp;
