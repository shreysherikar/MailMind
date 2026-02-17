import { NextResponse } from "next/server";

export async function POST(req: Request) {
    try {
        const { emailText, question } = await req.json();

        const apiKey = process.env.GROQ_API_KEY;

        if (!apiKey) {
            return NextResponse.json({ error: "Missing Groq API Key" });
        }

        const prompt = `
You are an AI assistant for emails.

EMAIL:
${emailText}

QUESTION:
${question}

Answer clearly:
`;

        const response = await fetch(
            "https://api.groq.com/openai/v1/chat/completions",
            {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "Authorization": `Bearer ${apiKey}`,
                },
                body: JSON.stringify({
                    model: "llama-3.3-70b-versatile",
                    messages: [
                        { role: "user", content: prompt },
                    ],
                    max_tokens: 1000,
                    temperature: 0.7,
                }),
            }
        );

        const data = await response.json();

        const reply =
            data?.choices?.[0]?.message?.content ||
            "No response from Groq";

        return NextResponse.json({ reply });
    } catch (err) {
        return NextResponse.json({ error: "Groq API Failed" });
    }
}
