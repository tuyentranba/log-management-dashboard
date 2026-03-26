import type { Metadata } from "next";
import Link from 'next/link'
import { Toaster } from "sonner";
import { Separator } from '@/components/ui/separator'
import { NuqsAdapter } from 'nuqs/adapters/next/app'
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
        <NuqsAdapter>
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
                  href="/analytics"
                  className="block px-4 py-2 rounded hover:bg-slate-200 transition-colors"
                >
                  Analytics
                </Link>
              </nav>
            </aside>

            {/* Main content */}
            <main className="flex-1">
              {children}
            </main>
          </div>
        </NuqsAdapter>
      </body>
    </html>
  );
}
