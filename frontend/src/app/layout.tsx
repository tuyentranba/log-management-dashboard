import type { Metadata } from "next";
import Link from 'next/link'
import { Toaster } from "sonner";
import { Separator } from '@/components/ui/separator'
import "./globals.css";

export const metadata: Metadata = {
  title: "Logs Dashboard",
  description: "High-performance log management system",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>
        <Toaster position="top-right" richColors />
        <div className="flex min-h-screen">
          {/* Sidebar */}
          <aside className="w-60 border-r bg-slate-50 p-4">
            <nav className="space-y-2">
              <Link
                href="/logs"
                className="block px-4 py-2 rounded hover:bg-slate-200 transition-colors"
              >
                Logs
              </Link>
              <Link
                href="/create"
                className="block px-4 py-2 rounded hover:bg-slate-200 transition-colors"
              >
                Create Log
              </Link>
              <Separator className="my-2" />
              <div className="px-4 py-2 text-slate-400 text-sm">
                Dashboard (Phase 5)
              </div>
            </nav>
          </aside>

          {/* Main content */}
          <main className="flex-1">
            {children}
          </main>
        </div>
      </body>
    </html>
  );
}
