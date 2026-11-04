
-- =====================================================
-- CivicTrack - Database Schema
-- Database: civictrack_db
-- MySQL Version: 8.0
-- =====================================================

CREATE DATABASE IF NOT EXISTS civictrack_db;

USE civictrack_db;


-- =====================================================
-- 1. DEPARTMENTS TABLE
-- =====================================================

CREATE TABLE departments (
    department_id INT AUTO_INCREMENT PRIMARY KEY,
    department_name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP
);


-- =====================================================
-- 2. USERS TABLE
-- =====================================================

CREATE TABLE users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(150) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    phone VARCHAR(15),
    role VARCHAR(20) NOT NULL,
    department_id INT,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP,

    CONSTRAINT chk_user_role
        CHECK (role IN ('citizen', 'staff', 'admin')),

    CONSTRAINT fk_users_department
        FOREIGN KEY (department_id)
        REFERENCES departments(department_id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE
);


-- =====================================================
-- 3. CATEGORIES TABLE
-- =====================================================

CREATE TABLE categories (
    category_id INT AUTO_INCREMENT PRIMARY KEY,
    department_id INT NOT NULL,
    category_name VARCHAR(100) NOT NULL,
    description TEXT,
    default_priority VARCHAR(20) NOT NULL DEFAULT 'Medium',
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP,

    CONSTRAINT uq_department_category
        UNIQUE (department_id, category_name),

    CONSTRAINT chk_category_priority
        CHECK (default_priority IN ('Low', 'Medium', 'High', 'Critical')),

    CONSTRAINT fk_categories_department
        FOREIGN KEY (department_id)
        REFERENCES departments(department_id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE
);


-- =====================================================
-- 4. LOCATIONS TABLE
-- =====================================================

CREATE TABLE locations (
    location_id INT AUTO_INCREMENT PRIMARY KEY,
    area VARCHAR(150) NOT NULL,
    city VARCHAR(100) NOT NULL,
    state VARCHAR(100) NOT NULL,
    pin_code VARCHAR(10),
    full_address VARCHAR(255) NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);


-- =====================================================
-- 5. SERVICE REQUESTS TABLE
-- =====================================================

CREATE TABLE service_requests (
    request_id INT AUTO_INCREMENT PRIMARY KEY,
    citizen_id INT NOT NULL,
    category_id INT NOT NULL,
    location_id INT NOT NULL,
    title VARCHAR(150) NOT NULL,
    description TEXT NOT NULL,
    priority VARCHAR(20) NOT NULL DEFAULT 'Medium',
    status VARCHAR(30) NOT NULL DEFAULT 'Submitted',
    sla_due_at DATETIME,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP,
    resolved_at DATETIME,

    CONSTRAINT chk_request_priority
        CHECK (priority IN ('Low', 'Medium', 'High', 'Critical')),

    CONSTRAINT chk_request_status
        CHECK (status IN (
            'Submitted',
            'Assigned',
            'In Progress',
            'Resolved',
            'Closed',
            'Cancelled'
        )),

    CONSTRAINT fk_requests_citizen
        FOREIGN KEY (citizen_id)
        REFERENCES users(user_id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,

    CONSTRAINT fk_requests_category
        FOREIGN KEY (category_id)
        REFERENCES categories(category_id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,

    CONSTRAINT fk_requests_location
        FOREIGN KEY (location_id)
        REFERENCES locations(location_id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE
);


-- =====================================================
-- 6. ASSIGNMENTS TABLE
-- =====================================================

CREATE TABLE assignments (
    assignment_id INT AUTO_INCREMENT PRIMARY KEY,
    request_id INT NOT NULL,
    staff_id INT NOT NULL,
    assigned_by INT NOT NULL,
    assigned_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    notes TEXT,
    is_current BOOLEAN NOT NULL DEFAULT TRUE,

    current_request_id INT
        GENERATED ALWAYS AS (
            CASE
                WHEN is_current = TRUE THEN request_id
                ELSE NULL
            END
        ) STORED,

    UNIQUE KEY current_request_id (current_request_id),

    KEY request_id (request_id),
    KEY staff_id (staff_id),
    KEY assigned_by (assigned_by),

    CONSTRAINT assignments_ibfk_1
        FOREIGN KEY (request_id)
        REFERENCES service_requests(request_id),

    CONSTRAINT assignments_ibfk_2
        FOREIGN KEY (staff_id)
        REFERENCES users(user_id),

    CONSTRAINT assignments_ibfk_3
        FOREIGN KEY (assigned_by)
        REFERENCES users(user_id)

) ENGINE=InnoDB
  DEFAULT CHARSET=utf8mb4
  COLLATE=utf8mb4_0900_ai_ci;


-- =====================================================
-- 7. STATUS HISTORY TABLE
-- =====================================================

CREATE TABLE status_history (
    history_id INT AUTO_INCREMENT PRIMARY KEY,
    request_id INT NOT NULL,
    old_status VARCHAR(30),
    new_status VARCHAR(30) NOT NULL,
    changed_by INT NOT NULL,
    change_note TEXT,
    changed_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT chk_old_status CHECK (
        old_status IS NULL OR old_status IN (
            'Submitted',
            'Assigned',
            'In Progress',
            'Resolved',
            'Closed',
            'Cancelled'
        )
    ),

    CONSTRAINT chk_new_status CHECK (
        new_status IN (
            'Submitted',
            'Assigned',
            'In Progress',
            'Resolved',
            'Closed',
            'Cancelled'
        )
    ),

    CONSTRAINT fk_history_request
        FOREIGN KEY (request_id)
        REFERENCES service_requests(request_id),

    CONSTRAINT fk_history_user
        FOREIGN KEY (changed_by)
        REFERENCES users(user_id)
);


-- =====================================================
-- 8. FEEDBACK TABLE
-- =====================================================

CREATE TABLE feedback (
    feedback_id INT AUTO_INCREMENT PRIMARY KEY,
    request_id INT NOT NULL UNIQUE,
    citizen_id INT NOT NULL,
    rating INT NOT NULL,
    comments TEXT,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP,

    CONSTRAINT chk_feedback_rating
        CHECK (rating BETWEEN 1 AND 5),

    CONSTRAINT fk_feedback_request
        FOREIGN KEY (request_id)
        REFERENCES service_requests(request_id),

    CONSTRAINT fk_feedback_citizen
        FOREIGN KEY (citizen_id)
        REFERENCES users(user_id)
);


-- =====================================================
-- 9. ATTACHMENTS TABLE
-- =====================================================

CREATE TABLE attachments (
    attachment_id INT AUTO_INCREMENT PRIMARY KEY,
    request_id INT NOT NULL,
    uploaded_by INT NOT NULL,
    file_name VARCHAR(255) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    mime_type VARCHAR(100) NOT NULL,
    file_size BIGINT NOT NULL,
    attachment_type VARCHAR(30) NOT NULL,
    uploaded_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT chk_attachment_type
        CHECK (attachment_type IN (
            'complaint_photo',
            'resolution_evidence'
        )),

    CONSTRAINT chk_attachment_file_size
        CHECK (file_size > 0),

    CONSTRAINT fk_attachments_request
        FOREIGN KEY (request_id)
        REFERENCES service_requests(request_id),

    CONSTRAINT fk_attachments_user
        FOREIGN KEY (uploaded_by)
        REFERENCES users(user_id)
);


-- =====================================================
-- END OF CIVICTRACK DATABASE SCHEMA
-- =====================================================
