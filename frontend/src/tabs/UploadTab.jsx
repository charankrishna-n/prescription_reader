import { useState, useRef } from 'react';
import { useAuth } from '../lib/AuthContext';
import { useData } from '../lib/DataContext';
import { prescriptionAPI } from '../lib/api';
import { Upload, AlertCircle, Loader, Check, Calendar, CheckSquare, Bell, RotateCcw, Save, Camera, X } from 'lucide-react';
import './UploadTab.css';

export default function UploadTab() {
  const { user } = useAuth();
  const { medicines, setMedicines, clearMedicines, prescriptionImage, setPrescriptionImage, savePrescription } = useData();
  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [prescriptionName, setPrescriptionName] = useState('');
  const [uploadError, setUploadError] = useState('');
  const [uploadSuccess, setUploadSuccess] = useState('');
  const [actionStatus, setActionStatus] = useState({});
  const [saveStatus, setSaveStatus] = useState('');
  const [uploadLoading, setUploadLoading] = useState(false);
  const [showCamera, setShowCamera] = useState(false);
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const fileInputRef = useRef(null);
  const streamRef = useRef(null);

  if (!user) {
    return <div className="upload-tab"><p>Please login first</p></div>;
  }

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile) {
      setFile(selectedFile);
      const reader = new FileReader();
      reader.onload = (event) => {
        setPreview(event.target.result);
        setPrescriptionImage(event.target.result);
      };
      reader.readAsDataURL(selectedFile);
      setUploadError('');
      setUploadSuccess('');
    }
  };

  const startCamera = async () => {
    try {
      setUploadError('');
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { 
          facingMode: 'environment',
          width: { ideal: 1280 },
          height: { ideal: 720 }
        }
      });
      streamRef.current = stream;
      setShowCamera(true);
      
      // Set video source after a small delay to ensure element is rendered
      setTimeout(() => {
        if (videoRef.current) {
          videoRef.current.srcObject = stream;
          videoRef.current.play().catch(err => {
            console.error('Play error:', err);
            setUploadError('Failed to start camera stream');
          });
        }
      }, 100);
    } catch (err) {
      setUploadError('Unable to access camera. Please check permissions.');
      console.error('Camera error:', err);
    }
  };

  const stopCamera = () => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach(track => track.stop());
      streamRef.current = null;
    }
    if (videoRef.current) {
      videoRef.current.srcObject = null;
    }
    setShowCamera(false);
  };

  const capturePhoto = () => {
    if (!videoRef.current || !canvasRef.current) {
      setUploadError('Camera not ready');
      return;
    }

    try {
      const video = videoRef.current;
      const canvas = canvasRef.current;
      
      // Set canvas dimensions to match video
      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight;
      
      if (canvas.width === 0 || canvas.height === 0) {
        setUploadError('Camera stream not ready. Please wait a moment and try again.');
        return;
      }
      
      const context = canvas.getContext('2d');
      
      // Draw image (mirror it)
      context.scale(-1, 1);
      context.drawImage(video, -canvas.width, 0);
      
      // Convert canvas to blob
      canvas.toBlob((blob) => {
        if (blob) {
          const file = new File([blob], 'camera-capture.jpg', { type: 'image/jpeg' });
          setFile(file);
          
          const reader = new FileReader();
          reader.onload = (event) => {
            setPreview(event.target.result);
            setPrescriptionImage(event.target.result);
            setUploadError('');
            setUploadSuccess('');
          };
          reader.readAsDataURL(file);
          
          stopCamera();
        } else {
          setUploadError('Failed to capture image');
        }
      }, 'image/jpeg', 0.95);
    } catch (err) {
      console.error('Capture error:', err);
      setUploadError('Failed to capture image: ' + err.message);
    }
  };

  const handleNewPrescription = () => {
    clearMedicines();
    setFile(null);
    setPreview(null);
    setPrescriptionName('');
    setUploadError('');
    setUploadSuccess('');
    setActionStatus({});
    setSaveStatus('');
  };

  const handleUpload = async () => {
    if (!file) {
      setUploadError('Please select an image');
      return;
    }

    setUploadLoading(true);
    setUploadError('');
    setUploadSuccess('');

    try {
      console.log('Starting upload...');
      const response = await prescriptionAPI.upload(file);
      console.log('Upload response:', response);
      const extractedMedicines = response.data.medicines || [];
      setMedicines(extractedMedicines);
      setUploadSuccess(`Successfully extracted ${extractedMedicines.length} medicines`);
      setFile(null);
      setPreview(null);
    } catch (err) {
      console.error('Upload error:', err);
      const errorMsg = err.response?.data?.detail || err.message || 'Failed to process prescription';
      setUploadError(errorMsg);
    } finally {
      setUploadLoading(false);
    }
  };

  const handleSavePrescription = async () => {
    if (!prescriptionName.trim()) {
      setSaveStatus('error');
      setUploadError('Please enter a prescription name');
      setTimeout(() => setSaveStatus(''), 2000);
      return;
    }

    try {
      setSaveStatus('loading');
      await savePrescription(prescriptionName, prescriptionImage);
      setSaveStatus('success');
      setTimeout(() => {
        setSaveStatus('');
        handleNewPrescription();
      }, 2000);
    } catch (err) {
      setSaveStatus('error');
      setUploadError('Failed to save prescription');
      setTimeout(() => setSaveStatus(''), 2000);
    }
  };

  const handleAddToTracker = async (medicine, index) => {
    try {
      setActionStatus(prev => ({ ...prev, [`tracker-${index}`]: 'loading' }));
      const trackerData = {
        medicine_name: medicine.name,
        dosage: medicine.dosage,
        frequency: medicine.frequency,
        time: new Date().toLocaleTimeString()
      };
      await prescriptionAPI.addToTracker(trackerData);
      setActionStatus(prev => ({ ...prev, [`tracker-${index}`]: 'success' }));
    } catch (err) {
      console.error('Tracker error:', err);
      setActionStatus(prev => ({ ...prev, [`tracker-${index}`]: 'error' }));
    }
  };

  const handleAddToCalendar = async (medicine, index) => {
    try {
      setActionStatus(prev => ({ ...prev, [`calendar-${index}`]: 'loading' }));
      const calendarData = {
        medicine_name: medicine.name,
        dosage: medicine.dosage,
        frequency: medicine.frequency,
        duration: medicine.duration,
        start_date: new Date().toISOString().split('T')[0]
      };
      await prescriptionAPI.addToCalendar(calendarData);
      setActionStatus(prev => ({ ...prev, [`calendar-${index}`]: 'success' }));
    } catch (err) {
      console.error('Calendar error:', err);
      setActionStatus(prev => ({ ...prev, [`calendar-${index}`]: 'error' }));
    }
  };

  const handleAddNotification = async (medicine, index) => {
    try {
      setActionStatus(prev => ({ ...prev, [`notification-${index}`]: 'loading' }));
      const notificationData = {
        name: medicine.name,
        dosage: medicine.dosage,
        frequency: medicine.frequency
      };
      await prescriptionAPI.addNotification(notificationData);
      setActionStatus(prev => ({ ...prev, [`notification-${index}`]: 'success' }));
    } catch (err) {
      console.error('Notification error:', err);
      setActionStatus(prev => ({ ...prev, [`notification-${index}`]: 'error' }));
    }
  };

  return (
    <div className="upload-tab">
      <div className="upload-container">
        {/* Upload Section */}
        <div className="upload-section">
          <h2>Upload Prescription</h2>

          {!showCamera ? (
            <>
              <div className="upload-options">
                <div className="upload-area" onClick={() => fileInputRef.current?.click()}>
                  <Upload className="upload-icon" />
                  <p>Click to upload or drag image here</p>
                  <span>PNG, JPG, JPEG</span>
                  <input
                    ref={fileInputRef}
                    type="file"
                    accept="image/*"
                    onChange={handleFileChange}
                    style={{ display: 'none' }}
                  />
                </div>

                <button onClick={startCamera} className="camera-button">
                  <Camera className="camera-icon" />
                  <span>Scan with Camera</span>
                </button>
              </div>
            </>
          ) : (
            <div className="camera-container">
              <video
                ref={videoRef}
                autoPlay
                playsInline
                muted
                className="camera-video"
              />
              <canvas ref={canvasRef} style={{ display: 'none' }} />
              
              <div className="camera-controls">
                <button onClick={capturePhoto} className="capture-btn">
                  <Camera size={24} />
                  Capture
                </button>
                <button onClick={stopCamera} className="cancel-btn">
                  <X size={24} />
                  Cancel
                </button>
              </div>
            </div>
          )}

          {(preview || prescriptionImage) && (
            <div className="preview-section">
              <h3>Preview</h3>
              <img src={preview || prescriptionImage} alt="Preview" className="preview-image" />
            </div>
          )}

          {uploadError && (
            <div className="error-message">
              <AlertCircle className="error-icon" />
              <span>{uploadError}</span>
            </div>
          )}

          {uploadSuccess && (
            <div className="success-message">
              <Check className="success-icon" />
              <span>{uploadSuccess}</span>
            </div>
          )}

          <button
            onClick={handleUpload}
            disabled={!file || uploadLoading}
            className="upload-button"
          >
            {uploadLoading ? (
              <>
                <Loader className="spinner" />
                Processing...
              </>
            ) : (
              <>
                <Upload className="button-icon" />
                Analyze Prescription
              </>
            )}
          </button>
        </div>

        {/* Results Section */}
        {medicines.length > 0 && (
          <div className="results-section">
            <div className="results-header">
              <h2>Extracted Medicines ({medicines.length})</h2>
              <button
                onClick={handleNewPrescription}
                className="new-prescription-btn"
                title="Upload a new prescription"
              >
                <RotateCcw size={16} />
                New Prescription
              </button>
            </div>
            <div className="medicines-grid">
              {medicines.map((medicine, index) => (
                <div key={index} className="medicine-item">
                  <div className="medicine-header">
                    <h3>{medicine.name}</h3>
                    <span className="confidence">
                      {(medicine.confidence * 100).toFixed(0)}%
                    </span>
                  </div>
                  <div className="medicine-details">
                    <div className="detail">
                      <span className="label">Dosage:</span>
                      <span className="value">{medicine.dosage}</span>
                    </div>
                    <div className="detail">
                      <span className="label">Frequency:</span>
                      <span className="value">{medicine.frequency}</span>
                    </div>
                    <div className="detail">
                      <span className="label">Duration:</span>
                      <span className="value">{medicine.duration}</span>
                    </div>
                    <div className="detail">
                      <span className="label">With Meal:</span>
                      <span className="value">{medicine.meal_context}</span>
                    </div>
                  </div>
                  <div className="medicine-actions">
                    <button
                      onClick={() => handleAddToTracker(medicine, index)}
                      className={`action-btn tracker-btn ${actionStatus[`tracker-${index}`]}`}
                      disabled={actionStatus[`tracker-${index}`] === 'loading'}
                      title="Add to Tracker"
                    >
                      <CheckSquare size={18} />
                      {actionStatus[`tracker-${index}`] === 'success' && <span className="status-text">Added</span>}
                      {actionStatus[`tracker-${index}`] === 'error' && <span className="status-text">Failed</span>}
                      {!actionStatus[`tracker-${index}`] && <span>Tracker</span>}
                    </button>
                    <button
                      onClick={() => handleAddToCalendar(medicine, index)}
                      className={`action-btn calendar-btn ${actionStatus[`calendar-${index}`]}`}
                      disabled={actionStatus[`calendar-${index}`] === 'loading'}
                      title="Add to Calendar"
                    >
                      <Calendar size={18} />
                      {actionStatus[`calendar-${index}`] === 'success' && <span className="status-text">Added</span>}
                      {actionStatus[`calendar-${index}`] === 'error' && <span className="status-text">Failed</span>}
                      {!actionStatus[`calendar-${index}`] && <span>Calendar</span>}
                    </button>
                    <button
                      onClick={() => handleAddNotification(medicine, index)}
                      className={`action-btn notification-btn ${actionStatus[`notification-${index}`]}`}
                      disabled={actionStatus[`notification-${index}`] === 'loading'}
                      title="Add Notification"
                    >
                      <Bell size={18} />
                      {actionStatus[`notification-${index}`] === 'success' && <span className="status-text">Added</span>}
                      {actionStatus[`notification-${index}`] === 'error' && <span className="status-text">Failed</span>}
                      {!actionStatus[`notification-${index}`] && <span>Notify</span>}
                    </button>
                  </div>
                </div>
              ))}
            </div>

            {/* Save Prescription Section */}
            <div className="save-prescription-section">
              <h3>Save This Prescription</h3>
              <div className="save-form">
                <input
                  type="text"
                  placeholder="Enter prescription name (e.g., Doctor Visit - Jan 2024)"
                  value={prescriptionName}
                  onChange={(e) => setPrescriptionName(e.target.value)}
                  className="prescription-name-input"
                />
                <button
                  onClick={handleSavePrescription}
                  disabled={uploadLoading || saveStatus === 'loading'}
                  className={`save-btn ${saveStatus}`}
                >
                  {saveStatus === 'loading' ? (
                    <>
                      <Loader className="spinner" />
                      Saving...
                    </>
                  ) : saveStatus === 'success' ? (
                    <>
                      <Check size={18} />
                      Saved!
                    </>
                  ) : (
                    <>
                      <Save size={18} />
                      Save Prescription
                    </>
                  )}
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
