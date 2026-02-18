"use client";

import { useEffect, useState, Fragment } from "react";
import { signOut, useSession, signIn } from "next-auth/react";
import SplashScreen from "@/components/SplashScreen";
import Link from "next/link";

interface Attachment {
  filename: string;
  mimeType: string;
  attachmentId: string;
}

interface Email {
  id: string;
  threadId?: string;
  messageId?: string;
  subject: string;
  from: string;
  date: string;
  snippet: string;
  body?: string;
  attachments?: Attachment[];
  label?: string[];
}

interface Task {
  text: string;
  done: boolean;
}




const LOGIN_SLIDES = [
  "/login/slide1.png",
  "/login/slide2.png",
  "/login/slide3.png",
  "/login/slide4.png",
  "/login/slide5.png",
];

export default function Home() {
  const { data: session } = useSession();
  useEffect(() => {
    console.log("SESSION:", session);
  }, [session]);

  const [hoverFile, setHoverFile] = useState<Attachment | null>(null);
  const [showSplash, setShowSplash] = useState(true);
  const [showProfile, setShowProfile] = useState(false);
  // 🕒 Current Date & Time
  const [currentTime, setCurrentTime] = useState(new Date());
  const [mounted, setMounted] = useState(false);
  const [groqQuestion, setGroqQuestion] = useState("");
  const [groqReply, setGroqReply] = useState("");
  const [loadingGroq, setLoadingGroq] = useState(false);



  const [hoveredBtn, setHoveredBtn] = useState<string | null>(null);

  // 🔔 Notification Count
  const [newMailCount, setNewMailCount] = useState(0);
  // 🔔 Notification Dropdown
  const [showNotifications, setShowNotifications] = useState(false);

  // 🔔 Store New Emails List
  const [newMails, setNewMails] = useState<Email[]>([]);
  // ✅ Toolbar Feature States
  const [showCompose, setShowCompose] = useState(false);
  const [showGroq, setShowGroq] = useState(false);





  const [aiReply, setAiReply] = useState("");
  const [loadingReply, setLoadingReply] = useState(false);
  const [editableReply, setEditableReply] = useState("");
  const [copied, setCopied] = useState(false);
  const [sending, setSending] = useState(false);
  const [aiPriorityMap, setAiPriorityMap] = useState<Record<string, { priority: string; reason: string }>>({});
  const [starredIds, setStarredIds] = useState<string[]>([]);
  const [snoozedIds, setSnoozedIds] = useState<string[]>([]);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [doneIds, setDoneIds] = useState<string[]>([]);

  // Load saved folders from localStorage on startup
  useEffect(() => {
    setStarredIds(JSON.parse(localStorage.getItem("starredIds") || "[]"));
    setSnoozedIds(JSON.parse(localStorage.getItem("snoozedIds") || "[]"));
    setDoneIds(JSON.parse(localStorage.getItem("doneIds") || "[]"));
  }, []);

  const [activeFolder, setActiveFolder] =
    useState("inbox"); // inbox | starred | snoozed | done | drafts | priority | deadline





  // AI States
  const [aiSummary, setAiSummary] = useState("");
  const [aiReason, setAiReason] = useState("");
  const [loadingAI, setLoadingAI] = useState(false);

  const [emails, setEmails] = useState<Email[]>([]);
  const [nextPageToken, setNextPageToken] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const [selectedMail, setSelectedMail] = useState<Email | null>(null);


  const [summary, setSummary] = useState<string>("");
  const [summarizing, setSummarizing] = useState(false);

  const [tasks, setTasks] = useState<Task[]>([]);
  // ✅ FIX 1: Default tab to "All Mails"
  const [activeTab, setActiveTab] = useState("All Mails");

  // 🔍 Search Query
  const [searchQuery, setSearchQuery] = useState("");

  // ✅ Deadline + Urgency Inputs
  const [deadline, setDeadline] = useState<string | null>("");
  const [urgency, setUrgency] = useState("Normal");



  const [currentSlide, setCurrentSlide] = useState(0);
  // ⭐ Toggle Star
  function toggleStar() {
    if (!selectedMail) return;

    setStarredIds((prev) => {
      const updated = prev.includes(selectedMail.id)
        ? prev.filter((id) => id !== selectedMail.id)
        : [...prev, selectedMail.id];

      localStorage.setItem("starredIds", JSON.stringify(updated));
      return updated;
    });
  }



  // ⏳ Snooze Email (hide from inbox)
  function snoozeMail() {
    if (!selectedMail) return;

    setSnoozedIds((prev) => {
      const updated = [...prev, selectedMail.id];
      localStorage.setItem("snoozedIds", JSON.stringify(updated));
      return updated;
    });

    setSelectedMail(null);
  }
  async function askGroq() {
    if (!selectedMail) {
      alert("Select an email first");
      return;
    }

    setLoadingGroq(true);
    setGroqReply("");

    const emailText =
      selectedMail.subject +
      "\n\n" +
      selectedMail.snippet +
      "\n\n" +
      (selectedMail.body || "");

    const res = await fetch("/api/groq", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        emailText,
        question: groqQuestion || "Summarize this email clearly",
      }),
    });

    const data = await res.json();

    if (data.reply) {
      setGroqReply(data.reply);
    } else {
      setGroqReply("Groq failed: " + data.error);
    }

    setLoadingGroq(false);
  }


  // ✅ Mark Done (remove from inbox)
  function markDone() {
    if (!selectedMail) return;

    setDoneIds((prev) => {
      const updated = [...prev, selectedMail.id];
      localStorage.setItem("doneIds", JSON.stringify(updated));
      return updated;
    });

    setSelectedMail(null);
  }
  // =======================================
  function deleteSelectedMail() {
    if (!selectedMail) {
      alert("❌ Please select an email first");
      return;
    }

    alert("🗑 Delete feature will be connected to Gmail API next");

    // Later we will call Gmail API delete here
  }





  // ✅ Fade slideshow runs only when NOT logged in
  useEffect(() => {
    if (session) return;

    const interval = setInterval(() => {
      setCurrentSlide((prev) => {
        let next = Math.floor(Math.random() * LOGIN_SLIDES.length);

        while (next === prev) {
          next = Math.floor(Math.random() * LOGIN_SLIDES.length);
        }

        return next;
      });
    }, 3500);

    return () => clearInterval(interval);
  }, [session]);


  const loadEmails = async () => {
    setLoading(true);

    const res = await fetch(
      `/api/gmail${nextPageToken ? `?pageToken=${nextPageToken}` : ""}`
    );

    const data = await res.json();

    setEmails((prev) => {
      const combined = [...prev, ...(data.emails || [])];

      // ✅ Remove duplicate emails using id
      const unique = Array.from(
        new Map(combined.map((mail) => [mail.id, mail])).values()
      );

      return unique;
    });

    setNextPageToken(data.nextPageToken || null);

    setLoading(false);
  };

  // ✅ FIXED: Combined function that fetches email AND generates AI
  const openMailAndGenerateAI = async (id: string, mailPreview: Email) => {
    // Reset AI states
    setAiSummary("");
    setAiReason("");
    setAiReply("");
    setLoadingAI(false);
    setDeadline(null);
    setUrgency("");


    // Fetch full email content
    const res = await fetch(`/api/gmail/message?id=${id}`);
    const fullEmailData = await res.json();

    // Show mail content
    setSelectedMail(fullEmailData);
    // ✅ Deadline Detection
    const combinedText =
      fullEmailData.subject + " " +
      fullEmailData.snippet + " " +
      fullEmailData.body;

    const detected = extractDeadline(combinedText);

    setDeadline(detected);
    setUrgency(getUrgencyLevel(detected));

  };

  async function generateReply() {
    console.log("✅ generateReply() running...");

    if (!selectedMail) {
      console.log("❌ No email selected");
      alert("Please select an email first");
      return;
    }

    console.log("📧 Email data:", {
      subject: selectedMail.subject,
      snippet: selectedMail.snippet?.substring(0, 100),
    });

    setLoadingReply(true);
    setAiReply("");

    try {
      console.log("🚀 Sending request to /api/ai/reply...");

      const res = await fetch("/api/ai/reply", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          subject: selectedMail.subject,
          snippet: selectedMail.snippet || selectedMail.body || "",
        }),
      });

      console.log("📥 Response status:", res.status);

      const data = await res.json();
      console.log("📦 Response data:", data);

      if (data.error) {
        console.error("❌ API Error:", data.error);
        alert("Error: " + data.error);
        setLoadingReply(false);
        return;
      }

      setAiReply(data.reply);
      setEditableReply(data.reply); // ✅ editable copy
      console.log("✅ Reply generated successfully!");
    } catch (error) {
      console.error("❌ Fetch error:", error);
      alert("Failed to generate reply. Check console for details.");
    }

    setLoadingReply(false);
  }

  async function generateSummary(mail: Email) {
    setLoadingAI(true);
    const emailContent = cleanEmailBody(mail.body || mail.snippet || "");

    if (!emailContent) {
      setAiSummary("⚠️ No email content available.");
      setLoadingAI(false);
      return;
    }

    const res = await fetch("/api/ai/summarize", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        subject: mail.subject,
        snippet: emailContent,
        from: mail.from,
        date: mail.date,
      }),
    });

    const data = await res.json();
    setAiSummary(data.summary || "No summary generated.");

    setLoadingAI(false);
  }

  // ✅ NEW: AI Priority function for individual emails
  async function generateAIPriorityForMail(mail: Email) {

    // ✅ Already generated → skip
    if (aiPriorityMap[mail.id]) return;

    const res = await fetch("/api/ai/priority", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        subject: mail.subject,
        snippet: mail.snippet,
      }),
    });

    const data = await res.json();

    if (data.result?.score) {
      setAiPriorityMap((prev) => ({
        ...prev,
        [mail.id]: data.result,
      }));
    }
  }


  async function generateExplanation(mail: Email) {
    setLoadingAI(true);
    const res = await fetch("/api/ai/explain", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        subject: mail.subject || "",
        snippet: mail.snippet || mail.body || "",
        from: mail.from,
        date: mail.date,
      }),
    });
    const data = await res.json();
    setAiReason(data.explanation || "No explanation generated.");
    setLoadingAI(false);
  }

  const summarizeEmail = async () => {
    if (!selectedMail?.body && !selectedMail?.snippet) return;

    setSummarizing(true);
    setSummary("");

    const res = await fetch("/api/ai/summarize", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        text: selectedMail.body || selectedMail.snippet,
      }),
    });

    const data = await res.json();

    const formatted = data.summary
      .replace(/https?:\/\/\S+/g, "")
      .replace(/🔗\s*\[Link Removed\]/g, "")
      .replace(/📌\s*PURPOSE:/g, "\n📌 PURPOSE:")
      .replace(/📅\s*DATE:/g, "\n📅 DATE:")
      .replace(/🔗\s*LINK:/g, "\n🔗 LINK: IS ATTACH BELOW🔻")
      .replace(/📋\s*SUMMARY:/g, "\n📋 SUMMARY:")
      .replace(/\[see link below ↓\]/g, "")
      .replace(/Click the below/g, "See link below")
      .replace(/CLICK HERE FOR LINK:/g, "")
      .trim();

    setSummary(formatted);
    setSummarizing(false);
  };

  function extractTasks(text: string) {
    const lower = text.toLowerCase();
    const tasks: string[] = [];

    if (
      lower.includes("payment due") ||
      lower.includes("pay now") ||
      lower.includes("invoice") ||
      lower.includes("bill")
    ) {
      tasks.push("💳 Make the payment");
    }

    if (
      lower.includes("meeting") ||
      lower.includes("zoom") ||
      lower.includes("google meet") ||
      lower.includes("schedule")
    ) {
      tasks.push("📅 Attend the meeting");
    }

    if (
      lower.includes("job") ||
      lower.includes("internship") ||
      lower.includes("interview") ||
      lower.includes("offer letter")
    ) {
      tasks.push("📝 Apply / Respond to recruiter");
    }

    if (lower.includes("deadline") || lower.includes("urgent")) {
      tasks.push("⏰ Take action immediately");
    }

    if (tasks.length === 0) tasks.push("📌 No urgent action required");

    return tasks;
  }
  function extractDeadline(text: string) {
    if (!text) return null;

    const lower = text.toLowerCase();

    // Common patterns
    if (lower.includes("tomorrow")) return "Tomorrow";
    if (lower.includes("today")) return "Today";

    // Match DD Month pattern like: 21 Feb
    const match = text.match(/\b(\d{1,2})\s?(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\b/i);

    if (match) {
      return match[0]; // Example: "21 Feb"
    }

    // Match full date: 21/02/2026
    const match2 = text.match(/\b\d{1,2}\/\d{1,2}\/\d{2,4}\b/);

    if (match2) {
      return match2[0];
    }

    return null;
  }
  function getUrgencyLevel(deadlineText: string | null) {
    if (!deadlineText) return "None";

    if (deadlineText === "Today") return "🔥 Very High";
    if (deadlineText === "Tomorrow") return "⚠️ High";

    return "📌 Medium";
  }


  useEffect(() => {
    setMounted(true);

    const interval = setInterval(() => {
      setCurrentTime(new Date());
    }, 1000);

    return () => clearInterval(interval);
  }, []);

  // ✅ FIX 4: Load emails when session is available
  useEffect(() => {
    if (!session) return;

    console.log("✅ Session found. Loading emails...");

    // Show splash screen
    setShowSplash(true);

    // Hide splash after 1.5 seconds
    const timer = setTimeout(() => {
      setShowSplash(false);
    }, 1500);

    // Load emails immediately (don't wait for splash)
    const fetchEmails = async () => {
      setLoading(true);

      try {
        const res = await fetch(`/api/gmail`);
        const data = await res.json();
        console.log("FIRST EMAIL:", data.emails[0]);


        console.log("📧 Emails loaded:", data.emails?.length || 0);

        setEmails(data.emails || []);
        setNextPageToken(data.nextPageToken || null);
        // 🔔 Notification Logic (New mails since last open)
        const lastSeen = localStorage.getItem("lastSeenTime");

          let freshMails: Email[] = [];

          if (lastSeen) {
            const lastTime = new Date(lastSeen).getTime();

            freshMails = (data.emails || []).filter((mail: Email) => {
              const mailTime = new Date(mail.date).getTime();
              return mailTime > lastTime;
            });
          }

          setNewMails(freshMails);
          setNewMailCount(freshMails.length);


      } catch (error) {
        console.error("❌ Error loading emails:", error);
      }

      setLoading(false);
    };

    fetchEmails();

    return () => clearTimeout(timer);
  }, [session]); // ✅ Only depends on session


  const refreshInbox = async () => {
    setEmails([]); // clear old emails
    setNextPageToken(null); // reset pagination
    await loadEmails(); // fetch fresh inbox
  };

  function getEmailCategory(mail: Email) {
    const subject = (mail.subject || "").toLowerCase();
    const snippet = (mail.snippet || "").toLowerCase();

    const text = subject + " " + snippet;

    if (
      text.includes("job") ||
      text.includes("intern") ||
      text.includes("interview") ||
      text.includes("apply")
    ) {
      return "Do Now";
    }

    if (
      text.includes("event") ||
      text.includes("meet") ||
      text.includes("schedule") ||
      text.includes("decision")
    ) {
      return "Needs Decision";
    }

    if (
      text.includes("newsletter") ||
      text.includes("update") ||
      text.includes("alert")
    ) {
      return "Waiting";
    }

    return "Low Energy";
  }


  function getPriorityScore(mail: any) {
    let score = 0;

    const subject = (mail.subject || "").toLowerCase();
    const snippet = (mail.snippet || "").toLowerCase();
    const text = subject + " " + snippet;

    if (
      text.includes("urgent") ||
      text.includes("today") ||
      text.includes("expires")
    )
      score += 50;
    else if (text.includes("tomorrow")) score += 40;
    else if (text.includes("deadline") || text.includes("last date"))
      score += 35;

    if (
      text.includes("job") ||
      text.includes("intern") ||
      text.includes("interview")
    )
      score += 20;
    else if (
      text.includes("payment") ||
      text.includes("invoice") ||
      text.includes("bill")
    )
      score += 18;
    else if (text.includes("meeting") || text.includes("event")) score += 15;
    else score += 5;

    if (mail.date) {
      const receivedDate = new Date(mail.date);
      const now = new Date();

      if (!isNaN(receivedDate.getTime())) {
        const diffHours =
          (now.getTime() - receivedDate.getTime()) / (1000 * 60 * 60);

        if (diffHours < 1) score += 30;
        else if (diffHours < 24) score += 25;
        else if (diffHours < 48) score += 15;
        else score += 5;
      }
    }

    return Math.min(score, 100);
  }

  function getPriorityColor(score: number) {
    if (score >= 80) return "#ff4d4d";
    if (score >= 50) return "#ffc107";
    return "#4caf50";
  }
  function getCategoryColor(category: string) {
    if (category === "Do Now") return "#EF4444"; // 🔥 Red
    if (category === "Needs Decision") return "#8B5CF6"; // 🟣 Purple
    if (category === "Waiting") return "#3B82F6"; // 🔵 Blue
    if (category === "Low Energy") return "#10B981"; // 🟢 Green

    return "#6B7280"; // Default Gray
  }

  function getBurnoutStats(emails: any[]) {
    let stressScore = 0;

    emails.forEach((mail) => {
      const text =
        (mail.subject || "").toLowerCase() +
        " " +
        (mail.snippet || "").toLowerCase();

      if (
        text.includes("urgent") ||
        text.includes("deadline") ||
        text.includes("asap") ||
        text.includes("immediately")
      ) {
        stressScore += 15;
      }

      if (getPriorityScore(mail) > 70) {
        stressScore += 10;
      }

      if (mail.date) {
        const dateObj = new Date(mail.date);
        const hour = dateObj.getHours();

        if (hour >= 23 || hour <= 5) {
          stressScore += 20;
        }
      }
    });

    if (stressScore > 100) stressScore = 100;

    let stressLevel = "Low";
    if (stressScore > 70) stressLevel = "High";
    else if (stressScore > 40) stressLevel = "Medium";

    let workloadTrend = emails.length > 15 ? "Increasing 📈" : "Stable ✅";

    let recommendation =
      stressLevel === "High"
        ? "Delegate or Snooze low-priority emails"
        : "You are managing well";

    return {
      stressScore,
      stressLevel,
      workloadTrend,
      recommendation,
    };
  }

  function isSpamEmail(mail: any) {
    const subject = (mail.subject || "").toLowerCase();
    const snippet = (mail.snippet || "").toLowerCase();
    const from = (mail.from || "").toLowerCase();

    const text = subject + " " + snippet;

    const spamWords = [
      "free",
      "offer",
      "limited time",
      "unsubscribe",
      "winner",
      "congratulations",
      "lottery",
      "claim",
      "buy now",
      "click here",
      "discount",
      "cash prize",
    ];

    for (let word of spamWords) {
      if (text.includes(word)) return true;
    }

    if (from.includes("noreply") && text.includes("unsubscribe")) {
      return true;
    }

    return false;
  }

  function isFirstTimeSender(mail: any, allEmails: any[]) {
    const sender = mail.from;
    const count = allEmails.filter((m) => m.from === sender).length;
    return count === 1;
  }

  function extractFirstLink(text: string) {
    if (!text) return null;

    const hrefMatch = text.match(/href=["']([^"']+)["']/i);
    if (hrefMatch && hrefMatch[1] && hrefMatch[1].startsWith("http")) {
      let link = hrefMatch[1];
      const lower = link.toLowerCase();
      if (
        !lower.includes("unsubscribe") &&
        !lower.includes("tracking") &&
        !lower.includes("email-alert") &&
        !lower.includes("manage") &&
        link.length < 500
      ) {
        link = link.replace(/&amp;/g, "&");
        return link;
      }
    }

    const cleanText = text.replace(/<[^>]*>/g, " ");
    const urlRegex = /https?:\/\/[^\s<>"{}|\\^`\[\]]+/g;
    const matches = cleanText.match(urlRegex);

    if (!matches || matches.length === 0) return null;

    const validLinks = matches.filter((url) => {
      const lower = url.toLowerCase();
      return (
        !lower.includes("unsubscribe") &&
        !lower.includes("tracking") &&
        !lower.includes("pixel") &&
        !lower.includes("beacon") &&
        !lower.includes("email.") &&
        !lower.includes("manage") &&
        !lower.includes("email-alert") &&
        url.length < 500
      );
    });

    if (validLinks.length === 0) return null;

    let link = validLinks[0];
    link = link.replace(/[.,;:)\]]+$/, "");
    link = link.replace(/&amp;/g, "&");

    return link;
  }

  function cleanEmailBody(text: string) {
    return text
      .replace(/<[^>]*>/g, "")
      .replace(/https?:\/\/\S+/g, "")
      .replace(/unsubscribe[\s\S]*/gi, "")
      .replace(/\s+/g, " ")
      .trim();
  }

  /* ✅ ADD THIS EXACTLY HERE */
  function extractEmail(raw: string) {
    if (!raw) return "";

    // Case 1: Name <email>
    const match = raw.match(/<(.+?)>/);
    if (match) return match[1];

    // Case 2: Direct email
    if (raw.includes("@")) return raw.trim();

    return "";
  }

  // ✅ Helper function to get initials from email
  function getInitials(email: string) {
    if (!email) return "?";
    const name = email.split("@")[0];
    const parts = name.split(/[._-]/);
    if (parts.length >= 2) {
      return (parts[0][0] + parts[1][0]).toUpperCase();
    }
    return name.substring(0, 2).toUpperCase();
  }

  // ✅ Action Button Style
  const actionBtn = {
    padding: "8px 14px",
    borderRadius: 10,
    border: "1px solid #E5E7EB",
    background: "white",
    cursor: "pointer",
    fontWeight: 600,
  };

  if (!session) {

    return (
      <div
        style={{
          minHeight: "100vh",
          background:
            "linear-gradient(135deg, #4F46E5 0%, #7C3AED 50%, #A78BFA 100%)",
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          padding: "60px",
          overflow: "hidden",
        }}
      >
        <div

        >

          {/* ✅ TOP HEADER ROW */}
          <div
            style={{
              position: "absolute",
              top: 25,
              left: 45,
              right: 45,
              display: "flex",
              alignItems: "center",
              justifyContent: "space-between",
            }}
          >
            {/* ✅ Left: Logo + Name */}
            <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
              <img
                src="/logo.png"
                alt="MailMind Logo"
                style={{
                  width: 42,
                  height: 42,
                  borderRadius: 10,
                  objectFit: "contain",
                }}
              />

              <h2
                style={{
                  color: "white",
                  fontWeight: 800,
                  fontSize: 22,
                  margin: 0,
                }}
              >
                MailMind
              </h2>
            </div>
            {/* Date & Time */}
            {mounted && (
              <div
                style={{
                  position: "absolute",
                  left: "50%",
                  transform: "translateX(-50%)",
                  padding: "8px 18px",
                  borderRadius: 14,
                  background: "rgba(255,255,255,0.12)",
                  backdropFilter: "blur(10px)",
                  color: "rgba(255,255,255,0.9)",
                  fontSize: 14,
                  fontWeight: 600,
                  letterSpacing: "0.5px",
                  whiteSpace: "nowrap",
                }}
              >
                {currentTime.toLocaleString("en-IN", {
                  weekday: "short",
                  day: "2-digit",
                  month: "short",
                  hour: "2-digit",
                  minute: "2-digit",
                })}
              </div>
            )}


            {/* ✅ Right: Features Button */}
            <Link href="/features" className="features-btn">
              Features →
            </Link>
          </div>



          {/* Brand Name */}

        </div>


        {/* ✅ Left Text Section */}
        <div style={{ maxWidth: "520px", color: "white" }}>
          <h1
            style={{
              fontSize: "64px",
              fontWeight: 800,
              lineHeight: 1.1,
            }}
          >
            Where email <br /> meets <br /> intelligence
          </h1>

          <p style={{ marginTop: 20, fontSize: 18, opacity: 0.9 }}>
            MailMind helps you summarize, prioritize and reply smarter —
            powered by AI.
          </p>

          {/* Buttons */}
          <div style={{ display: "flex", gap: 20, marginTop: 40 }}>
            <button
              onClick={() => signIn("google")}
              style={{
                padding: "14px 28px",
                borderRadius: 14,
                fontWeight: 700,
                cursor: "pointer",
                fontSize: 16,
                border: "none",
                position: "relative",
                overflow: "hidden",
                background: "white",
                color: "#2563EB",
              }}
              onMouseEnter={(e) => {
                const span = e.currentTarget.querySelector(
                  ".fill"
                ) as HTMLElement;
                span.style.transform = "translateX(0)";
                e.currentTarget.style.color = "white";
              }}
              onMouseLeave={(e) => {
                const span = e.currentTarget.querySelector(
                  ".fill"
                ) as HTMLElement;
                span.style.transform = "translateX(-100%)";
                e.currentTarget.style.color = "#2563EB";
              }}
            >
              {/* Fill Background */}
              <span
                className="fill"
                style={{
                  position: "absolute",
                  top: 0,
                  left: 0,
                  width: "100%",
                  height: "100%",
                  background: "linear-gradient(135deg,#2563EB,#0EA5E9)",
                  transform: "translateX(-100%)",
                  transition: "all 0.4s ease",
                  zIndex: 0,
                }}
              ></span>

              {/* Button Text */}
              <span style={{ position: "relative", zIndex: 1 }}>
                Sign in with Google →
              </span>
            </button>

            <button
              onClick={() => signIn("azure-ad")}
              style={{
                padding: "14px 32px",
                borderRadius: 14,
                fontWeight: 700,
                cursor: "pointer",
                fontSize: 16,
                border: "none",
                position: "relative",
                overflow: "hidden",

                // Default Background = White
                background: "white",
                color: "#2563EB",
              }}
              onMouseEnter={(e) => {
                const span = e.currentTarget.querySelector(
                  ".fill-outlook"
                ) as HTMLElement;

                // Slide Blue fill in
                span.style.transform = "translateX(0)";

                // Text becomes White
                e.currentTarget.style.color = "white";
              }}
              onMouseLeave={(e) => {
                const span = e.currentTarget.querySelector(
                  ".fill-outlook"
                ) as HTMLElement;

                // Slide fill back out
                span.style.transform = "translateX(-100%)";

                // Text becomes Blue again
                e.currentTarget.style.color = "#2563EB";
              }}
            >
              {/* Fill Background (Blue Slide) */}
              <span
                className="fill-outlook"
                style={{
                  position: "absolute",
                  top: 0,
                  left: 0,
                  width: "100%",
                  height: "100%",

                  // Hover Fill = Blue Gradient
                  background: "linear-gradient(135deg,#2563EB,#0EA5E9)",

                  transform: "translateX(-100%)",
                  transition: "all 0.4s ease",
                  zIndex: 0,
                }}
              ></span>

              {/* Button Text */}
              <span style={{ position: "relative", zIndex: 1 }}>
                Sign in with Outlook →
              </span>
            </button>





          </div>
        </div>

        {/* ✅ Right Flashcard Image Animation */}
        <div
          style={{
            width: "520px",
            height: "360px",
            borderRadius: 24,
            overflow: "hidden",
            position: "relative",
            boxShadow: "0 20px 60px rgba(0,0,0,0.25)",
          }}
        >
          <img
            key={currentSlide}
            src={LOGIN_SLIDES[currentSlide]}
            alt="slide"
            style={{
              width: "100%",
              height: "100%",
              objectFit: "cover",
              position: "absolute",
              animation: "fadeSlide 3.5s ease-in-out",

            }}
          />
        </div>

        {/* ✅ Animation CSS */}
        <style>
          {`
    @keyframes fadeSlide {
      0% {
        opacity: 0;
        transform: scale(0.98);
      }
      20% {
        opacity: 1;
        transform: scale(1);
      }
      80% {
        opacity: 1;
        transform: scale(1);
      }
      100% {
        opacity: 0;
        transform: scale(1.02);
      }
    }
  `}
        </style>

      </div>
    );
  }

  // ✅ FIX 3: Proper filtering with BOTH activeTab AND activeFolder
  const filteredEmails = emails.filter((mail) => {
    // Folder filtering first
    if (activeFolder === "starred") return starredIds.includes(mail.id);
    if (activeFolder === "snoozed") return snoozedIds.includes(mail.id);
    if (activeFolder === "done") return doneIds.includes(mail.id);
    if (activeFolder === "drafts")
      return mail.label?.includes("DRAFT");

    // Priority view - show all emails sorted by priority
    if (activeFolder === "priority") {
      // Will be sorted later, just don't filter out
      return true;
    }

    // Deadline view - show emails with deadlines
    if (activeFolder === "deadline") {
      // Check if email has deadline-related keywords or AI priority reason mentions deadline
      const hasDeadline = 
        mail.subject?.toLowerCase().match(/deadline|due|urgent|asap|today|tomorrow|this week/i) ||
        mail.snippet?.toLowerCase().match(/deadline|due|urgent|asap|today|tomorrow|this week/i) ||
        aiPriorityMap[mail.id]?.reason?.toLowerCase().includes('deadline');
      return hasDeadline;
    }

    // Inbox normal view hides snoozed/done
    if (activeFolder === "inbox") {
      if (snoozedIds.includes(mail.id)) return false;
      if (doneIds.includes(mail.id)) return false;
    }
    // 🔍 SEARCH FILTER (ADD HERE)
    if (searchQuery.trim() !== "") {
      const query = searchQuery.toLowerCase();

      const subjectMatch = mail.subject?.toLowerCase().includes(query);
      const snippetMatch = mail.snippet?.toLowerCase().includes(query);
      const fromMatch = mail.from?.toLowerCase().includes(query);

      if (!subjectMatch && !snippetMatch && !fromMatch) {
        return false;
      }
    }


    // Tab category filtering
    if (activeTab === "All Mails") return true;

    return getEmailCategory(mail) === activeTab;
  });

  // Sort emails based on active folder
  const sortedEmails = [...filteredEmails].sort((a, b) => {
    if (activeFolder === "priority") {
      // Sort by priority score (high to low)
      const priorityOrder: Record<string, number> = {
        'critical': 5,
        'high': 4,
        'medium': 3,
        'low': 2,
        'minimal': 1
      };
      const aPriority = aiPriorityMap[a.id]?.priority?.toLowerCase() || 'minimal';
      const bPriority = aiPriorityMap[b.id]?.priority?.toLowerCase() || 'minimal';
      return (priorityOrder[bPriority] || 0) - (priorityOrder[aPriority] || 0);
    }
    
    if (activeFolder === "deadline") {
      // Sort by date (most recent first for deadline urgency)
      return new Date(b.date).getTime() - new Date(a.date).getTime();
    }
    
    // Default: most recent first
    return new Date(b.date).getTime() - new Date(a.date).getTime();
  });



  const burnout = getBurnoutStats(sortedEmails);

  if (session && showSplash) {
    return <SplashScreen />;
  }

  return (
    <div className="h-screen flex flex-col">
      {/* ✅ Glass Outer Frame */}
      <div className="flex flex-col h-full m-4 rounded-3xl bg-white/40 backdrop-blur-2xl border border-white/30 shadow-xl overflow-hidden">

        {/* Premium Header with Gradient */}
        {/* ✅ TOP NAVBAR (Exact Reference Style) */}
        <div
          className="
               h-16 px-6 flex items-center justify-between
                bg-gradient-to-r from-[#3b4ba3] to-[#5876d6]
                text-white shadow-md"
        >



          {/* Left: Logo + Menu */}
          <div className="flex items-center gap-4">
            <button
              onClick={() => setSidebarOpen(!sidebarOpen)}
              className="text-2xl hover:opacity-80"
            >
              ☰
            </button>

            <h1 className="text-xl font-bold tracking-wide">
              MailMind
            </h1>
          </div>


          {/* 🔍 Search Bar */}
          <div className="hidden md:flex items-center bg-white/20 px-4 py-2 rounded-xl w-[320px]">
            <input
              type="text"
              placeholder="Search mails..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="bg-transparent outline-none text-white placeholder-white/70 w-full text-sm"
            />
          </div>

          {/* Right: Icons */}
          <div className="flex items-center gap-4">
            {/* Notification */}
            <div style={{ position: "relative" }}>
              {/* 🔔 Bell Button */}
              <button
                onClick={() => setShowNotifications(!showNotifications)}
                className="relative text-xl hover:opacity-80"
              >
                🔔

                {/* Badge Count */}
                {newMailCount > 0 && (
                  <span
                    style={{
                      position: "absolute",
                      top: "-6px",
                      right: "-6px",
                      background: "red",
                      color: "white",
                      fontSize: "11px",
                      fontWeight: "700",
                      padding: "3px 7px",
                      borderRadius: "999px",
                    }}
                  >
                    {newMailCount}
                  </span>
                )}
              </button>

              {/* 🔥 Notification Dropdown */}
              {showNotifications && (
                <div
                  style={{
                    position: "absolute",
                    top: "55px",
                    right: 0,
                    width: "320px",
                    background: "rgba(255,255,255,0.95)",
                    backdropFilter: "blur(20px)",
                    borderRadius: "18px",
                    boxShadow: "0 12px 40px rgba(0,0,0,0.18)",
                    border: "1px solid rgba(255,255,255,0.4)",
                    zIndex: 9999,
                    padding: "16px",
                  }}
                >
                  <h3 style={{ fontWeight: 700, marginBottom: 12 }}>
                    🔔 New Emails
                  </h3>

                  {/* If no new mails */}
                  {newMails.length === 0 && (
                    <p style={{ fontSize: 13, color: "#666" }}>
                      No new notifications 🎉
                    </p>
                  )}

                  {/* Show new mails */}
                  {newMails.slice(0, 5).map((mail) => (
                    <div
                      key={mail.id}
                      style={{
                        padding: "10px",
                        borderRadius: "12px",
                        marginBottom: "8px",
                        background: "#F3F4F6",
                        cursor: "pointer",
                      }}
                      onClick={() => {
                        openMailAndGenerateAI(mail.id, mail);
                        setShowNotifications(false);
                      }}
                    >
                      <p style={{ fontWeight: 700, fontSize: 13 }}>
                        {mail.subject}
                      </p>
                      <p style={{ fontSize: 12, color: "#555" }}>
                        {mail.snippet?.substring(0, 50)}...
                      </p>
                    </div>
                  ))}

                  {/* Mark All Seen Button */}
                  {newMailCount > 0 && (
                    <button
                      onClick={() => {
                        // Reset count only when user clicks
                        setNewMailCount(0);
                        setNewMails([]);
                        localStorage.setItem(
                          "lastSeenTime",
                          new Date().toISOString()
                        );
                        setShowNotifications(false);
                      }}
                      style={{
                        marginTop: 10,
                        width: "100%",
                        padding: "10px",
                        borderRadius: "12px",
                        border: "none",
                        background: "linear-gradient(135deg,#2563EB,#0EA5E9)",
                        color: "white",
                        fontWeight: 700,
                        cursor: "pointer",
                      }}
                    >
                      Mark all as seen ✅
                    </button>
                  )}
                </div>
              )}
            </div>




            {/* ✅ PROFILE DROPDOWN */}
            <div style={{ position: "relative" }}>

              {/* Profile Circle */}
              <div
                onClick={(e) => {
                  e.stopPropagation();
                  setShowProfile(!showProfile);
                }}
                style={{
                  width: 42,
                  height: 42,
                  borderRadius: "50%",
                  background: "rgba(255,255,255,0.25)",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  fontWeight: 700,
                  cursor: "pointer",
                }}
              >
                {session.user?.email?.[0].toUpperCase()}
              </div>

              {/* Dropdown Card */}
              {showProfile && (
                <div
                  onClick={(e) => e.stopPropagation()}
                  style={{
                    position: "absolute",
                    top: "55px",
                    right: 0,
                    width: "260px",
                    background: "rgba(255,255,255,0.92)",
                    backdropFilter: "blur(20px)",
                    borderRadius: "18px",
                    padding: "18px",
                    boxShadow: "0 12px 40px rgba(0,0,0,0.18)",
                    border: "1px solid rgba(255,255,255,0.4)",
                    zIndex: 9999,
                  }}
                >
                  {/* Gmail Email */}
                  <p style={{ fontWeight: 700, fontSize: 14, marginBottom: 6 }}>
                    Signed in as
                  </p>

                  <p
                    style={{
                      fontSize: 13,
                      color: "#444",
                      marginBottom: 14,
                      wordBreak: "break-word",
                    }}
                  >
                    {session.user?.email}
                  </p>

                  {/* Divider */}
                  <div
                    style={{
                      height: 1,
                      background: "#E5E7EB",
                      marginBottom: 12,
                    }}
                  />

                  {/* Logout */}
                  <button
                    onClick={() => signOut()}
                    style={{
                      width: "100%",
                      padding: "10px",
                      borderRadius: "12px",
                      border: "none",
                      background: "linear-gradient(135deg,#EF4444,#DC2626)",
                      color: "white",
                      fontWeight: 600,
                      cursor: "pointer",
                    }}
                  >
                    Logout
                  </button>
                </div>
              )}
            </div>


          </div>
        </div>


        {/* ✅ FIX 2: Sidebar as Fixed Overlay (OUTSIDE email list) */}
        {sidebarOpen && (
          <div
            style={{
              position: "fixed",
              top: 80,
              left: 0,
              width: 240,
              height: "calc(100vh - 80px)",
              background: "white",
              borderRight: "1px solid #E5E7EB",
              padding: 16,
              zIndex: 9999,
              boxShadow: "4px 0px 20px rgba(0,0,0,0.15)",
              overflowY: "auto",
            }}
          >
            <h3 style={{ fontSize: 14, marginBottom: 12, fontWeight: 700, color: "#111827" }}>📌 Dashboard</h3>
            {/* ✍ Compose Button */}
            <button
              onClick={() => {
                setShowCompose(true);
                setSidebarOpen(false);
              }}
              style={{
                width: "100%",
                padding: "12px",
                borderRadius: 12,
                border: "none",
                marginTop: 14,
                background: "linear-gradient(135deg,#2563EB,#0EA5E9)",
                color: "white",
                fontWeight: 700,
                cursor: "pointer",
              }}
            >
              ✍ Compose Mail
            </button>

            {/* 📝 Drafts Button */}
            <button
              onClick={() => {
                setActiveFolder("drafts");
                setSidebarOpen(false);
              }}
              style={{
                width: "100%",
                padding: "12px",
                borderRadius: 12,
                border: "1px solid #E5E7EB",
                marginTop: 10,
                background: "white",
                fontWeight: 700,
                cursor: "pointer",
              }}
            >
              📝 Drafts
            </button>


            {[
              { key: "inbox", label: "📥 Inbox" },
              { key: "starred", label: "⭐ Starred" },

            ].map((item) => (
              <div
                key={item.key}
                onClick={() => {
                  setActiveFolder(item.key);
                  setSidebarOpen(false);
                }}
                style={{
                  padding: "10px 12px",
                  borderRadius: 10,
                  cursor: "pointer",
                  fontWeight: 600,
                  marginBottom: 8,
                  background:
                    activeFolder === item.key ? "#DBEAFE" : "transparent",
                  transition: "all 0.2s ease",
                }}
                onMouseOver={(e) => {
                  if (activeFolder !== item.key) {
                    e.currentTarget.style.background = "#F3F4F6";
                  }
                }}
                onMouseOut={(e) => {
                  if (activeFolder !== item.key) {
                    e.currentTarget.style.background = "transparent";
                  }
                }}
              >
                {item.label}
              </div>

            ))}
            {[

              { key: "snoozed", label: "⏳ Snoozed" },
              { key: "done", label: "✅ Done" },
            ].map((item) => (
              <div
                key={item.key}
                onClick={() => {
                  setActiveFolder(item.key);
                  setSidebarOpen(false);
                }}
                style={{
                  padding: "10px 12px",
                  borderRadius: 10,
                  cursor: "pointer",
                  fontWeight: 600,
                  marginBottom: 8,
                  background:
                    activeFolder === item.key ? "#DBEAFE" : "transparent",
                }}
              >
                {item.label}
              </div>
            ))}

            {/* ✅ SMART VIEWS SECTION */}
            <hr style={{ margin: "16px 0", borderColor: "#E5E7EB" }} />
            <div style={{ 
              fontSize: 11, 
              fontWeight: 700, 
              color: "#9CA3AF", 
              marginBottom: 12,
              textTransform: "uppercase",
              letterSpacing: "0.5px"
            }}>
              Smart Views
            </div>
            {[
              { key: "priority", label: "By Priority", icon: "🎯" },
              { key: "deadline", label: "By Deadline", icon: "⏰" },
            ].map((item) => (
              <div
                key={item.key}
                onClick={() => {
                  setActiveFolder(item.key);
                  setSidebarOpen(false);
                }}
                style={{
                  padding: "10px 12px",
                  borderRadius: 10,
                  cursor: "pointer",
                  fontWeight: 600,
                  marginBottom: 8,
                  background:
                    activeFolder === item.key ? "#DBEAFE" : "transparent",
                  transition: "all 0.2s ease",
                }}
                onMouseOver={(e) => {
                  if (activeFolder !== item.key) {
                    e.currentTarget.style.background = "#F3F4F6";
                  }
                }}
                onMouseOut={(e) => {
                  if (activeFolder !== item.key) {
                    e.currentTarget.style.background = "transparent";
                  }
                }}
              >
                <span style={{ marginRight: 8 }}>{item.icon}</span>
                {item.label}
              </div>
            ))}

            {/* ✅ PASTE CATEGORY SECTION EXACTLY HERE */}
            <hr style={{ margin: "16px 0", borderColor: "#E5E7EB" }} />

            <div style={{ marginTop: 10 }}>

              <h3
                style={{
                  fontSize: 13,
                  marginBottom: 10,
                  fontWeight: 700,
                  color: "#111827",
                }}
              >
                📌 Categories
              </h3>

              {["All Mails", "Do Now", "Waiting", "Needs Decision", "Low Energy"].map(
                (tab) => (
                  <div
                    key={tab}
                    onClick={() => {
                      setActiveTab(tab);
                      setSidebarOpen(false);
                    }}
                    style={{
                      padding: "10px 12px",
                      borderRadius: 10,
                      cursor: "pointer",
                      fontWeight: 600,
                      marginBottom: 8,
                      background:
                        activeTab === tab ? "#EDE9FE" : "transparent",
                      color:
                        activeTab === tab ? "#6D28D9" : "#111827",
                    }}
                  >
                    {tab}
                  </div>
                )
              )}
            </div>


            {/* Close Button */}
            <button
              onClick={() => setSidebarOpen(false)}
              style={{
                marginTop: 20,
                width: "100%",
                padding: "10px",
                borderRadius: 10,
                border: "none",
                background: "#EF4444",
                color: "white",
                cursor: "pointer",
                fontWeight: 700,
              }}
            >
              Close Menu
            </button>
          </div>
        )}

        <div style={{ flex: 1, display: "flex", overflow: "hidden" }}>
          {/* Email List Sidebar - ✅ PREMIUM COMPACT DESIGN */}
          <div
            style={{
              width: "35%",
              borderRight: "1px solid #E5E7EB",
              overflowY: "auto",
              background: "#F8FAFF",
            }}
          >
            {/* Smart View Header */}
            {(activeFolder === "priority" || activeFolder === "deadline") && (
              <div style={{
                padding: "16px 20px",
                background: "white",
                borderBottom: "1px solid #E5E7EB",
                position: "sticky",
                top: 0,
                zIndex: 10,
              }}>
                <div style={{ 
                  fontSize: 14, 
                  fontWeight: 600, 
                  color: "#111827",
                  marginBottom: 4,
                  display: "flex",
                  alignItems: "center",
                  gap: 8
                }}>
                  <span>{activeFolder === "priority" ? "🎯" : "⏰"}</span>
                  {activeFolder === "priority" ? "By Priority" : "By Deadline"}
                </div>
                <div style={{ fontSize: 12, color: "#6B7280" }}>
                  {sortedEmails.length} {sortedEmails.length === 1 ? 'email' : 'emails'}
                </div>
              </div>
            )}

            {/* ✅ PREMIUM COMPACT EMAIL CARDS */}
            {sortedEmails.map((mail, index) => {
              const score = getPriorityScore(mail);
              const category = getEmailCategory(mail);



              return (
                <div
                  key={mail.id + "_" + index}
                  onClick={() => {
                    openMailAndGenerateAI(mail.id, mail);
                    generateAIPriorityForMail(mail);
                  }}
                  style={{
                    padding: 14,
                    marginBottom: 8,
                    marginLeft: 12,
                    marginRight: 12,
                    cursor: "pointer",
                    background: selectedMail?.id === mail.id
                      ? "linear-gradient(135deg, rgba(109, 40, 217, 0.08) 0%, rgba(37, 99, 235, 0.08) 100%)"
                      : "white",
                    borderRadius: 12,
                    border: selectedMail?.id === mail.id ? "2px solid #6D28D9" : "1px solid #E5E7EB",
                    transition: "all 0.2s ease",
                    boxShadow: selectedMail?.id === mail.id ? "0 4px 12px rgba(109, 40, 217, 0.15)" : "0 1px 3px rgba(0,0,0,0.05)",
                  }}
                  onMouseOver={(e) => {
                    if (selectedMail?.id !== mail.id) {
                      e.currentTarget.style.background = "white";
                      e.currentTarget.style.boxShadow = "0 2px 8px rgba(0,0,0,0.08)";
                    }
                  }}
                  onMouseOut={(e) => {
                    if (selectedMail?.id !== mail.id) {
                      e.currentTarget.style.background = "white";
                      e.currentTarget.style.boxShadow = "0 1px 3px rgba(0,0,0,0.05)";
                    }
                  }}
                >
                  {/* ✅ TOP ROW: Avatar + Subject + Badges */}
                  <div style={{ display: "flex", alignItems: "flex-start", gap: 10 }}>
                    {/* ✅ AVATAR */}
                    <div
                      style={{
                        width: 40,
                        height: 40,
                        borderRadius: 10,
                        background: "linear-gradient(135deg, #111827 0%, #2563EB 100%)",
                        display: "flex",
                        alignItems: "center",
                        justifyContent: "center",
                        color: "white",
                        fontWeight: 700,
                        fontSize: 14,
                        flexShrink: 0,
                        border: "2px solid white",
                        boxShadow: "0 2px 8px rgba(0,0,0,0.1)",
                      }}
                    >
                      {getInitials(mail.from)}
                    </div>

                    {/* ✅ CONTENT AREA */}
                    <div style={{ flex: 1, minWidth: 0 }}>
                      {/* Subject */}
                      <div style={{
                        fontWeight: 700,
                        color: "#111827",
                        fontSize: 14,
                        marginBottom: 4,
                        overflow: "hidden",
                        textOverflow: "ellipsis",
                        whiteSpace: "nowrap"
                      }}>
                        {mail.subject || "(No Subject)"}
                      </div>

                      {/* ✅ COMPACT SINGLE LINE SNIPPET */}
                      <p
                        style={{
                          margin: 0,
                          fontSize: 12,
                          color: "#6B7280",
                          overflow: "hidden",
                          textOverflow: "ellipsis",
                          whiteSpace: "nowrap",
                        }}
                      >
                        {mail.snippet}
                      </p>

                      {/* Date + Badges Row */}
                      <div style={{ display: "flex", alignItems: "center", gap: 6, marginTop: 6, flexWrap: "wrap" }}>


                        {/* Date */}
                        <span style={{ fontSize: 11, color: "#9CA3AF" }}>
                          {mail.date}
                        </span>

                        {/* Priority Badge (only in priority view) */}
                        {activeFolder === "priority" && aiPriorityMap[mail.id]?.priority && (
                          <span
                            style={{
                              padding: "2px 8px",
                              borderRadius: 6,
                              fontSize: 10,
                              fontWeight: 600,
                              background: 
                                aiPriorityMap[mail.id].priority.toLowerCase() === 'critical' ? '#FEE2E2' :
                                aiPriorityMap[mail.id].priority.toLowerCase() === 'high' ? '#FED7AA' :
                                aiPriorityMap[mail.id].priority.toLowerCase() === 'medium' ? '#FEF3C7' :
                                aiPriorityMap[mail.id].priority.toLowerCase() === 'low' ? '#D1FAE5' :
                                '#F3F4F6',
                              color:
                                aiPriorityMap[mail.id].priority.toLowerCase() === 'critical' ? '#991B1B' :
                                aiPriorityMap[mail.id].priority.toLowerCase() === 'high' ? '#9A3412' :
                                aiPriorityMap[mail.id].priority.toLowerCase() === 'medium' ? '#92400E' :
                                aiPriorityMap[mail.id].priority.toLowerCase() === 'low' ? '#065F46' :
                                '#6B7280',
                              border: '1px solid',
                              borderColor:
                                aiPriorityMap[mail.id].priority.toLowerCase() === 'critical' ? '#FCA5A5' :
                                aiPriorityMap[mail.id].priority.toLowerCase() === 'high' ? '#FDBA74' :
                                aiPriorityMap[mail.id].priority.toLowerCase() === 'medium' ? '#FDE68A' :
                                aiPriorityMap[mail.id].priority.toLowerCase() === 'low' ? '#6EE7B7' :
                                '#E5E7EB',
                            }}
                          >
                            {aiPriorityMap[mail.id].priority.toUpperCase()}
                          </span>
                        )}

                        {/* Deadline Badge (only in deadline view) */}
                        {activeFolder === "deadline" && (
                          <span
                            style={{
                              padding: "2px 8px",
                              borderRadius: 6,
                              fontSize: 10,
                              fontWeight: 600,
                              background: "#FEF3C7",
                              color: "#92400E",
                              border: '1px solid #FDE68A',
                            }}
                          >
                            ⏰ DEADLINE
                          </span>
                        )}

                        {/* First Time Sender Badge */}
                        {isFirstTimeSender(mail, emails) && (
                          <span
                            style={{
                              padding: "2px 8px",
                              borderRadius: 8,
                              fontSize: 10,
                              fontWeight: 700,
                              background: "linear-gradient(135deg, #0EA5E9 0%, #2563EB 100%)",
                              color: "white",
                            }}
                          >
                            🆕 New
                          </span>
                        )}

                        {/* Spam Badge */}
                        {isSpamEmail(mail) && (
                          <span
                            style={{
                              backgroundColor: "#dc2626",
                              color: "white",
                              padding: "2px 8px",
                              borderRadius: 8,
                              fontSize: 10,
                              fontWeight: 700,
                            }}
                          >
                            🚫 SPAM
                          </span>
                        )}
                      </div>
                    </div>
                  </div>

                  {/* ✅ PRIORITY BADGE - COMPACT VERSION */}
                  <div

                    style={{
                      display: "inline-block",
                      padding: "4px 10px",
                      borderRadius: "12px",
                      fontSize: "11px",
                      fontWeight: "bold",
                      marginTop: "8px",
                      background: `linear-gradient(135deg, ${getCategoryColor(category)}, #00000020)`,
                      color: "white",
                    }}
                  >
                    {category} • {score}

                  </div>

                  {/* AI Priority Reason - Compact */}
                  {aiPriorityMap[mail.id] && (
                    <p style={{
                      fontSize: 11,
                      color: "#6B7280",
                      marginTop: 4,
                      marginBottom: 0,
                      lineHeight: 1.4
                    }}>
                      {aiPriorityMap[mail.id].reason}
                    </p>
                  )}
                </div>
              );
            })}

            {nextPageToken && (
              <button
                onClick={loadEmails}
                disabled={loading}
                style={{
                  width: "calc(100% - 24px)",
                  margin: "12px",
                  padding: 12,
                  background: loading ? "#E5E7EB" : "linear-gradient(135deg, #6D28D9 0%, #2563EB 100%)",
                  color: "white",
                  border: "none",
                  borderRadius: 10,
                  fontWeight: 600,
                  cursor: loading ? "not-allowed" : "pointer",
                  boxShadow: "0 2px 8px rgba(109, 40, 217, 0.2)",
                }}
              >
                {loading ? "Loading..." : "Load More"}
              </button>
            )}
          </div>

          {/* Email Detail Panel */}
          <div
            style={{
              flex: 1,
              padding: 18,
              background: "#F8FAFF",
              overflowY: "scroll",
            }}
          >
            {!selectedMail ? (
              <div style={{
                textAlign: "center",
                paddingTop: 60,
                color: "#6B7280"
              }}>
                <h2 style={{ fontSize: 24, fontWeight: 700, color: "#111827" }}>
                  📩 Select an email to view
                </h2>
                <p style={{ marginTop: 12 }}>Choose an email from the list to see details and AI insights</p>
              </div>
            ) : (
              <Fragment>
                {/* Email Header - ✅ STICKY WITH QUICK ACTIONS */}
                <div style={{
                  marginBottom: 24,
                  padding: 12,
                  background: "white",
                  borderRadius: 16,
                  boxShadow: "0 2px 8px rgba(0,0,0,0.04)",
                  border: "1px solid #E5E7EB",
                }}>
                  <h2 style={{ fontSize: 16, fontWeight: 100, color: "#111827", margin: 0 }}>
                    {selectedMail.subject}
                  </h2>
                  <p style={{ color: "#6B7280", marginTop: 12, marginBottom: 6 }}>
                    <strong style={{ color: "#111827" }}>From:</strong> {selectedMail.from}
                  </p>
                  <p style={{ color: "#6B7280", margin: 0 }}>
                    <strong style={{ color: "#111827" }}>Date:</strong> {selectedMail.date}
                  </p>

                  <div style={{
                    display: "flex",
                    gap: 10,
                    marginTop: 12,
                    alignItems: "center",
                    flexWrap: "wrap"
                  }}>

                    <button
                      onClick={toggleStar}
                      style={{
                        padding: "6px 10px",
                        fontSize: 12,
                        borderRadius: 8,
                        border: "1px solid #ddd",
                        cursor: "pointer",
                        background: starredIds.includes(selectedMail.id)
                          ? "#FEF9C3"
                          : "white",
                      }}
                    >
                      ⭐ Star
                    </button>

                    <button
                      onClick={snoozeMail}
                      style={{
                        padding: "6px 10px",
                        fontSize: 12,
                        borderRadius: 8,
                        border: "1px solid #ddd",
                        cursor: "pointer",
                        background: "white",
                      }}
                    >
                      ⏳ Snooze
                    </button>

                    <button
                      onClick={markDone}
                      style={{
                        padding: "6px 10px",
                        fontSize: 12,
                        borderRadius: 8,
                        border: "1px solid #ddd",
                        cursor: "pointer",
                        background: "#DCFCE7",
                      }}
                    >
                      ✅ Done
                    </button>
                    {/* 🗑️ Delete */}
                    <button
                      onClick={deleteSelectedMail}
                      title="Delete Email"
                      style={{
                        padding: "6px 10px",
                        fontSize: 14,
                        borderRadius: 8,
                        border: "1px solid #ddd",
                        cursor: "pointer",
                        background: "#FEE2E2",
                      }}
                    >
                      🗑️
                    </button>

                    {/* 💎 Groq AI */}
                    <button
                      onClick={() => setShowGroq(true)}
                      title="Ask Groq"
                      style={{
                        padding: "6px 10px",
                        fontSize: 14,
                        borderRadius: 8,
                        border: "1px solid #ddd",
                        cursor: "pointer",
                        background: "#DBEAFE",
                      }}
                    >
                      💎 Ask Groq
                    </button>
                  </div>
                </div>
                {/* ✅ DEADLINE DETECTOR CARD */}
                {deadline && (
                  <div
                    style={{
                      background: "linear-gradient(135deg, #FEF9C3 0%, #FDE68A 100%)",
                      padding: 10,
                      borderRadius: 10,
                      marginBottom: 0,
                      border: "1px solid #FACC15",
                      boxShadow: "0 2px 8px rgba(0,0,0,0.05)",
                    }}
                  >
                    <h3 style={{ margin: 0, fontWeight: 800, color: "#92400E" }}>
                      ⏰ Deadline Alert
                    </h3>

                    <p style={{ marginTop: 8, fontSize: 14, color: "#78350F" }}>
                      📅 <strong>Deadline:</strong> {deadline}
                    </p>

                    <p style={{ marginTop: 4, fontSize: 14, color: "#78350F" }}>
                      ⚠️ <strong>Urgency:</strong> {urgency}
                    </p>
                  </div>
                )}

                {/* ✅ STEP 4A - GRID FOR AI SUMMARY + WHY IMPORTANT */}
                <div
                  style={{
                    display: "grid",
                    gridTemplateColumns: "1fr 1fr",
                    gap: 18,
                    marginBottom: 22,
                  }}
                >
                  {/* AI Summary Card */}
                  <div style={{
                    background: "linear-gradient(135deg, rgba(109, 40, 217, 0.03) 0%, rgba(37, 99, 235, 0.03) 100%)",
                    padding: 16,
                    borderRadius: 16,
                    boxShadow: "0 2px 8px rgba(0,0,0,0.04)",
                    border: "1px solid #E5E7EB"
                  }}>
                    <h3 style={{ fontSize: 15, marginBottom: 14, fontWeight: 700, color: "#111827" }}>
                      ✨ AI Summary
                    </h3>
                    <button
                      onClick={() => generateSummary(selectedMail)}
                      style={{
                        padding: "10px 18px",
                        borderRadius: 10,
                        border: "none",
                        background: "linear-gradient(135deg, #6D28D9 0%, #2563EB 100%)",
                        color: "white",
                        cursor: "pointer",
                        fontWeight: 600,
                        marginBottom: 14,
                        boxShadow: "0 4px 12px rgba(109, 40, 217, 0.25)",
                        transition: "all 0.3s ease",
                      }}
                      onMouseOver={(e) => {
                        e.currentTarget.style.transform = "translateY(-2px)";
                        e.currentTarget.style.boxShadow = "0 6px 16px rgba(109, 40, 217, 0.35)";
                      }}
                      onMouseOut={(e) => {
                        e.currentTarget.style.transform = "translateY(0)";
                        e.currentTarget.style.boxShadow = "0 4px 12px rgba(109, 40, 217, 0.25)";
                      }}
                    >
                      Generate Summary
                    </button>

                    <div
                      style={{
                        lineHeight: 1.8,
                        whiteSpace: "pre-wrap",
                        background: "white",
                        padding: 18,
                        borderRadius: 12,
                        fontSize: 14,
                        color: "#374151",
                        border: "1px solid #E5E7EB"
                      }}
                    >
                      {loadingAI ? "🔄 Generating AI summary..." : aiSummary || "Click button to generate summary"}
                    </div>
                  </div>

                  {/* Why Important Card */}
                  <div
                    style={{
                      background: "linear-gradient(135deg, rgba(109, 40, 217, 0.03) 0%, rgba(14, 165, 233, 0.03) 100%)",
                      padding: 24,
                      borderRadius: 16,
                      boxShadow: "0 2px 8px rgba(0,0,0,0.04)",
                      border: "1px solid #E5E7EB"
                    }}
                  >
                    <h3 style={{ fontSize: 18, marginBottom: 14, fontWeight: 700, color: "#111827" }}>
                      📌 Why Important?
                    </h3>
                    <button
                      onClick={() => generateExplanation(selectedMail)}
                      style={{
                        padding: "10px 18px",
                        background: "linear-gradient(135deg, #6D28D9 0%, #2563EB 100%)",
                        color: "white",
                        borderRadius: 10,
                        border: "none",
                        cursor: "pointer",
                        marginBottom: 14,
                        fontWeight: 600,
                        boxShadow: "0 4px 12px rgba(109, 40, 217, 0.25)",
                        transition: "all 0.3s ease",
                      }}
                      onMouseOver={(e) => {
                        e.currentTarget.style.transform = "translateY(-2px)";
                        e.currentTarget.style.boxShadow = "0 6px 16px rgba(109, 40, 217, 0.35)";
                      }}
                      onMouseOut={(e) => {
                        e.currentTarget.style.transform = "translateY(0)";
                        e.currentTarget.style.boxShadow = "0 4px 12px rgba(109, 40, 217, 0.25)";
                      }}
                    >
                      Explain Importance
                    </button>

                    <div
                      style={{
                        lineHeight: 1.8,
                        whiteSpace: "pre-wrap",
                        background: "white",
                        padding: 18,
                        borderRadius: 12,
                        fontSize: 14,
                        color: "#374151",
                        border: "1px solid #E5E7EB"
                      }}
                    >
                      {aiReason || "Click button to explain importance"}
                    </div>
                  </div>
                </div>

                {/* ✅ STEP 4B - GRID FOR TASKS + BURNOUT */}
                <div
                  style={{
                    display: "grid",
                    gridTemplateColumns: "1fr 1fr",
                    gap: 18,
                    marginBottom: 22,
                  }}
                >
                  {/* Tasks Extracted */}
                  <div
                    style={{
                      background: "linear-gradient(135deg, rgba(14, 165, 233, 0.03) 0%, rgba(37, 99, 235, 0.03) 100%)",
                      padding: 24,
                      borderRadius: 16,
                      boxShadow: "0 2px 8px rgba(0,0,0,0.04)",
                      border: "1px solid #E5E7EB"
                    }}
                  >
                    <h3 style={{ fontSize: 18, marginBottom: 14, fontWeight: 700, color: "#111827" }}>
                      ✅ Tasks Extracted
                    </h3>
                    {extractTasks(selectedMail?.snippet || selectedMail?.body || "").map((task, i) => (
                      <p key={i} style={{ marginBottom: 8, color: "#374151", fontSize: 14 }}>
                        • {task}
                      </p>
                    ))}
                  </div>

                  {/* Burnout Dashboard */}
                  <div
                    style={{
                      background: "linear-gradient(135deg, rgba(109, 40, 217, 0.05) 0%, rgba(37, 99, 235, 0.05) 100%)",
                      padding: 24,
                      borderRadius: 16,
                      boxShadow: "0 2px 8px rgba(0,0,0,0.04)",
                      border: "1px solid #E5E7EB"
                    }}
                  >
                    <h3 style={{ fontSize: 18, marginBottom: 14, fontWeight: 700, color: "#111827" }}>
                      🔥 Burnout Dashboard
                    </h3>
                    <p style={{ marginBottom: 8, color: "#374151", fontSize: 14 }}>
                      <strong style={{ color: "#111827" }}>Stress Level:</strong> {burnout.stressLevel}
                    </p>
                    <p style={{ marginBottom: 8, color: "#374151", fontSize: 14 }}>
                      <strong style={{ color: "#111827" }}>Workload Trend:</strong> {burnout.workloadTrend}
                    </p>
                    <p style={{ fontSize: 13, color: "#6B7280", marginTop: 12 }}>
                      <strong style={{ color: "#111827" }}>Recommendation:</strong> {burnout.recommendation}
                    </p>
                  </div>
                </div>

                {/* AI Reply Generator - ✅ FULL WIDTH */}
                <div
                  style={{
                    background: "linear-gradient(135deg, rgba(14, 165, 233, 0.05) 0%, rgba(37, 99, 235, 0.05) 100%)",
                    padding: 24,
                    borderRadius: 16,
                    marginBottom: 20,
                    boxShadow: "0 2px 8px rgba(0,0,0,0.04)",
                    border: "1px solid #E5E7EB",
                    maxWidth: "100%",
                  }}
                >
                  <h3 style={{ fontSize: 18, marginBottom: 14, fontWeight: 700, color: "#111827" }}>
                    💬 AI Reply Generator
                  </h3>

                  <button
                    onClick={generateReply}
                    style={{
                      padding: "10px 18px",
                      borderRadius: 10,
                      background: "linear-gradient(135deg, #0EA5E9 0%, #2563EB 100%)",
                      color: "white",
                      border: "none",
                      cursor: "pointer",
                      fontSize: 14,
                      fontWeight: 600,
                      boxShadow: "0 4px 12px rgba(14, 165, 233, 0.25)",
                      transition: "all 0.3s ease",
                    }}
                    onMouseOver={(e) => {
                      e.currentTarget.style.transform = "translateY(-2px)";
                      e.currentTarget.style.boxShadow = "0 6px 16px rgba(14, 165, 233, 0.35)";
                    }}
                    onMouseOut={(e) => {
                      e.currentTarget.style.transform = "translateY(0)";
                      e.currentTarget.style.boxShadow = "0 4px 12px rgba(14, 165, 233, 0.25)";
                    }}
                  >
                    {loadingReply ? "Generating..." : "Generate Reply"}
                  </button>

                  {/* Show Generated Reply */}
                  {aiReply && (
                    <div
                      style={{
                        marginTop: 14,
                        padding: 18,
                        background: "white",
                        borderRadius: 12,
                        border: "1px solid #E5E7EB",
                        whiteSpace: "pre-wrap",
                        lineHeight: 1.7,
                        fontSize: 14,
                        color: "#374151"
                      }}
                    >
                      {aiReply}
                    </div>
                  )}

                  {/* ✍ Editable Reply + Copy + Send Section */}
                  {aiReply && (
                    <div
                      style={{
                        marginTop: 18,
                        padding: 18,
                        background: "white",
                        borderRadius: 12,
                        border: "1px solid #E5E7EB",
                      }}
                    >
                      <h4 style={{ fontWeight: 700, marginBottom: 10, color: "#111827" }}>
                        ✍ Edit Reply Before Sending
                      </h4>

                      {/* Editable Textarea */}
                      <textarea
                        value={editableReply}
                        onChange={(e) => setEditableReply(e.target.value)}
                        rows={6}
                        style={{
                          width: "100%",
                          padding: 14,
                          borderRadius: 10,
                          border: "1px solid #E5E7EB",
                          fontSize: 14,
                          resize: "none",
                          fontFamily: "inherit",
                          color: "#374151"
                        }}
                      />

                      {/* Buttons Row */}
                      <div
                        style={{
                          display: "flex",
                          gap: 12,
                          marginTop: 14,
                        }}
                      >
                        {/* 📋 Copy Button */}
                        <button
                          onClick={() => {
                            navigator.clipboard.writeText(editableReply);
                            setCopied(true);
                            setTimeout(() => setCopied(false), 2000);
                          }}
                          style={{
                            padding: "10px 16px",
                            borderRadius: 10,
                            border: "none",
                            cursor: "pointer",
                            background: copied ? "#10b981" : "linear-gradient(135deg, #6D28D9 0%, #2563EB 100%)",
                            color: "white",
                            fontWeight: 600,
                            transition: "all 0.3s ease",
                            boxShadow: "0 4px 12px rgba(109, 40, 217, 0.25)",
                          }}
                        >
                          {copied ? "✅ Copied!" : "📋 Copy"}
                        </button>

                        {/* ✉ Send Button */}
                        <button
                          onClick={async () => {
                            if (!selectedMail) return alert("Select email first");

                            const recipient = extractEmail(selectedMail.from);

                            if (!recipient) {
                              alert("❌ Cannot reply: No valid recipient email found");
                              return;
                            }

                            const res = await fetch("/api/gmail/reply", {
                              method: "POST",
                              headers: { "Content-Type": "application/json" },
                              body: JSON.stringify({
                                to: recipient,
                                subject: selectedMail.subject,
                                body: editableReply,
                                threadId: selectedMail.threadId,
                                originalMessageId: selectedMail.messageId,
                              }),
                            });

                            const data = await res.json();

                            if (data.success) {
                              alert("✅ Reply Sent Successfully!");
                            } else {
                              alert("❌ Error: " + data.error);
                            }
                          }}
                          style={{
                            padding: "10px 16px",
                            borderRadius: 10,
                            border: "none",
                            cursor: "pointer",
                            background: "linear-gradient(135deg, #0EA5E9 0%, #2563EB 100%)",
                            color: "white",
                            fontWeight: 600,
                            transition: "all 0.3s ease",
                            boxShadow: "0 4px 12px rgba(14, 165, 233, 0.25)",
                          }}
                        >
                          ✉ Reply Now
                        </button>
                      </div>
                    </div>
                  )}
                </div>

                {/* Link Section */}
                {extractFirstLink(selectedMail?.body || selectedMail?.snippet || "") && (
                  <div style={{
                    marginBottom: 20,
                    padding: 20,
                    background: "linear-gradient(135deg, rgba(109, 40, 217, 0.05) 0%, rgba(14, 165, 233, 0.05) 100%)",
                    borderRadius: 16,
                    border: "1px solid #E5E7EB"
                  }}>
                    <a
                      href={extractFirstLink(selectedMail?.body || selectedMail?.snippet || "") || "#"}
                      target="_blank"
                      rel="noreferrer"
                      style={{
                        display: "inline-block",
                        padding: "12px 24px",
                        background: "linear-gradient(135deg, #0EA5E9 0%, #2563EB 100%)",
                        color: "white",
                        textDecoration: "none",
                        borderRadius: 10,
                        fontSize: 15,
                        fontWeight: 700,
                        boxShadow: "0 4px 12px rgba(14, 165, 233, 0.25)",
                        transition: "all 0.3s ease",
                      }}
                      onMouseOver={(e) => {
                        e.currentTarget.style.transform = "translateY(-2px)";
                        e.currentTarget.style.boxShadow = "0 6px 16px rgba(14, 165, 233, 0.35)";
                      }}
                      onMouseOut={(e) => {
                        e.currentTarget.style.transform = "translateY(0)";
                        e.currentTarget.style.boxShadow = "0 4px 12px rgba(14, 165, 233, 0.25)";
                      }}
                    >
                      🔗 CLICK HERE FOR LINK
                    </a>
                  </div>
                )}

                {/* Related Emails */}
                <div
                  style={{
                    background: "linear-gradient(135deg, rgba(14, 165, 233, 0.03) 0%, rgba(109, 40, 217, 0.03) 100%)",
                    padding: 24,
                    borderRadius: 16,
                    marginBottom: 20,
                    boxShadow: "0 2px 8px rgba(0,0,0,0.04)",
                    border: "1px solid #E5E7EB"
                  }}
                >
                  <h3 style={{ fontSize: 18, marginBottom: 14, fontWeight: 700, color: "#111827" }}>
                    📌 Related Emails
                  </h3>
                  {emails
                    .filter((m) => m.subject?.includes(selectedMail.subject.split(" ")[0]))
                    .slice(0, 3)
                    .map((m) => (
                      <p key={m.id} style={{ marginBottom: 8, color: "#374151", fontSize: 14 }}>
                        • {m.subject}
                      </p>
                    ))}
                </div>

                {/* Full Email Content */}
                <div
                  style={{
                    background: "white",
                    padding: 24,
                    borderRadius: 16,
                    marginBottom: 20,
                    boxShadow: "0 2px 8px rgba(0,0,0,0.04)",
                    border: "1px solid #E5E7EB"
                  }}
                >
                  <h3 style={{ fontSize: 18, marginBottom: 14, fontWeight: 700, color: "#111827" }}>
                    📩 Full Email Content
                  </h3>

                  <iframe
                    srcDoc={`<base target="_blank" />${selectedMail?.body || "<p>No content available</p>"}`}
                    style={{
                      width: "100%",
                      height: "650px",
                      border: "1px solid #E5E7EB",
                      borderRadius: 12,
                      background: "white",
                    }}
                  />
                </div>

                {/* 📎 Attachments Section */}
                {(selectedMail?.attachments?.length ?? 0) > 0 && (
                  <div
                    style={{
                      marginTop: 20,
                      padding: 24,
                      borderRadius: 16,
                      background: "linear-gradient(135deg, rgba(109, 40, 217, 0.03) 0%, rgba(14, 165, 233, 0.03) 100%)",
                      border: "1px solid #E5E7EB"
                    }}
                  >
                    <h3 style={{ fontWeight: 700, marginBottom: 14, color: "#111827", fontSize: 18 }}>
                      📎 Attachments
                    </h3>

                    {selectedMail.attachments?.map((file: any) => (
                      <div
                        key={file.attachmentId}
                        style={{
                          display: "flex",
                          justifyContent: "space-between",
                          alignItems: "center",
                          padding: 16,
                          background: "white",
                          borderRadius: 12,
                          border: "1px solid #E5E7EB",
                          marginBottom: 12,
                        }}
                      >
                        {/* File Name */}
                        <div>
                          <div style={{ fontWeight: 600, color: "#111827" }}>📎 {file.filename}</div>
                          <p style={{ fontSize: 12, color: "#6B7280", margin: "4px 0 0 0" }}>{file.mimeType}</p>
                        </div>

                        {/* Buttons */}
                        <div style={{ display: "flex", gap: 10 }}>
                          {/* 👁 Preview */}
                          <button
                            onClick={() => setHoverFile(file)}
                            style={{
                              background: "linear-gradient(135deg, #6D28D9 0%, #2563EB 100%)",
                              color: "white",
                              border: "none",
                              padding: "8px 14px",
                              borderRadius: 8,
                              cursor: "pointer",
                              fontWeight: 600,
                              boxShadow: "0 2px 8px rgba(109, 40, 217, 0.25)",
                              transition: "all 0.3s ease",
                            }}
                          >
                            👁 Preview
                          </button>

                          {/* ⬇ Download */}
                          <a
                            href={`/api/gmail/attachment?id=${selectedMail.id}&att=${file.attachmentId}&mime=${file.mimeType}`}
                            target="_blank"
                            style={{
                              background: "linear-gradient(135deg, #0EA5E9 0%, #2563EB 100%)",
                              color: "white",
                              padding: "8px 14px",
                              borderRadius: 8,
                              textDecoration: "none",
                              fontWeight: 600,
                              boxShadow: "0 2px 8px rgba(14, 165, 233, 0.25)",
                              transition: "all 0.3s ease",
                              display: "inline-block",
                            }}
                          >
                            ⬇ Download
                          </a>
                        </div>
                      </div>
                    ))}
                  </div>
                )}

                {/* ✅ Center Preview Modal */}
                {hoverFile && (
                  <div
                    onClick={() => setHoverFile(null)}
                    style={{
                      position: "fixed",
                      top: 0,
                      left: 0,
                      width: "100vw",
                      height: "100vh",
                      background: "rgba(17, 24, 39, 0.7)",
                      backdropFilter: "blur(8px)",
                      display: "flex",
                      justifyContent: "center",
                      alignItems: "center",
                      zIndex: 9999,
                    }}
                  >
                    <div
                      onClick={(e) => e.stopPropagation()}
                      style={{
                        width: "560px",
                        height: "480px",
                        background: "white",
                        borderRadius: 20,
                        padding: 24,
                        boxShadow: "0 20px 60px rgba(0,0,0,0.3)",
                      }}
                    >
                      <button
                        onClick={() => setHoverFile(null)}
                        style={{
                          float: "right",
                          background: "#dc2626",
                          color: "white",
                          border: "none",
                          borderRadius: 10,
                          padding: "8px 14px",
                          cursor: "pointer",
                          fontWeight: 600,
                        }}
                      >
                        ✖ Close
                      </button>

                      <h3 style={{ fontWeight: 700, marginBottom: 16, color: "#111827" }}>
                        👁 Preview: {hoverFile.filename}
                      </h3>

                      {hoverFile.mimeType.startsWith("image/") && (
                        <img
                          src={`/api/gmail/attachment?id=${selectedMail.id}&att=${hoverFile.attachmentId}&mime=${hoverFile.mimeType}`}
                          alt="preview"
                          style={{
                            width: "100%",
                            height: "360px",
                            objectFit: "contain",
                            borderRadius: 12,
                          }}
                        />
                      )}

                      {hoverFile.mimeType === "application/pdf" && (
                        <iframe
                          src={`/api/gmail/attachment?id=${selectedMail.id}&att=${hoverFile.attachmentId}&mime=${hoverFile.mimeType}`}
                          style={{
                            width: "100%",
                            height: "360px",
                            border: "none",
                            borderRadius: 12,
                          }}
                        />
                      )}

                      {!hoverFile.mimeType.startsWith("image/") &&
                        hoverFile.mimeType !== "application/pdf" && (
                          <p style={{ fontSize: 14, color: "#6B7280", marginTop: 20, textAlign: "center" }}>
                            Preview not available for this file type.
                          </p>
                        )}
                    </div>
                  </div>
                )}
              </Fragment>
            )}
          </div>
        </div>
      </div>
      {/* ✅ COMPOSE MODAL POPUP */}
      {showCompose && (
        <div
          style={{
            position: "fixed",
            top: 0,
            left: 0,
            width: "100%",
            height: "100%",
            background: "rgba(0,0,0,0.55)",
            display: "flex",
            justifyContent: "center",
            alignItems: "center",
            zIndex: 99999,
          }}
        >
          <div
            style={{
              width: 520,
              background: "white",
              padding: 24,
              borderRadius: 18,
              boxShadow: "0 20px 60px rgba(0,0,0,0.3)",
            }}
          >
            <h2 style={{ fontWeight: 800, fontSize: 18 }}>
              ✍ Compose Email
            </h2>

            <input
              placeholder="To"
              style={{
                width: "100%",
                padding: 12,
                marginTop: 14,
                borderRadius: 10,
                border: "1px solid #ddd",
              }}
            />

            <input
              placeholder="Subject"
              style={{
                width: "100%",
                padding: 12,
                marginTop: 10,
                borderRadius: 10,
                border: "1px solid #ddd",
              }}
            />

            <textarea
              placeholder="Write your email..."
              rows={6}
              style={{
                width: "100%",
                padding: 12,
                marginTop: 10,
                borderRadius: 10,
                border: "1px solid #ddd",
              }}
            />

            <div style={{ display: "flex", gap: 10, marginTop: 16 }}>
              <button
                style={{
                  flex: 1,
                  padding: 12,
                  borderRadius: 10,
                  border: "none",
                  background: "linear-gradient(135deg,#2563EB,#0EA5E9)",
                  color: "white",
                  fontWeight: 700,
                  cursor: "pointer",
                }}
              >
                Send
              </button>

              <button
                onClick={() => setShowCompose(false)}
                style={{
                  flex: 1,
                  padding: 12,
                  borderRadius: 10,
                  border: "none",
                  background: "#EF4444",
                  color: "white",
                  fontWeight: 700,
                  cursor: "pointer",
                }}
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
      {/* ✅ GROQ AI MODAL POPUP */}
      {showGroq && (
        <div
          style={{
            position: "fixed",
            top: 0,
            left: 0,
            width: "100%",
            height: "100%",
            background: "rgba(0,0,0,0.55)",
            display: "flex",
            justifyContent: "center",
            alignItems: "center",
            zIndex: 99999,
          }}
        >
          <div
            style={{
              width: 520,
              background: "white",
              padding: 24,
              borderRadius: 18,
              boxShadow: "0 20px 60px rgba(0,0,0,0.3)",
            }}
          >
            <h2 style={{ fontWeight: 800, fontSize: 18 }}>
              💎 Ask Groq AI
            </h2>

            {/* Question Input */}
            <textarea
              rows={4}
              value={groqQuestion}
              onChange={(e) => setGroqQuestion(e.target.value)}
              placeholder="Ask Groq about this email..."
              style={{
                width: "100%",
                padding: 12,
                borderRadius: 10,
                border: "1px solid #ddd",
                marginTop: 12,
              }}
            />

            {/* Ask Button */}
            <button
              onClick={askGroq}
              style={{
                marginTop: 14,
                width: "100%",
                padding: 12,
                borderRadius: 10,
                border: "none",
                background: "linear-gradient(135deg,#2563EB,#0EA5E9)",
                color: "white",
                fontWeight: 700,
                cursor: "pointer",
              }}
            >
              {loadingGroq ? "Thinking..." : "Ask Groq 💎"}
            </button>

            {/* Reply Output */}
            {groqReply && (
              <div
                style={{
                  marginTop: 14,
                  padding: 14,
                  background: "#F3F4F6",
                  borderRadius: 12,
                  fontSize: 14,
                  whiteSpace: "pre-wrap",
                  border: "1px solid #E5E7EB",
                }}
              >
                {groqReply}
              </div>
            )}

            {/* Close */}
            <button
              onClick={() => {
                setShowGroq(false);
                setGroqQuestion("");
                setGroqReply("");
              }}
              style={{
                marginTop: 14,
                width: "100%",
                padding: 12,
                borderRadius: 10,
                border: "none",
                background: "#EF4444",
                color: "white",
                fontWeight: 700,
                cursor: "pointer",
              }}
            >
              Close
            </button>
          </div>
        </div>
      )}



    </div>

  );
}
