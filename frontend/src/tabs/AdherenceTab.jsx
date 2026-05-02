import { useEffect } from 'react';
import { useAuth } from '../lib/AuthContext';
import { useData } from '../lib/DataContext';
import { AlertCircle } from 'lucide-react';
import './AdherenceTab.css';

export default function AdherenceTab() {
  const { user } = useAuth();
  const { adherence, fetchAdherence } = useData();

  useEffect(() => {
    if (user) {
      fetchAdherence();
    }
  }, [user, fetchAdherence]);

  if (!user) {
    return <div className="adherence-tab"><p>Please login first</p></div>;
  }

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
