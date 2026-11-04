
-- =====================================================
-- CivicTrack - SQL Views
-- Database: civictrack_db
-- MySQL Version: 8.0
-- =====================================================

USE civictrack_db;


-- =====================================================
-- 1. COMPLETE COMPLAINT DETAILS
-- =====================================================

CREATE OR REPLACE VIEW vw_complaint_details AS
SELECT
    service_requests.request_id,
    service_requests.title,
    service_requests.description,
    service_requests.priority,
    service_requests.status,
    service_requests.created_at,
    service_requests.resolved_at,
    users.full_name AS citizen_name,
    users.email AS citizen_email,
    categories.category_name,
    departments.department_name,
    locations.area,
    locations.city,
    locations.state
FROM service_requests
INNER JOIN users
    ON service_requests.citizen_id = users.user_id
INNER JOIN categories
    ON service_requests.category_id = categories.category_id
INNER JOIN departments
    ON categories.department_id = departments.department_id
INNER JOIN locations
    ON service_requests.location_id = locations.location_id;


-- =====================================================
-- 2. DEPARTMENT-WISE COMPLAINT SUMMARY
-- =====================================================

CREATE OR REPLACE VIEW vw_department_complaint_summary AS
SELECT
    departments.department_id,
    departments.department_name,
    COUNT(service_requests.request_id) AS total_complaints,

    SUM(CASE
        WHEN service_requests.status = 'Submitted'
        THEN 1 ELSE 0
    END) AS submitted_complaints,

    SUM(CASE
        WHEN service_requests.status = 'Assigned'
        THEN 1 ELSE 0
    END) AS assigned_complaints,

    SUM(CASE
        WHEN service_requests.status = 'In Progress'
        THEN 1 ELSE 0
    END) AS in_progress_complaints,

    SUM(CASE
        WHEN service_requests.status = 'Resolved'
        THEN 1 ELSE 0
    END) AS resolved_complaints,

    SUM(CASE
        WHEN service_requests.status = 'Closed'
        THEN 1 ELSE 0
    END) AS closed_complaints,

    SUM(CASE
        WHEN service_requests.status = 'Cancelled'
        THEN 1 ELSE 0
    END) AS cancelled_complaints

FROM departments
LEFT JOIN categories
    ON departments.department_id = categories.department_id
LEFT JOIN service_requests
    ON categories.category_id = service_requests.category_id

GROUP BY
    departments.department_id,
    departments.department_name;


-- =====================================================
-- 3. COMPLAINT RESOLUTION METRICS
-- =====================================================

CREATE OR REPLACE VIEW vw_complaint_resolution_metrics AS
SELECT
    service_requests.request_id,
    service_requests.title,
    service_requests.priority,
    service_requests.status,
    service_requests.created_at,
    service_requests.resolved_at,

    TIMESTAMPDIFF(
        HOUR,
        service_requests.created_at,
        service_requests.resolved_at
    ) AS resolution_hours,

    categories.category_name,
    departments.department_name

FROM service_requests
INNER JOIN categories
    ON service_requests.category_id = categories.category_id
INNER JOIN departments
    ON categories.department_id = departments.department_id

WHERE service_requests.status IN ('Resolved', 'Closed');


-- =====================================================
-- 4. CURRENT STAFF WORKLOAD
-- =====================================================

CREATE OR REPLACE VIEW vw_staff_workload AS
SELECT
    users.user_id AS staff_id,
    users.full_name AS staff_name,
    departments.department_name,
    COUNT(assignments.assignment_id)
        AS current_assigned_complaints

FROM users
LEFT JOIN departments
    ON users.department_id = departments.department_id
LEFT JOIN assignments
    ON users.user_id = assignments.staff_id
    AND assignments.is_current = TRUE

WHERE users.role = 'staff'

GROUP BY
    users.user_id,
    users.full_name,
    departments.department_name;


-- =====================================================
-- 5. MONTHLY COMPLAINT TRENDS
-- =====================================================

CREATE OR REPLACE VIEW vw_monthly_complaint_trends AS
SELECT
    YEAR(created_at) AS complaint_year,
    MONTH(created_at) AS complaint_month,
    DATE_FORMAT(created_at, '%Y-%m') AS complaint_period,
    COUNT(request_id) AS total_complaints

FROM service_requests

GROUP BY
    YEAR(created_at),
    MONTH(created_at),
    DATE_FORMAT(created_at, '%Y-%m');


-- =====================================================
-- END OF CIVICTRACK SQL VIEWS
-- =====================================================
