import { useState } from 'react';
import { motion } from 'framer-motion';
import { Plus, Calendar, Globe, Check } from 'lucide-react';
import { reminderAPI } from '../lib/api';

export default function MedicineCard({ medicine, language }) {
  const [added, setAdded] = useState(false);
  const [loading, setLoading] = useState(false);

  const handleAddToTracker = async () => {
    setLoading(true);
    try {
      await reminderAPI.addReminder({
        medicine_name: medicine.name,
        dosage: medicine.dosage,
        frequency: medicine.frequency,
        duration: medicine.duration,
      });
      setAdded(true);
      setTimeout(() => setAdded(false), 2000);
    } catch (err) {
      console.error('Failed to add reminder:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      className="bg-slate-800 border border-slate-700 rounded-xl p-6 hover:border-slate-600 transition"
    >
      <div className="flex items-start justify-between mb-4">
        <div className="flex-1">
          <h3 className="text-lg font-bold text-white mb-1">{medicine.name}</h3>
          <p className="text-sm text-slate-400">
            Confidence: {(medicine.confidence * 100).toFixed(0)}%
          </p>
        </div>
      </div>

      {/* Details Grid */}
      <div className="grid grid-cols-2 gap-4 mb-6">
        <div className="bg-slate-700/50 rounded-lg p-3">
          <p className="text-xs text-slate-400 mb-1">Dosage</p>
          <p className="text-sm font-semibold text-white">{medicine.dosage}</p>
        </div>
        <div className="bg-slate-700/50 rounded-lg p-3">
          <p className="text-xs text-slate-400 mb-1">Frequency</p>
          <p className="text-sm font-semibold text-white">{medicine.frequency}</p>
        </div>
        <div className="bg-slate-700/50 rounded-lg p-3">
          <p className="text-xs text-slate-400 mb-1">Duration</p>
          <p className="text-sm font-semibold text-white">{medicine.duration}</p>
        </div>
        <div className="bg-slate-700/50 rounded-lg p-3">
          <p className="text-xs text-slate-400 mb-1">With Meal</p>
          <p className="text-sm font-semibold text-white">{medicine.meal_context}</p>
        </div>
      </div>

      {/* Action Buttons */}
      <div className="flex gap-3">
        <motion.button
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
          onClick={handleAddToTracker}
          disabled={loading || added}
          className={`flex-1 py-2 rounded-lg font-semibold transition flex items-center justify-center gap-2 ${
            added
              ? 'bg-green-500/20 text-green-400 border border-green-500/30'
              : 'bg-indigo-600 hover:bg-indigo-700 text-white border border-indigo-600'
          }`}
        >
          {added ? (
            <>
              <Check className="w-4 h-4" />
              Added
            </>
          ) : (
            <>
              <Plus className="w-4 h-4" />
              Tracker
            </>
          )}
        </motion.button>

        <motion.button
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
          className="flex-1 py-2 bg-slate-700 hover:bg-slate-600 text-white rounded-lg font-semibold transition flex items-center justify-center gap-2 border border-slate-600"
        >
          <Calendar className="w-4 h-4" />
          Calendar
        </motion.button>

        <motion.button
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
          className="flex-1 py-2 bg-slate-700 hover:bg-slate-600 text-white rounded-lg font-semibold transition flex items-center justify-center gap-2 border border-slate-600"
        >
          <Globe className="w-4 h-4" />
          Translate
        </motion.button>
      </div>
    </motion.div>
  );
}
