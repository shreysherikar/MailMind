import { NextResponse } from "next/server";
import Groq from "groq-sdk";

export async function POST(req: Request) {
  const { text } = await req.json();

  const safeText = (text || "").slice(0, 2000);

  const prompt = `
Extract tasks and deadlines from this email.

Return JSON only in this format:

{
  "tasks": [
    {
      "task": "Submit resume",
      "deadline": "Tomorrow"
    }
  ]
}

Email:
${safeText}
`;

  try {
    const groq = new Groq({
      apiKey: process.env.GROQ_API_KEY!,
    });

    const chatCompletion = await groq.chat.completions.create({
      model: "llama-3.1-8b-instant",
      messages: [{ role: "user", content: prompt }],
    });

    let output: unknown = chatCompletion.choices[0].message.content;

    try {
      output = JSON.parse(output as string);
    } catch {
      output = { tasks: [] };
    }

    return NextResponse.json(output);
  } catch (error: unknown) {
    console.error("TASK EXTRACT ERROR:", error);

    if (error && typeof error === "object" && "status" in error && (error as { status: number }).status === 429) {
      return NextResponse.json({ tasks: [] }, { status: 429 });
    }

    return NextResponse.json({ tasks: [] }, { status: 500 });
  }
}
