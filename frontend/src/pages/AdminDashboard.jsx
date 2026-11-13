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
import { clearAccessToken } from '../services/api'
import ThemeToggle from '../components/ThemeToggle'
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

                  <Bar
                    dataKey="total_complaints"
                    name="Complaints"
                    fill="#438ED0"
                    radius={[0, 5, 5, 0]}
                    barSize={15}
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
