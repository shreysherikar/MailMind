"use client";

export default function FeaturesPage() {
    const features = [
        {
            title: "AI Summary",
            desc: "Generates quick and clear summaries of long emails using AI.",
        },
        {
            title: "Why Important?",
            desc: "Explains why a mail matters so you never miss critical messages.",
        },
        {
            title: "Priority Scoring",
            desc: "AI assigns a score from 0–100 to rank urgent emails first.",
        },
        {
            title: "Task Extraction",
            desc: "Detects action items like meetings, payments, deadlines automatically.",
        },
        {
            title: "Burnout Dashboard",
            desc: "Detects stress signals and workload trends from inbox activity.",
        },
        {
            title: "AI Reply Generator",
            desc: "Creates professional replies instantly with editable text support.",
        },
        {
            title: "Snooze Emails",
            desc: "Temporarily hide emails and revisit them later without losing them.",
        },
        {
            title: "Starred Folder",
            desc: "Save important emails permanently for quick access anytime.",
        },
    ];

    return (
        <div
            style={{
                minHeight: "100vh",
                background:
                    "linear-gradient(135deg, #4F46E5 0%, #7C3AED 50%, #A78BFA 100%)",
                padding: "60px",
                color: "white",
            }}
        >
            {/* ✅ Page Heading */}
            <h1
                style={{
                    fontSize: "52px",
                    fontWeight: 800,
                    marginBottom: "20px",
                }}
            >
                🚀 MailMind Features
            </h1>

            <p style={{ fontSize: 18, opacity: 0.9, marginBottom: 50 }}>
                Explore what makes MailMind a next-gen AI email assistant.
            </p>

            {/* ✅ Feature Cards Grid */}
            <div
                style={{
                    display: "grid",
                    gridTemplateColumns: "repeat(4, 1fr)",
                    gap: "25px",
                }}
            >
                {features.map((item, index) => (
                    <div key={index} className="flip-card">
                        <div className="flip-inner">
                            {/* Front Side */}
                            <div className="flip-front">
                                <h2>{item.title}</h2>
                            </div>

                            {/* Back Side */}
                            <div className="flip-back">
                                <p>{item.desc}</p>
                            </div>
                        </div>
                    </div>
                ))}
            </div>

            {/* ✅ Bottom Button */}
            <button
                style={{
                    marginTop: 70,
                    width: "100%",
                    padding: "18px",
                    fontSize: 18,
                    fontWeight: 700,
                    borderRadius: 18,
                    border: "none",
                    background: "rgba(255,255,255,0.18)",
                    color: "white",
                    cursor: "pointer",
                    backdropFilter: "blur(20px)",
                }}
            >
                ✨ New Features Coming Soon…
            </button>

            {/* ✅ Flip Animation CSS */}
            <style>{`
        .flip-card {
          background: transparent;
          width: 100%;
          height: 180px;
          perspective: 1000px;
        }

        .flip-inner {
          width: 100%;
          height: 100%;
          position: relative;
          transform-style: preserve-3d;
          transition: transform 0.7s;
        }

        .flip-card:hover .flip-inner {
          transform: rotateY(180deg);
        }

        .flip-front,
        .flip-back {
          position: absolute;
          width: 100%;
          height: 100%;
          border-radius: 18px;
          display: flex;
          align-items: center;
          justify-content: center;
          backface-visibility: hidden;
          padding: 20px;
          font-weight: 700;
        }

        .flip-front {
          background: rgba(255,255,255,0.15);
          backdrop-filter: blur(18px);
          border: 1px solid rgba(255,255,255,0.25);
          font-size: 20px;
        }

        .flip-back {
          background: rgba(0,0,0,0.35);
          transform: rotateY(180deg);
          font-size: 15px;
          font-weight: 500;
          line-height: 1.5;
        }
      `}</style>
        </div>
    );
}
