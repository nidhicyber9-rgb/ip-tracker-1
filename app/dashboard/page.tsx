export default function DashboardHome() {
  return (
    <main className="page-shell">
      <div className="card">
        <h1>Dashboard</h1>
        <p>Choose a tracking link from your dashboard or view captures by ID.</p>
        <p>This app includes the tracking target page at <code>/t/[code]</code> and capture results at <code>/dashboard/results/[id]</code>.</p>
      </div>
    </main>
  );
}
