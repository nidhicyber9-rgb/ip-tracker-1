export default function DashboardHome() {
  return (
    <main className="page-shell">
      <section className="section">
        <div className="dashboard-hero">
          <div>
            <p className="eyebrow">Dashboard</p>
            <h1>Track links and review capture results.</h1>
            <p className="hero-text">This dashboard is a template shell for your tracking system. Add links, view details, and inspect capture results by ID.</p>
          </div>
          <div className="dashboard-summary">
            <div className="summary-card">
              <span>Active links</span>
              <strong>0</strong>
            </div>
            <div className="summary-card">
              <span>Recent captures</span>
              <strong>0</strong>
            </div>
          </div>
        </div>

        <div className="dashboard-grid">
          <div className="dashboard-panel">
            <h2>Tracking link template</h2>
            <p>Create a link and share it with a target. Data will appear in the capture results page.</p>
            <code>/dashboard/results/[id]</code>
          </div>
          <div className="dashboard-panel">
            <h2>Target landing page</h2>
            <p>The target visit page is served at <code>/t/[code]</code> and redirects to the final destination after capture.</p>
          </div>
        </div>
      </section>
    </main>
  );
}
