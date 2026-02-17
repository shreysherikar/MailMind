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
                        "You are an email assistant. Give priority score from 1-100 and one short reason.",
                },
                {
                    role: "user",
                    content: `
Email Subject: ${subject}
Email Snippet: ${snippet}

Respond ONLY as JSON:

{
  "score": number,
  "reason": "string"
}
          `,
                },
            ],
        });

        const raw = chat.choices[0]?.message?.content || "";

        // Extract JSON safely
        const match = raw.match(/\{[\s\S]*\}/);

        if (!match) {
            return NextResponse.json({
                result: { score: 50, reason: "AI could not generate priority" },
            });
        }

        const parsed = JSON.parse(match[0]);

        return NextResponse.json({
            result: parsed,
        });

    } catch (err) {
        const message = err instanceof Error ? err.message : "Unknown error";
        console.log("Priority API Error:", message);

        return NextResponse.json(
            { error: message },
            { status: 500 }
        );
    }
}