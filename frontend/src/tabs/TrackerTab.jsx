import { useState, useEffect } from 'react';
import { useAuth } from '../lib/AuthContext';
import { useData } from '../lib/DataContext';
import { CheckCircle2, Circle, AlertCircle, Loader, Plus, Trash2 } from 'lucide-react';
import './TrackerTab.css';

export default function TrackerTab() {
  const { user } = useAuth();
  const { medicines, trackerItems, fetchTracker, addToTracker, updateTrackerItem, deleteFromTracker, loading, error } = useData();
  const [localError, setLocalError] = useState('');

  useEffect(() => {
    if (user) {
      fetchTracker();
    }
  }, [user, fetchTracker]);

  if (!user) {
    return <div className="tracker-tab"><p>Please login first</p></div>;
  }

  const handleToggle = async (itemId, currentStatus) => {
    try {
      await updateTrackerItem(itemId, !currentStatus);
    } catch (err) {
      console.error('Failed to update tracker:', err);
    }
  };

  const handleAddToTracker = async (medicine) => {
    try {
      setLocalError('');
      await addToTracker(medicine);
    } catch (err) {
      console.error('Failed to add to tracker:', err);
      setLocalError('Failed to add medicine to tracker');
      setTimeout(() => setLocalError(''), 3000);
    }
  };

  const handleDeleteItem = async (itemId) => {
    try {
      await deleteFromTracker(itemId);
    } catch (err) {
      console.error('Failed to delete:', err);
    }
  };

  const todayItems = trackerItems.filter(item => {
    const itemDate = new Date(item.date).toDateString();
    const today = new Date().toDateString();
    return itemDate === today;
  });

  const takenCount = todayItems.filter(item => item.taken).length;
  const totalCount = todayItems.length;
  const percentage = totalCount > 0 ? Math.round((takenCount / totalCount) * 100) : 0;

  return (
    <div className="tracker-tab">
      <div className="tracker-container">
        {/* Stats */}
        <div className="stats-section">
          <div className="stat-card">
            <div className="stat-value">{totalCount}</div>
            <div className="stat-label">Today's Medicines</div>
          </div>
          <div className="stat-card">
            <div className="stat-value">{takenCount}</div>
            <div className="stat-label">Taken</div>
          </div>
          <div className="stat-card">
            <div className="stat-value">{percentage}%</div>
            <div className="stat-label">Adherence</div>
          </div>
        </div>

        {/* Progress Bar */}
        {totalCount > 0 && (
          <div className="progress-section">
            <div className="progress-bar">
              <div className="progress-fill" style={{ width: `${percentage}%` }}></div>
            </div>
            <p className="progress-text">{takenCount} of {totalCount} medicines taken</p>
          </div>
        )}

        {/* Tracker Items */}
        {todayItems.length === 0 ? (
          <div className="empty-state">
            <AlertCircle className="empty-icon" />
            <p>No medicines scheduled for today</p>
          </div>
        ) : (
          <div className="items-section">
            <h2>Today's Schedule</h2>
            <div className="items-list">
              {todayItems.map((item) => (
                <div key={item.id} className={`tracker-item ${item.taken ? 'taken' : ''}`}>
                  <button
                    onClick={() => handleToggle(item.id, item.taken)}
                    disabled={loading}
                    className="toggle-btn"
                  >
                    {loading ? (
                      <Loader className="spinner" />
                    ) : item.taken ? (
                      <CheckCircle2 className="icon checked" />
                    ) : (
                      <Circle className="icon" />
                    )}
                  </button>
                  <div className="item-info">
                    <h3>{item.medicine_name}</h3>
                    <p className="item-details">
                      {item.dosage} • {item.frequency}
                    </p>
                  </div>
                  <div className="item-time">
                    {item.time || 'No time set'}
                  </div>
                  <button
                    onClick={() => handleDeleteItem(item.id)}
                    className="delete-btn"
                    title="Remove from tracker"
                  >
                    <Trash2 size={16} />
                  </button>
                </div>
              ))}
            </div>
          </div>
        )}

        {error && (
          <div className="error-message">
            <AlertCircle className="error-icon" />
            <span>{error}</span>
          </div>
        )}

        {localError && (
          <div className="error-message">
            <AlertCircle className="error-icon" />
            <span>{localError}</span>
          </div>
        )}

        {medicines.length > 0 && (
          <div className="add-medicines-section">
            <h2>Add Medicines to Tracker</h2>
            <div className="medicines-list">
              {medicines.map((medicine, index) => (
                <div key={index} className="medicine-card">
                  <div className="medicine-info">
                    <h3>{medicine.name}</h3>
                    <p className="medicine-details">
                      {medicine.dosage} • {medicine.frequency}
                    </p>
                  </div>
                  <button
                    onClick={() => handleAddToTracker(medicine)}
                    disabled={loading}
                    className="add-btn"
                  >
                    {loading ? <Loader className="spinner" /> : <Plus className="icon" />}
                  </button>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
