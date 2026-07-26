import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Sentinel Twin",
  description: "Next-Gen Autonomous BMS",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="dark">
      <body className="antialiased min-h-screen flex flex-col">
        <header className="glass-panel m-4 p-4 flex justify-between items-center sticky top-0 z-50">
          <div className="font-bold text-xl tracking-tight">
            Sentinel <span className="text-[var(--color-accent)]">Twin</span>
          </div>
          <nav className="flex gap-6 text-sm font-medium">
            <a href="/" className="hover:text-[var(--color-primary)] text-[var(--color-secondary)]">Dashboard</a>
            <a href="/ai" className="hover:text-[var(--color-primary)] text-[var(--color-secondary)]">AI Control</a>
            <a href="/analytics" className="hover:text-[var(--color-primary)] text-[var(--color-secondary)]">Analytics</a>
          </nav>
        </header>
        <main className="flex-1 px-4">
          {children}
        </main>
      </body>
    </html>
  );
}
