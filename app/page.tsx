import Link from 'next/link';

export default function HomePage() {
  return (
    <main className="page-shell">
      <div className="card">
        <h1>IP Tracker</h1>
        <p>Admin dashboard and tracking pages for your Supabase-powered tracker.</p>
        <div className="button-group">
          <Link href="/login" className="button">Login</Link>
          <Link href="/dashboard" className="button button-secondary">Dashboard</Link>
          <Link href="/admin" className="button button-secondary">Admin</Link>
        </div>
      </div>
    </main>
  );
}
