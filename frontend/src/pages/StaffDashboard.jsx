import { useEffect, useState } from 'react'
import {
  PieChart,
  Pie,
  Cell,
  Tooltip,
  ResponsiveContainer,
  Legend,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid
} from 'recharts'
import { useNavigate } from 'react-router-dom'
import {
  ClipboardList,
  Clock,
  CheckCircle,
  LogOut,
  RefreshCw
} from 'lucide-react'

import api, { clearAccessToken } from '../services/api'
import ThemeToggle from '../components/ThemeToggle'
import './StaffDashboard.css'

function StaffDashboard() {
  const navigate = useNavigate()

  const [user, setUser] = useState(null)
  const [assignments, setAssignments] = useState([])
  const [assignmentHistory, setAssignmentHistory] = useState([])
  const [currentPage, setCurrentPage] = useState(1)
const itemsPerPage = 5
  const [searchTerm, setSearchTerm] = useState('')
const [statusFilter, setStatusFilter] = useState('All')
const [priorityFilter, setPriorityFilter] = useState('All')
useEffect(() => {
  setCurrentPage(1)
}, [searchTerm, statusFilter, priorityFilter])
  const [categories, setCategories] = useState([])
const [locations, setLocations] = useState([])
const [departments, setDepartments] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  const [selectedComplaint, setSelectedComplaint] = useState(null)
const [newStatus, setNewStatus] = useState('In Progress')
const [changeNote, setChangeNote] = useState('')
const [updatingStatus, setUpdatingStatus] = useState(false)
const [statusError, setStatusError] = useState('')
const [statusSuccess, setStatusSuccess] = useState('')
const [complaintDetails, setComplaintDetails] = useState(null)
const [detailsLoading, setDetailsLoading] = useState(false)
const [detailsError, setDetailsError] = useState('')
const [attachments, setAttachments] = useState([])
const [selectedFile, setSelectedFile] = useState(null)
const [uploadingAttachment, setUploadingAttachment] = useState(false)
const [attachmentError, setAttachmentError] = useState('')
const [attachmentSuccess, setAttachmentSuccess] = useState('')
  const fetchDashboardData = async () => {
    try {
      setLoading(true)
      setError('')

     const [
  userResponse,
  assignmentsResponse,
  historyResponse,
  categoriesResponse,
  locationsResponse,
  departmentsResponse
] = await Promise.all([
  api.get('/auth/me'),
  api.get('/assignments/my-assignments'),
  api.get('/assignments/my-history'),
  api.get('/categories'),
  api.get('/locations'),
  api.get('/departments')
])

setUser(userResponse.data)
setAssignments(assignmentsResponse.data)
setAssignmentHistory(historyResponse.data)
setCategories(categoriesResponse.data)
setLocations(locationsResponse.data)
setDepartments(departmentsResponse.data)
    } catch (error) {
      if (error.response?.status === 401) {
        clearAccessToken()
        navigate('/login')
        return
      }

      setError(
        error.response?.data?.detail ||
        'Unable to load dashboard data. Please try again.'
      )
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchDashboardData()
  }, [])

  const handleLogout = () => {
    clearAccessToken()
    navigate('/login')
  }
  const handleViewDetails = async (requestId) => {
    try {
      setDetailsLoading(true)
      setDetailsError('')
      setComplaintDetails(null)
      setAttachments([])
      setSelectedFile(null)
      setAttachmentError('')
      setAttachmentSuccess('')

      const [detailsResponse, attachmentsResponse] = await Promise.all([
        api.get(`/service-requests/${requestId}`),
        api.get(`/attachments/request/${requestId}`)
      ])

      setComplaintDetails(detailsResponse.data)
      setAttachments(attachmentsResponse.data)

    } catch (error) {
      if (error.response?.status === 401) {
        clearAccessToken()
        navigate('/login', { replace: true })
        return
      }

      setDetailsError(
        error.response?.data?.detail ||
        'Unable to load complaint details and attachments.'
      )
    } finally {
      setDetailsLoading(false)
    }
  }

  // Upload resolution evidence
  const handleUploadAttachment = async () => {
    if (!selectedFile || !complaintDetails) {
      setAttachmentError('Please select an image first.')
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
    uploadData.append('attachment_type', 'resolution_evidence')

    try {
      setUploadingAttachment(true)
      setAttachmentError('')
      setAttachmentSuccess('')

      const requestId = complaintDetails.complaint.request_id

      const response = await api.post(
        `/attachments/upload/${requestId}`,
        uploadData
      )

      setAttachmentSuccess(
        response.data.message || 'Evidence uploaded successfully.'
      )

      setSelectedFile(null)

      const attachmentsResponse = await api.get(
        `/attachments/request/${requestId}`
      )

      setAttachments(attachmentsResponse.data)

    } catch (error) {
      setAttachmentError(
        error.response?.data?.detail ||
        'Unable to upload evidence. Please try again.'
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

    } catch (error) {
      setAttachmentError(
        error.response?.data?.detail ||
        'Unable to download this attachment.'
      )
    }
  }

  const handleStatusUpdate = async (event) => {
  event.preventDefault()

  if (!selectedComplaint) return

  if (changeNote.trim().length < 10 || changeNote.trim().length > 500) {
    setStatusError('Change note must contain between 10 and 500 characters.')
    return
  }

  try {
    setUpdatingStatus(true)
    setStatusError('')
    setStatusSuccess('')

    await api.patch(
      `/service-requests/${selectedComplaint.request_id}/status`,
      {
        status: newStatus,
        change_note: changeNote.trim()
      }
    )

    setStatusSuccess('Complaint status updated successfully.')

    setChangeNote('')
    setSelectedComplaint(null)

    await fetchDashboardData()

  } catch (error) {
    setStatusError(
      error.response?.data?.detail ||
      'Unable to update complaint status. Please try again.'
    )
  } finally {
    setUpdatingStatus(false)
  }
}
  const totalAssignments = assignments.length

  const inProgressCount = assignments.filter(
    (item) => item.status === 'In Progress'
  ).length

  const resolvedCount = assignments.filter(
    (item) => item.status === 'Resolved'
  ).length

  const assignedCount = assignments.filter(
    (item) => item.status === 'Assigned'
  ).length
  const statusChartData = [
  { name: 'Assigned', value: assignedCount },
  { name: 'In Progress', value: inProgressCount },
  { name: 'Resolved', value: resolvedCount }
]

const STATUS_COLORS = ['#3B82F6', '#F59E0B', '#10B981']
const priorityChartData = [
  {
    name: 'Low',
    value: assignments.filter(item => item.priority === 'Low').length
  },
  {
    name: 'Medium',
    value: assignments.filter(item => item.priority === 'Medium').length
  },
  {
    name: 'High',
    value: assignments.filter(item => item.priority === 'High').length
  },
  {
    name: 'Critical',
    value: assignments.filter(item => item.priority === 'Critical').length
  }
]

const PRIORITY_COLORS = ['#10B981', '#3B82F6', '#F59E0B', '#8B5CF6']
const complaintTrendData = Object.values(
  assignments.reduce((result, item) => {
    const date = item.assigned_at?.split('T')[0]

    if (date) {
      result[date] = result[date] || {
        date,
        complaints: 0
      }

      result[date].complaints += 1
    }

    return result
  }, {})
).sort((a, b) => a.date.localeCompare(b.date))
  const filteredAssignments = assignments.filter((item) => {
  const matchesSearch = item.title
    ?.toLowerCase()
    .includes(searchTerm.toLowerCase())

  const matchesStatus =
    statusFilter === 'All' || item.status === statusFilter

  const matchesPriority =
    priorityFilter === 'All' || item.priority === priorityFilter

  return matchesSearch && matchesStatus && matchesPriority
})
const totalPages = Math.ceil(filteredAssignments.length / itemsPerPage)

const startIndex = (currentPage - 1) * itemsPerPage

const paginatedAssignments = filteredAssignments.slice(
  startIndex,
  startIndex + itemsPerPage
)
 return (
  <div className="staff-dashboard">

    <header className="staff-header">
      <div>
        <h1>Staff Dashboard</h1>
        <p>Welcome, {user?.full_name || 'Staff Member'}</p>

<p className="staff-department-info">
  Department: {
    departments.find(
      department =>
        String(department.department_id) === String(user?.department_id)
    )?.department_name || 'Not assigned'
  }
</p>
      </div>

      <div className="staff-header-actions">
        <ThemeToggle />

        <button onClick={fetchDashboardData} className="staff-action-btn">
          <RefreshCw size={18} />
          Refresh
        </button>

        <button onClick={handleLogout} className="staff-action-btn logout-btn">
          <LogOut size={18} />
          Logout
        </button>
      </div>
    </header>

    {loading ? (
      <p className="staff-message">Loading dashboard...</p>
    ) : error ? (
      <div className="staff-error">
        {error}
        <button onClick={fetchDashboardData}>Try Again</button>
      </div>
    ) : (
      <>
        <section className="staff-stats">

          <div className="staff-stat-card">
            <ClipboardList size={25} />
            <div>
              <h3>{totalAssignments}</h3>
              <p>Current Assignments</p>
            </div>
          </div>

          <div className="staff-stat-card">
            <Clock size={25} />
            <div>
              <h3>{assignedCount}</h3>
              <p>Pending (Assigned)</p>
            </div>
          </div>

          <div className="staff-stat-card">
            <RefreshCw size={25} />
            <div>
              <h3>{inProgressCount}</h3>
              <p>In Progress</p>
            </div>
          </div>

          <div className="staff-stat-card">
            <CheckCircle size={25} />
            <div>
              <h3>{resolvedCount}</h3>
              <p>Resolved</p>
            </div>
          </div>

        </section>
<section className="staff-analytics-section">
  <h2>Complaint Analytics</h2>

  <div className="staff-charts-grid">
    <div className="staff-chart-card">
      <h3>Complaint Status Distribution</h3>

      <ResponsiveContainer width="100%" height={280}>
        <PieChart>
          <Pie
            data={statusChartData}
            dataKey="value"
            nameKey="name"
            cx="50%"
            cy="50%"
            outerRadius={90}
            label
          >
            {statusChartData.map((entry, index) => (
              <Cell
                key={`status-${index}`}
                fill={STATUS_COLORS[index]}
              />
            ))}
          </Pie>

          <Tooltip />
          <Legend />
        </PieChart>
      </ResponsiveContainer>
    </div>

    <div className="staff-chart-card">
      <h3>Complaint Priority Distribution</h3>

      <ResponsiveContainer width="100%" height={280}>
        <PieChart>
          <Pie
            data={priorityChartData}
            dataKey="value"
            nameKey="name"
            cx="50%"
            cy="50%"
            outerRadius={90}
            label
          >
            {priorityChartData.map((entry, index) => (
              <Cell
                key={`priority-${index}`}
                fill={PRIORITY_COLORS[index]}
              />
            ))}
          </Pie>

          <Tooltip />
          <Legend />
        </PieChart>
      </ResponsiveContainer>
    </div>
    <div className="staff-chart-card staff-trend-chart">
  <h3>Date-wise Complaint Assignment Trend</h3>

  <ResponsiveContainer width="100%" height={300}>
    <BarChart data={complaintTrendData}>
      <CartesianGrid strokeDasharray="3 3" />
      <XAxis dataKey="date" />
      <YAxis allowDecimals={false} />
      <Tooltip />
      <Legend />
      <Bar
        dataKey="complaints"
        name="Assigned Complaints"
        fill="#3B82F6"
        radius={[6, 6, 0, 0]}
      />
    </BarChart>
  </ResponsiveContainer>
</div>
  </div>
</section>
        <section className="staff-assignments-section">
          <h2>My Assigned Complaints</h2>
          <div className="staff-filters">

  <input
    type="text"
    placeholder="Search complaints by title..."
    value={searchTerm}
    onChange={(e) => setSearchTerm(e.target.value)}
  />

  <select
    value={statusFilter}
    onChange={(e) => setStatusFilter(e.target.value)}
  >
    <option value="All">All Statuses</option>
    <option value="Assigned">Assigned</option>
    <option value="In Progress">In Progress</option>
    <option value="Resolved">Resolved</option>
  </select>

  <select
    value={priorityFilter}
    onChange={(e) => setPriorityFilter(e.target.value)}
  >
    <option value="All">All Priorities</option>
    <option value="Low">Low</option>
    <option value="Medium">Medium</option>
    <option value="High">High</option>
    <option value="Critical">Critical</option>
  </select>

</div>

          {assignments.length === 0 ? (
  <div className="staff-empty-state">
    <ClipboardList size={40} />
    <h3>No Assignments Yet</h3>
    <p>You currently have no assigned complaints.</p>
  </div>
) : filteredAssignments.length === 0 ? (
  <div className="staff-empty-state">
    <ClipboardList size={40} />
    <h3>No Matching Complaints Found</h3>
    <p>Try changing your search or filters.</p>
  </div>
) : (
  <div className="staff-assignments-list">

    {paginatedAssignments.map((item) => (
                <div className="staff-assignment-card" key={item.assignment_id}>

                  <div className="staff-assignment-top">
                    <span>Request #{item.request_id}</span>
                    <span className="staff-status">{item.status}</span>
                  </div>

                  <h3>{item.title}</h3>
                  <p>{item.description}</p>
                  <div className="staff-assignment-category">
  <span>
    Category: {
      categories.find(
        category => category.category_id === item.category_id
      )?.category_name || 'Not available'
    }
  </span>

  <span>
  Department: {
    departments.find(department =>
      String(department.department_id) ===
      String(
        categories.find(
          category => category.category_id === item.category_id
        )?.department_id
      )
    )?.department_name || 'Not available'
  }
</span>
</div>

                  <div className="staff-assignment-details">
                    <span>
                      Priority: <strong>{item.priority}</strong>
                    </span>

                    <span>
                      Assigned: {
                        item.assigned_at
                          ? new Date(item.assigned_at).toLocaleDateString()
                          : 'Not available'
                      }
                    </span>

                    <span>
                      SLA Due: {
                        item.sla_due_at
                          ? new Date(item.sla_due_at).toLocaleDateString()
                          : 'Not available'
                      }
                    </span>
                  </div>

                  {item.assignment_notes && (
                    <div className="staff-assignment-notes">
                      <strong>Assignment Notes:</strong>
                      <p>{item.assignment_notes}</p>
                    </div>
                  )}
<button
  className="staff-view-details-btn"
  onClick={() => handleViewDetails(item.request_id)}
>
  View Details
</button>
                  {item.status !== 'Resolved' && (
                    <button
                      className="staff-update-btn"
                      onClick={() => {
                        setSelectedComplaint(item)
                       setNewStatus(
  item.status === 'Assigned' ? 'In Progress' : 'Resolved'
)
                        setChangeNote('')
                        setStatusError('')
                        setStatusSuccess('')
                      }}
                    >
                      Update Status
                    </button>
                  )}

                </div>
                            ))}
            </div>
          )}

          {filteredAssignments.length > 0 && (
            <div className="staff-pagination">
              <button
                disabled={currentPage === 1}
                onClick={() => setCurrentPage(currentPage - 1)}
              >
                Previous
              </button>

              <span>
                Page {currentPage} of {totalPages}
              </span>

              <button
                disabled={currentPage === totalPages}
                onClick={() => setCurrentPage(currentPage + 1)}
              >
                Next
              </button>
            </div>
          )}

        </section>
        <section className="staff-assignments-section staff-history-list-section">
  <h2>My Assignment History</h2>

  {assignmentHistory.filter(item => !item.is_current).length === 0 ? (
    <div className="staff-empty-state">
      <ClipboardList size={40} />
      <h3>No Assignment History</h3>
      <p>You haven't completed or previously handled any assignments yet.</p>
    </div>
  ) : (
    <div className="staff-assignments-list">
      {assignmentHistory
        .filter(item => !item.is_current)
        .map(item => (
          <div
            className="staff-assignment-card"
            key={item.assignment_id}
          >
            <div className="staff-assignment-top">
              <span>Request #{item.request_id}</span>
              <span className="staff-status">{item.status}</span>
            </div>

            <h3>{item.title}</h3>
            <p>{item.description}</p>

            <div className="staff-assignment-details">
              <span>
                Priority: <strong>{item.priority}</strong>
              </span>

              <span>
                Assigned: {
                  item.assigned_at
                    ? new Date(item.assigned_at).toLocaleDateString()
                    : 'Not available'
                }
              </span>

              <span>
                Resolved: {
                  item.resolved_at
                    ? new Date(item.resolved_at).toLocaleDateString()
                    : 'Not resolved'
                }
              </span>
            </div>

            {item.assignment_notes && (
              <div className="staff-assignment-notes">
                <strong>Assignment Notes:</strong>
                <p>{item.assignment_notes}</p>
              </div>
            )}

            <button
              className="staff-view-details-btn"
              onClick={() => handleViewDetails(item.request_id)}
            >
              View Details
            </button>
          </div>
        ))}
    </div>
  )}
</section>
                {selectedComplaint && (
          <div className="staff-modal-overlay">
            <div className="staff-modal">

              <h2>Update Complaint Status</h2>

              <p>
                Request #{selectedComplaint.request_id} - {selectedComplaint.title}
              </p>

              <form onSubmit={handleStatusUpdate}>

                <label htmlFor="staff-status">New Status</label>

                <select
  id="staff-status"
  value={newStatus}
  onChange={(event) => setNewStatus(event.target.value)}
>
  {selectedComplaint.status === 'Assigned' && (
    <option value="In Progress">In Progress</option>
  )}

  {selectedComplaint.status === 'In Progress' && (
    <option value="Resolved">Resolved</option>
  )}
</select>

                <label htmlFor="staff-change-note">Change Note</label>

                <textarea
                  id="staff-change-note"
                  value={changeNote}
                  onChange={(event) => setChangeNote(event.target.value)}
                  placeholder="Describe the work completed or progress made..."
                  minLength={10}
                  maxLength={500}
                  rows={4}
                  required
                />

                <p className="staff-character-count">
                  {changeNote.length}/500 characters (minimum 10)
                </p>

                {statusError && (
                  <p className="staff-form-error">{statusError}</p>
                )}

                {statusSuccess && (
                  <p className="staff-form-success">{statusSuccess}</p>
                )}

                <div className="staff-modal-actions">

                  <button
                    type="button"
                    onClick={() => setSelectedComplaint(null)}
                    disabled={updatingStatus}
                  >
                    Cancel
                  </button>

                  <button type="submit" disabled={updatingStatus}>
                    {updatingStatus ? 'Updating...' : 'Save Changes'}
                  </button>

                </div>

              </form>

            </div>
          </div>
        )}
        {(detailsLoading || detailsError || complaintDetails) && (
  <div className="staff-modal-overlay">
    <div className="staff-modal staff-details-modal">

      <div className="staff-details-header">
        <h2>Complaint Details</h2>

        <button
          type="button"
          onClick={() => {
  setComplaintDetails(null)
  setDetailsError('')
  setAttachments([])
  setSelectedFile(null)
  setAttachmentError('')
  setAttachmentSuccess('')
}}
        >
          ×
        </button>
      </div>

      {detailsLoading ? (
        <p className="staff-message">Loading complaint details...</p>
      ) : detailsError ? (
        <p className="staff-form-error">{detailsError}</p>
      ) : (
        <>
          <div className="staff-details-content">

            <h3>
              Request #{complaintDetails.complaint.request_id}
            </h3>
<div className="staff-citizen-info">
  <h3>Citizen Information</h3>

  <div className="staff-detail-item">
    <strong>Name:</strong>
    <span>{complaintDetails.citizen?.full_name || 'Not available'}</span>
  </div>

  <div className="staff-detail-item">
    <strong>Email:</strong>
    <span>{complaintDetails.citizen?.email || 'Not available'}</span>
  </div>

  <div className="staff-detail-item">
    <strong>Phone:</strong>
    <span>{complaintDetails.citizen?.phone || 'Not provided'}</span>
  </div>
</div>
            <div className="staff-detail-item">
              <strong>Title:</strong>
              <span>{complaintDetails.complaint.title}</span>
            </div>

            <div className="staff-detail-item">
              <strong>Description:</strong>
              <span>{complaintDetails.complaint.description}</span>
            </div>

            <div className="staff-detail-item">
              <strong>Priority:</strong>
              <span>{complaintDetails.complaint.priority}</span>
            </div>

            <div className="staff-detail-item">
              <strong>Status:</strong>
              <span>{complaintDetails.complaint.status}</span>
            </div>

           <div className="staff-detail-item">
  <strong>Category:</strong>
  <span>
    {categories.find(
      category =>
        category.category_id === complaintDetails.complaint.category_id
    )?.category_name || 'Not available'}
  </span>
</div>

           <div className="staff-detail-item">
  <strong>Location:</strong>
  <span>
    {locations.find(
      location =>
        location.location_id === complaintDetails.complaint.location_id
    )?.full_address || 'Not available'}
  </span>
</div>

            <div className="staff-detail-item">
              <strong>Submitted:</strong>
              <span>
                {complaintDetails.complaint.created_at
                  ? new Date(
                      complaintDetails.complaint.created_at
                    ).toLocaleString()
                  : 'Not available'}
              </span>
            </div>

            <div className="staff-detail-item">
              <strong>SLA Due:</strong>
              <span>
                {complaintDetails.complaint.sla_due_at
                  ? new Date(
                      complaintDetails.complaint.sla_due_at
                    ).toLocaleString()
                  : 'Not available'}
              </span>
            </div>

            <div className="staff-detail-item">
              <strong>Resolved At:</strong>
              <span>
                {complaintDetails.complaint.resolved_at
                  ? new Date(
                      complaintDetails.complaint.resolved_at
                    ).toLocaleString()
                  : 'Not resolved yet'}
              </span>
            </div>

          </div>

          <div className="staff-history-section">

            <h3>Status History</h3>

            {complaintDetails.status_history.length === 0 ? (
              <p>No status history available.</p>
            ) : (
              complaintDetails.status_history.map((history) => (
                <div
                  className="staff-history-item"
                  key={history.history_id}
                >
                  <h4>
                    {history.old_status || 'Initial'} → {history.new_status}
                  </h4>

                  <p>{history.change_note || 'No additional note.'}</p>

                  <span>
                    {history.changed_at
                      ? new Date(history.changed_at).toLocaleString()
                      : 'Date not available'}
                  </span>

                  <small>Updated by User #{history.changed_by}</small>
                </div>
              ))
            )}

          </div>

          {/* Complaint Attachments */}
          <div className="staff-history-section">
            <h3>Complaint Attachments</h3>

            {attachments.length === 0 ? (
              <p>No attachments uploaded yet.</p>
            ) : (
              attachments.map(attachment => (
                <div
                  className="staff-history-item"
                  key={attachment.attachment_id}
                >
                  <h4>{attachment.file_name}</h4>

                  <p>
                    Type: {attachment.attachment_type === 'complaint_photo'
                      ? 'Complaint Photo'
                      : 'Resolution Evidence'}
                  </p>

                  <span>
                    Uploaded: {
                      attachment.uploaded_at
                        ? new Date(attachment.uploaded_at).toLocaleString()
                        : 'Not available'
                    }
                  </span>

                  <button
                    type="button"
                    onClick={() => handleDownloadAttachment(attachment)}
                  >
                    Download
                  </button>
                </div>
              ))
            )}

            {['In Progress', 'Resolved'].includes(
              complaintDetails.complaint.status
            ) && (
              <div className="staff-attachment-upload">
                <h3>Upload Resolution Evidence</h3>

                <p>
                  Upload a JPG, JPEG or PNG image (maximum 5 MB).
                </p>

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
                  <p className="staff-form-error">
                    {attachmentError}
                  </p>
                )}

                {attachmentSuccess && (
                  <p className="staff-form-success">
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
                    : 'Upload Evidence'}
                </button>
              </div>
            )}

            {attachmentError && !['In Progress', 'Resolved'].includes(
              complaintDetails.complaint.status
            ) && (
              <p className="staff-form-error">
                {attachmentError}
              </p>
            )}
          </div>

        </>

      )}

    </div>
  </div>
)}
      </>
    )}

  </div>
)
}

export default StaffDashboard