import { NextResponse } from "next/server";
import Groq from "groq-sdk";

export async function POST(req: Request) {
  try {
    const { subject, snippet } = await req.json();

    // ✅ Trim input
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
Explain why this email is important in 2-3 bullet points.

Subject: ${subject}

Body:
${safeSnippet}
          `,
        },
      ],
    });

    return NextResponse.json({
      explanation: chatCompletion.choices[0].message.content,
    });
  } catch (error: any) {
    console.error("EXPLAIN ERROR:", error);

    if (error?.status === 429) {
      return NextResponse.json(
        {
          explanation:
            "⚠️ Rate limit reached. Please wait 1 minute before retrying.",
        },
        { status: 429 }
      );
    }

    return NextResponse.json(
      { explanation: "❌ Error generating explanation" },
      { status: 500 }
    );
  }
}
