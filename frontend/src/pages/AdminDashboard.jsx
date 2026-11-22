import { useEffect, useState } from 'react'
import {
  ClipboardList,
  Clock,
  CheckCircle,
  AlertTriangle,
  Star,
  Users,  
  LogOut
} from 'lucide-react'

import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell
} from 'recharts'

import {
  getComplaintOverview,
  getComplaintTrends,
  getCategoryAnalytics,
  getDepartmentAnalytics,
  getStaffWorkload,
  getSLAPerformance,
  getPriorityAnalytics,
  getResolutionTime,
  getFeedbackAnalytics
} from '../services/analyticsService'

import './AdminDashboard.css'
import { useNavigate } from 'react-router-dom'
import api, { clearAccessToken } from '../services/api'
import ThemeToggle from '../components/ThemeToggle'
import {
  getAllComplaints,
  getActiveStaff,
  assignComplaint,
  getComplaintDetails,
  getAllAssignments,
  createStaff,
  updateStaff,
  getDepartments,
  getAllStaff,
  updateStaffStatus,
  getAllAttachments
} from '../services/adminService'
import { getCategories } from '../services/categoryService'

const PRIORITY_COLORS = ['#D97777', '#E8A45D', '#438ED0', '#42A98B']

function EmptyState({ message = 'No data available yet.' }) {
  return <p className="chart-empty">{message}</p>
}

function AdminDashboard() {
  const navigate = useNavigate()

  const handleLogout = () => {
    clearAccessToken()
    navigate('/login')
  }
  const [analytics, setAnalytics] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  // Complaint Management
const [complaints, setComplaints] = useState([])
const [staffMembers, setStaffMembers] = useState([])
const [departmentList, setDepartmentList] = useState([])
const [managedStaff, setManagedStaff] = useState([])
const [staffSearchTerm, setStaffSearchTerm] = useState('')
const [staffDepartmentFilter, setStaffDepartmentFilter] = useState('')
const [staffStatusFilter, setStaffStatusFilter] = useState('')
const [staffStatusUpdating, setStaffStatusUpdating] = useState(null)
// Staff Management
const [showStaffForm, setShowStaffForm] = useState(false)
const [newStaffName, setNewStaffName] = useState('')
const [newStaffEmail, setNewStaffEmail] = useState('')
const [newStaffPassword, setNewStaffPassword] = useState('')
const [newStaffPhone, setNewStaffPhone] = useState('')
const [newStaffDepartment, setNewStaffDepartment] = useState('')
const [staffCreating, setStaffCreating] = useState(false)
const [staffMessage, setStaffMessage] = useState('')
const [staffError, setStaffError] = useState('')
// Edit Staff
const [editingStaff, setEditingStaff] = useState(null)
const [editStaffName, setEditStaffName] = useState('')
const [editStaffPhone, setEditStaffPhone] = useState('')
const [editStaffDepartment, setEditStaffDepartment] = useState('')
const [staffUpdating, setStaffUpdating] = useState(false)
const [assignments, setAssignments] = useState([])
const [complaintCategories, setComplaintCategories] = useState([])
const [complaintsLoading, setComplaintsLoading] = useState(true)
const [complaintError, setComplaintError] = useState('')

const [searchTerm, setSearchTerm] = useState('')
const [statusFilter, setStatusFilter] = useState('')
const [priorityFilter, setPriorityFilter] = useState('')

const [selectedComplaint, setSelectedComplaint] = useState(null)
const [openActionMenuId, setOpenActionMenuId] = useState(null)
const [complaintDetails, setComplaintDetails] = useState(null)
const [detailsLoading, setDetailsLoading] = useState(false)
const [detailsError, setDetailsError] = useState('')
const [selectedStaff, setSelectedStaff] = useState('')
const [assignmentNotes, setAssignmentNotes] = useState('')
const [assignmentLoading, setAssignmentLoading] = useState(false)
const [assignmentMessage, setAssignmentMessage] = useState('')
// Admin Attachment Management
const [allAttachments, setAllAttachments] = useState([])
const [attachmentsLoading, setAttachmentsLoading] = useState(false)
const [attachmentsError, setAttachmentsError] = useState('')
  useEffect(() => {
    const fetchAnalytics = async () => {
      const token = localStorage.getItem('civictrack_access_token')

      if (!token) {
  navigate('/login', { replace: true })
  return
}

      try {
        const [
          overview,
          trends,
          categories,
          departments,
          staff,
          sla,
          priority,
          resolution,
          feedback
        ] = await Promise.all([
          getComplaintOverview(),
          getComplaintTrends(),
          getCategoryAnalytics(),
          getDepartmentAnalytics(),
          getStaffWorkload(),
          getSLAPerformance(),
          getPriorityAnalytics(),
          getResolutionTime(),
          getFeedbackAnalytics()
        ])

        setAnalytics({
          overview,
          trends,
          categories,
          departments,
          staff,
          sla,
          priority,
          resolution,
          feedback
        })
      } catch (err) {
        setError(
          err.response?.data?.detail ||
          'Unable to load analytics. Please check your login and backend.'
        )
      } finally {
        setLoading(false)
      }
    }

    fetchAnalytics()
    }, [navigate])

    // Fetch complaints and active staff members
useEffect(() => {
  const fetchComplaintData = async () => {
    try {
      setComplaintsLoading(true)
      setComplaintError('')

     const [complaintData, staffData, categoryData, assignmentData, departmentData,managedStaffData] =
  await Promise.all([
    getAllComplaints({
      search: searchTerm || undefined,
      status: statusFilter || undefined,
      priority: priorityFilter || undefined
    }),
    getActiveStaff(),
    getCategories(),
    getAllAssignments(),
    getDepartments(),
    getAllStaff(),
  ])

setComplaints(complaintData)
setStaffMembers(staffData)
setDepartmentList(departmentData)
setComplaintCategories(categoryData)
setAssignments(assignmentData)
setManagedStaff(managedStaffData)
    } catch (err) {
      setComplaintError(
        err.response?.data?.detail ||
        'Unable to load complaints. Please try again.'
      )
    } finally {
      setComplaintsLoading(false)
    }
  }

  fetchComplaintData()
}, [searchTerm, statusFilter, priorityFilter])
// Fetch all complaint attachments (Admin only)
useEffect(() => {
  const fetchAttachments = async () => {
    try {
      setAttachmentsLoading(true)
      setAttachmentsError('')

      const attachmentData = await getAllAttachments()
      setAllAttachments(attachmentData)
    } catch (err) {
      setAttachmentsError(
        err.response?.data?.detail ||
        'Unable to load attachments. Please try again.'
      )
    } finally {
      setAttachmentsLoading(false)
    }
  }

  fetchAttachments()
}, [])

  if (loading) {
    return <div className="dashboard-message">Loading dashboard...</div>
  }

  if (error) {
    return <div className="dashboard-message error-message">{error}</div>
  }

  const {
    overview,
    trends,
    categories,
    departments,
    staff,
    sla,
    priority,
    resolution,
    feedback
  } = analytics

  const kpis = [
    {
      title: 'Total Complaints',
      value: overview.total_complaints,
      icon: ClipboardList,
      color: 'blue'
    },
    {
      title: 'Submitted',
      value: overview.submitted_complaints,
      icon: Clock,
      color: 'purple'
    },
    {
      title: 'In Progress',
      value: overview.in_progress_complaints,
      icon: Users,
      color: 'orange'
    },
    {
      title: 'Resolved',
      value: overview.resolved_complaints,
      icon: CheckCircle,
      color: 'green'
    },
    {
      title: 'Overdue',
      value: overview.overdue_complaints,
      icon: AlertTriangle,
      color: 'red'
    },
    {
      title: 'Average Rating',
      value: `${overview.average_feedback_rating ?? 0} / 5`,
      icon: Star,
      color: 'teal'
    }
  ]

  const trendData = trends.trends || []
  const categoryData = categories.categories || []
  const departmentData = departments.departments || []
  const staffData = staff.staff_workload || []
  const priorityData = priority.priorities || []
  const feedbackData = feedback.rating_distribution || []

  const slaPercentage = Math.min(
    100,
    Math.max(0, Number(sla.sla_compliance_percentage) || 0)
  )
// Find the department of the selected complaint
const selectedCategory = selectedComplaint
  ? complaintCategories.find(
      category => category.category_id === selectedComplaint.category_id
    )
  : null

// Show only staff from the matching department
const eligibleStaff = selectedCategory
  ? staffMembers.filter(
      staff => staff.department_id === selectedCategory.department_id
    )
  : []

  const complaintAssignmentHistory = complaintDetails?.complaint
  ? assignments.filter(
      assignment =>
        assignment.request_id === complaintDetails.complaint.request_id
    )
  : []

  const handleAssignComplaint = async () => {
  if (!selectedComplaint || !selectedStaff) return

  try {
    setAssignmentLoading(true)
    setComplaintError('')
    setAssignmentMessage('')

    await assignComplaint({
      request_id: selectedComplaint.request_id,
      staff_id: Number(selectedStaff),
      notes: assignmentNotes.trim() || null
    })

    setAssignmentMessage('Complaint assigned successfully.')

    setSelectedComplaint(null)
    setSelectedStaff('')
    setAssignmentNotes('')

    // Refresh the complaint list
    try {
      const [updatedComplaints, updatedAssignments] = await Promise.all([
  getAllComplaints({
    search: searchTerm || undefined,
    status: statusFilter || undefined,
    priority: priorityFilter || undefined
  }),
  getAllAssignments()
])

setComplaints(updatedComplaints)
setAssignments(updatedAssignments)
    } catch {
      setComplaintError(
        'Assignment succeeded, but the complaint list could not be refreshed.'
      )
    }

  } catch (err) {
    setComplaintError(
      err.response?.data?.detail ||
      'Unable to assign complaint. Please try again.'
    )
  } finally {
    setAssignmentLoading(false)
  }
}

const handleCreateStaff = async (e) => {
  e.preventDefault()

  try {
    setStaffCreating(true)
    setStaffError('')
    setStaffMessage('')

    await createStaff({
      full_name: newStaffName.trim(),
      email: newStaffEmail.trim(),
      password: newStaffPassword,
      phone: newStaffPhone.trim() || null,
      department_id: Number(newStaffDepartment)
    })

    setStaffMessage('Staff member created successfully.')

    setNewStaffName('')
    setNewStaffEmail('')
    setNewStaffPassword('')
    setNewStaffPhone('')
    setNewStaffDepartment('')
    setShowStaffForm(false)

    const [updatedStaff, allStaffData] = await Promise.all([
  getActiveStaff(),
  getAllStaff()
])

setStaffMembers(updatedStaff)
setManagedStaff(allStaffData)
  } catch (err) {
    setStaffError(
      err.response?.data?.detail ||
      'Unable to create staff member. Please try again.'
    )
  } finally {
    setStaffCreating(false)
  }
}
const handleUpdateStaff = async (e) => {
  e.preventDefault()

  if (!editingStaff) return

  try {
    setStaffUpdating(true)
    setStaffError('')
    setStaffMessage('')

    await updateStaff(editingStaff.user_id, {
      full_name: editStaffName.trim(),
      phone: editStaffPhone.trim() || null,
      department_id: Number(editStaffDepartment)
    })

    setStaffMessage('Staff member updated successfully.')
    setEditingStaff(null)

   const [updatedStaff, allStaffData] = await Promise.all([
  getActiveStaff(),
  getAllStaff()
])

setStaffMembers(updatedStaff)
setManagedStaff(allStaffData)

  } catch (err) {
    setStaffError(
      err.response?.data?.detail ||
      'Unable to update staff member. Please try again.'
    )
  } finally {
    setStaffUpdating(false)
  }
}
const handleToggleStaffStatus = async (staff) => {
  const nextStatus = !staff.is_active

  try {
    setStaffStatusUpdating(staff.user_id)
    setStaffError('')
    setStaffMessage('')

    const result = await updateStaffStatus(
      staff.user_id,
      nextStatus
    )

    setStaffMessage(result.message)

    const [activeStaffData, allStaffData] = await Promise.all([
      getActiveStaff(),
      getAllStaff()
    ])

    setStaffMembers(activeStaffData)
    setManagedStaff(allStaffData)

  } catch (err) {
    setStaffError(
      err.response?.data?.detail ||
      'Unable to update staff status. Please try again.'
    )
  } finally {
    setStaffStatusUpdating(null)
  }
}
const handleViewComplaint = async (requestId) => {
  try {
    setDetailsLoading(true)
    setDetailsError('')
    setComplaintDetails(null)

    const data = await getComplaintDetails(requestId)

    setComplaintDetails(data)
  } catch (err) {
    setDetailsError(
      err.response?.data?.detail ||
      'Unable to load complaint details. Please try again.'
    )
  } finally {
    setDetailsLoading(false)
  }
}// Download complaint attachment (Admin only)
const handleDownloadAttachment = async (attachmentId, fileName) => {
  try {
    const response = await api.get(
      `/attachments/${attachmentId}/download`,
      { responseType: 'blob' }
    )

    const url = window.URL.createObjectURL(response.data)
    const link = document.createElement('a')

    link.href = url
    link.download = fileName
    document.body.appendChild(link)
    link.click()

    link.remove()
    window.URL.revokeObjectURL(url)
  } catch (err) {
    setAttachmentsError('Unable to download attachment. Please try again.')
  }
}
const filteredStaffMembers = managedStaff.filter((staff) => {
  const searchValue = staffSearchTerm.toLowerCase().trim()

  const matchesSearch =
    staff.full_name.toLowerCase().includes(searchValue) ||
    staff.email.toLowerCase().includes(searchValue)

  const matchesDepartment =
    !staffDepartmentFilter ||
    String(staff.department_id) === staffDepartmentFilter

  const matchesStatus =
    !staffStatusFilter ||
    (staffStatusFilter === 'active'
      ? staff.is_active
      : !staff.is_active)

  return matchesSearch && matchesDepartment && matchesStatus
})
  return (
    <div className="admin-dashboard">

      <header className="dashboard-header">
        <div>
          <span className="dashboard-tag">
            CIVICTRACK ADMINISTRATION
          </span>

          <h1>Analytics Dashboard</h1>

          <p>
            Monitor complaints and public service performance.
          </p>
        </div>

<div className="dashboard-header-actions">
  <ThemeToggle />

  <span className="admin-status">Administrator</span>

  <button
    className="logout-button"
    onClick={handleLogout}
  >
    <LogOut size={16} />
    <span>Logout</span>
  </button>
</div>
</header>
{/* Complaint Management Section */}
<section className="admin-complaints-section">
  <div className="admin-complaints-heading">
    <div>
      <h2>Complaint Management</h2>
      <p>View complaints and assign them to the appropriate staff members.</p>
    </div>
  </div>

  {assignmentMessage && (
    <div className="admin-complaints-success">
      {assignmentMessage}
    </div>
  )}

  {complaintError && (
    <div className="admin-complaints-error">
      {complaintError}
    </div>
  )}

  <div className="admin-complaints-filters">
    <input
      type="text"
      placeholder="Search complaints..."
      value={searchTerm}
      onChange={(e) => setSearchTerm(e.target.value)}
    />

    <select
      value={statusFilter}
      onChange={(e) => setStatusFilter(e.target.value)}
    >
      <option value="">All Statuses</option>
      <option value="Submitted">Submitted</option>
      <option value="Assigned">Assigned</option>
      <option value="In Progress">In Progress</option>
      <option value="Resolved">Resolved</option>
      <option value="Cancelled">Cancelled</option>
      <option value="Closed">Closed</option>
    </select>

    <select
      value={priorityFilter}
      onChange={(e) => setPriorityFilter(e.target.value)}
    >
      <option value="">All Priorities</option>
      <option value="Low">Low</option>
      <option value="Medium">Medium</option>
      <option value="High">High</option>
      <option value="Urgent">Urgent</option>
      <option value="Critical">Critical</option>
    </select>
  </div>

  {complaintsLoading ? (
    <p>Loading complaints...</p>
  ) : complaints.length === 0 ? (
    <p className="admin-complaints-empty">No complaints found.</p>
  ) : (
    <div className="admin-complaints-table-wrapper">
      <table className="admin-complaints-table">
        <thead>
          <tr>
            <th>ID</th>
            <th>Complaint</th>
            <th>Category</th>
            <th>Priority</th>
            <th>Status</th>
            <th>Date</th>
            <th>Action</th>
          </tr>
        </thead>

        <tbody>
          {complaints.map((complaint) => {
            const category = complaintCategories.find(
              (item) => item.category_id === complaint.category_id
            )

            return (
              <tr key={complaint.request_id}>
                <td>#{complaint.request_id}</td>
                <td>{complaint.title}</td>
                <td>{category?.category_name || 'Unknown'}</td>
                <td>{complaint.priority}</td>
                <td>{complaint.status}</td>
                <td>
                  {complaint.created_at
                    ? new Date(complaint.created_at).toLocaleDateString()
                    : '-'}
                </td>
               <td>
  <div className="admin-action-menu-wrapper">
    <button
      type="button"
      className="admin-action-menu-trigger"
      onClick={() =>
        setOpenActionMenuId(
          openActionMenuId === complaint.request_id
            ? null
            : complaint.request_id
        )
      }
    >
      ⋯
    </button>

    {openActionMenuId === complaint.request_id && (
      <div className="admin-action-dropdown">
        <button
          type="button"
          onClick={() => {
            handleViewComplaint(complaint.request_id)
            setOpenActionMenuId(null)
          }}
        >
          View Details
        </button>

        {['Submitted', 'Assigned'].includes(complaint.status) && (
          <button
            type="button"
            onClick={() => {
              setSelectedComplaint(complaint)
              setSelectedStaff('')
              setAssignmentNotes('')
              setAssignmentMessage('')
              setOpenActionMenuId(null)
            }}
          >
            Assign Complaint
          </button>
        )}
      </div>
    )}
  </div>
</td>
              </tr>
            )
          })}
        </tbody>
      </table>
    </div>
  )}

  {selectedComplaint && (
    <div className="admin-complaints-assignment">
      <h3>Assign Complaint #{selectedComplaint.request_id}</h3>
      <p>{selectedComplaint.title}</p>

      <label htmlFor="staff-selection">Select Staff Member</label>
      <select
        id="staff-selection"
        value={selectedStaff}
        onChange={(e) => setSelectedStaff(e.target.value)}
      >
        <option value="">Choose staff member</option>
        {eligibleStaff.map((staff) => (
          <option key={staff.user_id} value={staff.user_id}>
            {staff.full_name}
          </option>
        ))}
      </select>

      {eligibleStaff.length === 0 && (
        <p>No active staff members are available in this department.</p>
      )}

      <label htmlFor="assignment-notes">Assignment Notes (Optional)</label>
      <textarea
        id="assignment-notes"
        value={assignmentNotes}
        onChange={(e) => setAssignmentNotes(e.target.value)}
        placeholder="Enter assignment instructions..."
        maxLength={500}
      />

      <div className="admin-complaints-assignment-actions">
        <button
          type="button"
          onClick={handleAssignComplaint}
          disabled={!selectedStaff || assignmentLoading}
        >
          {assignmentLoading ? 'Assigning...' : 'Confirm Assignment'}
        </button>

        <button
          type="button"
          onClick={() => {
            setSelectedComplaint(null)
            setSelectedStaff('')
            setAssignmentNotes('')
          }}
        >
          Cancel
        </button>
      </div>
    </div>
  )}
</section>
{/* Staff Management */}
<section className="admin-staff-section">
  <div className="admin-staff-header">
    <div>
      <h2>Staff Management</h2>
      <p>Manage staff members and their department assignments.</p>
    </div>

    <button
      type="button"
      onClick={() => {
        setShowStaffForm(!showStaffForm)
        setStaffError('')
        setStaffMessage('')
      }}
    >
      {showStaffForm ? 'Cancel' : '+ Add Staff Member'}
    </button>
  </div>

  {staffMessage && (
    <p className="admin-staff-success">{staffMessage}</p>
  )}

  {staffError && (
    <p className="admin-staff-error">{staffError}</p>
  )}

  {showStaffForm && (
    <form onSubmit={handleCreateStaff} className="admin-staff-form">
      <input
        type="text"
        placeholder="Full Name"
        value={newStaffName}
        onChange={(e) => setNewStaffName(e.target.value)}
        required
        minLength={2}
      />

      <input
        type="email"
        placeholder="Email Address"
        value={newStaffEmail}
        onChange={(e) => setNewStaffEmail(e.target.value)}
        required
      />

      <input
        type="password"
        placeholder="Password (minimum 8 characters)"
        value={newStaffPassword}
        onChange={(e) => setNewStaffPassword(e.target.value)}
        required
        minLength={8}
      />

      <input
        type="tel"
        placeholder="Phone Number (optional)"
        value={newStaffPhone}
        onChange={(e) => setNewStaffPhone(e.target.value)}
      />

      <select
        value={newStaffDepartment}
        onChange={(e) => setNewStaffDepartment(e.target.value)}
        required
      >
        <option value="">Select Department</option>

        {departmentList
          .filter((department) => department.is_active)
          .map((department) => (
            <option
              key={department.department_id}
              value={department.department_id}
            >
              {department.department_name}
            </option>
          ))}
      </select>

      <button type="submit" disabled={staffCreating}>
        {staffCreating ? 'Creating...' : 'Create Staff Account'}
      </button>
    </form>
  )}
{editingStaff && (
  <form onSubmit={handleUpdateStaff} className="admin-staff-form">
    <h3>Edit Staff Member</h3>

    <input
      type="text"
      placeholder="Full Name"
      value={editStaffName}
      onChange={(e) => setEditStaffName(e.target.value)}
      required
      minLength={2}
    />

    <input
      type="tel"
      placeholder="Phone Number (optional)"
      value={editStaffPhone}
      onChange={(e) => setEditStaffPhone(e.target.value)}
    />

    <select
      value={editStaffDepartment}
      onChange={(e) => setEditStaffDepartment(e.target.value)}
      required
    >
      <option value="">Select Department</option>

      {departmentList
        .filter((department) => department.is_active)
        .map((department) => (
          <option
            key={department.department_id}
            value={department.department_id}
          >
            {department.department_name}
          </option>
        ))}
    </select>

    <button type="submit" disabled={staffUpdating}>
      {staffUpdating ? 'Updating...' : 'Save Changes'}
    </button>

    <button
      type="button"
      onClick={() => setEditingStaff(null)}
    >
      Cancel
    </button>
  </form>
)}
  <div className="admin-staff-list">
    <h3>Staff Members ({filteredStaffMembers.length})</h3>
<div className="admin-staff-filters">

  <input
    type="text"
    placeholder="Search by name or email..."
    value={staffSearchTerm}
    onChange={(e) => setStaffSearchTerm(e.target.value)}
  />

  <select
    value={staffDepartmentFilter}
    onChange={(e) => setStaffDepartmentFilter(e.target.value)}
  >
    <option value="">All Departments</option>

    {departmentList.map((department) => (
      <option
        key={department.department_id}
        value={String(department.department_id)}
      >
        {department.department_name}
      </option>
    ))}
  </select>

  <select
    value={staffStatusFilter}
    onChange={(e) => setStaffStatusFilter(e.target.value)}
  >
    <option value="">All Statuses</option>
    <option value="active">Active</option>
    <option value="inactive">Inactive</option>
  </select>

</div>
   {filteredStaffMembers.length === 0 ? (
  <p>No staff members match your filters.</p>
    ) : (
      <div className="admin-staff-grid">
        {filteredStaffMembers.map((staff) => (
         <div className="admin-staff-card" key={staff.user_id}>
  <h4>{staff.full_name}</h4>
  <p>{staff.email}</p>
  <span>
    {departmentList.find(
      (department) =>
        department.department_id === staff.department_id
    )?.department_name || 'Unknown Department'}
  </span>
<p className={`staff-status ${staff.is_active ? 'active' : 'inactive'}`}>
  {staff.is_active ? 'Active' : 'Inactive'}
</p>

<button
  type="button"
  className={`staff-status-toggle ${
  staff.is_active ? 'deactivate' : 'activate'
}`}
  onClick={() => handleToggleStaffStatus(staff)}
  disabled={staffStatusUpdating === staff.user_id}
>
  {staffStatusUpdating === staff.user_id
    ? 'Updating...'
    : staff.is_active
      ? 'Deactivate'
      : 'Activate'}
</button>
  <button
    type="button"
    onClick={() => {
      setEditingStaff(staff)
      setEditStaffName(staff.full_name)
      setEditStaffPhone(staff.phone || '')
      setEditStaffDepartment(String(staff.department_id))
      setShowStaffForm(false)
      setStaffMessage('')
      setStaffError('')
    }}
  >
    Edit Staff
  </button>
</div>
        ))}
      </div>
    )}
  </div>
</section>
{/* Admin Attachment Management */}
<section className="admin-attachments-section">
  <div className="admin-attachments-header">
    <div>
      <h2>Complaint Attachments</h2>
      <p>View and download photos and resolution evidence uploaded for complaints.</p>
    </div>
    <span>Total: {allAttachments.length}</span>
  </div>

  {attachmentsError && (
    <p className="admin-attachments-error">{attachmentsError}</p>
  )}

  {attachmentsLoading ? (
    <p>Loading attachments...</p>
  ) : allAttachments.length === 0 ? (
    <p>No complaint attachments available.</p>
  ) : (
    <div className="admin-attachments-table-wrapper">
      <table className="admin-attachments-table">
        <thead>
          <tr>
            <th>Attachment ID</th>
            <th>Complaint ID</th>
            <th>File Name</th>
            <th>Attachment Type</th>
            <th>Uploaded By</th>
            <th>Uploaded On</th>
            <th>Action</th>
          </tr>
        </thead>

        <tbody>
          {allAttachments.map((attachment) => (
            <tr key={attachment.attachment_id}>
              <td>#{attachment.attachment_id}</td>
              <td>#{attachment.request_id}</td>
              <td>{attachment.file_name}</td>
              <td>
                {attachment.attachment_type === 'complaint_photo'
                  ? 'Complaint Photo'
                  : 'Resolution Evidence'}
              </td>
              <td>User #{attachment.uploaded_by}</td>
              <td>
                {attachment.uploaded_at
                  ? new Date(attachment.uploaded_at).toLocaleString()
                  : '-'}
              </td>
              <td>
                <button
                  type="button"
                  onClick={() =>
                    handleDownloadAttachment(
                      attachment.attachment_id,
                      attachment.file_name
                    )
                  }
                >
                  Download
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )}
</section>
{/* Complaint Details Popup */}
{(detailsLoading || detailsError || complaintDetails) && (
  <div className="admin-details-overlay">
    <div className="admin-details-modal">

      <div className="admin-details-header">
        <div>
          <h2>Complaint Details</h2>
          {complaintDetails?.complaint && (
            <p>
              Complaint #{complaintDetails.complaint.request_id}
            </p>
          )}
        </div>

        <button
          type="button"
          onClick={() => {
            setComplaintDetails(null)
            setDetailsError('')
          }}
        >
          ×
        </button>
      </div>

      {detailsLoading ? (
        <p>Loading complaint details...</p>
      ) : detailsError ? (
        <p className="admin-complaints-error">
          {detailsError}
        </p>
      ) : complaintDetails?.complaint && (
        <>
          <div className="admin-details-content">
            <h3>{complaintDetails.complaint.title}</h3>

            <div className="admin-details-grid">
              <div>
                <span>Category</span>
                <strong>
                  {complaintCategories.find(
                    category =>
                      category.category_id ===
                      complaintDetails.complaint.category_id
                  )?.category_name || 'Unknown'}
                </strong>
              </div>

              <div>
                <span>Priority</span>
                <strong>
                  {complaintDetails.complaint.priority}
                </strong>
              </div>

              <div>
                <span>Status</span>
                <strong>
                  {complaintDetails.complaint.status}
                </strong>
              </div>

              <div>
                <span>Citizen ID</span>
                <strong>
                  {complaintDetails.complaint.citizen_id}
                </strong>
              </div>

              <div>
                <span>Location ID</span>
                <strong>
                  {complaintDetails.complaint.location_id}
                </strong>
              </div>

              <div>
                <span>Submitted On</span>
                <strong>
                  {new Date(
                    complaintDetails.complaint.created_at
                  ).toLocaleString()}
                </strong>
              </div>
            </div>

            <div className="admin-details-description">
              <h4>Description</h4>
              <p>
                {complaintDetails.complaint.description}
              </p>
            </div>

            <div className="admin-details-history">
              <h4>Status History</h4>

              {complaintDetails.status_history.length === 0 ? (
                <p>No status history available.</p>
              ) : (
                <div className="admin-history-list">
                  {complaintDetails.status_history.map(history => (
                    <div
                      className="admin-history-item"
                      key={history.history_id}
                    >
                      <div className="admin-history-dot"></div>

                      <div>
                        <strong>
                          {history.old_status
                            ? `${history.old_status} → ${history.new_status}`
                            : history.new_status}
                        </strong>

                        <p>{history.change_note}</p>

                        <span>
                          Changed by User #{history.changed_by}
                        </span>

                        <span>
                          {new Date(
                            history.changed_at
                          ).toLocaleString()}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
            <div className="admin-details-history">
  <h4>Assignment History</h4>

  {complaintAssignmentHistory.length === 0 ? (
    <p>No assignment history available.</p>
  ) : (
    <div className="admin-history-list">
      {complaintAssignmentHistory.map(assignment => {
        const staff = managedStaff.find(
          member => member.user_id === assignment.staff_id
        )

        return (
          <div
            className="admin-history-item"
            key={assignment.assignment_id}
          >
            <div className="admin-history-dot"></div>

            <div>
              <strong>
                Assigned to {staff?.full_name || `Staff #${assignment.staff_id}`}
              </strong>

              <p>
                {assignment.notes || 'No assignment notes provided.'}
              </p>

              <span>
                {assignment.is_current
                  ? 'Current assignment'
                  : 'Previous assignment'}
              </span>

              <span>
                Assigned on {new Date(assignment.assigned_at).toLocaleString()}
              </span>
            </div>
          </div>
        )
      })}
    </div>
  )}
</div>
          </div>
        </>
      )}
    </div>
  </div>
)}
      {/* KPI CARDS */}
      <section className="kpi-grid">
        {kpis.map((item) => {
          const Icon = item.icon

          return (
            <div className="kpi-card" key={item.title}>
              <div className={`kpi-indicator ${item.color}`} />

              <div className="kpi-card-content">
                <div className={`kpi-icon ${item.color}`}>
                  <Icon size={20} />
                </div>

                <p>{item.title}</p>
                <h2>{item.value}</h2>
              </div>
            </div>
          )
        })}
      </section>

      {/* CHARTS */}
      <section className="analytics-grid">

        {/* MONTHLY TRENDS */}
        <div className="analytics-card">
          <h3>Monthly Complaint Trends</h3>
          <p>Submitted and resolved complaints</p>

          {trendData.length === 0 ? (
            <EmptyState />
          ) : (
            <div className="chart-container">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={trendData}>
                  <CartesianGrid
                    strokeDasharray="3 3"
                    vertical={false}
                    stroke="#E9EEF5"
                  />

                  <XAxis
                    dataKey="month"
                    tick={{ fontSize: 11 }}
                    axisLine={false}
                    tickLine={false}
                  />

                  <YAxis
                    allowDecimals={false}
                    tick={{ fontSize: 11 }}
                    axisLine={false}
                    tickLine={false}
                  />

                  <Tooltip />
                  <Legend />

                  <Line
                    type="monotone"
                    dataKey="submitted"
                    name="Submitted"
                    stroke="#438ED0"
                    strokeWidth={3}
                    dot={{ r: 4 }}
                  />

                  <Line
                    type="monotone"
                    dataKey="resolved"
                    name="Resolved"
                    stroke="#42A98B"
                    strokeWidth={3}
                    dot={{ r: 4 }}
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>
          )}
        </div>

        {/* SLA PERFORMANCE */}
        <div className="analytics-card">
          <h3>SLA Performance</h3>
          <p>Service-level agreement compliance</p>

          <div className="sla-chart-content">
            <div className="sla-percentage">
              {sla.sla_compliance_percentage ?? 0}%
            </div>

            <div className="sla-progress-track">
              <div
                className="sla-progress-fill"
                style={{ width: `${slaPercentage}%` }}
              />
            </div>

            <span className="sla-caption">
              SLA compliance percentage
            </span>
          </div>

          <div className="sla-details">
            <div>
              <span>SLA-eligible complaints</span>
              <strong>{sla.total_complaints_with_sla ?? 0}</strong>
            </div>
            <div>
              <span>Resolved on time</span>
              <strong>{sla.resolved_within_sla}</strong>
            </div>

            <div>
              <span>Resolved late</span>
              <strong>{sla.resolved_late}</strong>
            </div>

            <div>
              <span>Currently overdue</span>
              <strong>{sla.overdue_active_complaints}</strong>
            </div>
          </div>
        </div>

        {/* CATEGORY DISTRIBUTION */}
        <div className="analytics-card">
          <h3>Complaint Categories</h3>
          <p>Number of complaints by category</p>

          {categoryData.length === 0 ? (
            <EmptyState />
          ) : (
            <div className="chart-container category-chart">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart
                  data={categoryData}
                  layout="vertical"
                  margin={{ left: 15, right: 15 }}
                >
                  <CartesianGrid
                    strokeDasharray="3 3"
                    horizontal={false}
                    stroke="#E9EEF5"
                  />

                  <XAxis
                    type="number"
                    allowDecimals={false}
                    tick={{ fontSize: 10 }}
                    axisLine={false}
                    tickLine={false}
                  />

                  <YAxis
                    type="category"
                    dataKey="category_name"
                    width={125}
                    tick={{ fontSize: 10 }}
                    axisLine={false}
                    tickLine={false}
                  />

                  <Tooltip />
                  <Legend />

                  <Bar
                    dataKey="resolved_complaints"
                    name="Resolved"
                    stackId="a"
                    fill="#36A879"
                  />

                  <Bar
                    dataKey="active_complaints"
                    name="Active"
                    stackId="a"
                    fill="#438ED0"
                  />

                  <Bar
                     dataKey="cancelled_complaints"
                     name="Cancelled"
                     stackId="a"
                     fill="#E6A23C"
                     radius={[0, 5, 5, 0]}
                  />
                </BarChart>
              </ResponsiveContainer>
            </div>
          )}
        </div>

        {/* PRIORITY DISTRIBUTION */}
        <div className="analytics-card">
          <h3>Priority Distribution</h3>
          <p>Complaints grouped by priority</p>

          {priorityData.length === 0 ? (
            <EmptyState />
          ) : (
            <div className="priority-chart-layout">
              <div className="priority-pie">
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={priorityData}
                      dataKey="total_complaints"
                      nameKey="priority"
                      cx="50%"
                      cy="50%"
                      innerRadius={55}
                      outerRadius={85}
                      paddingAngle={3}
                    >
                      {priorityData.map((item, index) => (
                        <Cell
                          key={item.priority}
                          fill={PRIORITY_COLORS[index % PRIORITY_COLORS.length]}
                        />
                      ))}
                    </Pie>

                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
              </div>

              <div className="priority-legend">
                {priorityData.map((item, index) => (
                  <div className="priority-legend-row" key={item.priority}>
                    <span
                      className="legend-dot"
                      style={{
                        backgroundColor:
                          PRIORITY_COLORS[index % PRIORITY_COLORS.length]
                      }}
                    />

                    <span>{item.priority}</span>

                    <strong>{item.total_complaints}</strong>
                    <small>{item.percentage}%</small>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* DEPARTMENT PERFORMANCE */}
        <div className="analytics-card">
          <h3>Department Performance</h3>
          <p>Complaint resolution by department</p>

          {departmentData.length === 0 ? (
            <EmptyState />
          ) : (
            <div className="chart-container department-chart">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart
                  data={departmentData}
                  layout="vertical"
                  margin={{ left: 15, right: 15 }}
                >
                  <CartesianGrid
                    strokeDasharray="3 3"
                    horizontal={false}
                    stroke="#E9EEF5"
                  />

                  <XAxis
                    type="number"
                    domain={[0, 100]}
                    unit="%"
                    tick={{ fontSize: 10 }}
                    axisLine={false}
                    tickLine={false}
                  />

                  <YAxis
                    type="category"
                    dataKey="department_name"
                    width={125}
                    tick={{ fontSize: 10 }}
                    axisLine={false}
                    tickLine={false}
                  />

                  <Tooltip />

                  <Bar
                    dataKey="resolution_percentage"
                    name="Resolution"
                    fill="#42A98B"
                    radius={[0, 5, 5, 0]}
                    barSize={17}
                  />
                </BarChart>
              </ResponsiveContainer>
            </div>
          )}
        </div>

        {/* STAFF WORKLOAD */}
        <div className="analytics-card">
          <h3>Staff Workload</h3>
          <p>Current complaint assignments</p>

          {staffData.length === 0 ? (
            <EmptyState />
          ) : (
            <div className="staff-table-wrapper">
              <table className="staff-table">
                <thead>
                  <tr>
                    <th>Staff Member</th>
                    <th>Assigned</th>
                    <th>Active</th>
                  </tr>
                </thead>

                <tbody>
                  {staffData.map((item) => (
                    <tr key={item.staff_id}>
                      <td>{item.staff_name}</td>
                      <td>{item.assigned_complaints}</td>
                      <td>
                        <span className="active-count">
                          {item.active_complaints}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>

        {/* RESOLUTION TIME */}
<div className="analytics-card">
  <h3>Resolution Time</h3>
  <p>Average time taken to resolve complaints</p>

  <div className="resolution-value">
    {resolution.average_resolution_hours ?? 0}
    <span> hours</span>
  </div>

  <div className="sla-details">
    <div>
      <span>Median</span>
      <strong>{resolution.median_resolution_hours ?? 0} hrs</strong>
    </div>

    <div>
      <span>Minimum</span>
      <strong>{resolution.minimum_resolution_hours ?? 0} hrs</strong>
    </div>

    <div>
      <span>Maximum</span>
      <strong>{resolution.maximum_resolution_hours ?? 0} hrs</strong>
    </div>

    <div>
      <span>Total resolved</span>
      <strong>{resolution.total_resolved_complaints}</strong>
    </div>
  </div>
</div>

        {/* CITIZEN FEEDBACK */}
        <div className="analytics-card">
          <h3>Citizen Feedback</h3>
          <p>Feedback received from citizens</p>

          <div className="resolution-value feedback-value">
            <Star size={25} fill="#E9B65B" stroke="#E9B65B" />
            {feedback.average_rating ?? 0}
            <span>/ 5</span>
          </div>

          <div className="sla-details">
            <div>
              <span>Total feedback</span>
              <strong>{feedback.total_feedback}</strong>
            </div>

            <div>
              <span>Minimum rating</span>
              <strong>{feedback.minimum_rating}</strong>
            </div>

            <div>
              <span>Maximum rating</span>
              <strong>{feedback.maximum_rating}</strong>
            </div>
          </div>

          {feedbackData.length > 0 && (
            <div className="feedback-distribution">
              <h4>Rating Distribution</h4>

              {feedbackData.map((item) => (
                <div className="feedback-row" key={item.rating}>
                  <span>{item.rating} stars</span>
                  <strong>{item.total_feedback}</strong>
                </div>
              ))}
            </div>
          )}
        </div>

      </section>
    </div>
  )
}

export default AdminDashboard
