import { getServerSession } from "next-auth";
import { authOptions } from "../../auth/[...nextauth]/route";
import { google } from "googleapis";
import { NextResponse } from "next/server";

/* -----------------------------
   ✅ Decode Base64
-------------------------------- */
function decodeBase64(data: string) {
  return Buffer.from(
    data.replace(/-/g, "+").replace(/_/g, "/"),
    "base64"
  ).toString("utf-8");
}

/* -----------------------------
   ✅ Extract Full Body Recursively
-------------------------------- */
function extractBody(payload: any): string {
  if (!payload) return "";

  // ✅ Prefer HTML
  if (payload.parts) {
    for (const part of payload.parts) {
      if (part.mimeType === "text/html" && part.body?.data) {
        return decodeBase64(part.body.data);
      }
    }
  }

  // ✅ Fallback plain text
  if (payload.body?.data) {
    return decodeBase64(payload.body.data);
  }

  return "";
}

/* -----------------------------
   ✅ Extract Attachments Info Recursively
-------------------------------- */
function extractAttachments(payload: any): any[] {
  let files: any[] = [];

  if (!payload.parts) return files;

  for (const part of payload.parts) {
    // ✅ Attachment found
    if (part.filename && part.body?.attachmentId) {
      files.push({
        filename: part.filename,
        mimeType: part.mimeType,
        attachmentId: part.body.attachmentId,
      });
    }

    // ✅ Recursive nested search
    if (part.parts) {
      files = files.concat(extractAttachments(part));
    }
  }

  return files;
}

/* -----------------------------
   ✅ GET Single Gmail Message
-------------------------------- */
export async function GET(req: Request) {
  try {
    const session = await getServerSession(authOptions);

    if (!session) {
      return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
    }

    const { searchParams } = new URL(req.url);
    const id = searchParams.get("id");

    if (!id) {
      return NextResponse.json({ error: "Missing ID" }, { status: 400 });
    }

    // ✅ Google Auth
    const auth = new google.auth.OAuth2();
    auth.setCredentials({
      access_token: (session as any).accessToken,
    });

    const gmail = google.gmail({ version: "v1", auth });

    // ✅ Fetch Full Email
    const msg = await gmail.users.messages.get({
      userId: "me",
      id,
      format: "full",
    });
    const threadId = msg.data.threadId;
    const messageId =
      msg.data.payload?.headers?.find(
        (h: any) => h.name === "Message-ID"
      )?.value || "";

    // ✅ Headers
    const headers = msg.data.payload?.headers || [];

    const getHeader = (name: string) =>
      headers.find((h: any) => h.name === name)?.value || "";

    // ✅ Extract Body + Attachments
    const body = extractBody(msg.data.payload);
    const attachments = extractAttachments(msg.data.payload);

    // ✅ Return Response
    return NextResponse.json({
      id,
      threadId,        // ✅ ADD
      messageId,       // ✅ ADD

      subject: getHeader("Subject"),
      from: getHeader("From"),
      date: getHeader("Date"),

      body: extractBody(msg.data.payload),
      snippet: msg.data.snippet || "",

      attachments,
    });

  } catch (err: any) {
    return NextResponse.json(
      { error: err.message || "Something went wrong" },
      { status: 500 }
    );
  }
}
