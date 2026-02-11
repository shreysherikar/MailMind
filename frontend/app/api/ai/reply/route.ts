import { NextResponse } from "next/server";
import Groq from "groq-sdk";

const groq = new Groq({
    apiKey: process.env.GROQ_API_KEY!,
});

export async function POST(req: Request) {
    try {
        const { subject, snippet } = await req.json();

        const chat = await groq.chat.completions.create({
            model: "llama-3.1-8b-instant",

            messages: [
                {
                    role: "system",
                    content:
                        "You are an email assistant. Write a short, polite, professional reply.",
                },
                {
                    role: "user",
                    content: `
Subject: ${subject}

Email Content:
${snippet}

Write a reply message:
          `,
                },
            ],
        });

        const replyText =
            chat.choices[0]?.message?.content || "No reply generated.";

        return NextResponse.json({
            reply: replyText,
        });
    } catch (err: any) {
        return NextResponse.json(
            { error: err.message },
            { status: 500 }
        );
    }
}
