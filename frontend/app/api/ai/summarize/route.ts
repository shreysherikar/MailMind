import { NextResponse } from "next/server";
import Groq from "groq-sdk";

export async function POST(req: Request) {
  try {
    const { subject, snippet, from, date } = await req.json();

    // ✅ Trim input to avoid token overload
    const safeSnippet = (snippet || "").slice(0, 2000);

    const groq = new Groq({
      apiKey: process.env.GROQ_API_KEY!,
    });

    const chatCompletion = await groq.chat.completions.create({
      model: "llama-3.1-8b-instant",

      messages: [
        {
          role: "user",
          content: `
You are an email assistant.

Summarize this email clearly in this format:

📩 From: ...
📅 Received Date: ...
⏳ Deadline: (if mentioned)
📌 Summary: (2-3 lines)

Email:

Subject: ${subject}
From: ${from}
Received: ${date}

Body:
${safeSnippet}
          `,
        },
      ],
    });

    return NextResponse.json({
      summary: chatCompletion.choices[0].message.content,
    });
  } catch (error) {
    console.error("SUMMARY ERROR:", error);

    // Handle Rate Limit
    if (error && typeof error === "object" && "status" in error && (error as { status: number }).status === 429) {
      return NextResponse.json(
        {
          summary:
            "⚠️ Groq rate limit reached. Please wait 1 minute and try again.",
        },
        { status: 429 }
      );
    }

    return NextResponse.json(
      { summary: "❌ Error generating summary" },
      { status: 500 }
    );
  }
}
