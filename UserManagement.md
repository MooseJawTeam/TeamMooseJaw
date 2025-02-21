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

### 4. User Deactivation
- Administrators can **deactivate** and **reactivate** user accounts.
- Deactivated users **cannot log in** or access system resources.

### 5. User Interface
- A **web-based interface** allows administrators to manage users and roles.
- The interface is designed to be **user-friendly and intuitive**.

## Project Setup & Deployment

### GitHub Repository & Collaboration
- The project is managed on **GitHub** with a structured workflow.
- Team members track progress using **GitHub Issues and Projects**.

### Azure Deployment
- The application is deployed on **Azure App Service**.
- Authentication is configured using **Azure AD**.

### CI/CD Pipeline
- **GitHub Actions** automate the deployment process.
- Code changes are tested and deployed seamlessly.

## Deliverables
- **[GitHub Repository](https://github.com/MooseJawTeam/TeamMooseJaw)**
- **GitHub Project Board Link**
- **Collaboration Report Screenshot** (GitHub Contributors Graph)
- **Peer Review for Another Project**
