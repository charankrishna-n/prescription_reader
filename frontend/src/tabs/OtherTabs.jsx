// NotificationsTab.jsx
import { useState, useEffect } from 'react';
import { useAuth } from '../lib/AuthContext';
import { useData } from '../lib/DataContext';
import { Bell, AlertCircle } from 'lucide-react';
import './NotificationsTab.css';

export function NotificationsTab() {
  const { user } = useAuth();
  const { notifications, fetchNotifications } = useData();

  useEffect(() => {
    if (user) {
      fetchNotifications();
    }
  }, [user, fetchNotifications]);

  if (!user) return <div className="notifications-tab"><p>Please login first</p></div>;

  return (
    <div className="notifications-tab">
      <div className="notifications-container">
        <h2>Notifications</h2>
        {notifications.length === 0 ? (
          <div className="empty-state">
            <Bell className="empty-icon" />
            <p>No notifications</p>
          </div>
        ) : (
          <div className="notifications-list">
            {notifications.map((notif, idx) => (
              <div key={idx} className={`notification-item ${notif.type}`}>
                <div className="notif-icon">
                  {notif.type === 'pending' ? '⏰' : '❌'}
                </div>
                <div className="notif-content">
                  <h3>{notif.medicine_name}</h3>
                  <p>{notif.message}</p>
                  <span className="notif-time">{notif.time}</span>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

// AdherenceTab.jsx
export function AdherenceTab() {
  const { user } = useAuth();
  const { adherence, fetchAdherence } = useData();

  useEffect(() => {
    if (user) {
      fetchAdherence();
    }
  }, [user, fetchAdherence]);

  if (!user) return <div className="adherence-tab"><p>Please login first</p></div>;

  return (
    <div className="adherence-tab">
      <div className="adherence-container">
        <h2>Adherence Report</h2>
        {adherence ? (
          <div className="adherence-stats">
            <div className="stat-card">
              <div className="stat-value">{adherence.percentage}%</div>
              <div className="stat-label">Overall Adherence</div>
            </div>
            <div className="stat-card">
              <div className="stat-value">{adherence.total_medicines}</div>
              <div className="stat-label">Total Medicines</div>
            </div>
            <div className="stat-card">
              <div className="stat-value">{adherence.taken_medicines}</div>
              <div className="stat-label">Taken</div>
            </div>
            <div className="stat-card">
              <div className="stat-value">{adherence.missed_medicines}</div>
              <div className="stat-label">Missed</div>
            </div>
          </div>
        ) : (
          <div className="empty-state">
            <AlertCircle className="empty-icon" />
            <p>No adherence data available</p>
          </div>
        )}
      </div>
    </div>
  );
}

// DoctorPanelTab.jsx
export function DoctorPanelTab() {
  const { user, userType } = useAuth();
  const [patients, setPatients] = useState([]);

  if (!user || userType !== 'doctor') {
    return <div className="doctor-panel-tab"><p>Doctor access only</p></div>;
  }

  return (
    <div className="doctor-panel-tab">
      <div className="doctor-container">
        <h2>Patient Management</h2>
        <div className="patients-grid">
          {patients.length === 0 ? (
            <div className="empty-state">
              <AlertCircle className="empty-icon" />
              <p>No patients assigned</p>
            </div>
          ) : (
            patients.map((patient, idx) => (
              <div key={idx} className="patient-card">
                <h3>{patient.name}</h3>
                <p>{patient.email}</p>
                <div className="patient-stats">
                  <span>Adherence: {patient.adherence}%</span>
                  <span>Medicines: {patient.medicines}</span>
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}

// ProfileTab.jsx
export function ProfileTab() {
  const { user, logout } = useAuth();

  if (!user) return <div className="profile-tab"><p>Please login first</p></div>;

  return (
    <div className="profile-tab">
      <div className="profile-container">
        <div className="profile-card">
          <h2>Profile</h2>
          <div className="profile-info">
            <div className="info-item">
              <label>Email</label>
              <p>{user.email}</p>
            </div>
          </div>
          <button onClick={logout} className="logout-button">
            Logout
          </button>
        </div>
      </div>
    </div>
  );
}
