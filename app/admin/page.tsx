'use client';

import { useEffect, useState } from 'react';
import { supabase } from '@/lib/supabase';

export default function AdminDashboard() {
  const [stats, setStats] = useState({ users: 0, links: 0, captures: 0 });
  const [recentCaptures, setRecentCaptures] = useState<any[]>([]);

  useEffect(() => {
    loadStats();
  }, []);

  const loadStats = async () => {
    const { count: users } = await supabase.from('profiles').select('*', { count: 'exact', head: true });
    const { count: links } = await supabase.from('tracking_links').select('*', { count: 'exact', head: true });
    const { count: captures } = await supabase.from('captured_data').select('*', { count: 'exact', head: true });
    setStats({ users: users || 0, links: links || 0, captures: captures || 0 });

    const { data } = await supabase.from('captured_data').select('*, tracking_links(title)').order('captured_at', { ascending: false }).limit(20);
    if (data) setRecentCaptures(data);
  };

  return (
    <div>
      <h1 style={{ fontSize: '28px', fontWeight: 700, color: '#1a1a2e', marginBottom: '8px' }}>Admin Dashboard</h1>
      <p style={{ color: '#666', marginBottom: '30px' }}>Overview of all platform activity</p>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '20px', marginBottom: '30px' }}>
        {[
          { icon: '👥', label: 'Total Users', value: stats.users },
          { icon: '🔗', label: 'Total Links', value: stats.links },
          { icon: '📥', label: 'Total Captures', value: stats.captures },
        ].map((s) => (
          <div key={s.label} style={{ background: 'white', padding: '24px', borderRadius: '15px', boxShadow: '0 2px 10px rgba(0,0,0,0.05)' }}>
            <span style={{ fontSize: '32px' }}>{s.icon}</span>
            <p style={{ fontSize: '28px', fontWeight: 700, color: '#1a1a2e', marginTop: '8px' }}>{s.value}</p>
            <p style={{ color: '#666', fontSize: '13px' }}>{s.label}</p>
          </div>
        ))}
      </div>

      <div style={{ background: 'white', borderRadius: '15px', padding: '24px', boxShadow: '0 2px 10px rgba(0,0,0,0.05)' }}>
        <h2 style={{ fontSize: '18px', fontWeight: 600, color: '#1a1a2e', marginBottom: '20px' }}>Recent Captures Across All Users</h2>
        {recentCaptures.length === 0 ? (
          <p style={{ color: '#999', textAlign: 'center', padding: '30px' }}>No captures yet</p>
        ) : (
          <div style={{ overflowX: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse' }}>
              <thead>
                <tr>
                  <th style={{ textAlign: 'left', padding: '12px 16px', borderBottom: '2px solid #f0f2f5', color: '#666', fontSize: '13px', fontWeight: 600, textTransform: 'uppercase' }}>IP</th>
                  <th style={{ textAlign: 'left', padding: '12px 16px', borderBottom: '2px solid #f0f2f5', color: '#666', fontSize: '13px', fontWeight: 600, textTransform: 'uppercase' }}>Link</th>
                  <th style={{ textAlign: 'left', padding: '12px 16px', borderBottom: '2px solid #f0f2f5', color: '#666', fontSize: '13px', fontWeight: 600, textTransform: 'uppercase' }}>Location</th>
                  <th style={{ textAlign: 'left', padding: '12px 16px', borderBottom: '2px solid #f0f2f5', color: '#666', fontSize: '13px', fontWeight: 600, textTransform: 'uppercase' }}>Device</th>
                  <th style={{ textAlign: 'left', padding: '12px 16px', borderBottom: '2px solid #f0f2f5', color: '#666', fontSize: '13px', fontWeight: 600, textTransform: 'uppercase' }}>Time</th>
                </tr>
              </thead>
              <tbody>
                {recentCaptures.map((c) => (
                  <tr key={c.id} style={{ borderBottom: '1px solid #f0f2f5' }}>
                    <td style={{ padding: '12px 16px', fontSize: '14px' }}><code style={{ background: '#f0f2f5', padding: '3px 6px', borderRadius: '4px', fontSize: '12px' }}>{c.ip_address || 'N/A'}</code></td>
                    <td style={{ padding: '12px 16px', fontSize: '14px', color: '#444' }}>{c.tracking_links?.title || 'Unknown'}</td>
                    <td style={{ padding: '12px 16px', fontSize: '14px', color: '#444' }}>{[c.city, c.country].filter(Boolean).join(', ') || 'N/A'}</td>
                    <td style={{ padding: '12px 16px', fontSize: '14px', color: '#444' }}>{c.device_type || 'N/A'}</td>
                    <td style={{ padding: '12px 16px', fontSize: '14px', color: '#444' }}>{new Date(c.captured_at).toLocaleString()}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
