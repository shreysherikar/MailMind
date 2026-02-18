import { NextResponse } from "next/server";
import { google } from "googleapis";
import { getServerSession } from "next-auth";
import { authOptions } from "../../auth/[...nextauth]/route";

/* -----------------------------
   ✅ Base64 Encode Helper
-------------------------------- */
function encodeBase64(str: string) {
    return Buffer.from(str)
        .toString("base64")
        .replace(/\+/g, "-")
        .replace(/\//g, "_")
        .replace(/=+$/, "");
}

/* -----------------------------
   ✅ POST: Send Gmail Reply
-------------------------------- */
export async function POST(req: Request) {
    try {
        // ✅ Session Check
        const session = await getServerSession(authOptions);

        if (!session) {
            return NextResponse.json(
                { error: "Unauthorized" },
                { status: 401 }
            );
        }

        // ✅ Frontend Data
        const { to, subject, body, threadId, originalMessageId } =
            await req.json();

        // ✅ Validation
        if (!to) {
            return NextResponse.json(
                { error: "Recipient address required" },
                { status: 400 }
            );
        }

        if (!body) {
            return NextResponse.json(
                { error: "Email body is required" },
                { status: 400 }
            );
        }

        // ✅ OAuth Setup
        const auth = new google.auth.OAuth2();
        auth.setCredentials({
            access_token: session.accessToken,
        });

        const gmail = google.gmail({ version: "v1", auth });

        /* -----------------------------
           ✅ Proper Reply Headers
        -------------------------------- */
        const rawMessage = [
            `To: ${to}`,
            `Subject: Re: ${subject}`,
            `In-Reply-To: <${originalMessageId}>`,
            `References: <${originalMessageId}>`,
            "",
            body,
        ].join("\n");

        // ✅ Encode Message
        const encodedMessage = encodeBase64(rawMessage);

        // ✅ Send Reply
        const sent = await gmail.users.messages.send({
            userId: "me",
            requestBody: {
                raw: encodedMessage,
                threadId: threadId,
            },
        });

        console.log("✅ Reply Sent To:", to);

        return NextResponse.json({
            success: true,
            sent,
        });
    } catch (err) {
        console.log("Reply Error:", err instanceof Error ? err.message : err);

        return NextResponse.json(
            { error: err instanceof Error ? err.message : "Unknown error" },
            { status: 500 }
        );
    }
}
