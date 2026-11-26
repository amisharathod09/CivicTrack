
-- ============================================================
-- CivicTrack
-- Business Analytics SQL Queries
-- Database: civictrack_db
-- Purpose: Operational and Business Performance Analysis
-- ============================================================

USE civictrack_db;

-- ============================================================
-- QUERY 1: Complaint Distribution by Category
-- Business Question:
-- Which complaint categories receive the most complaints?
-- ============================================================

SELECT
    categories.category_name,
    COUNT(service_requests.request_id) AS total_complaints
FROM categories
LEFT JOIN service_requests
    ON categories.category_id = service_requests.category_id
GROUP BY
    categories.category_id,
    categories.category_name
ORDER BY
    total_complaints DESC;


-- ============================================================
-- QUERY 2: Area-wise Complaint Analysis
-- Business Question:
-- Which areas report the highest number of complaints?
-- ============================================================

SELECT
    locations.area,
    locations.city,
    COUNT(service_requests.request_id) AS total_complaints
FROM locations
LEFT JOIN service_requests
    ON locations.location_id = service_requests.location_id
GROUP BY
    locations.location_id,
    locations.area,
    locations.city
ORDER BY
    total_complaints DESC;


-- ============================================================
-- QUERY 3: Department-wise Resolution Performance
-- Business Question:
-- Which departments resolve the highest percentage of complaints?
-- ============================================================

SELECT
    departments.department_name,
    COUNT(service_requests.request_id) AS total_complaints,
    SUM(
        CASE
            WHEN service_requests.status IN ('Resolved', 'Closed')
            THEN 1
            ELSE 0
        END
    ) AS resolved_complaints,
    SUM(
        CASE
            WHEN service_requests.status IN (
                'Submitted', 'Assigned', 'In Progress'
            )
            THEN 1
            ELSE 0
        END
    ) AS active_complaints,
    ROUND(
        SUM(
            CASE
                WHEN service_requests.status IN ('Resolved', 'Closed')
                THEN 1
                ELSE 0
            END
        ) * 100.0 / NULLIF(COUNT(service_requests.request_id), 0),
        2
    ) AS resolution_percentage
FROM departments
LEFT JOIN categories
    ON departments.department_id = categories.department_id
LEFT JOIN service_requests
    ON categories.category_id = service_requests.category_id
GROUP BY
    departments.department_id,
    departments.department_name
ORDER BY
    resolution_percentage DESC;


-- ============================================================
-- QUERY 4: SLA Performance Analysis
-- Business Question:
-- How many complaints were resolved within or after SLA?
-- How many active complaints are overdue?
-- ============================================================

SELECT
    COUNT(
        CASE
            WHEN status != 'Cancelled'
            THEN request_id
        END
    ) AS total_non_cancelled,
    COUNT(
        CASE
            WHEN status IN ('Resolved', 'Closed')
            THEN request_id
        END
    ) AS completed_complaints,
    SUM(
        CASE
            WHEN status IN ('Resolved', 'Closed')
             AND resolved_at <= sla_due_at
            THEN 1
            ELSE 0
        END
    ) AS resolved_within_sla,
    SUM(
        CASE
            WHEN status IN ('Resolved', 'Closed')
             AND resolved_at > sla_due_at
            THEN 1
            ELSE 0
        END
    ) AS resolved_late,
    SUM(
        CASE
            WHEN status IN ('Submitted', 'Assigned', 'In Progress')
             AND sla_due_at < NOW()
            THEN 1
            ELSE 0
        END
    ) AS overdue_active_complaints,
    ROUND(
        SUM(
            CASE
                WHEN status IN ('Resolved', 'Closed')
                 AND resolved_at <= sla_due_at
                THEN 1
                ELSE 0
            END
        ) * 100.0 /
        NULLIF(
            COUNT(
                CASE
                    WHEN status IN ('Resolved', 'Closed')
                    THEN request_id
                END
            ),
            0
        ),
        2
    ) AS sla_compliance_percentage
FROM service_requests
WHERE sla_due_at IS NOT NULL
  AND status != 'Cancelled';


-- ============================================================
-- QUERY 5: Staff Performance Analysis
-- Business Question:
-- How many complaints has each staff member handled?
-- What is their current workload?
-- ============================================================

SELECT
    users.user_id,
    users.full_name,

    COUNT(DISTINCT assignments.request_id)
        AS total_complaints_assigned,

    COUNT(DISTINCT
        CASE
            WHEN assignments.is_current = 1
            THEN assignments.request_id
        END
    ) AS current_assignments,

    COUNT(DISTINCT
        CASE
            WHEN assignments.is_current = 1
             AND service_requests.status IN (
                 'Submitted', 'Assigned', 'In Progress'
             )
            THEN assignments.request_id
        END
    ) AS active_complaints,

    COUNT(DISTINCT
        CASE
            WHEN assignments.is_current = 1
             AND service_requests.status IN ('Resolved', 'Closed')
            THEN assignments.request_id
        END
    ) AS resolved_complaints

FROM users

LEFT JOIN assignments
    ON users.user_id = assignments.staff_id

LEFT JOIN service_requests
    ON assignments.request_id = service_requests.request_id

WHERE users.role = 'staff'

GROUP BY
    users.user_id,
    users.full_name

ORDER BY
    current_assignments DESC,
    total_complaints_assigned DESC;


-- ============================================================
-- QUERY 6: Complaint Resolution Time Analysis
-- Business Question:
-- Which complaint categories take the longest to resolve?
-- ============================================================

SELECT
    categories.category_name,

    COUNT(service_requests.request_id)
        AS resolved_complaints,

    ROUND(
        AVG(
            TIMESTAMPDIFF(
                HOUR,
                service_requests.created_at,
                service_requests.resolved_at
            )
        ),
        2
    ) AS average_resolution_hours,

    MIN(
        TIMESTAMPDIFF(
            HOUR,
            service_requests.created_at,
            service_requests.resolved_at
        )
    ) AS minimum_resolution_hours,

    MAX(
        TIMESTAMPDIFF(
            HOUR,
            service_requests.created_at,
            service_requests.resolved_at
        )
    ) AS maximum_resolution_hours

FROM service_requests

INNER JOIN categories
    ON service_requests.category_id = categories.category_id

WHERE service_requests.status IN ('Resolved', 'Closed')
  AND service_requests.resolved_at IS NOT NULL
  AND service_requests.resolved_at >= service_requests.created_at

GROUP BY
    categories.category_id,
    categories.category_name

ORDER BY
    average_resolution_hours DESC;


-- ============================================================
-- QUERY 7: Complaint Status Distribution
-- Business Question:
-- What is the distribution of complaints across different statuses?
-- ============================================================

SELECT
    status,
    COUNT(request_id) AS total_complaints,

    ROUND(
        COUNT(request_id) * 100.0 /
        (SELECT COUNT(*) FROM service_requests),
        2
    ) AS percentage

FROM service_requests

GROUP BY status

ORDER BY total_complaints DESC;


-- ============================================================
-- QUERY 8: Priority-wise Complaint Analysis
-- Business Question:
-- How are complaints distributed across priority levels?
-- ============================================================

SELECT
    priority,

    COUNT(request_id) AS total_complaints,

    SUM(
        CASE
            WHEN status IN ('Submitted', 'Assigned', 'In Progress')
            THEN 1
            ELSE 0
        END
    ) AS active_complaints,

    SUM(
        CASE
            WHEN status IN ('Resolved', 'Closed')
            THEN 1
            ELSE 0
        END
    ) AS resolved_complaints,

    SUM(
        CASE
            WHEN status = 'Cancelled'
            THEN 1
            ELSE 0
        END
    ) AS cancelled_complaints

FROM service_requests

GROUP BY priority

ORDER BY
    CASE priority
        WHEN 'Critical' THEN 1
        WHEN 'High' THEN 2
        WHEN 'Medium' THEN 3
        WHEN 'Low' THEN 4
        ELSE 5
    END;


-- ============================================================
-- QUERY 9: Monthly Complaint Trend Analysis
-- Business Question:
-- How does complaint volume change month by month?
-- ============================================================

SELECT
    YEAR(created_at) AS complaint_year,

    MONTH(created_at) AS complaint_month,

    DATE_FORMAT(created_at, '%Y-%m') AS month_year,

    COUNT(request_id) AS total_complaints

FROM service_requests

GROUP BY
    YEAR(created_at),
    MONTH(created_at),
    DATE_FORMAT(created_at, '%Y-%m')

ORDER BY
    complaint_year,
    complaint_month;


-- ============================================================
-- QUERY 10: Area-wise Resolution Performance
-- Business Question:
-- Which areas have the most complaints and what is their resolution rate?
-- ============================================================

SELECT
    locations.area,
    locations.city,

    COUNT(service_requests.request_id)
        AS total_complaints,

    SUM(
        CASE
            WHEN service_requests.status IN ('Resolved', 'Closed')
            THEN 1
            ELSE 0
        END
    ) AS resolved_complaints,

    SUM(
        CASE
            WHEN service_requests.status IN (
                'Submitted', 'Assigned', 'In Progress'
            )
            THEN 1
            ELSE 0
        END
    ) AS active_complaints,

    ROUND(
        SUM(
            CASE
                WHEN service_requests.status IN ('Resolved', 'Closed')
                THEN 1
                ELSE 0
            END
        ) * 100.0 /
        NULLIF(COUNT(service_requests.request_id), 0),
        2
    ) AS resolution_percentage

FROM locations

LEFT JOIN service_requests
    ON locations.location_id = service_requests.location_id

GROUP BY
    locations.location_id,
    locations.area,
    locations.city

ORDER BY
    total_complaints DESC,
    resolution_percentage DESC;
