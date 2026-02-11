"use client";

import React from "react";

type Props = {
    activeFolder: string;
    setActiveFolder: (f: string) => void;
    counts: { inbox: number; starred: number; snoozed: number; done: number };
    projects: string[];
    setActiveProject: (p: string | null) => void;
};

export default function NavColumn({
    activeFolder,
    setActiveFolder,
    counts,
    projects,
    setActiveProject,
}: Props) {
    const NavButton = ({
        label,
        id,
        count,
        icon,
    }: {
        label: string;
        id: string;
        count?: number;
        icon?: React.ReactNode;
    }) => (
        <button
            onClick={() => {
                setActiveProject(null);
                setActiveFolder(id);
            }}
            style={{
                width: "100%",
                textAlign: "left",
                padding: "8px 12px",
                borderRadius: 10,
                display: "flex",
                alignItems: "center",
                justifyContent: "space-between",
                gap: 12,
                border: "none",
                cursor: "pointer",
                background: activeFolder === id ? "rgba(37,99,235,0.08)" : "transparent",
                color: activeFolder === id ? "#0f172a" : "#111827",
                fontWeight: 600,
                fontSize: 13,
            }}
        >
            <span style={{ display: "flex", alignItems: "center", gap: 10 }}>
                <span style={{
                    width: 28,
                    height: 28,
                    borderRadius: 8,
                    display: "inline-flex",
                    alignItems: "center",
                    justifyContent: "center",
                    background: activeFolder === id ? "#2563EB" : "#EEF2FF",
                    color: activeFolder === id ? "white" : "#2563EB",
                    fontWeight: 800,
                    fontSize: 12,
                }}>{icon || label[0]}</span>
                <span>{label}</span>
            </span>

            <span style={{
                minWidth: 28,
                textAlign: "center",
                fontSize: 12,
                color: "#111827",
                background: "rgba(0,0,0,0.04)",
                padding: "4px 8px",
                borderRadius: 999
            }}>{typeof count === "number" ? count : ""}</span>
        </button>
    );

    return (
        <div style={{
            width: 220,
            padding: 12,
            borderRight: "1px solid #E6EEF6",
            background: "#FAFCFF",
            display: "flex",
            flexDirection: "column",
            gap: 12,
            fontSize: 13
        }}>
            <div style={{ fontWeight: 800, fontSize: 14, color: "#0f172a", padding: "6px 6px" }}>Mail</div>

            <NavButton id="inbox" label="Inbox" count={counts.inbox} icon="📥" />
            <NavButton id="starred" label="Starred" count={counts.starred} icon="⭐" />
            <NavButton id="snoozed" label="Snoozed" count={counts.snoozed} icon="⏳" />
            <NavButton id="done" label="Done" count={counts.done} icon="✅" />

            <hr style={{ border: "none", borderTop: "1px solid #E6EEF6", margin: "6px 0" }} />

            <div style={{ fontWeight: 800, color: "#0f172a", fontSize: 13, padding: "6px 6px" }}>
                Projects
            </div>

            <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
                {projects && projects.length > 0 ? (
                    projects.map((p) => (
                        <button
                            key={p}
                            onClick={() => {
                                setActiveFolder("project");
                                setActiveProject(p);
                            }}
                            style={{
                                padding: "8px 10px",
                                borderRadius: 8,
                                textAlign: "left",
                                border: "none",
                                cursor: "pointer",
                                background: "transparent",
                                fontSize: 13,
                                color: "#0f172a",
                            }}
                        >
                            {p}
                        </button>
                    ))
                ) : (
                    <div style={{ color: "#6B7280", fontSize: 12 }}>No projects yet</div>
                )}
            </div>
        </div>
    );
}
