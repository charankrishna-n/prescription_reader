import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import Sidebar from './components/Sidebar';
import Header from './components/Header';
import DashboardPage from './pages/DashboardPage';
import MedicinesPage from './pages/MedicinesPage';
import RemindersPage from './pages/RemindersPage';
import InsightsPage from './pages/InsightsPage';
import ProfilePage from './pages/ProfilePage';
import './Dashboard.css';

function Dashboard() {
  const [currentPage, setCurrentPage] = useState('dashboard');
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [language, setLanguage] = useState('en');
  const [user, setUser] = useState({
    name: 'John Doe',
    age: 35,
    gender: 'Male',
    language: 'en',
  });

  const renderPage = () => {
    switch (currentPage) {
      case 'dashboard':
        return <DashboardPage language={language} user={user} />;
      case 'medicines':
        return <MedicinesPage language={language} />;
      case 'reminders':
        return <RemindersPage language={language} />;
      case 'insights':
        return <InsightsPage language={language} />;
      case 'profile':
        return <ProfilePage language={language} user={user} setUser={setUser} setLanguage={setLanguage} />;
      default:
        return <DashboardPage language={language} user={user} />;
    }
  };

  return (
    <div className="dashboard-container">
      <Sidebar 
        currentPage={currentPage} 
        setCurrentPage={setCurrentPage}
        sidebarOpen={sidebarOpen}
        setSidebarOpen={setSidebarOpen}
        language={language}
      />
      
      <div className="main-content">
        <Header 
          sidebarOpen={sidebarOpen}
          setSidebarOpen={setSidebarOpen}
          language={language}
          setLanguage={setLanguage}
          user={user}
        />
        
        <main className="page-content">
          <AnimatePresence mode="wait">
            <motion.div
              key={currentPage}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.3 }}
            >
              {renderPage()}
            </motion.div>
          </AnimatePresence>
        </main>
      </div>
    </div>
  );
}

export default Dashboard;
