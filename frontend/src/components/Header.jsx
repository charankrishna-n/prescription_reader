import { motion } from 'framer-motion';
import { LogOut, Bell, User } from 'lucide-react';

export default function Header({ user, onLogout }) {
  return (
    <motion.header
      initial={{ opacity: 0, y: -20 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-slate-800 border-b border-slate-700 sticky top-0 z-50"
    >
      <div className="max-w-7xl mx-auto px-4 py-4 flex items-center justify-between">
        {/* Logo */}
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-gradient-to-br from-indigo-600 to-indigo-700 rounded-lg flex items-center justify-center">
            <span className="text-white font-bold text-lg">Rx</span>
          </div>
          <div>
            <h1 className="text-white font-bold text-lg">RxAssist AI</h1>
            <p className="text-xs text-slate-400">Smart Prescription Management</p>
          </div>
        </div>

        {/* Right Section */}
        <div className="flex items-center gap-4">
          {/* Notifications */}
          <motion.button
            whileHover={{ scale: 1.1 }}
            whileTap={{ scale: 0.95 }}
            className="relative p-2 hover:bg-slate-700 rounded-lg transition"
          >
            <Bell className="w-5 h-5 text-slate-400 hover:text-white transition" />
            <span className="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full"></span>
          </motion.button>

          {/* User Menu */}
          <div className="flex items-center gap-3 pl-4 border-l border-slate-700">
            <div className="w-8 h-8 bg-gradient-to-br from-indigo-600 to-indigo-700 rounded-full flex items-center justify-center">
              <User className="w-4 h-4 text-white" />
            </div>
            <div className="hidden sm:block">
              <p className="text-sm font-medium text-white">{user?.email}</p>
              <p className="text-xs text-slate-400">Patient</p>
            </div>
          </div>

          {/* Logout */}
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={onLogout}
            className="p-2 hover:bg-red-500/10 rounded-lg transition"
          >
            <LogOut className="w-5 h-5 text-slate-400 hover:text-red-400 transition" />
          </motion.button>
        </div>
      </div>
    </motion.header>
  );
}
