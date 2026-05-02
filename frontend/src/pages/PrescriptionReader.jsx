import { useState } from 'react';
import './PrescriptionReader.css';

export default function PrescriptionReader({ onLogout }) {
  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [medicines, setMedicines] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile) {
      setFile(selectedFile);
      const reader = new FileReader();
      reader.onload = (event) => {
        setPreview(event.target.result);
      };
      reader.readAsDataURL(selectedFile);
      setError('');
      setMedicines([]);
    }
  };

  const handleUpload = async () => {
    if (!file) {
      setError('Please select an image');
      return;
    }

    setLoading(true);
    setError('');
    const formData = new FormData();
    formData.append('file', file);

    try {
      const token = localStorage.getItem('token');
      const response = await fetch('http://localhost:8000/predict', {
        method: 'POST',
        headers: { Authorization: `Bearer ${token}` },
        body: formData,
      });

      const data = await response.json();

      if (response.ok) {
        setMedicines(data.medicines || []);
      } else {
        setError(data.message || 'Failed to process prescription');
      }
    } catch (err) {
      setError('Error uploading file. Make sure backend is running.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="reader-container">
      <div className="reader-header">
        <h1>Prescription Reader</h1>
        <button onClick={onLogout} className="logout-button">Logout</button>
      </div>

      <div className="reader-content">
        <div className="upload-section">
          <h2>Upload Prescription</h2>
          <div className="upload-area">
            <input
              type="file"
              accept="image/*"
              onChange={handleFileChange}
              id="file-input"
              className="file-input"
            />
            <label htmlFor="file-input" className="upload-label">
              <div className="upload-icon">📷</div>
              <p>Click to select or drag image here</p>
              <span>PNG, JPG, JPEG</span>
            </label>
          </div>

          {preview && (
            <div className="preview-section">
              <h3>Preview</h3>
              <img src={preview} alt="Preview" className="preview-image" />
            </div>
          )}

          {error && <div className="error-message">{error}</div>}

          <button
            onClick={handleUpload}
            disabled={!file || loading}
            className="upload-button"
          >
            {loading ? 'Processing...' : 'Analyze Prescription'}
          </button>
        </div>

        {medicines.length > 0 && (
          <div className="medicines-section">
            <h2>Medicines Found</h2>
            <div className="medicines-list">
              {medicines.map((medicine, index) => (
                <div key={index} className="medicine-card">
                  <div className="medicine-name">{medicine.name}</div>
                  <div className="medicine-details">
                    {medicine.dosage && (
                      <div className="detail">
                        <span className="label">Dosage:</span>
                        <span className="value">{medicine.dosage}</span>
                      </div>
                    )}
                    {medicine.frequency && (
                      <div className="detail">
                        <span className="label">Frequency:</span>
                        <span className="value">{medicine.frequency}</span>
                      </div>
                    )}
                    {medicine.duration && (
                      <div className="detail">
                        <span className="label">Duration:</span>
                        <span className="value">{medicine.duration}</span>
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
