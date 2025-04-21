# User Management System - #TeamMooseJaw

## Project Overview
The **User Management System** is a web-based application designed to manage user authentication, roles, and access 
control while leveraging **Microsoft 365 authentication**. The application is built using the **Django** framework 
and integrates with **Microsoft Graph API** to fetch and store user information. 
The system is deployed on **Azure** and utilizes **GitHub Actions** for automated deployment.

## Technology Stack
- **Backend**: Django (Python)
- **Database**: MySQL
- **Authentication**: Microsoft 365 (via Microsoft Graph API)
- **Deployment**: Azure (App Service)
- **CI/CD**: GitHub Actions
- **Frontend**: HTML, CSS (for responsiveness)
- **PDF Generation**: WeasyPrint, ReportLab, PyPDF2
- **Document Storage**: Local file system (with S3 support)

## Key Features

### 1. Authentication
- Users can log in using their **Office 365 credentials**.
- Authentication is handled securely via **Microsoft Graph API**.

### 2. User Management
- Administrators can **create, read, update, and delete (CRUD)** user accounts.
- User attributes include **name, email, role, and status**.
- The default user role is **"basicuser"**.

### 3. Role-Based Access Control (RBAC)
- The system supports multiple user roles with varying access levels.
- Administrators can assign roles to users.
- Role-based permissions control access to specific system features.

### 4. Document Approval System
- **Request Types**:
  - RCE (Request for Course Exception)
  - Special Circumstance Requests
- **Approval Workflow**:
  - Users submit requests with supporting documentation
  - Administrators review and make decisions (Approve/Deny)
  - System generates official decision documents
  - Users can view and download decision documents
- **Document Tracking**:
  - Status tracking (Pending, Approved, Denied)
  - Timestamp recording for all actions
  - Comment/remark system for decisions

### 5. PDF Generation and Management
- **Document Types**:
  - Approval Letters
  - Denial Letters
  - Decision Documents
- **Features**:
  - Dynamic PDF generation with custom templates
  - Admin signature integration
  - Document versioning
  - Secure document storage
  - Document viewing and downloading capabilities
- **Template System**:
  - Customizable HTML templates
  - Dynamic content insertion
  - Professional formatting
  - Consistent branding

### 6. User Deactivation
- Administrators can **deactivate** and **reactivate** user accounts.
- Deactivated users **cannot log in** or access system resources.

### 7. User Interface
- A **web-based interface** allows administrators to manage users and roles.
- The interface is designed to be **user-friendly and intuitive**.
- Document viewing and management interface
- Approval workflow dashboard

## Project Setup & Deployment

### GitHub Repository & Collaboration
- The project is managed on **GitHub** with a structured workflow.
- Team members track progress using **GitHub Issues and Projects**.

### Azure Deployment
- The application is deployed on **Azure App Service**.
- Authentication is configured using **Azure AD**.
- Document storage configured for both development and production.

### CI/CD Pipeline
- **GitHub Actions** automate the deployment process.
- Code changes are tested and deployed seamlessly.

## Technical Implementation Details

### PDF Generation
- Uses WeasyPrint for HTML to PDF conversion
- Template-based document generation
- Support for admin signatures
- Secure document storage and retrieval

### Approval System
- Role-based access control for approvals
- Document status tracking
- Email notifications for status changes
- Audit trail for all approval actions

### Security Features
- Secure document storage
- Role-based access to documents
- Document version control
- Secure signature handling

## Deliverables
- **[GitHub Repository](https://github.com/MooseJawTeam/TeamMooseJaw)**
- **GitHub Project Board Link**
- **Collaboration Report Screenshot** (GitHub Contributors Graph)
- **Peer Review for Another Project**

## Contributors
- Christa Ongouya
- Christian Barajas
- 
