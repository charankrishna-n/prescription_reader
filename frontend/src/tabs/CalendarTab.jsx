import { useState, useEffect } from 'react';
import { useAuth } from '../lib/AuthContext';
import { useData } from '../lib/DataContext';
import { Calendar, Plus, AlertCircle, Loader, Trash2 } from 'lucide-react';
import './CalendarTab.css';

export default function CalendarTab() {
  const { user } = useAuth();
  const { medicines, calendarItems, fetchCalendar, addToCalendar, deleteFromCalendar, loading, error, clearError } = useData();
  const [selectedMedicine, setSelectedMedicine] = useState(null);
  const [currentMonth, setCurrentMonth] = useState(new Date());
  const [localError, setLocalError] = useState('');

  useEffect(() => {
    if (user) {
      fetchCalendar();
    }
  }, [user, fetchCalendar]);

  if (!user) {
    return <div className="calendar-tab"><p>Please login first</p></div>;
  }

  const handleAddToCalendar = async (medicine) => {
    try {
      setLocalError('');
      await addToCalendar(medicine);
      setSelectedMedicine(null);
    } catch (err) {
      console.error('Failed to add to calendar:', err);
      setLocalError('Failed to add medicine to calendar');
      setTimeout(() => setLocalError(''), 3000);
    }
  };

  const handleDeleteItem = async (itemId) => {
    try {
      await deleteFromCalendar(itemId);
    } catch (err) {
      console.error('Failed to delete:', err);
    }
  };

  const getDaysInMonth = (date) => {
    return new Date(date.getFullYear(), date.getMonth() + 1, 0).getDate();
  };

  const getFirstDayOfMonth = (date) => {
    return new Date(date.getFullYear(), date.getMonth(), 1).getDay();
  };

  const daysInMonth = getDaysInMonth(currentMonth);
  const firstDay = getFirstDayOfMonth(currentMonth);
  const days = [];

  for (let i = 0; i < firstDay; i++) {
    days.push(null);
  }

  for (let i = 1; i <= daysInMonth; i++) {
    days.push(i);
  }

  const getMedicinesForDate = (day) => {
    if (!day) return [];
    const dateStr = new Date(currentMonth.getFullYear(), currentMonth.getMonth(), day)
      .toISOString()
      .split('T')[0];
    return calendarItems.filter(item => item.date === dateStr);
  };

  return (
    <div className="calendar-tab">
      <div className="calendar-container">
        {/* Calendar */}
        <div className="calendar-section">
          <div className="calendar-header">
            <button onClick={() => setCurrentMonth(new Date(currentMonth.getFullYear(), currentMonth.getMonth() - 1))}>
              ←
            </button>
            <h2>
              {currentMonth.toLocaleString('default', { month: 'long', year: 'numeric' })}
            </h2>
            <button onClick={() => setCurrentMonth(new Date(currentMonth.getFullYear(), currentMonth.getMonth() + 1))}>
              →
            </button>
          </div>

          <div className="calendar-grid">
            {['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'].map(day => (
              <div key={day} className="calendar-day-header">
                {day}
              </div>
            ))}

            {days.map((day, index) => (
              <div key={index} className={`calendar-day ${day ? 'active' : 'empty'}`}>
                {day && (
                  <>
                    <div className="day-number">{day}</div>
                    <div className="day-medicines">
                      {getMedicinesForDate(day).map((item, idx) => (
                        <div key={idx} className="medicine-badge">
                          {item.medicine_name}
                        </div>
                      ))}
                    </div>
                  </>
                )}
              </div>
            ))}
          </div>
        </div>

        {/* Add to Calendar */}
        <div className="add-section">
          <h2>Add Medicine to Calendar</h2>

          {medicines.length === 0 ? (
            <div className="empty-state">
              <AlertCircle className="empty-icon" />
              <p>Upload a prescription first to add medicines to calendar</p>
            </div>
          ) : (
            <div className="medicines-list">
              {medicines.map((medicine, index) => (
                <div key={index} className="medicine-card">
                  <div className="medicine-info">
                    <h3>{medicine.name}</h3>
                    <p className="medicine-details">
                      {medicine.dosage} • {medicine.frequency} • {medicine.duration}
                    </p>
                  </div>
                  <button
                    onClick={() => handleAddToCalendar(medicine)}
                    disabled={loading}
                    className="add-btn"
                  >
                    {loading ? <Loader className="spinner" /> : <Plus className="icon" />}
                  </button>
                </div>
              ))}
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
        </div>
      </div>

      {/* Calendar Items List */}
      {calendarItems.length > 0 && (
        <div className="calendar-items">
          <h2>Scheduled Medicines</h2>
          <div className="items-list">
            {calendarItems.map((item, index) => (
              <div key={index} className="item-card">
                <div className="item-date">
                  <Calendar className="icon" />
                  <span>{new Date(item.date).toLocaleDateString()}</span>
                </div>
                <div className="item-info">
                  <h3>{item.medicine_name}</h3>
                  <p>{item.dosage} • {item.frequency}</p>
                </div>
                <button
                  onClick={() => handleDeleteItem(item.id)}
                  className="delete-btn"
                  title="Remove from calendar"
                >
                  <Trash2 size={16} />
                </button>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
