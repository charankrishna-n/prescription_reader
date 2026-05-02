import { useState, useEffect } from 'react';
import { AuthProvider, useAuth } from './lib/AuthContext';
import { DataProvider } from './lib/DataContext';
import LoginTab from './tabs/LoginTab';
import UploadTab from './tabs/UploadTab';
import CalendarTab from './tabs/CalendarTab';
import TrackerTab from './tabs/TrackerTab';
import NotificationsTab from './tabs/NotificationsTab';
import AdherenceTab from './tabs/AdherenceTab';
import DoctorPanelTab from './tabs/DoctorPanelTab';
import ProfileTab from './tabs/ProfileTab';
import './App.css';

function AppContent() {
  const { user, userType } = useAuth();
  const [activeTab, setActiveTab] = useState('upload');

  if (!user) {
    return <LoginTab />;
  }

  const tabs = [
    { id: 'upload', label: 'Upload', component: UploadTab },
    { id: 'calendar', label: 'Calendar', component: CalendarTab },
    { id: 'tracker', label: 'Tracker', component: TrackerTab },
    { id: 'notifications', label: 'Notifications', component: NotificationsTab },
    { id: 'adherence', label: 'Adherence', component: AdherenceTab },
    { id: 'doctor', label: 'Doctor Panel', component: DoctorPanelTab, doctorOnly: true },
    { id: 'profile', label: 'Profile', component: ProfileTab },
  ];

  const visibleTabs = tabs.filter(tab => {
    if (tab.doctorOnly && userType !== 'doctor') return false;
    return true;
  });

  const currentTab = tabs.find(t => t.id === activeTab);
  const CurrentComponent = currentTab?.component;

  return (
    <div className="app-container">
      {/* Header */}
      <header className="app-header">
        <div className="header-content">
          <h1 className="app-title">RxAssist AI</h1>
          <p className="app-subtitle">Smart Prescription Management</p>
        </div>
        {user && <div className="user-info">{user.email}</div>}
      </header>

      {/* Tabs Navigation */}
      <nav className="tabs-nav">
        <div className="tabs-container">
          {visibleTabs.map(tab => (
            <button
              key={tab.id}
              className={`tab-button ${activeTab === tab.id ? 'active' : ''}`}
              onClick={() => setActiveTab(tab.id)}
            >
              {tab.label}
            </button>
          ))}
        </div>
      </nav>

      {/* Tab Content */}
      <main className="tab-content">
        {CurrentComponent && <CurrentComponent />}
      </main>
    </div>
  );
}

function App() {
  return (
    <AuthProvider>
      <DataProvider>
        <AppContent />
      </DataProvider>
    </AuthProvider>
  );
}

export default App;
