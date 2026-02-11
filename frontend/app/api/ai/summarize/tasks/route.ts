import { NextResponse } from "next/server";

export async function POST(req: Request) {
  const { text } = await req.json();

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
${text}
`;

  const res = await fetch("https://api.openai.com/v1/chat/completions", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${process.env.OPENAI_API_KEY}`,
    },
    body: JSON.stringify({
      model: "gpt-4o-mini",
      messages: [{ role: "user", content: prompt }],
    }),
  });

  const data = await res.json();

  let output = data.choices?.[0]?.message?.content;

  try {
    output = JSON.parse(output);
  } catch {
    output = { tasks: [] };
  }

  return NextResponse.json(output);
}
