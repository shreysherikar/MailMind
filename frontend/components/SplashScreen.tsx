"use client";

import { useEffect, useState } from "react";

export default function SplashScreen() {
    const [animate, setAnimate] = useState(false);

    useEffect(() => {
        // Trigger animation after component loads
        setTimeout(() => {
            setAnimate(true);
        }, 100);
    }, []);

    return (
        <div
            style={{
                height: "100vh",
                width: "100vw",
                display: "flex",
                justifyContent: "center",
                alignItems: "center",
                background: "white",
            }}
        >
            <img
                src="/logo.png"
                alt="Mail Mind Logo"
                style={{
                    width: animate ? "230px" : "40px", // ✅ zoom small → big
                    opacity: animate ? 1 : 0, // ✅ fade transparent → visible
                    transition: "all 1.5s ease-in-out", // ✅ smooth animation
                }}
            />
        </div>
    );
}
