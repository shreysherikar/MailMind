import { NextResponse } from "next/server";

export async function POST(req: Request) {
    try {
        const { emailText, question } = await req.json();

        const apiKey = process.env.GEMINI_API_KEY;

        if (!apiKey) {
            return NextResponse.json({ error: "Missing Gemini API Key" });
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
            `https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key=${apiKey}`,
            {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    contents: [
                        {
                            parts: [{ text: prompt }],
                        },
                    ],
                }),
            }
        );

        const data = await response.json();

        console.log("Gemini Response:", data);

        const reply =
            data?.candidates?.[0]?.content?.parts?.[0]?.text ||
            "❌ No response from Gemini";

        return NextResponse.json({ reply });
    } catch (err) {
        return NextResponse.json({ error: "Gemini API Failed" });
    }
}
