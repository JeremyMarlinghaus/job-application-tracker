DROP DATABASE IF EXISTS job_tracker;
CREATE DATABASE job_tracker;
USE job_tracker;

CREATE TABLE companies (
    company_id INT AUTO_INCREMENT PRIMARY KEY,
    company_name VARCHAR(100) NOT NULL,
    industry VARCHAR(50),
    website VARCHAR(200),
    city VARCHAR(50),
    state VARCHAR(50),
    notes TEXT
);

CREATE TABLE jobs (
    job_id INT AUTO_INCREMENT PRIMARY KEY,
    company_id INT,
    job_title VARCHAR(100) NOT NULL,
    job_type ENUM('Full-time', 'Part-time', 'Contract', 'Internship'),
    salary_min INT,
    salary_max INT,
    job_url VARCHAR(300),
    date_posted DATE,
    requirements JSON,
    CONSTRAINT fk_jobs_company
        FOREIGN KEY (company_id) REFERENCES companies(company_id)
        ON DELETE CASCADE
);

CREATE TABLE applications (
    application_id INT AUTO_INCREMENT PRIMARY KEY,
    job_id INT,
    application_date DATE NOT NULL,
    status ENUM('Applied', 'Screening', 'Interview', 'Offer', 'Rejected', 'Withdrawn'),
    resume_version VARCHAR(50),
    cover_letter_sent BOOLEAN,
    interview_data JSON,
    CONSTRAINT fk_applications_job
        FOREIGN KEY (job_id) REFERENCES jobs(job_id)
        ON DELETE CASCADE
);

CREATE TABLE contacts (
    contact_id INT AUTO_INCREMENT PRIMARY KEY,
    company_id INT,
    contact_name VARCHAR(100) NOT NULL,
    title VARCHAR(100),
    email VARCHAR(100),
    phone VARCHAR(20),
    linkedin_url VARCHAR(200),
    notes TEXT,
    CONSTRAINT fk_contacts_company
        FOREIGN KEY (company_id) REFERENCES companies(company_id)
        ON DELETE CASCADE
);

INSERT INTO companies (company_id, company_name, industry, website, city, state, notes)
VALUES
(1, 'Tech Solutions Inc', 'Technology', 'www.techsolutions.com', 'Miami', 'Florida', NULL),
(2, 'Data Analytics Corp', 'Data Science', 'www.dataanalytics.com', 'Austin', 'Texas', NULL),
(3, 'Cloud Systems LLC', 'Cloud Computing', 'www.cloudsystems.com', 'Seattle', 'Washington', NULL),
(4, 'Digital Innovations', 'Software', 'www.digitalinnovations.com', 'San Francisco', 'California', 'Applied to Senior Developer position on 2026-04-01'),
(5, 'Smart Tech Group', 'AI/ML', 'www.smarttech.com', 'Boston', 'Massachusetts', NULL),
(6, 'New Tech Corp', 'Technology', NULL, 'Denver', 'Colorado', NULL);

INSERT INTO jobs (job_id, company_id, job_title, job_type, salary_min, salary_max, job_url, date_posted, requirements)
VALUES
(1, 1, 'Software Developer', 'Full-time', 70000, 90000, NULL, '2025-01-15', JSON_ARRAY('Python', 'SQL', 'Git')),
(2, 1, 'Database Administrator', 'Full-time', 75000, 95000, NULL, '2025-01-10', JSON_ARRAY('MySQL', 'SQL', 'Database Design')),
(3, 2, 'Data Analyst', 'Full-time', 65000, 85000, NULL, '2025-01-12', JSON_ARRAY('SQL', 'Excel', 'Tableau')),
(4, 3, 'Cloud Engineer', 'Full-time', 80000, 100000, NULL, '2025-01-08', JSON_ARRAY('AWS', 'Linux', 'Cloud')),
(5, 4, 'Junior Developer', 'Full-time', 55000, 70000, NULL, '2025-01-14', JSON_ARRAY('Java', 'HTML', 'CSS')),
(6, 4, 'Senior Developer', 'Full-time', 95000, 120000, NULL, '2025-01-14', JSON_ARRAY('Python', 'Flask', 'SQL', 'Leadership')),
(7, 5, 'ML Engineer', 'Full-time', 90000, 115000, NULL, '2025-01-11', JSON_ARRAY('Python', 'Machine Learning', 'TensorFlow')),
(8, 1, 'QA Engineer', 'Full-time', 60000, 80000, NULL, '2025-01-05', JSON_ARRAY('Testing', 'Automation', 'Selenium')),
(9, 2, 'Business Analyst', 'Full-time', 65000, 85000, NULL, '2025-01-06', JSON_ARRAY('Analysis', 'Excel', 'Communication')),
(10, 2, 'Data Scientist', 'Full-time', 85000, 110000, NULL, '2025-01-07', JSON_ARRAY('Python', 'SQL', 'Machine Learning')),
(11, 3, 'DevOps Engineer', 'Full-time', 80000, 105000, NULL, '2025-01-08', JSON_ARRAY('Docker', 'CI/CD', 'Linux')),
(12, 3, 'Security Analyst', 'Full-time', 75000, 95000, NULL, '2025-01-09', JSON_ARRAY('Security', 'Risk Analysis', 'Networking')),
(13, 4, 'UI/UX Designer', 'Full-time', 60000, 80000, NULL, '2025-01-10', JSON_ARRAY('Figma', 'UI Design', 'UX Research')),
(14, 5, 'Product Manager', 'Full-time', 90000, 120000, NULL, '2025-01-11', JSON_ARRAY('Product Strategy', 'Communication', 'Leadership')),
(15, 1, 'Technical Writer', 'Contract', 55000, 75000, NULL, '2025-01-12', JSON_ARRAY('Writing', 'Documentation', 'Communication')),
(16, 2, 'Intern - Data', 'Internship', 30000, 40000, NULL, '2025-01-13', JSON_ARRAY('SQL', 'Excel', 'Data Analysis')),
(17, 4, 'Intern - Development', 'Internship', 32000, 42000, NULL, '2025-01-14', JSON_ARRAY('Java', 'HTML', 'CSS')),
(18, 6, 'Software Architect', 'Full-time', 120000, 150000, NULL, NULL, JSON_ARRAY('System Design', 'Architecture', 'Leadership'));

INSERT INTO applications (application_id, job_id, application_date, status, resume_version, cover_letter_sent, interview_data)
VALUES
(1, 1, '2025-01-16', 'Applied', 'v2.1', TRUE, JSON_OBJECT('response_date', NULL, 'interview_date', NULL, 'notes', NULL)),
(2, 3, '2025-01-13', 'Interview', 'v2.1', TRUE, JSON_OBJECT('response_date', NULL, 'interview_date', NULL, 'notes', 'Originally Interview Scheduled; later Interview Completed in transaction example')),
(3, 4, '2025-01-09', 'Rejected', 'v2.0', FALSE, JSON_OBJECT('response_date', NULL, 'interview_date', NULL, 'notes', NULL)),
(4, 5, '2025-01-15', 'Applied', 'v2.1', TRUE, JSON_OBJECT('response_date', NULL, 'interview_date', NULL, 'notes', NULL)),
(5, 7, '2025-01-12', 'Screening', 'v2.1', TRUE, JSON_OBJECT('response_date', NULL, 'interview_date', NULL, 'notes', 'Originally Phone Screen')),
(6, 6, CURDATE(), 'Applied', 'v3.0', TRUE, JSON_OBJECT('response_date', NULL, 'interview_date', NULL, 'notes', 'Added in transaction example'));

INSERT INTO contacts (contact_id, company_id, contact_name, title, email, phone, linkedin_url, notes)
VALUES
(1, 1, 'Sarah Johnson', 'HR Manager', 'sjohnson@techsolutions.com', NULL, NULL, NULL),
(2, 2, 'Michael Chen', 'Technical Recruiter', 'mchen@dataanalytics.com', NULL, NULL, NULL),
(3, 3, 'Emily Williams', 'Hiring Manager', 'ewilliams@cloudsystems.com', NULL, NULL, NULL),
(4, 4, 'David Brown', 'Senior Developer', NULL, NULL, NULL, NULL),
(5, 5, 'Lisa Garcia', 'Talent Acquisition', 'lgarcia@smarttech.com', NULL, NULL, NULL),
(6, 6, 'Jennifer Martinez', 'CTO', 'jmartinez@newtechcorp.com', NULL, NULL, NULL),
(7, 4, 'Robert Kim', 'Engineering Manager', 'rkim@digitalinnovations.com', NULL, NULL, NULL);
