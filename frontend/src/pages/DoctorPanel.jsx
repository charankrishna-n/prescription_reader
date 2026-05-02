import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { LogOut, Search, TrendingUp, AlertCircle } from 'lucide-react';
import { useAuth } from '../lib/AuthContext';
import { useNavigate } from 'react-router-dom';
import Header from '../components/Header';

export default function DoctorPanel() {
  const { logout, user } = useAuth();
  const navigate = useNavigate();
  const [patients, setPatients] = useState([
    {
      id: 1,
      name: 'John Doe',
      email: 'john@example.com',
      adherence: 85,
      medicines: 3,
      lastUpdate: '2 hours ago',
    },
    {
      id: 2,
      name: 'Jane Smith',
      email: 'jane@example.com',
      adherence: 92,
      medicines: 2,
      lastUpdate: '1 hour ago',
    },
  ]);
  const [searchTerm, setSearchTerm] = useState('');

  const handleLogout = () => {
    logout();
    navigate('/doctor-login');
  };

  const filteredPatients = patients.filter(
    (p) =>
      p.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      p.email.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="min-h-screen bg-slate-900">
      <Header user={user} onLogout={handleLogout} />

      <div className="max-w-7xl mx-auto px-4 py-8">
        {/* Search */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8"
        >
          <div className="relative">
            <Search className="absolute left-3 top-3 w-5 h-5 text-slate-500" />
            <input
              type="text"
              placeholder="Search patients..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-4 py-2 bg-slate-800 border border-slate-700 rounded-lg text-white placeholder-slate-500 focus:outline-none focus:border-pink-500"
            />
          </div>
        </motion.div>

        {/* Patients Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredPatients.map((patient, index) => (
            <motion.div
              key={patient.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
              className="bg-slate-800 border border-slate-700 rounded-xl p-6 hover:border-slate-600 transition cursor-pointer group"
            >
              {/* Header */}
              <div className="flex items-start justify-between mb-4">
                <div>
                  <h3 className="text-lg font-bold text-white">{patient.name}</h3>
                  <p className="text-sm text-slate-400">{patient.email}</p>
                </div>
                <div className="w-10 h-10 bg-gradient-to-br from-pink-600 to-pink-700 rounded-full flex items-center justify-center">
                  <span className="text-white font-bold text-sm">
                    {patient.name.charAt(0)}
                  </span>
                </div>
              </div>

              {/* Stats */}
              <div className="space-y-3 mb-4">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-slate-400">Adherence</span>
                  <div className="flex items-center gap-2">
                    <div className="w-24 h-2 bg-slate-700 rounded-full overflow-hidden">
                      <div
                        className="h-full bg-gradient-to-r from-green-500 to-green-600"
                        style={{ width: `${patient.adherence}%` }}
                      ></div>
                    </div>
                    <span className="text-sm font-semibold text-white">
                      {patient.adherence}%
                    </span>
                  </div>
                </div>

                <div className="flex items-center justify-between">
                  <span className="text-sm text-slate-400">Active Medicines</span>
                  <span className="text-sm font-semibold text-white">
                    {patient.medicines}
                  </span>
                </div>

                <div className="flex items-center justify-between">
                  <span className="text-sm text-slate-400">Last Update</span>
                  <span className="text-sm text-slate-300">{patient.lastUpdate}</span>
                </div>
              </div>

              {/* Action Button */}
              <motion.button
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                className="w-full py-2 bg-gradient-to-r from-pink-600 to-pink-700 hover:from-pink-700 hover:to-pink-800 text-white font-semibold rounded-lg transition"
              >
                View Details
              </motion.button>
            </motion.div>
          ))}
        </div>

        {/* Empty State */}
        {filteredPatients.length === 0 && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="text-center py-12"
          >
            <AlertCircle className="w-12 h-12 text-slate-500 mx-auto mb-4" />
            <p className="text-slate-400">No patients found</p>
          </motion.div>
        )}
      </div>
    </div>
  );
}
