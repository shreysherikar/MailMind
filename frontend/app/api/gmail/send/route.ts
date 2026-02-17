import { getServerSession } from "next-auth";
import { authOptions } from "../../auth/[...nextauth]/route";
import { google } from "googleapis";
import { NextResponse } from "next/server";

function makeEmail(to: string, subject: string, message: string) {
    const emailLines = [
        `To: ${to}`,
        `Subject: Re: ${subject}`,
        "Content-Type: text/plain; charset=utf-8",
        "",
        message,
    ];

    return Buffer.from(emailLines.join("\n"))
        .toString("base64")
        .replace(/\+/g, "-")
        .replace(/\//g, "_")
        .replace(/=+$/, "");
}

export async function POST(req: Request) {
    try {
        const session = await getServerSession(authOptions);

        if (!session || !session.accessToken) {
            return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
        }

        const { to, subject, body } = await req.json();

        const auth = new google.auth.OAuth2();
        auth.setCredentials({
            access_token: session.accessToken,
        });

        const gmail = google.gmail({ version: "v1", auth });

        const rawMessage = makeEmail(to, subject, body);

        await gmail.users.messages.send({
            userId: "me",
            requestBody: {
                raw: rawMessage,
            },
        });

        return NextResponse.json({ success: true });
    } catch (err) {
        console.log("Send Email Error:", err instanceof Error ? err.message : err);
        return NextResponse.json({ error: err instanceof Error ? err.message : "Unknown error" }, { status: 500 });
    }
}
