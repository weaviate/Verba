import type { AppProps } from 'next/app'
import Navbar from '../components/Navbar'
import { useEffect } from 'react'

import { PT_Mono } from 'next/font/google'

const pt_mono = PT_Mono({ weight: "400", subsets: ["latin"] })

import '../app/globals.css'

function MyApp({ Component, pageProps }: AppProps) {
    useEffect(() => {
        document.body.style.backgroundImage = "url('/background.png')";
        document.body.style.backgroundPosition = 'center';
        document.body.style.backgroundSize = 'cover';
        document.body.style.backgroundRepeat = 'no-repeat';
    }, [])

    return (
        <div className={pt_mono.className}>
            <Navbar />
            <Component {...pageProps} />
        </div>
    )
}

export default MyApp