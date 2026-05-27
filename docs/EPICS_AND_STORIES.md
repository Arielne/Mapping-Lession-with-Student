# Epics and User Stories – CourseMatch

**Version:** 1.0  
**Format:** As a [role], I want [feature], so that [benefit]  
**Acceptance Criteria:** Given / When / Then

---

## Epic 1: Authentication and Role Management

**Goal:** Người dùng có thể đăng ký, đăng nhập, và hệ thống kiểm soát quyền truy cập theo role.

---

### US-1.1 – Đăng ký tài khoản

**As a** new user,  
**I want to** register an account with my name, email, password, and role,  
**So that** I can access the CourseMatch system.

**Acceptance Criteria:**

> **Given** I am on the Register page  
> **When** I fill in full_name, email, password, role (student/admin) and submit  
> **Then** a new user record is created in MongoDB with hashed password  
> **And** I receive a success response with my user info (no password)  
> **And** if email already exists, I receive a 400 error

---

### US-1.2 – Đăng nhập

**As a** registered user,  
**I want to** log in with my email and password,  
**So that** I receive a JWT token to access protected features.

**Acceptance Criteria:**

> **Given** I am on the Login page  
> **When** I submit valid email and password  
> **Then** I receive a JWT access_token  
> **And** the token is stored in frontend state (AuthContext)  
> **And** I am redirected to the home page  
> **And** if credentials are wrong, I see an error message

---

### US-1.3 – Xem thông tin tài khoản

**As a** logged-in user,  
**I want to** view my account information,  
**So that** I can confirm my name, email, and role.

**Acceptance Criteria:**

> **Given** I am logged in  
> **When** I navigate to the profile page or call GET /auth/me  
> **Then** I see my full_name, email, role, and created_at  
> **And** if my token is expired, I am redirected to login

---

### US-1.4 – Role-based route protection

**As a** student,  
**I want to** be prevented from accessing admin pages,  
**So that** admin functions are secure.

**Acceptance Criteria:**

> **Given** I am logged in as a student  
> **When** I try to access /admin/upload-course  
> **Then** I am redirected to home page or shown a 403 error  
> **And** the upload course API returns 403 if called with student JWT

---

## Epic 2: Course Document Upload and Extraction

**Goal:** Admin có thể upload tài liệu khóa học thật và hệ thống tự động trích xuất, vector hóa.

---

### US-2.1 – Admin upload tài liệu khóa học

**As an** admin,  
**I want to** upload a PDF or DOCX course document with a title,  
**So that** the system can process it and make it available for matching.

**Acceptance Criteria:**

> **Given** I am logged in as admin on the Upload Course page  
> **When** I select a PDF/DOCX file, enter a title, and click Upload  
> **Then** the file is sent to POST /course-documents/upload  
> **And** a course_document record is created with status "uploaded"  
> **And** I see a success message with the document ID  
> **And** if I try to upload a non-PDF/DOCX file, I see a format error

---

### US-2.2 – Hệ thống tự động trích xuất text

**As an** admin,  
**I want** the system to automatically extract text from uploaded course files,  
**So that** I don't have to manually copy content.

**Acceptance Criteria:**

> **Given** a course document has been uploaded (status: "uploaded")  
> **When** the backend processes the file  
> **Then** `extracted_text` is populated from the file content  
> **And** `cleaned_text`, `keywords`, `binary_vector` are computed  
> **And** `processing_status` is updated to "processed"  
> **And** if extraction fails, status is "failed" with error_message

---

### US-2.3 – Xem danh sách khóa học

**As a** user (admin or student),  
**I want to** view a list of all available course documents,  
**So that** I can see what courses are in the system.

**Acceptance Criteria:**

> **Given** I am logged in  
> **When** I navigate to the Course Documents page  
> **Then** I see a list of courses with title, processing status, and keywords  
> **And** only "processed" courses show keywords and vector info

---

### US-2.4 – Admin xóa khóa học

**As an** admin,  
**I want to** delete a course document,  
**So that** I can remove outdated or incorrect course data.

**Acceptance Criteria:**

> **Given** I am logged in as admin  
> **When** I click Delete on a course document  
> **Then** the document is removed from MongoDB  
> **And** related match_results are handled (or orphaned records are noted)  
> **And** if I am a student, Delete button is not shown

---

## Epic 3: Student Document Upload and Extraction

**Goal:** Học viên có thể upload CV hoặc tài liệu nhu cầu học tập thật.

---

### US-3.1 – Student upload tài liệu nhu cầu học tập

**As a** student,  
**I want to** upload my CV or learning-need document (PDF/DOCX),  
**So that** the system can extract my skills and match me with courses.

**Acceptance Criteria:**

> **Given** I am logged in as student on the Upload Document page  
> **When** I select a PDF/DOCX file and click Upload  
> **Then** the file is sent to POST /student-documents/upload  
> **And** a student_document record is created with my user_id  
> **And** processing begins automatically  
> **And** I see the document in my document list with status "uploaded" → "processed"

---

### US-3.2 – Xem tài liệu của mình

**As a** student,  
**I want to** view my uploaded documents and their extracted keywords,  
**So that** I can verify the system extracted the right skills.

**Acceptance Criteria:**

> **Given** I am logged in as student  
> **When** I navigate to My Documents page  
> **Then** I see only my own documents (not other students')  
> **And** processed documents show detected_keywords and binary_vector  
> **And** failed documents show error_message

---

## Epic 4: Binary Vector Matching

**Goal:** Học viên có thể chạy matching và nhận danh sách khóa học phù hợp.

---

### US-4.1 – Chạy matching

**As a** student,  
**I want to** trigger course matching for my uploaded document,  
**So that** I get a ranked list of courses that match my needs.

**Acceptance Criteria:**

> **Given** my student document has status "processed"  
> **When** I click "Find Matching Courses"  
> **Then** POST /matching/run/{student_document_id} is called  
> **And** the system computes Jaccard similarity with all processed course documents  
> **And** results are saved to match_results collection  
> **And** I am redirected to the Match Results page

---

### US-4.2 – Xem kết quả matching

**As a** student,  
**I want to** view the top-3 matching courses with scores and matched keywords,  
**So that** I can decide which course to enroll in.

**Acceptance Criteria:**

> **Given** matching has been run  
> **When** I view the Match Results page  
> **Then** I see courses ranked by Jaccard score (highest first)  
> **And** each result shows course title, match_score, matched_keywords  
> **And** results are limited to top-3 by default (adjustable)  
> **And** a course with 0.0 score appears at the bottom

---

## Epic 5: Algorithm Evaluation

**Goal:** Admin có thể đánh giá độ chính xác của thuật toán bằng dữ liệu thật có nhãn.

---

### US-5.1 – Học viên xác nhận nhãn

**As a** student,  
**I want to** confirm which course is actually right for me,  
**So that** my choice can be used as a label to evaluate algorithm accuracy.

**Acceptance Criteria:**

> **Given** I have viewed my matching results  
> **When** I select the course(s) that are truly relevant to me and confirm  
> **Then** POST /evaluation/labels is called with my validated_course_ids  
> **And** label_source is saved as "student_selected"  
> **And** my student_document is updated with validated_course_ids

---

### US-5.2 – Admin xem metrics đánh giá

**As an** admin,  
**I want to** view Top-1 Accuracy, Hit Rate@3, and Average Processing Time,  
**So that** I can assess how well the Jaccard algorithm performs.

**Acceptance Criteria:**

> **Given** at least 5 student documents have validated labels  
> **When** I navigate to the Evaluation page  
> **Then** I see Top-1 Accuracy as a percentage  
> **And** I see Hit Rate@3 as a percentage  
> **And** I see Average Processing Time in milliseconds  
> **And** metrics are computed only from real labeled data (not demo data)

---

### US-5.3 – Admin xem báo cáo chi tiết

**As an** admin,  
**I want to** view a per-student breakdown of matching accuracy,  
**So that** I can present detailed evaluation results in the project report.

**Acceptance Criteria:**

> **Given** I am on the Evaluation page  
> **When** I view the detailed report  
> **Then** I see each student's predicted top-1 course, validated course, and whether top-1 was correct  
> **And** I see which students had the correct course in their top-3  
> **And** the data matches the MongoDB match_results collection

---

## Epic 6: Cloud Deployment

**Goal:** Hệ thống chạy được trên Azure với MongoDB Atlas.

---

### US-6.1 – Deploy backend lên Azure App Service

**As a** developer,  
**I want to** deploy the FastAPI backend to Azure App Service,  
**So that** the API is accessible from the internet.

**Acceptance Criteria:**

> **Given** the backend code is pushed to GitHub  
> **When** I deploy to Azure App Service  
> **Then** `https://<app>.azurewebsites.net/docs` is accessible  
> **And** environment variables are configured in App Service settings (not .env file)  
> **And** MongoDB Atlas connection works from Azure

---

### US-6.2 – Deploy frontend lên Azure Static Web Apps

**As a** developer,  
**I want to** deploy the React frontend to Azure Static Web Apps,  
**So that** users can access the web app from anywhere.

**Acceptance Criteria:**

> **Given** the frontend is built with `npm run build`  
> **When** I deploy to Azure Static Web Apps  
> **Then** the frontend URL is accessible in browser  
> **And** VITE_API_BASE_URL points to the deployed Azure backend  
> **And** login, upload, and matching all work on production

---

### US-6.3 – CORS hoạt động trên production

**As a** developer,  
**I want** the backend to accept requests only from the production frontend domain,  
**So that** cross-origin requests are secure.

**Acceptance Criteria:**

> **Given** both frontend and backend are deployed  
> **When** frontend makes API calls to backend  
> **Then** CORS headers allow the frontend domain  
> **And** requests from other origins are blocked  
> **And** OPTIONS preflight requests return 200
