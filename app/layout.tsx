import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'IP Tracker',
  description: 'IP Tracker dashboard and target page',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
