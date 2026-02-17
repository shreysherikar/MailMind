import "./globals.css";
import Providers from "./providers";

export const metadata = {
  title: "MailMind",
  description: "Where email meets intelligence",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="bg-[var(--bg)] text-[var(--text)]">
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
