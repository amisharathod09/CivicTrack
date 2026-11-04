
-- =====================================================
-- CivicTrack - Database Indexes
-- Database: civictrack_db
-- MySQL Version: 8.0
-- =====================================================

USE civictrack_db;


-- 1. Service Requests: Search by status
CREATE INDEX idx_requests_status
ON service_requests(status);


-- 2. Service Requests: Sort or filter by creation date
CREATE INDEX idx_requests_created_at
ON service_requests(created_at);


-- 3. Service Requests: Filter by status and creation date
CREATE INDEX idx_requests_status_created
ON service_requests(status, created_at);


-- 4. Assignments: Find current assignments for staff
CREATE INDEX idx_assignments_staff_current
ON assignments(staff_id, is_current);


-- 5. Status History: Find a request's history by date
CREATE INDEX idx_history_request_changed
ON status_history(request_id, changed_at);


-- =====================================================
-- END OF CIVICTRACK INDEXES
-- =====================================================

/* 
Understand the indexes
Index	Purpose
idx_requests_status	-Find complaints by status
idx_requests_created_at	-Find complaints by creation date
idx_requests_status_created	-Filter by status and date together
idx_assignments_staff_current-	Find current assignments for a staff member
idx_history_request_changed-	Retrieve complaint history in date order
*/