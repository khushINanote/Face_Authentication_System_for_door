import React, { useState, useRef, useCallback } from 'react';
import Webcam from 'react-webcam';
import axios from 'axios';
import { Camera, ShieldCheck, UserPlus, Fingerprint, RefreshCcw, Loader2 } from 'lucide-react';

const API_BASE = 'http://localhost:5000';

function App() {
  const webcamRef = useRef(null);
  const [userId, setUserId] = useState('');
  const [status, setStatus] = useState('idle'); // idle, processing, success, error
  const [message, setMessage] = useState('Position your face in the frame');
  const [result, setResult] = useState(null);

  const capture = useCallback(() => {
    return webcamRef.current.getScreenshot();
  }, [webcamRef]);

  const handleRegister = async () => {
    if (!userId) {
      setStatus('error');
      setMessage('Please enter a User ID');
      return;
    }

    setStatus('processing');
    setMessage('Capturing and registering...');

    const imageSrc = capture();
    try {
      const res = await axios.post(`${API_BASE}/register`, {
        userId,
        image: imageSrc
      });
      setStatus('success');
      setMessage(res.data.message);
    } catch (err) {
      setStatus('error');
      setMessage(err.response?.data?.error || 'Registration failed');
    }
  };

  const handleAuthenticate = async () => {
    setStatus('processing');
    setMessage('Verifying identity and liveness...');
    setResult(null);

    const imageSrc = capture();
    try {
      const res = await axios.post(`${API_BASE}/authenticate`, {
        image: imageSrc
      });
      
      if (res.data.status === 'success') {
        setStatus('success');
        setMessage('Authentication Successful');
        setResult(res.data);
      } else {
        setStatus('error');
        setMessage(res.data.reason || 'Authentication Failed');
      }
    } catch (err) {
      setStatus('error');
      setMessage('Server error during authentication');
    }
  };

  const reset = () => {
    setStatus('idle');
    setMessage('Position your face in the frame');
    setResult(null);
  };

  return (
    <div className="app-container">
      <header>
        <h1>SECURE AUTH</h1>
        <p className="subtitle">Advanced Face Authentication with Anti-Spoofing</p>
      </header>

      <div className="main-grid">
        <div className="camera-panel">
          <div className="camera-feed">
            <Webcam
              audio={false}
              ref={webcamRef}
              screenshotFormat="image/jpeg"
              videoConstraints={{ width: 1280, height: 720, facingMode: 'user' }}
              style={{ width: '100%', height: '100%', objectFit: 'cover', borderRadius: '16px' }}
            />
            {status === 'processing' && <div className="scan-line"></div>}
          </div>
          
          <div style={{ marginTop: '1.5rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <div className={`status-badge status-${status}`}>
              {status === 'processing' && <Loader2 className="animate-spin" size={16} />}
              {status === 'success' && <ShieldCheck size={16} />}
              {status === 'error' && <RefreshCcw size={16} />}
              {status}
            </div>
            <p style={{ fontSize: '0.9rem', color: 'var(--text-secondary)' }}>{message}</p>
          </div>
        </div>

        <div className="controls">
          <div className="input-group">
            <label style={{ display: 'block', marginBottom: '0.5rem', fontSize: '0.9rem', color: 'var(--text-secondary)' }}>User ID</label>
            <input 
              type="text" 
              placeholder="e.g. john_doe" 
              value={userId}
              onChange={(e) => setUserId(e.target.value)}
            />
          </div>

          <button className="btn btn-primary" onClick={handleRegister} disabled={status === 'processing'}>
            <UserPlus size={20} />
            Register Face
          </button>

          <div style={{ height: '1px', background: 'var(--glass-border)', margin: '0.5rem 0' }}></div>

          <button className="btn btn-primary" style={{ background: 'linear-gradient(135deg, var(--accent-secondary), #a855f7)' }} onClick={handleAuthenticate} disabled={status === 'processing'}>
            <Fingerprint size={20} />
            Authenticate
          </button>

          <button className="btn btn-secondary" onClick={reset}>
            <RefreshCcw size={20} />
            Reset
          </button>

          {result && (
            <div style={{ marginTop: '1rem', padding: '1rem', background: 'rgba(16, 185, 129, 0.1)', borderRadius: '12px', border: '1px solid rgba(16, 185, 129, 0.2)' }}>
              <p style={{ color: 'var(--success)', fontWeight: '600' }}>Welcome, {result.identity}!</p>
              <p style={{ fontSize: '0.8rem', color: 'rgba(16, 185, 129, 0.7)' }}>Confidence: {(100 * (1 - result.distance)).toFixed(2)}%</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default App;
