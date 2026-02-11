"use client";

export default function EmailList(props: any) {
    const {
        emails,
        filteredEmails,
        activeTab,
        setActiveTab,
        selectedMail,
        openMailAndGenerateAI,
        generateAIPriorityForMail,
        getPriorityScore,
        getPriorityColor,
        isSpamEmail,
        isFirstTimeSender,
        nextPageToken,
        loadEmails,
        loading,
    } = props;

    return (
        <div
            style={{
                width: "35%",
                borderRight: "1px solid #E5E7EB",
                overflowY: "auto",
                background: "white",
            }}
        >
            {/* Tabs */}
            <div
                style={{
                    padding: 15,
                    borderBottom: "1px solid #E5E7EB",
                    background: "#F8FAFF",
                    display: "flex",
                    gap: 8,
                    flexWrap: "wrap",
                }}
            >
                {["All Mails", "Do Now", "Waiting", "Needs Decision", "Low Energy"].map(
                    (tab) => (
                        <button
                            key={tab}
                            onClick={() => setActiveTab(tab)}
                            style={{
                                padding: "8px 14px",
                                borderRadius: 10,
                                border: "none",
                                cursor: "pointer",
                                background:
                                    activeTab === tab
                                        ? "linear-gradient(135deg,#6D28D9,#2563EB)"
                                        : "#E5E7EB",
                                color: activeTab === tab ? "white" : "#111827",
                                fontSize: 13,
                                fontWeight: 600,
                            }}
                        >
                            {tab}
                        </button>
                    )
                )}
            </div>

            {/* Email Items */}
            {filteredEmails.map((mail: any, index: number) => {
                const score = getPriorityScore(mail);

                return (
                    <div
                        key={mail.id + "_" + index}
                        onClick={() => {
                            openMailAndGenerateAI(mail.id, mail);
                            generateAIPriorityForMail(mail);
                        }}
                        style={{
                            margin: "10px",
                            padding: "14px 16px",
                            borderRadius: 18,
                            cursor: "pointer",
                            display: "flex",
                            gap: 14,
                            alignItems: "flex-start",
                            background:
                                selectedMail?.id === mail.id
                                    ? "rgba(99,102,241,0.12)"
                                    : "white",
                            boxShadow:
                                selectedMail?.id === mail.id
                                    ? "0 8px 20px rgba(99,102,241,0.25)"
                                    : "0 2px 10px rgba(0,0,0,0.06)",
                            transition: "all 0.25s ease",
                        }}
                    >
                        {/* Avatar */}
                        <div
                            style={{
                                width: 46,
                                height: 46,
                                borderRadius: "50%",
                                background: "linear-gradient(135deg,#6D28D9,#2563EB)",
                                display: "flex",
                                alignItems: "center",
                                justifyContent: "center",
                                fontWeight: 800,
                                fontSize: 16,
                                color: "white",
                                flexShrink: 0,
                            }}
                        >
                            {mail.from?.charAt(0)?.toUpperCase() || "M"}
                        </div>

                        {/* Content */}
                        <div style={{ flex: 1 }}>
                            {/* Sender */}
                            <p
                                style={{
                                    margin: 0,
                                    fontSize: 13,
                                    fontWeight: 700,
                                    color: "#111827",
                                }}
                            >
                                {mail.from?.split("<")[0] || "Unknown Sender"}
                            </p>

                            {/* Subject */}
                            <h4
                                style={{
                                    margin: "4px 0",
                                    fontSize: 15,
                                    fontWeight: 800,
                                    color: "#1F2937",
                                }}
                            >
                                {mail.subject || "No Subject"}
                            </h4>

                            {/* Snippet */}
                            <p
                                style={{
                                    margin: 0,
                                    fontSize: 13,
                                    color: "#6B7280",
                                    whiteSpace: "nowrap",
                                    overflow: "hidden",
                                    textOverflow: "ellipsis",
                                    maxWidth: "250px",
                                }}
                            >
                                {mail.snippet}
                            </p>

                            {/* Tags */}
                            <div style={{ display: "flex", gap: 8, marginTop: 10 }}>
                                <span
                                    style={{
                                        fontSize: 12,
                                        fontWeight: 700,
                                        padding: "4px 10px",
                                        borderRadius: 999,
                                        background: getPriorityColor(score),
                                        color: "white",
                                    }}
                                >
                                    ⚡ {score}
                                </span>

                                {isSpamEmail(mail) && (
                                    <span
                                        style={{
                                            fontSize: 12,
                                            fontWeight: 700,
                                            padding: "4px 10px",
                                            borderRadius: 999,
                                            background: "#DC2626",
                                            color: "white",
                                        }}
                                    >
                                        🚫 Spam
                                    </span>
                                )}

                                {isFirstTimeSender(mail, emails) && (
                                    <span
                                        style={{
                                            fontSize: 12,
                                            fontWeight: 700,
                                            padding: "4px 10px",
                                            borderRadius: 999,
                                            background: "#2563EB",
                                            color: "white",
                                        }}
                                    >
                                        🆕 New
                                    </span>
                                )}
                            </div>

                            {/* Meter */}
                            <div
                                style={{
                                    marginTop: 10,
                                    height: 6,
                                    width: "100%",
                                    borderRadius: 999,
                                    background: "#E5E7EB",
                                }}
                            >
                                <div
                                    style={{
                                        height: "100%",
                                        width: `${score}%`,
                                        borderRadius: 999,
                                        background: getPriorityColor(score),
                                    }}
                                />
                            </div>
                        </div>
                    </div>
                );
            })}

            {/* Load More */}
            {nextPageToken && (
                <button
                    onClick={loadEmails}
                    disabled={loading}
                    style={{
                        width: "100%",
                        padding: 14,
                        background: loading ? "#E5E7EB" : "#2563EB",
                        color: "white",
                        border: "none",
                        fontWeight: 600,
                        cursor: "pointer",
                    }}
                >
                    {loading ? "Loading..." : "Load More"}
                </button>
            )}
        </div>
    );
}
