import { useState, useEffect } from 'react';
import { useAuth } from '../lib/AuthContext';
import { useData } from '../lib/DataContext';
import { LogOut, FileText, Trash2, Eye, AlertCircle, Loader, Edit2, Save, X } from 'lucide-react';
import './ProfileTab.css';

export default function ProfileTab() {
  const { user, logout } = useAuth();
  const { prescriptions, fetchPrescriptions, loadPrescription, deletePrescription, loading } = useData();
  const [selectedPrescription, setSelectedPrescription] = useState(null);
  const [prescriptionDetails, setPrescriptionDetails] = useState(null);
  const [isEditingProfile, setIsEditingProfile] = useState(false);
  const [profileData, setProfileData] = useState({
    name: '',
    age: '',
    gender: '',
    phone: '',
    bloodGroup: '',
    familyDoctor: '',
    address: '',
    height: '',
    weight: ''
  });
  const [editData, setEditData] = useState({ ...profileData });
  const [saveStatus, setSaveStatus] = useState('');

  useEffect(() => {
    if (user) {
      fetchPrescriptions();
      // Load profile data from localStorage
      const savedProfile = localStorage.getItem('userProfile');
      if (savedProfile) {
        const profile = JSON.parse(savedProfile);
        setProfileData(profile);
        setEditData(profile);
      }
    }
  }, [user, fetchPrescriptions]);

  const handleViewPrescription = async (prescription) => {
    try {
      await loadPrescription(prescription.id);
      setSelectedPrescription(prescription);
      setPrescriptionDetails(prescription);
    } catch (err) {
      console.error('Failed to load prescription:', err);
    }
  };

  const handleDeletePrescription = async (prescriptionId) => {
    if (window.confirm('Are you sure you want to delete this prescription?')) {
      try {
        await deletePrescription(prescriptionId);
        if (selectedPrescription?.id === prescriptionId) {
          setSelectedPrescription(null);
          setPrescriptionDetails(null);
        }
      } catch (err) {
        console.error('Failed to delete prescription:', err);
      }
    }
  };

  const handleEditProfile = () => {
    setEditData({ ...profileData });
    setIsEditingProfile(true);
  };

  const handleSaveProfile = () => {
    if (!editData.name.trim()) {
      setSaveStatus('error');
      setTimeout(() => setSaveStatus(''), 2000);
      return;
    }

    try {
      setSaveStatus('loading');
      setProfileData(editData);
      localStorage.setItem('userProfile', JSON.stringify(editData));
      setSaveStatus('success');
      setIsEditingProfile(false);
      setTimeout(() => setSaveStatus(''), 2000);
    } catch (err) {
      setSaveStatus('error');
      setTimeout(() => setSaveStatus(''), 2000);
    }
  };

  const handleCancelEdit = () => {
    setEditData({ ...profileData });
    setIsEditingProfile(false);
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setEditData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleLogout = () => {
    logout();
  };

  if (!user) {
    return <div className="profile-tab"><p>Please login first</p></div>;
  }

  return (
    <div className="profile-tab">
      <div className="profile-container">
        {/* User Profile Section */}
        <div className="user-section">
          {!isEditingProfile ? (
            <div className="user-card">
              <div className="user-avatar">
                {profileData.name ? profileData.name.charAt(0).toUpperCase() : user.email.charAt(0).toUpperCase()}
              </div>
              <div className="user-details">
                <h2>{profileData.name || user.email}</h2>
                <p className="user-email">{user.email}</p>
                <p className="user-type">Patient Account</p>
              </div>
              <div className="user-actions">
                <button onClick={handleEditProfile} className="edit-profile-btn">
                  <Edit2 size={18} />
                  Edit Profile
                </button>
                <button onClick={handleLogout} className="logout-btn">
                  <LogOut size={18} />
                  Logout
                </button>
              </div>
            </div>
          ) : (
            <div className="edit-profile-card">
              <h2>Edit Profile</h2>
              <div className="edit-form">
                <div className="form-group">
                  <label>Full Name *</label>
                  <input
                    type="text"
                    name="name"
                    value={editData.name}
                    onChange={handleInputChange}
                    placeholder="Enter your full name"
                    className="form-input"
                  />
                </div>

                <div className="form-row">
                  <div className="form-group">
                    <label>Age</label>
                    <input
                      type="number"
                      name="age"
                      value={editData.age}
                      onChange={handleInputChange}
                      placeholder="Enter your age"
                      className="form-input"
                      min="0"
                      max="150"
                    />
                  </div>
                  <div className="form-group">
                    <label>Gender</label>
                    <select
                      name="gender"
                      value={editData.gender}
                      onChange={handleInputChange}
                      className="form-input"
                    >
                      <option value="">Select Gender</option>
                      <option value="Male">Male</option>
                      <option value="Female">Female</option>
                      <option value="Other">Other</option>
                    </select>
                  </div>
                </div>

                <div className="form-row">
                  <div className="form-group">
                    <label>Height (cm)</label>
                    <input
                      type="number"
                      name="height"
                      value={editData.height}
                      onChange={handleInputChange}
                      placeholder="Enter your height in cm"
                      className="form-input"
                      min="0"
                    />
                  </div>
                  <div className="form-group">
                    <label>Weight (kg)</label>
                    <input
                      type="number"
                      name="weight"
                      value={editData.weight}
                      onChange={handleInputChange}
                      placeholder="Enter your weight in kg"
                      className="form-input"
                      min="0"
                      step="0.1"
                    />
                  </div>
                </div>

                <div className="form-row">
                  <div className="form-group">
                    <label>Phone Number</label>
                    <input
                      type="tel"
                      name="phone"
                      value={editData.phone}
                      onChange={handleInputChange}
                      placeholder="Enter your phone number"
                      className="form-input"
                    />
                  </div>
                  <div className="form-group">
                    <label>Blood Group</label>
                    <select
                      name="bloodGroup"
                      value={editData.bloodGroup}
                      onChange={handleInputChange}
                      className="form-input"
                    >
                      <option value="">Select Blood Group</option>
                      <option value="O+">O+</option>
                      <option value="O-">O-</option>
                      <option value="A+">A+</option>
                      <option value="A-">A-</option>
                      <option value="B+">B+</option>
                      <option value="B-">B-</option>
                      <option value="AB+">AB+</option>
                      <option value="AB-">AB-</option>
                    </select>
                  </div>
                </div>

                <div className="form-group">
                  <label>Family Doctor Name</label>
                  <input
                    type="text"
                    name="familyDoctor"
                    value={editData.familyDoctor}
                    onChange={handleInputChange}
                    placeholder="Enter your family doctor's name"
                    className="form-input"
                  />
                </div>

                <div className="form-group">
                  <label>Address</label>
                  <textarea
                    name="address"
                    value={editData.address}
                    onChange={handleInputChange}
                    placeholder="Enter your address"
                    className="form-input form-textarea"
                    rows="3"
                  />
                </div>

                <div className="form-actions">
                  <button
                    onClick={handleSaveProfile}
                    disabled={saveStatus === 'loading'}
                    className={`save-profile-btn ${saveStatus}`}
                  >
                    {saveStatus === 'loading' ? (
                      <>
                        <Loader className="spinner" />
                        Saving...
                      </>
                    ) : saveStatus === 'success' ? (
                      <>
                        <Save size={18} />
                        Saved!
                      </>
                    ) : (
                      <>
                        <Save size={18} />
                        Save Profile
                      </>
                    )}
                  </button>
                  <button onClick={handleCancelEdit} className="cancel-btn">
                    <X size={18} />
                    Cancel
                  </button>
                </div>
              </div>
            </div>
          )}

          {/* Profile Info Display */}
          {!isEditingProfile && (profileData.name || profileData.age || profileData.phone) && (
            <div className="profile-info-grid">
              {profileData.age && (
                <div className="info-item">
                  <span className="info-label">Age</span>
                  <span className="info-value">{profileData.age}</span>
                </div>
              )}
              {profileData.gender && (
                <div className="info-item">
                  <span className="info-label">Gender</span>
                  <span className="info-value">{profileData.gender}</span>
                </div>
              )}
              {profileData.phone && (
                <div className="info-item">
                  <span className="info-label">Phone</span>
                  <span className="info-value">{profileData.phone}</span>
                </div>
              )}
              {profileData.bloodGroup && (
                <div className="info-item">
                  <span className="info-label">Blood Group</span>
                  <span className="info-value">{profileData.bloodGroup}</span>
                </div>
              )}
              {profileData.familyDoctor && (
                <div className="info-item">
                  <span className="info-label">Family Doctor</span>
                  <span className="info-value">{profileData.familyDoctor}</span>
                </div>
              )}
              {profileData.height && (
                <div className="info-item">
                  <span className="info-label">Height</span>
                  <span className="info-value">{profileData.height} cm</span>
                </div>
              )}
              {profileData.weight && (
                <div className="info-item">
                  <span className="info-label">Weight</span>
                  <span className="info-value">{profileData.weight} kg</span>
                </div>
              )}
              {profileData.address && (
                <div className="info-item full-width">
                  <span className="info-label">Address</span>
                  <span className="info-value">{profileData.address}</span>
                </div>
              )}
            </div>
          )}
        </div>

        {/* Prescriptions */}
        <div className="prescriptions-section">
          <h2>My Prescriptions</h2>
          
          {prescriptions.length === 0 ? (
            <div className="empty-state">
              <FileText className="empty-icon" />
              <p>No prescriptions saved yet</p>
              <span>Upload and save prescriptions to view them here</span>
            </div>
          ) : (
            <div className="prescriptions-grid">
              {prescriptions.map((prescription) => (
                <div key={prescription.id} className="prescription-card">
                  {prescription.image && (
                    <div className="prescription-image">
                      <img src={prescription.image} alt={prescription.name} />
                    </div>
                  )}
                  <div className="prescription-info">
                    <h3>{prescription.name}</h3>
                    <p className="prescription-date">
                      {new Date(prescription.created_at).toLocaleDateString()}
                    </p>
                    <p className="prescription-medicines">
                      {prescription.medicines?.length || 0} medicines
                    </p>
                  </div>
                  <div className="prescription-actions">
                    <button
                      onClick={() => handleViewPrescription(prescription)}
                      className="view-btn"
                      title="View details"
                    >
                      <Eye size={16} />
                      View
                    </button>
                    <button
                      onClick={() => handleDeletePrescription(prescription.id)}
                      className="delete-btn"
                      title="Delete prescription"
                    >
                      <Trash2 size={16} />
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Prescription Details */}
        {selectedPrescription && (
          <div className="prescription-details-section">
            <div className="details-header">
              <h2>{selectedPrescription.name}</h2>
              <button
                onClick={() => {
                  setSelectedPrescription(null);
                  setPrescriptionDetails(null);
                }}
                className="close-btn"
              >
                ✕
              </button>
            </div>

            {selectedPrescription.image && (
              <div className="details-image">
                <img src={selectedPrescription.image} alt={selectedPrescription.name} />
              </div>
            )}

            {/* Medicines */}
            {selectedPrescription.medicines && selectedPrescription.medicines.length > 0 && (
              <div className="details-section">
                <h3>Medicines ({selectedPrescription.medicines.length})</h3>
                <div className="medicines-list">
                  {selectedPrescription.medicines.map((medicine, idx) => (
                    <div key={idx} className="medicine-item">
                      <div className="medicine-name">{medicine.name}</div>
                      <div className="medicine-info">
                        <span>{medicine.dosage}</span>
                        <span>•</span>
                        <span>{medicine.frequency}</span>
                        <span>•</span>
                        <span>{medicine.duration}</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Calendar Items */}
            {prescriptionDetails?.calendar && prescriptionDetails.calendar.length > 0 && (
              <div className="details-section">
                <h3>Calendar Schedule ({prescriptionDetails.calendar.length})</h3>
                <div className="items-list">
                  {prescriptionDetails.calendar.map((item, idx) => (
                    <div key={idx} className="item">
                      <span className="item-date">
                        {new Date(item.date).toLocaleDateString()}
                      </span>
                      <span className="item-medicine">{item.medicine_name}</span>
                      <span className="item-frequency">{item.frequency}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Tracker Items */}
            {prescriptionDetails?.tracker && prescriptionDetails.tracker.length > 0 && (
              <div className="details-section">
                <h3>Tracker Items ({prescriptionDetails.tracker.length})</h3>
                <div className="items-list">
                  {prescriptionDetails.tracker.map((item, idx) => (
                    <div key={idx} className={`item ${item.taken ? 'taken' : ''}`}>
                      <span className="item-status">
                        {item.taken ? '✓' : '○'}
                      </span>
                      <span className="item-medicine">{item.medicine_name}</span>
                      <span className="item-date">
                        {new Date(item.date).toLocaleDateString()}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Notifications */}
            {prescriptionDetails?.notifications && prescriptionDetails.notifications.length > 0 && (
              <div className="details-section">
                <h3>Pending Notifications ({prescriptionDetails.notifications.length})</h3>
                <div className="items-list">
                  {prescriptionDetails.notifications.map((item, idx) => (
                    <div key={idx} className="item notification">
                      <span className="item-icon">⏰</span>
                      <span className="item-medicine">{item.medicine_name}</span>
                      <span className="item-time">{item.time}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
