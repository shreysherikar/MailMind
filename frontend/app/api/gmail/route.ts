import { getServerSession } from "next-auth";
import { authOptions } from "../auth/[...nextauth]/route";
import { google } from "googleapis";
import { NextResponse } from "next/server";

export async function GET(req: Request) {
  try {
    const session = await getServerSession(authOptions);

    if (!session || !session.accessToken) {
      return NextResponse.json({ emails: [], nextPageToken: null });
    }

    const { searchParams } = new URL(req.url);
    const pageToken = searchParams.get("pageToken") || undefined;

    const auth = new google.auth.OAuth2();
    auth.setCredentials({
      access_token: session.accessToken,
    });

    const gmail = google.gmail({ version: "v1", auth });

    // Step 1: Fetch Inbox Message IDs
    const listRes = await gmail.users.messages.list({
      userId: "me",
      maxResults: 20,
      pageToken,
    });

    const messages = listRes.data.messages || [];

    // Step 2: Fetch Metadata for Each Email
    const emails = await Promise.all(
      messages.map(async (m) => {
        const msg = await gmail.users.messages.get({
          userId: "me",
          id: m.id!,
          format: "metadata",
          metadataHeaders: ["Subject", "From", "Date"],
        });

        const headers = msg.data.payload?.headers || [];

          const get = (name: string) =>
            headers.find((h) => h.name === name)?.value || "";

        return {
          id: m.id,

          subject: get("Subject"),
          from: get("From"),

          // ✅ FIX 1: Always provide a valid date
          date: get("Date") || new Date().toISOString(),

          // ✅ FIX 2: Snippet should never be undefined
          snippet: msg.data.snippet || "",
        };
      })
    );

    // Step 3: Return Inbox Emails
    return NextResponse.json({
      emails,
      nextPageToken: listRes.data.nextPageToken || null,
    });
  } catch (err) {
    return NextResponse.json({
      emails: [],
      nextPageToken: null,
      error: err instanceof Error ? err.message : "Unknown error",
    });
  }
}
