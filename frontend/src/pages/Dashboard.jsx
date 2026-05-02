import { useState } from 'react';
import { motion } from 'framer-motion';
import { Upload, Plus, Calendar, Globe, LogOut, AlertCircle, Loader } from 'lucide-react';
import { useAuth } from '../lib/AuthContext';
import { useNavigate } from 'react-router-dom';
import { prescriptionAPI } from '../lib/api';
import MedicineCard from '../components/MedicineCard';
import Header from '../components/Header';

export default function Dashboard() {
  const { logout, user } = useAuth();
  const navigate = useNavigate();
  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [medicines, setMedicines] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [language, setLanguage] = useState('en');

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile) {
      setFile(selectedFile);
      const reader = new FileReader();
      reader.onload = (event) => setPreview(event.target.result);
      reader.readAsDataURL(selectedFile);
      setError('');
    }
  };

  const handleUpload = async () => {
    if (!file) {
      setError('Please select an image');
      return;
    }

    setLoading(true);
    setError('');

    try {
      const response = await prescriptionAPI.upload(file);
      setMedicines(response.data.medicines || []);
      setFile(null);
      setPreview(null);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to process prescription');
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <div className="min-h-screen bg-slate-900">
      <Header user={user} onLogout={handleLogout} />

      <div className="max-w-7xl mx-auto px-4 py-8">
        {/* Language Selector */}
        <div className="flex justify-end mb-6">
          <select
            value={language}
            onChange={(e) => setLanguage(e.target.value)}
            className="px-4 py-2 bg-slate-800 border border-slate-700 rounded-lg text-white text-sm focus:outline-none focus:border-indigo-500"
          >
            <option value="en">English</option>
            <option value="ta">Tamil</option>
            <option value="hi">Hindi</option>
          </select>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Upload Section */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="lg:col-span-1"
          >
            <div className="bg-slate-800 border border-slate-700 rounded-2xl p-6">
              <h2 className="text-xl font-bold text-white mb-6">Upload Prescription</h2>

              {/* Upload Area */}
              <div
                onClick={() => document.getElementById('file-input').click()}
                className="border-2 border-dashed border-slate-600 hover:border-indigo-500 rounded-xl p-8 text-center cursor-pointer transition group"
              >
                <Upload className="w-12 h-12 text-slate-500 group-hover:text-indigo-500 mx-auto mb-3 transition" />
                <p className="text-slate-300 font-medium mb-1">Click to upload</p>
                <p className="text-slate-500 text-sm">PNG, JPG, JPEG</p>
                <input
                  id="file-input"
                  type="file"
                  accept="image/*"
                  onChange={handleFileChange}
                  className="hidden"
                />
              </div>

              {/* Preview */}
              {preview && (
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  className="mt-4"
                >
                  <p className="text-sm text-slate-400 mb-2">Preview</p>
                  <img
                    src={preview}
                    alt="Preview"
                    className="w-full h-48 object-cover rounded-lg border border-slate-700"
                  />
                </motion.div>
              )}

              {/* Error */}
              {error && (
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  className="mt-4 flex items-center gap-2 p-3 bg-red-500/10 border border-red-500/30 rounded-lg"
                >
                  <AlertCircle className="w-4 h-4 text-red-500 flex-shrink-0" />
                  <p className="text-sm text-red-400">{error}</p>
                </motion.div>
              )}

              {/* Upload Button */}
              <button
                onClick={handleUpload}
                disabled={!file || loading}
                className="w-full mt-4 py-2 bg-gradient-to-r from-indigo-600 to-indigo-700 hover:from-indigo-700 hover:to-indigo-800 disabled:opacity-50 disabled:cursor-not-allowed text-white font-semibold rounded-lg transition flex items-center justify-center gap-2"
              >
                {loading ? (
                  <>
                    <Loader className="w-4 h-4 animate-spin" />
                    Processing...
                  </>
                ) : (
                  <>
                    <Upload className="w-4 h-4" />
                    Analyze
                  </>
                )}
              </button>
            </div>
          </motion.div>

          {/* Medicines Section */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="lg:col-span-2"
          >
            {medicines.length > 0 ? (
              <div>
                <h2 className="text-xl font-bold text-white mb-6">
                  Medicines Found ({medicines.length})
                </h2>
                <div className="space-y-4">
                  {medicines.map((medicine, index) => (
                    <MedicineCard
                      key={index}
                      medicine={medicine}
                      language={language}
                    />
                  ))}
                </div>
              </div>
            ) : (
              <div className="bg-slate-800 border border-slate-700 rounded-2xl p-12 text-center">
                <div className="w-16 h-16 bg-slate-700 rounded-full flex items-center justify-center mx-auto mb-4">
                  <Upload className="w-8 h-8 text-slate-500" />
                </div>
                <p className="text-slate-400">Upload a prescription to see medicines</p>
              </div>
            )}
          </motion.div>
        </div>
      </div>
    </div>
  );
}
