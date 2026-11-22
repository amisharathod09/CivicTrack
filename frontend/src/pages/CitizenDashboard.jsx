
import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  FileText,
  Clock,
  CheckCircle,
  XCircle,
  LogOut,
  RefreshCw,
  PlusCircle
} from 'lucide-react'

import api, { clearAccessToken } from '../services/api'
import ThemeToggle from '../components/ThemeToggle'
import './CitizenDashboard.css'

function CitizenDashboard() {
  const navigate = useNavigate()

  const [user, setUser] = useState(null)
  const [complaints, setComplaints] = useState([])
  const [categories, setCategories] = useState([])
  const [locations, setLocations] = useState([])
  const [feedbackList, setFeedbackList] = useState([])
  const [feedbackRating, setFeedbackRating] = useState(5)
const [feedbackComment, setFeedbackComment] = useState('')
const [selectedFeedbackComplaint, setSelectedFeedbackComplaint] = useState(null)
const [feedbackSubmitting, setFeedbackSubmitting] = useState(false)
const [feedbackError, setFeedbackError] = useState('')
const [feedbackSuccess, setFeedbackSuccess] = useState('')

  const [loading, setLoading] = useState(true)
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState('')
  const [formError, setFormError] = useState('')
  const [successMessage, setSuccessMessage] = useState('')

  const [selectedComplaint, setSelectedComplaint] = useState(null)
  const [complaintDetails, setComplaintDetails] = useState(null)
  const [detailsLoading, setDetailsLoading] = useState(false)
  const [detailsError, setDetailsError] = useState('')
const [attachments, setAttachments] = useState([])
const [selectedFile, setSelectedFile] = useState(null)
const [uploadingAttachment, setUploadingAttachment] = useState(false)
const [attachmentError, setAttachmentError] = useState('')
const [attachmentSuccess, setAttachmentSuccess] = useState('')
  const [formData, setFormData] = useState({
    category_id: '',
    location_id: '',
    title: '',
    description: ''
  })

  // Fetch dashboard information
  const fetchDashboardData = async () => {
    setLoading(true)
    setError('')

    try {
      const [
        userResponse,
        complaintsResponse,
        categoriesResponse,
        locationsResponse,
        feedbackResponse
      ] = await Promise.all([
        api.get('/auth/me'),
        api.get('/service-requests/my-complaints'),
        api.get('/categories'),
        api.get('/locations'),
        api.get('/feedback/my-feedback')
      ])

      setUser(userResponse.data)
      setComplaints(complaintsResponse.data)
      setFeedbackList(feedbackResponse.data)

      setCategories(
        categoriesResponse.data.filter(
          category => category.is_active
        )
      )

      setLocations(locationsResponse.data)
    } catch (err) {
      if (err.response?.status === 401) {
        clearAccessToken()
        navigate('/login', { replace: true })
        return
      }

      setError(
        err.response?.data?.detail ||
        'Unable to load your dashboard. Please try again.'
      )
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchDashboardData()
  }, [])

  // Logout
  const handleLogout = () => {
    clearAccessToken()
    navigate('/login', { replace: true })
  }

  // Handle form input changes
  const handleInputChange = (event) => {
    const { name, value } = event.target

    setFormData(current => ({
      ...current,
      [name]: value
    }))

    setFormError('')
    setSuccessMessage('')
  }

  // Submit a new complaint
  const handleComplaintSubmit = async (event) => {
    event.preventDefault()

    setFormError('')
    setSuccessMessage('')

    if (
      !formData.category_id ||
      !formData.location_id ||
      !formData.title.trim() ||
      !formData.description.trim()
    ) {
      setFormError('Please fill in all the fields.')
      return
    }

    setSubmitting(true)

    try {
      await api.post('/service-requests', {
        category_id: Number(formData.category_id),
        location_id: Number(formData.location_id),
        title: formData.title.trim(),
        description: formData.description.trim()
      })

      setFormData({
        category_id: '',
        location_id: '',
        title: '',
        description: ''
      })

      setSuccessMessage(
        'Your complaint has been submitted successfully.'
      )

      await fetchDashboardData()
    } catch (err) {
      if (err.response?.status === 401) {
        clearAccessToken()
        navigate('/login', { replace: true })
        return
      }

      setFormError(
        err.response?.data?.detail ||
        'Unable to submit your complaint. Please try again.'
      )
    } finally {
      setSubmitting(false)
    }
  }

  // Fetch and display complaint details
  const handleViewDetails = async (complaint) => {
  setSelectedComplaint(complaint)
  setComplaintDetails(null)
  setAttachments([])
  setDetailsError('')
  setAttachmentError('')
  setAttachmentSuccess('')
  setDetailsLoading(true)

  try {
    const [detailsResponse, attachmentsResponse] = await Promise.all([
      api.get(`/service-requests/${complaint.request_id}`),
      api.get(`/attachments/request/${complaint.request_id}`)
    ])

    setComplaintDetails(detailsResponse.data)
    setAttachments(attachmentsResponse.data)

  } catch (err) {
    if (err.response?.status === 401) {
      clearAccessToken()
      navigate('/login', { replace: true })
      return
    }

    setDetailsError(
      err.response?.data?.detail ||
      'Unable to load complaint details and attachments.'
    )
  } finally {
    setDetailsLoading(false)
  }
}

  // Close complaint details popup
  const closeComplaintDetails = () => {
    setSelectedComplaint(null)
    setComplaintDetails(null)
    setDetailsError('')
  }
// Upload a complaint photo
const handleUploadAttachment = async () => {
  if (!selectedFile || !selectedComplaint) {
    setAttachmentError('Please select a photo first.')
    return
  }

  if (!['image/jpeg', 'image/png'].includes(selectedFile.type)) {
    setAttachmentError('Only JPG, JPEG and PNG images are allowed.')
    return
  }

  if (selectedFile.size > 5 * 1024 * 1024) {
    setAttachmentError('File size must not exceed 5 MB.')
    return
  }

  const uploadData = new FormData()
  uploadData.append('file', selectedFile)
  uploadData.append('attachment_type', 'complaint_photo')

  try {
    setUploadingAttachment(true)
    setAttachmentError('')
    setAttachmentSuccess('')

    const response = await api.post(
      `/attachments/upload/${selectedComplaint.request_id}`,
      uploadData
    )

    setAttachmentSuccess(
      response.data.message || 'Photo uploaded successfully.'
    )

    setSelectedFile(null)

    const attachmentsResponse = await api.get(
      `/attachments/request/${selectedComplaint.request_id}`
    )

    setAttachments(attachmentsResponse.data)

  } catch (err) {
    setAttachmentError(
      err.response?.data?.detail ||
      'Unable to upload the photo. Please try again.'
    )
  } finally {
    setUploadingAttachment(false)
  }
}

// Download an attachment
const handleDownloadAttachment = async (attachment) => {
  try {
    const response = await api.get(
      `/attachments/${attachment.attachment_id}/download`,
      { responseType: 'blob' }
    )

    const fileUrl = window.URL.createObjectURL(response.data)
    const link = document.createElement('a')

    link.href = fileUrl
    link.download = attachment.file_name

    document.body.appendChild(link)
    link.click()
    link.remove()

    window.URL.revokeObjectURL(fileUrl)

  } catch (err) {
    setAttachmentError(
      err.response?.data?.detail ||
      'Unable to download this attachment.'
    )
  }
}
  // Cancel a complaint
const handleCancelComplaint = async (requestId) => {
  const confirmed = window.confirm(
    'Are you sure you want to cancel this complaint?'
  )

  if (!confirmed) return

  setError('')
  setSuccessMessage('')

  try {
    await api.patch(`/service-requests/${requestId}/cancel`)

    setSuccessMessage('Your complaint has been cancelled successfully.')

    await fetchDashboardData()
  } catch (err) {
    if (err.response?.status === 401) {
      clearAccessToken()
      navigate('/login', { replace: true })
      return
    }

    setError(
      err.response?.data?.detail ||
      'Unable to cancel this complaint. Please try again.'
    )
  }
}
  // Count complaints by status
  const getCount = (status) => {
    return complaints.filter(
      complaint => complaint.status === status
    ).length
  }
const handleSubmitFeedback = async (requestId) => {
  try {
    setFeedbackSubmitting(true)
    setFeedbackError('')
    setFeedbackSuccess('')

    await api.post('/feedback', {
      request_id: requestId,
      rating: Number(feedbackRating),
      comments: feedbackComment.trim() || null
    })

    setFeedbackSuccess('Feedback submitted successfully!')
    setFeedbackComment('')
    setFeedbackRating(5)
    setSelectedFeedbackComplaint(null)

    await fetchDashboardData()
  } catch (error) {
    setFeedbackError(
      error.response?.data?.detail || 'Unable to submit feedback.'
    )
  } finally {
    setFeedbackSubmitting(false)
  }
}
const handleUpdateFeedback = async (feedbackId) => {
  try {
    setFeedbackSubmitting(true)
    setFeedbackError('')
    setFeedbackSuccess('')

    await api.patch(`/feedback/${feedbackId}`, {
      rating: Number(feedbackRating),
      comments: feedbackComment.trim() || null
    })

    setFeedbackSuccess('Feedback updated successfully!')
    setSelectedFeedbackComplaint(null)

    await fetchDashboardData()
  } catch (error) {
    setFeedbackError(
      error.response?.data?.detail || 'Unable to update feedback.'
    )
  } finally {
    setFeedbackSubmitting(false)
  }
}
  // Format dates
  const formatDate = (date) => {
    if (!date) return 'Not available'

    return new Date(date).toLocaleDateString('en-IN', {
      day: 'numeric',
      month: 'short',
      year: 'numeric'
    })
  }

  // Create readable location name
  const getLocationLabel = (location) => {
    return [
      location.area,
      location.city,
      location.state
    ].filter(Boolean).join(', ') || location.full_address
  }

  return (
    <div className="citizen-dashboard">

      {/* Header */}
      <header className="citizen-header">
        <div className="citizen-brand">
          <span className="citizen-brand-icon">C</span>
          <span>CivicTrack</span>
        </div>

        <div className="citizen-header-actions">
          <ThemeToggle />

          <button
            type="button"
            className="citizen-logout"
            onClick={handleLogout}
          >
            <LogOut size={17} />
            Logout
          </button>
        </div>
      </header>

      <main className="citizen-main">

        {/* Welcome section */}
        <section className="citizen-welcome">
          <div>
            <span className="citizen-eyebrow">
              CITIZEN PORTAL
            </span>

            <h1>
              Welcome{user?.full_name ? `, ${user.full_name}` : ''}
            </h1>

            <p>
              Submit civic issues and keep track of your complaints.
            </p>
          </div>

          <button
            type="button"
            className="citizen-refresh"
            onClick={fetchDashboardData}
            disabled={loading}
          >
            <RefreshCw size={17} />
            Refresh
          </button>
        </section>

        {loading ? (
          <div className="citizen-message">
            Loading your dashboard...
          </div>
        ) : error ? (
          <div className="citizen-error">
            <p>{error}</p>

            <button
              type="button"
              onClick={fetchDashboardData}
            >
              Try Again
            </button>
          </div>
        ) : (
          <>

            {/* Dashboard statistics */}
            <section className="citizen-stats">

              <div className="citizen-stat-card">
                <div className="citizen-stat-icon total-icon">
                  <FileText size={22} />
                </div>

                <div>
                  <span>Total Complaints</span>
                  <h2>{complaints.length}</h2>
                </div>
              </div>

              <div className="citizen-stat-card">
                <div className="citizen-stat-icon progress-icon">
                  <Clock size={22} />
                </div>

                <div>
                  <span>In Progress</span>
                  <h2>{getCount('In Progress')}</h2>
                </div>
              </div>

              <div className="citizen-stat-card">
                <div className="citizen-stat-icon resolved-icon">
                  <CheckCircle size={22} />
                </div>

                <div>
                  <span>Resolved</span>
                  <h2>{getCount('Resolved')}</h2>
                </div>
              </div>

              <div className="citizen-stat-card">
                <div className="citizen-stat-icon cancelled-icon">
                  <XCircle size={22} />
                </div>

                <div>
                  <span>Cancelled</span>
                  <h2>{getCount('Cancelled')}</h2>
                </div>
              </div>

            </section>

            {/* Submit complaint section */}
            <section className="citizen-submit-section">

              <div className="citizen-section-heading">
                <div>
                  <h2>
                    <PlusCircle size={21} />
                    Submit a Complaint
                  </h2>

                  <p>
                    Report a civic issue in your area.
                  </p>
                </div>
              </div>

              {successMessage && (
                <div className="complaint-success">
                  {successMessage}
                </div>
              )}

              {formError && (
                <div className="complaint-form-error">
                  {formError}
                </div>
              )}

              <form
                className="complaint-form"
                onSubmit={handleComplaintSubmit}
              >
                <div className="complaint-form-grid">

                  {/* Category */}
                  <div className="complaint-form-field">
                    <label htmlFor="category_id">
                      Complaint Category
                    </label>

                    <select
                      id="category_id"
                      name="category_id"
                      value={formData.category_id}
                      onChange={handleInputChange}
                      required
                    >
                      <option value="">
                        Select a category
                      </option>

                      {categories.map(category => (
                        <option
                          key={category.category_id}
                          value={category.category_id}
                        >
                          {category.category_name}
                        </option>
                      ))}
                    </select>
                  </div>

                  {/* Location */}
                  <div className="complaint-form-field">
                    <label htmlFor="location_id">
                      Complaint Location
                    </label>

                    <select
                      id="location_id"
                      name="location_id"
                      value={formData.location_id}
                      onChange={handleInputChange}
                      required
                    >
                      <option value="">
                        Select a location
                      </option>

                      {locations.map(location => (
                        <option
                          key={location.location_id}
                          value={location.location_id}
                        >
                          {getLocationLabel(location)}
                        </option>
                      ))}
                    </select>
                  </div>

                  {/* Title */}
                  <div className="complaint-form-field full-width">
                    <label htmlFor="title">
                      Complaint Title
                    </label>

                    <input
                      id="title"
                      name="title"
                      type="text"
                      placeholder="Example: Road damage near school"
                      value={formData.title}
                      onChange={handleInputChange}
                      maxLength={200}
                      required
                    />
                  </div>

                  {/* Description */}
                  <div className="complaint-form-field full-width">
                    <label htmlFor="description">
                      Description
                    </label>

                    <textarea
                      id="description"
                      name="description"
                      placeholder="Describe the civic issue and where it is happening..."
                      value={formData.description}
                      onChange={handleInputChange}
                      rows={4}
                      required
                    />
                  </div>

                </div>

                <button
                  type="submit"
                  className="complaint-submit-button"
                  disabled={submitting}
                >
                  {submitting
                    ? 'Submitting...'
                    : 'Submit Complaint'}
                </button>
              </form>
            </section>

            {/* My complaints section */}
            <section className="citizen-complaints-section">

              <div className="citizen-section-heading">
                <div>
                  <h2>My Complaints</h2>

                  <p>
                    View and track your submitted complaints.
                  </p>
                </div>
              </div>

              {complaints.length === 0 ? (
                <div className="citizen-empty">
                  <FileText size={38} />

                  <h3>No complaints yet</h3>

                  <p>
                    Your submitted complaints will appear here.
                  </p>
                </div>
              ) : (
                <div className="citizen-complaint-list">

                  {complaints.map(complaint => {
                    const category = categories.find(
                      item =>
                        item.category_id === complaint.category_id
                    )

                    const location = locations.find(
                      item =>
                        item.location_id === complaint.location_id
                    )
                    const existingFeedback = feedbackList.find(
                       (feedback) => feedback.request_id === complaint.request_id
                    )
                    return (
                      <article
                        className="citizen-complaint-card"
                        key={complaint.request_id}
                      >

                        <div className="complaint-card-top">
                          <div>
                            <span className="complaint-id">
                              Complaint #{complaint.request_id}
                            </span>

                            <h3>{complaint.title}</h3>
                          </div>

                          <span
                            className={`complaint-status status-${complaint.status
                              .toLowerCase()
                              .replace(/\s+/g, '-')}`}
                          >
                            {complaint.status}
                          </span>
                        </div>

                        <p className="complaint-description">
                          {complaint.description}
                        </p>

                        <div className="complaint-details">

                          <span>
                            Category:{' '}
                            <strong>
                              {category?.category_name || 'Not available'}
                            </strong>
                          </span>

                          <span>
                            Location:{' '}
                            <strong>
                              {location
                                ? getLocationLabel(location)
                                : 'Not available'}
                            </strong>
                          </span>

                          <span>
                            Priority:{' '}
                            <strong>{complaint.priority}</strong>
                          </span>

                          <span>
                            Submitted:{' '}
                            <strong>
                              {formatDate(complaint.created_at)}
                            </strong>
                          </span>

                        </div>

                        <button
                          type="button"
                          className="view-complaint-button"
                          onClick={() => handleViewDetails(complaint)}
                        >
                          View Details
                        </button>
                        {['Submitted', 'Assigned'].includes(complaint.status) && (
                          <button
                             type="button"
                             className="cancel-complaint-button"
                             onClick={() => handleCancelComplaint(complaint.request_id)}
                           >
                            Cancel Complaint
                          </button>
                        )}  
                        {complaint.status === 'Resolved' && (
  feedbackList.some(
    (feedback) => feedback.request_id === complaint.request_id
  ) ? (
    <button
      type="button"
      className="feedback-button"
      onClick={() => {
        const existingFeedback = feedbackList.find(
          (feedback) => feedback.request_id === complaint.request_id
        )

        setSelectedFeedbackComplaint(complaint)
        setFeedbackRating(existingFeedback.rating)
        setFeedbackComment(existingFeedback.comments || '')
        setFeedbackError('')
        setFeedbackSuccess('')
      }}
    >
      Edit Feedback
    </button>
  ) : (
    <button
      type="button"
      className="feedback-button"
      onClick={() => {
        setSelectedFeedbackComplaint(complaint)
        setFeedbackRating(5)
        setFeedbackComment('')
        setFeedbackError('')
        setFeedbackSuccess('')
      }}
    >
      Give Feedback
    </button>
  )
)}
                      </article>
                    )
                  })}

                </div>
              )}

            </section>

            {/* Complaint details popup */}
            {selectedComplaint && (
              <div
                className="complaint-modal-overlay"
                onClick={closeComplaintDetails}
              >
                <div
                  className="complaint-modal"
                  onClick={(event) => event.stopPropagation()}
                >

                  {/* Popup header */}
                  <div className="complaint-modal-header">
                    <div>
                      <span className="complaint-id">
                        Complaint #{selectedComplaint.request_id}
                      </span>

                      <h2>Complaint Details</h2>
                    </div>

                    <button
                      type="button"
                      className="complaint-modal-close"
                      onClick={closeComplaintDetails}
                      aria-label="Close complaint details"
                    >
                      ×
                    </button>
                  </div>

                  {/* Loading state */}
                  {detailsLoading ? (
                    <p className="citizen-message">
                      Loading complaint details...
                    </p>
                  ) : detailsError ? (
                    <p className="complaint-form-error">
                      {detailsError}
                    </p>
                  ) : complaintDetails ? (
                    <>

                      {/* Complaint information */}
                      <div className="complaint-modal-information">

                        <h3>
                          {complaintDetails.complaint.title}
                        </h3>

                        <p>
                          {complaintDetails.complaint.description}
                        </p>

                        <div className="complaint-modal-grid">

                          <div>
                            <span>Category</span>

                            <strong>
                              {categories.find(
                                category =>
                                  category.category_id ===
                                  complaintDetails.complaint.category_id
                              )?.category_name || 'Not available'}
                            </strong>
                          </div>

                          <div>
                            <span>Location</span>

                            <strong>
                              {(() => {
                                const location = locations.find(
                                  item =>
                                    item.location_id ===
                                    complaintDetails.complaint.location_id
                                )

                                return location
                                  ? getLocationLabel(location)
                                  : 'Not available'
                              })()}
                            </strong>
                          </div>

                          <div>
                            <span>Priority</span>

                            <strong>
                              {complaintDetails.complaint.priority}
                            </strong>
                          </div>

                          <div>
                            <span>Current Status</span>

                            <strong>
                              {complaintDetails.complaint.status}
                            </strong>
                          </div>

                          <div>
                            <span>Submitted</span>

                            <strong>
                              {formatDate(
                                complaintDetails.complaint.created_at
                              )}
                            </strong>
                          </div>

                          <div>
                            <span>Resolved</span>

                            <strong>
                              {formatDate(
                                complaintDetails.complaint.resolved_at
                              )}
                            </strong>
                          </div>

                        </div>
                      </div>

                      {/* Status history */}
                      <div className="complaint-history">

                        <h3>Status History</h3>

                        {!complaintDetails.status_history ||
                        complaintDetails.status_history.length === 0 ? (
                          <p>No status history available.</p>
                        ) : (
                          <div className="complaint-history-list">

                            {complaintDetails.status_history.map(record => (
                              <div
                                className="complaint-history-item"
                                key={record.history_id}
                              >
                                <div className="history-marker"></div>

                                <div className="history-content">
                                  <strong>
                                    {record.new_status}
                                  </strong>

                                  {record.change_note && (
                                    <p>{record.change_note}</p>
                                  )}

                                  <span>
                                    {formatDate(record.changed_at)}
                                  </span>
                                </div>
                              </div>
                            ))}

                          </div>
                        )}

                      </div>

                      {/* Complaint Attachments */}
                      <div className="complaint-history">
                        <h3>Complaint Attachments</h3>

                        {attachments.length === 0 ? (
                          <p>No attachments uploaded yet.</p>
                        ) : (
                          <div className="complaint-history-list">
                            {attachments.map(attachment => (
                              <div
                                className="complaint-history-item"
                                key={attachment.attachment_id}
                              >
                                <div className="history-marker"></div>

                                <div className="history-content">
                                  <strong>{attachment.file_name}</strong>

                                  <p>
                                    Type: {attachment.attachment_type === 'complaint_photo'
                                      ? 'Complaint Photo'
                                      : attachment.attachment_type}
                                  </p>

                                  <span>
                                    Uploaded: {formatDate(attachment.uploaded_at)}
                                  </span>

                                  <button
                                    type="button"
                                    onClick={() => handleDownloadAttachment(attachment)}
                                  >
                                    Download
                                  </button>
                                </div>
                              </div>
                            ))}
                          </div>
                        )}

                        {['Submitted', 'Assigned', 'In Progress'].includes(
                          complaintDetails.complaint.status
                        ) && (
                          <div className="complaint-attachment-upload">
                            <h3>Upload Complaint Photo</h3>

                            <input
                              type="file"
                              accept=".jpg,.jpeg,.png,image/jpeg,image/png"
                              onChange={(event) => {
                                setSelectedFile(event.target.files[0] || null)
                                setAttachmentError('')
                                setAttachmentSuccess('')
                              }}
                            />

                            {selectedFile && (
                              <p>Selected file: {selectedFile.name}</p>
                            )}

                            {attachmentError && (
                              <p className="complaint-form-error">
                                {attachmentError}
                              </p>
                            )}

                            {attachmentSuccess && (
                              <p className="complaint-success">
                                {attachmentSuccess}
                              </p>
                            )}

                            <button
                              type="button"
                              onClick={handleUploadAttachment}
                              disabled={!selectedFile || uploadingAttachment}
                            >
                              {uploadingAttachment
                                ? 'Uploading...'
                                : 'Upload Photo'}
                            </button>
                          </div>
                        )}

                        {!['Submitted', 'Assigned', 'In Progress'].includes(
                          complaintDetails.complaint.status
                        ) && (
                          <p>
                            Photo uploads are unavailable for this complaint status.
                          </p>
                        )}
                      </div>

                    </>
                  ) : null}

                </div>
              </div>
            )}
{/* Feedback Modal */}
{selectedFeedbackComplaint && (
  <div className="feedback-modal-overlay">
    <div className="feedback-modal">

      <div className="feedback-modal-header">
        <h2>
          {feedbackList.some(
            (feedback) =>
              feedback.request_id === selectedFeedbackComplaint.request_id
          )
            ? 'Edit Feedback'
            : 'Give Feedback'}
        </h2>

        <button
          type="button"
          onClick={() => setSelectedFeedbackComplaint(null)}
        >
          ×
        </button>
      </div>

      <p>
        Complaint: {selectedFeedbackComplaint.title}
      </p>

      {feedbackError && (
        <p className="feedback-error">{feedbackError}</p>
      )}

      <form
        onSubmit={(event) => {
          event.preventDefault()

          const existingFeedback = feedbackList.find(
            (feedback) =>
              feedback.request_id === selectedFeedbackComplaint.request_id
          )

          if (existingFeedback) {
            handleUpdateFeedback(existingFeedback.feedback_id)
          } else {
            handleSubmitFeedback(selectedFeedbackComplaint.request_id)
          }
        }}
      >

        <div className="feedback-form-field">
          <label>Rating</label>

          <select
            value={feedbackRating}
            onChange={(event) => setFeedbackRating(event.target.value)}
          >
            <option value={5}>5 - Excellent</option>
            <option value={4}>4 - Very Good</option>
            <option value={3}>3 - Good</option>
            <option value={2}>2 - Fair</option>
            <option value={1}>1 - Poor</option>
          </select>
        </div>

        <div className="feedback-form-field">
          <label>Comments</label>

          <textarea
            value={feedbackComment}
            onChange={(event) => setFeedbackComment(event.target.value)}
            placeholder="Share your experience..."
            rows={4}
          />
        </div>

        <div className="feedback-modal-actions">
          <button
            type="button"
            onClick={() => setSelectedFeedbackComplaint(null)}
          >
            Cancel
          </button>

          <button
            type="submit"
            disabled={feedbackSubmitting}
          >
            {feedbackSubmitting
              ? 'Saving...'
              : feedbackList.some(
                  (feedback) =>
                    feedback.request_id === selectedFeedbackComplaint.request_id
                )
                ? 'Update Feedback'
                : 'Submit Feedback'}
          </button>
        </div>

      </form>
    </div>
  </div>
)}

          </>
        )}

      </main>
    </div>
  )
}

export default CitizenDashboard
