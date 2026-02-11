"use client";

import React from "react";

type Props = {
    emails: any[];
    folder: string;
    activeProject: string | null;
    starredIds: string[];
    snoozedIds: string[];
    doneIds: string[];
    openMail: (id: string, mail: any) => void;
    generateAIPriorityForMail: (mail: any) => void;
    getPriorityScore: (mail: any) => number;
    isSpamEmail: (mail: any) => boolean;
};

export default function EmailListCompact({
    emails,
    folder,
    activeProject,
    starredIds,
    snoozedIds,
    doneIds,
    openMail,
    generateAIPriorityForMail,
    getPriorityScore,
    isSpamEmail,
}: Props) {
    // apply general filters (hide snoozed/done always)
    let list = emails.filter((m) => !doneIds.includes(m.id) && !snoozedIds.includes(m.id));

    if (folder === "starred") {
        list = list.filter((m) => starredIds.includes(m.id));
    } else if (folder === "snoozed") {
        list = emails.filter((m) => snoozedIds.includes(m.id));
    } else if (folder === "done") {
        list = emails.filter((m) => doneIds.includes(m.id));
    } else if (folder === "project" && activeProject) {
        // simple heuristic: project name in subject
        list = list.filter((m) =>
            (m.subject || "").toLowerCase().includes(activeProject.toLowerCase())
        );
    } else {
        // inbox: show all (non-snoozed, non-done)
        list = list;
    }

    return (
        <div style={{ width: "360px", overflowY: "auto", padding: "12px" }}>
            {list.map((mail, i) => {
                const score = getPriorityScore(mail);

                return (
                    <div
                        key={mail.id || i}
                        onClick={() => {
                            openMail(mail.id, mail);
                            generateAIPriorityForMail(mail);
                        }}
                        style={{
                            padding: 10,
                            borderRadius: 10,
                            marginBottom: 10,
                            cursor: "pointer",
                            background: "white",
                            border: "1px solid #EDF2F7",
                            boxShadow: "0 1px 2px rgba(12,12,12,0.03)",
                            display: "flex",
                            gap: 10,
                            alignItems: "flex-start",
                            fontSize: 12,
                        }}
                    >
                        <div style={{
                            width: 40,
                            height: 40,
                            borderRadius: 10,
                            background: "#EEF2FF",
                            display: "flex",
                            alignItems: "center",
                            justifyContent: "center",
                            fontWeight: 700,
                            color: "#1E293B",
                        }}>
                            {(mail.from || "M").slice(0, 2).toUpperCase()}
                        </div>

                        <div style={{ flex: 1, minWidth: 0 }}>
                            <div style={{ display: "flex", justifyContent: "space-between", gap: 8, alignItems: "center" }}>
                                <div style={{ fontWeight: 700, whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>
                                    {mail.subject || "(No subject)"}
                                </div>
                                <div style={{ fontSize: 11, color: "#6B7280" }}>{mail.date?.slice(0, 16)}</div>
                            </div>

                            <div style={{ color: "#6B7280", fontSize: 12, marginTop: 6, whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>
                                {mail.snippet}
                            </div>

                            <div style={{ marginTop: 8, display: "flex", gap: 8, alignItems: "center", flexWrap: "wrap" }}>
                                <div style={{ background: getPriorityColorInline(score), color: "white", padding: "4px 8px", borderRadius: 999, fontSize: 11 }}>
                                    ⚡ {score}
                                </div>

                                {isSpamEmail(mail) && <div style={{ background: "#FCA5A5", padding: "4px 8px", borderRadius: 999, fontSize: 11 }}>🚫 SPAM</div>}
                            </div>
                        </div>
                    </div>
                );
            })}
            {list.length === 0 && <div style={{ color: "#6B7280", fontSize: 13, paddingTop: 6 }}>No mails here</div>}
        </div>
    );
}

/** small helper local (can't import page's getPriorityColor easily) */
function getPriorityColorInline(score: number) {
    if (score >= 80) return "#ff4d4d";
    if (score >= 50) return "#ffc107";
    return "#4caf50";
}
