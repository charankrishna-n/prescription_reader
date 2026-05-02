import { useState, useEffect } from 'react';
import { useAuth } from '../lib/AuthContext';
import { useData } from '../lib/DataContext';
import { Bell, AlertCircle, Trash2, Plus, Clock, Volume2 } from 'lucide-react';
import './NotificationsTab.css';

export default function NotificationsTab() {
  const { user } = useAuth();
  const { notifications, fetchNotifications, deleteNotification } = useData();
  const [showAddForm, setShowAddForm] = useState(false);
  const [formData, setFormData] = useState({
    medicine_name: '',
    alarm_time: '09:00',
    frequency: 'Daily'
  });
  const [activeAlarms, setActiveAlarms] = useState({});
  const [currentTime, setCurrentTime] = useState(new Date());

  useEffect(() => {
    if (user) {
      fetchNotifications();
    }
  }, [user, fetchNotifications]);

  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentTime(new Date());
      checkAlarms();
    }, 1000);
    return () => clearInterval(interval);
  }, [notifications]);

  const checkAlarms = () => {
    const now = new Date();
    const currentTimeStr = `${String(now.getHours()).padStart(2, '0')}:${String(now.getMinutes()).padStart(2, '0')}`;

    notifications.forEach(notif => {
      const alarmTime = notif.alarm_time || notif.time;
      if (alarmTime === currentTimeStr && !activeAlarms[notif.id]) {
        triggerAlarm(notif);
        setActiveAlarms(prev => ({ ...prev, [notif.id]: true }));
        setTimeout(() => {
          setActiveAlarms(prev => ({ ...prev, [notif.id]: false }));
        }, 60000);
      }
    });
  };

  const triggerAlarm = (notif) => {
    playAlarmSound();
    showBrowserNotification(notif);
  };

  const playAlarmSound = () => {
    try {
      const audioContext = new (window.AudioContext || window.webkitAudioContext)();
      const oscillator = audioContext.createOscillator();
      const gainNode = audioContext.createGain();
      
      oscillator.connect(gainNode);
      gainNode.connect(audioContext.destination);
      
      oscillator.frequency.value = 800;
      oscillator.type = 'sine';
      
      gainNode.gain.setValueAtTime(0.3, audioContext.currentTime);
      gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 2);
      
      oscillator.start(audioContext.currentTime);
      oscillator.stop(audioContext.currentTime + 2);
    } catch (err) {
      console.error('Audio error:', err);
    }
  };

  const showBrowserNotification = (notif) => {
    if ('Notification' in window && Notification.permission === 'granted') {
      new Notification(`Time to take ${notif.medicine_name}!`, {
        body: `Frequency: ${notif.frequency}`,
        icon: '💊'
      });
    }
  };

  if (!user) {
    return <div className="notifications-tab"><p>Please login first</p></div>;
  }

  const handleDeleteNotification = async (itemId) => {
    try {
      await deleteNotification(itemId);
    } catch (err) {
      console.error('Failed to delete notification:', err);
    }
  };

  const handleAddNotification = async () => {
    if (!formData.medicine_name.trim()) {
      alert('Please enter medicine name');
      return;
    }
    try {
      const response = await fetch('http://localhost:8000/api/notifications', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({
          medicine_name: formData.medicine_name,
          alarm_time: formData.alarm_time,
          frequency: formData.frequency,
          message: `Take ${formData.medicine_name} at ${formData.alarm_time}`,
          time: formData.alarm_time
        })
      });
      await fetchNotifications();
      setFormData({ medicine_name: '', alarm_time: '09:00', frequency: 'Daily' });
      setShowAddForm(false);
      
      if ('Notification' in window && Notification.permission !== 'granted') {
        Notification.requestPermission();
      }
    } catch (err) {
      console.error('Failed to add notification:', err);
    }
  };

  const getTimeUntilAlarm = (alarmTime) => {
    const now = new Date();
    const [hours, minutes] = alarmTime.split(':').map(Number);
    let alarmDate = new Date();
    alarmDate.setHours(hours, minutes, 0);
    
    if (alarmDate < now) {
      alarmDate.setDate(alarmDate.getDate() + 1);
    }
    
    const diff = alarmDate - now;
    const hoursLeft = Math.floor(diff / (1000 * 60 * 60));
    const minutesLeft = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
    
    return `${hoursLeft}h ${minutesLeft}m`;
  };

  return (
    <div className="notifications-tab">
      <div className="notifications-container">
        <div className="notifications-header">
          <h2>Medicine Alarms</h2>
          <button 
            onClick={() => setShowAddForm(!showAddForm)}
            className="add-notification-btn"
          >
            <Plus size={18} />
            Set Alarm
          </button>
        </div>

        {showAddForm && (
          <div className="add-notification-form">
            <div className="form-group">
              <label>Medicine Name</label>
              <input
                type="text"
                placeholder="Enter medicine name"
                value={formData.medicine_name}
                onChange={(e) => setFormData({...formData, medicine_name: e.target.value})}
                className="form-input"
              />
            </div>
            <div className="form-row">
              <div className="form-group">
                <label>Alarm Time</label>
                <div className="time-input-wrapper">
                  <Clock size={18} />
                  <input
                    type="time"
                    value={formData.alarm_time}
                    onChange={(e) => setFormData({...formData, alarm_time: e.target.value})}
                    className="form-input"
                  />
                </div>
              </div>
              <div className="form-group">
                <label>Frequency</label>
                <select
                  value={formData.frequency}
                  onChange={(e) => setFormData({...formData, frequency: e.target.value})}
                  className="form-input"
                >
                  <option value="Daily">Daily</option>
                  <option value="Twice Daily">Twice Daily</option>
                  <option value="Thrice Daily">Thrice Daily</option>
                  <option value="Weekly">Weekly</option>
                  <option value="As Needed">As Needed</option>
                </select>
              </div>
            </div>
            <div className="form-actions">
              <button onClick={handleAddNotification} className="save-btn">Set Alarm</button>
              <button onClick={() => setShowAddForm(false)} className="cancel-btn">Cancel</button>
            </div>
          </div>
        )}

        {notifications.length === 0 ? (
          <div className="empty-state">
            <Bell className="empty-icon" />
            <p>No alarms set</p>
            <span>Set medicine alarms to get reminders</span>
          </div>
        ) : (
          <div className="notifications-list">
            {notifications.map((notif, idx) => (
              <div key={idx} className={`notification-item ${activeAlarms[notif.id] ? 'active' : ''}`}>
                <div className="notif-icon">
                  <Clock size={24} />
                </div>
                <div className="notif-content">
                  <h3>{notif.medicine_name}</h3>
                  <div className="notif-meta">
                    <span className="notif-time">
                      <Clock size={14} />
                      {notif.alarm_time || notif.time}
                    </span>
                    <span className="notif-frequency">{notif.frequency}</span>
                    <span className="time-until">
                      In {getTimeUntilAlarm(notif.alarm_time || notif.time)}
                    </span>
                  </div>
                </div>
                {activeAlarms[notif.id] && (
                  <div className="alarm-active">
                    <Volume2 size={20} className="alarm-icon" />
                    <span>Alarm!</span>
                  </div>
                )}
                <button
                  onClick={() => handleDeleteNotification(notif.id)}
                  className="delete-btn"
                  title="Remove alarm"
                >
                  <Trash2 size={16} />
                </button>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
