import { useState, useEffect } from 'react';
import { useAuth } from '../lib/AuthContext';
import { AlertCircle } from 'lucide-react';
import './DoctorPanelTab.css';

export default function DoctorPanelTab() {
  const { user, userType } = useAuth();
  const [patients, setPatients] = useState([]);

  useEffect(() => {
    // Fetch patients from backend
    if (user && userType === 'doctor') {
      // TODO: Fetch from API
      setPatients([]);
    }
  }, [user, userType]);

  if (!user || userType !== 'doctor') {
    return (
      <div className="doctor-panel-tab">
        <div className="access-denied">
          <AlertCircle className="icon" />
          <p>Doctor access only</p>
        </div>
      </div>
    );
  }

  return (
    <div className="doctor-panel-tab">
      <div className="doctor-container">
        <h2>Patient Management</h2>
        {patients.length === 0 ? (
          <div className="empty-state">
            <AlertCircle className="empty-icon" />
            <p>No patients assigned</p>
          </div>
        ) : (
          <div className="patients-grid">
            {patients.map((patient, idx) => (
              <div key={idx} className="patient-card">
                <h3>{patient.name}</h3>
                <p className="patient-email">{patient.email}</p>
                <div className="patient-stats">
                  <div className="stat">
                    <span className="label">Adherence</span>
                    <span className="value">{patient.adherence}%</span>
                  </div>
                  <div className="stat">
                    <span className="label">Medicines</span>
                    <span className="value">{patient.medicines}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
