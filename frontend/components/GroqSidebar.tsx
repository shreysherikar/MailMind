"use client";

import React, { useState } from "react";

interface GroqSidebarProps {
    selectedMail: {
        subject: string;
        snippet: string;
        body?: string;
    } | null;
}

export default function GroqSidebar({ selectedMail }: GroqSidebarProps) {
    const [question, setQuestion] = useState("");
    const [reply, setReply] = useState("");
    const [loading, setLoading] = useState(false);

    async function askGroq() {
        if (!selectedMail) return;

        setLoading(true);
        setReply("");

        const res = await fetch("/api/groq", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                emailText:
                    selectedMail.subject +
                    "\n\n" +
                    selectedMail.snippet +
                    "\n\n" +
                    (selectedMail.body || ""),
                question: question || "Summarize this email clearly",
            }),
        });

        const data = await res.json();

        setReply(data.reply || "No response from Groq");
        setLoading(false);
    }

    return (
        <div
            style={{
                width: "340px",
                borderLeft: "1px solid #E5E7EB",
                background: "white",
                padding: "18px",
                display: "flex",
                flexDirection: "column",
                height: "100%",
            }}
        >
            <h2 style={{ fontWeight: 800, fontSize: 18, marginBottom: 14 }}>
                Groq Assistant
            </h2>

            <div style={{ fontSize: 13, color: "#555", marginBottom: 18 }}>
                <p style={{ marginBottom: 8 }}>Try asking:</p>

                <button
                    onClick={() => setQuestion("Summarize this email")}
                    style={suggestBtn}
                >
                    Summarize
                </button>

                <button
                    onClick={() => setQuestion("What action should I take?")}
                    style={suggestBtn}
                >
                    Action Needed
                </button>

                <button
                    onClick={() => setQuestion("Write a reply for this email")}
                    style={suggestBtn}
                >
                    Draft Reply
                </button>
            </div>

            <textarea
                value={question}
                onChange={(e) => setQuestion(e.target.value)}
                placeholder="Ask Groq about this email..."
                rows={3}
                style={{
                    width: "100%",
                    padding: 12,
                    borderRadius: 12,
                    border: "1px solid #ddd",
                    resize: "none",
                    fontSize: 14,
                }}
            />

            <button
                onClick={askGroq}
                style={{
                    marginTop: 12,
                    padding: 12,
                    borderRadius: 12,
                    border: "none",
                    background: "linear-gradient(135deg,#2563EB,#0EA5E9)",
                    color: "white",
                    fontWeight: 700,
                    cursor: "pointer",
                }}
            >
                {loading ? "Thinking..." : "Ask Groq"}
            </button>

            <div
                style={{
                    marginTop: 18,
                    flex: 1,
                    background: "#F9FAFB",
                    padding: 14,
                    borderRadius: 14,
                    border: "1px solid #E5E7EB",
                    fontSize: 14,
                    whiteSpace: "pre-wrap",
                    overflowY: "auto",
                }}
            >
                {reply || "Groq will answer here..."}
            </div>
        </div>
    );
}

const suggestBtn = {
    display: "block",
    width: "100%",
    textAlign: "left" as const,
    padding: "8px 10px",
    marginBottom: 6,
    borderRadius: 10,
    border: "1px solid #E5E7EB",
    background: "#F3F4F6",
    cursor: "pointer",
    fontSize: 13,
    fontWeight: 600,
};
