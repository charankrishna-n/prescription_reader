import { useState } from 'react';
import { useAuth } from '../lib/AuthContext';
import { authAPI } from '../lib/api';
import { Mail, Lock, AlertCircle, Loader } from 'lucide-react';
import './LoginTab.css';

export default function LoginTab() {
  const { user, login } = useAuth();
  const [mode, setMode] = useState('user');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const response = mode === 'user'
        ? await authAPI.login(email, password)
        : await authAPI.doctorLogin(email, password);

      const { token, email: userEmail } = response.data;
      localStorage.setItem('token', token);
      login({ email: userEmail }, mode);
    } catch (err) {
      setError(err.response?.data?.detail || 'Login failed');
    } finally {
      setLoading(false);
    }
  };

  if (user) {
    return (
      <div className="login-success">
        <div className="success-card">
          <h2>Welcome, {user.email}!</h2>
          <p>You are logged in as {mode === 'doctor' ? 'Doctor' : 'Patient'}</p>
          <p className="info-text">Navigate to other tabs to continue</p>
        </div>
      </div>
    );
  }

  return (
    <div className="login-tab">
      <div className="login-container">
        <div className="login-card">
          <h2>Login</h2>

          <div className="mode-selector">
            <button
              className={`mode-btn ${mode === 'user' ? 'active' : ''}`}
              onClick={() => setMode('user')}
            >
              Patient
            </button>
            <button
              className={`mode-btn ${mode === 'doctor' ? 'active' : ''}`}
              onClick={() => setMode('doctor')}
            >
              Doctor
            </button>
          </div>

          <form onSubmit={handleSubmit} className="login-form">
            <div className="form-group">
              <label>Email</label>
              <div className="input-wrapper">
                <Mail className="input-icon" />
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder={mode === 'user' ? 'test@example.com' : 'doctor@example.com'}
                  required
                />
              </div>
            </div>

            <div className="form-group">
              <label>Password</label>
              <div className="input-wrapper">
                <Lock className="input-icon" />
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••"
                  required
                />
              </div>
            </div>

            {error && (
              <div className="error-message">
                <AlertCircle className="error-icon" />
                <span>{error}</span>
              </div>
            )}

            <button type="submit" disabled={loading} className="login-button">
              {loading ? (
                <>
                  <Loader className="spinner" />
                  Logging in...
                </>
              ) : (
                'Login'
              )}
            </button>
          </form>

          <div className="demo-hint">
            <p><strong>Demo Credentials:</strong></p>
            <p>Patient: test@example.com / password123</p>
            <p>Doctor: doctor@example.com / password123</p>
          </div>
        </div>
      </div>
    </div>
  );
}
