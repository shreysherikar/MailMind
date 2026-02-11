import { getServerSession } from "next-auth";
import { authOptions } from "../../auth/[...nextauth]/route";
import { google } from "googleapis";
import { NextResponse } from "next/server";

/* -----------------------------
   ✅ GET Attachment Download
-------------------------------- */
export async function GET(req: Request) {
    try {
        const session = await getServerSession(authOptions);

        if (!session) {
            return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
        }

        const { searchParams } = new URL(req.url);

        // Message ID
        const id = searchParams.get("id");

        // Attachment ID
        const att = searchParams.get("att");

        if (!id || !att) {
            return NextResponse.json(
                { error: "Missing id or attachmentId" },
                { status: 400 }
            );
        }

        // ✅ Google Auth
        const auth = new google.auth.OAuth2();
        auth.setCredentials({
            access_token: (session as any).accessToken,
        });

        const gmail = google.gmail({ version: "v1", auth });

        // ✅ Fetch Attachment Data
        const attachmentRes = await gmail.users.messages.attachments.get({
            userId: "me",
            messageId: id,
            id: att,
        });

        const data = attachmentRes.data.data;

        if (!data) {
            return NextResponse.json(
                { error: "Attachment not found" },
                { status: 404 }
            );
        }

        // Gmail sends Base64 URL-safe string
        const fileBuffer = Buffer.from(
            data.replace(/-/g, "+").replace(/_/g, "/"),
            "base64"
        );

        // ✅ Return File as Download
        const mimeType = searchParams.get("mime") || "application/octet-stream";

        return new NextResponse(fileBuffer, {
            headers: {
                "Content-Type": mimeType,
            },
        });

    } catch (err: any) {
        return NextResponse.json(
            { error: err.message || "Failed to download attachment" },
            { status: 500 }
        );
    }
}
