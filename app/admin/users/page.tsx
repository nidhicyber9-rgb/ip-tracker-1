'use client';

import { useEffect, useState } from 'react';
import { supabase } from '@/lib/supabase';

export default function AdminUsers() {
  const [users, setUsers] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadUsers();
  }, []);

  const loadUsers = async () => {
    const { data } = await supabase
      .from('profiles')
      .select('*')
      .order('created_at', { ascending: false });
    if (data) setUsers(data);
    setLoading(false);
  };

  if (loading) return <div style={{ textAlign: 'center', padding: '50px', color: '#999' }}>Loading...</div>;

  return (
    <div>
      <h1 style={{ fontSize: '28px', fontWeight: 700, color: '#1a1a2e', marginBottom: '8px' }}>User Management</h1>
      <p style={{ color: '#666', marginBottom: '30px' }}>View all registered users</p>

      <div style={{ background: 'white', borderRadius: '15px', padding: '24px', boxShadow: '0 2px 10px rgba(0,0,0,0.05)' }}>
        <div style={{ overflowX: 'auto' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse' }}>
            <thead>
              <tr>
                <th style={{ textAlign: 'left', padding: '12px 16px', borderBottom: '2px solid #f0f2f5', color: '#666', fontSize: '13px', fontWeight: 600, textTransform: 'uppercase' }}>Email</th>
                <th style={{ textAlign: 'left', padding: '12px 16px', borderBottom: '2px solid #f0f2f5', color: '#666', fontSize: '13px', fontWeight: 600, textTransform: 'uppercase' }}>Role</th>
                <th style={{ textAlign: 'left', padding: '12px 16px', borderBottom: '2px solid #f0f2f5', color: '#666', fontSize: '13px', fontWeight: 600, textTransform: 'uppercase' }}>Name</th>
                <th style={{ textAlign: 'left', padding: '12px 16px', borderBottom: '2px solid #f0f2f5', color: '#666', fontSize: '13px', fontWeight: 600, textTransform: 'uppercase' }}>Joined</th>
              </tr>
            </thead>
            <tbody>
              {users.map((user) => (
                <tr key={user.id} style={{ borderBottom: '1px solid #f0f2f5' }}>
                  <td style={{ padding: '12px 16px', fontSize: '14px', color: '#444' }}>{user.email}</td>
                  <td style={{ padding: '12px 16px' }}>
                    <span style={{
                      padding: '4px 12px', borderRadius: '20px',
                      background: user.role === 'admin' ? '#667eea' : '#22c55e',
                      color: 'white', fontSize: '12px', fontWeight: 600,
                    }}>
                      {user.role}
                    </span>
                  </td>
                  <td style={{ padding: '12px 16px', fontSize: '14px', color: '#444' }}>{user.full_name || 'N/A'}</td>
                  <td style={{ padding: '12px 16px', fontSize: '14px', color: '#444' }}>{new Date(user.created_at).toLocaleDateString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
