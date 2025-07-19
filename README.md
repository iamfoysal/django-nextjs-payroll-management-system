# Payroll Management System

**A comprehensive, full-stack payroll management solution built with Django and Next.js**

**Demo Credentials:**
- Username: `admin`
- Password: `admin123`

## 📋 Table of Contents

1. [Overview](#overview)
2. [Features](#features)
3. [Technology Stack](#technology-stack)
4. [Architecture](#architecture)
5. [Installation & Setup](#installation--setup)
6. [API Documentation](#api-documentation)
7. [User Guide](#user-guide)
8. [Development Guide](#development-guide)
9. [Deployment](#deployment)
10. [Contributing](#contributing)
11. [License](#license)

## 🎯 Overview

The Payroll Management System is a modern, full-stack web application designed to streamline payroll operations for organizations of all sizes. Built with Django REST Framework for the backend and Next.js for the frontend, this system provides comprehensive employee lifecycle management, attendance tracking, leave management, and automated payroll processing.

### Key Highlights

- **Role-based Access Control**: Separate interfaces for Admin, HR, and Employee roles
- **Real-time Attendance Tracking**: Clock in/out functionality with overtime calculation
- **Automated Payroll Processing**: Generate payslips with detailed salary breakdowns
- **Leave Management Workflow**: Complete leave application and approval system
- **Professional UI/UX**: Modern, responsive design with shadcn/ui components
- **RESTful API**: Well-documented API endpoints for all operations
- **Security**: JWT-based authentication with secure data handling

## ✨ Features

### 🏠 Dashboard
- Real-time employee statistics and metrics
- Attendance rate monitoring (91.2% present today)
- Overtime tracking and analysis
- Recent activities and notifications
- Quick action buttons for common tasks

### 👥 Employee Management
- Complete CRUD operations for employee records
- Advanced search and filtering capabilities
- Department and role assignment
- Salary configuration (fixed/hourly rates)
- Professional employee directory with avatars
- Role-based access control for HR/Admin

### ⏰ Attendance Tracking
- Real-time clock in/out functionality
- Automatic working hours calculation
- Overtime tracking and reporting
- Location-based attendance (Office/Remote)
- Break time management
- Weekly and monthly attendance trends
- Department-wise attendance analytics

### 🏖️ Leave Management
- Multiple leave types (Annual, Sick, Personal, Emergency)
- Leave balance tracking with visual progress bars
- Complete approval workflow for HR/Admin
- Leave history and status tracking
- Advanced filtering and search capabilities
- Emergency contact management

### 💰 Payroll Processing
- Generate payroll for selected pay periods
- Detailed payslip views with earnings/deductions breakdown
- Tax calculation with configurable rules
- Mark payments as paid functionality
- Role-based access (HR/Admin generate, employees view)
- Export capabilities for PDF/Excel
- Salary comparison and analytics

### 📊 Reports & Analytics
- Working hours reports (daily/weekly/monthly)
- Overtime analysis and cost tracking
- Leave summary and breakdown reports
- Payroll summary with comparison charts
- Employee performance insights
- Department-wise analytics
- Exportable reports (PDF/Excel)

### 🔐 Security & Authentication
- JWT-based authentication system
- Role-based access control (Admin/HR/Employee)
- Protected API endpoints
- Secure password handling
- Session management

## 🛠️ Technology Stack

### Backend
- **Django 5.2**: Web framework
- **Django REST Framework 3.15.2**: API development
- **PostgreSQL**: Database (SQLite for development)
- **JWT**: Authentication tokens
- **Django CORS Headers**: Cross-origin resource sharing
- **Django Filter**: Advanced filtering capabilities

### Frontend
- **Next.js 14**: React framework
- **React 18**: UI library
- **Tailwind CSS**: Styling framework
- **shadcn/ui**: Component library
- **Lucide Icons**: Icon library
- **Axios**: HTTP client
- **date-fns**: Date manipulation

### Development Tools
- **Python 3.11**: Backend runtime
- **Node.js 20**: Frontend runtime
- **pnpm**: Package manager
- **Vite**: Build tool

## 🏗️ Architecture

The system follows a modern microservices architecture with clear separation between frontend and backend:

```
┌─────────────────┐    ┌─────────────────┐
│   Next.js       │    │   Django        │
│   Frontend      │◄──►│   Backend       │
│   (Port 5173)   │    │   (Port 8000)   │
└─────────────────┘    └─────────────────┘
         │                       │
         │                       │
         ▼                       ▼
┌─────────────────┐    ┌─────────────────┐
│   Static Files  │    │   PostgreSQL    │
│   (Deployed)    │    │   Database      │
└─────────────────┘    └─────────────────┘
```

### Database Schema

The system uses a well-structured database schema with the following key models:

- **Employee**: Custom user model with role-based permissions
- **Department**: Organizational structure
- **Attendance**: Daily attendance records with clock in/out times
- **Leave**: Leave applications and approvals
- **Payroll**: Salary calculations and payment records
- **Report**: Analytics and reporting data

## 🚀 Installation & Setup

### Prerequisites

- Python 3.11+
- Node.js 20+
- pnpm (or npm)
- Git

### Backend Setup

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd payroll_system
   ```

2. **Create and activate virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables:**
   ```bash
   export SECRET_KEY="your-secret-key"
   export DEBUG=True
   export ALLOWED_HOSTS="localhost,127.0.0.1"
   ```

5. **Run migrations:**
   ```bash
   python manage.py migrate
   ```

6. **Create default groups and admin user:**
   ```bash
   python manage.py setup_payroll_system --create-admin
   ```

7. **Start the development server:**
   ```bash
   python manage.py runserver 0.0.0.0:8000
   ```

### Frontend Setup

1. **Navigate to frontend directory:**
   ```bash
   cd payroll-frontend
   ```

2. **Install dependencies:**
   ```bash
   pnpm install
   ```

3. **Start the development server:**
   ```bash
   pnpm run dev --host
   ```

4. **Access the application:**
   Open [http://localhost:5173](http://localhost:5173) in your browser

### Default Credentials

- **Username:** admin
- **Password:** admin123

## 📚 API Documentation

The system provides a comprehensive RESTful API with the following endpoints:

### Authentication Endpoints

```
POST /api/auth/login/          # User login
POST /api/auth/logout/         # User logout
POST /api/auth/refresh/        # Refresh JWT token
GET  /api/auth/user/           # Get current user info
```

### Employee Management

```
GET    /api/employees/         # List all employees
POST   /api/employees/         # Create new employee
GET    /api/employees/{id}/    # Get employee details
PUT    /api/employees/{id}/    # Update employee
DELETE /api/employees/{id}/    # Delete employee
```

### Attendance Management

```
GET    /api/attendance/        # List attendance records
POST   /api/attendance/        # Create attendance record
POST   /api/attendance/clock-in/    # Clock in
POST   /api/attendance/clock-out/   # Clock out
GET    /api/attendance/my-records/  # Get user's records
```

### Leave Management

```
GET    /api/leaves/            # List leave requests
POST   /api/leaves/            # Create leave request
PUT    /api/leaves/{id}/       # Update leave request
GET    /api/leaves/my-leaves/  # Get user's leaves
POST   /api/leaves/{id}/approve/    # Approve leave
POST   /api/leaves/{id}/reject/     # Reject leave
```

### Payroll Management

```
GET    /api/payroll/           # List payroll records
POST   /api/payroll/generate/ # Generate payroll
GET    /api/payroll/{id}/      # Get payroll details
POST   /api/payroll/{id}/pay/ # Mark as paid
```

### Reports & Analytics

```
GET    /api/reports/working-hours/     # Working hours report
GET    /api/reports/overtime/          # Overtime report
GET    /api/reports/leave-summary/     # Leave summary
GET    /api/reports/payroll-summary/   # Payroll summary
```

## 👥 User Guide

### For Employees

1. **Login**: Use your credentials to access the system
2. **Dashboard**: View your personal statistics and quick actions
3. **Attendance**: Clock in/out and view your attendance history
4. **Leave Management**: Apply for leaves and track their status
5. **Payslips**: View and download your salary slips

### For HR Personnel

1. **Employee Management**: Add, edit, and manage employee records
2. **Leave Approvals**: Review and approve/reject leave requests
3. **Attendance Monitoring**: Track employee attendance and overtime
4. **Payroll Processing**: Generate and manage payroll for all employees
5. **Reports**: Generate various reports for analysis

### For Administrators

1. **Full System Access**: Complete control over all system features
2. **User Management**: Create and manage user accounts and roles
3. **System Configuration**: Configure departments, leave types, and policies
4. **Advanced Reports**: Access to comprehensive analytics and insights

## 💻 Development Guide

### Project Structure

```
payroll_system/
├── payroll_backend/          # Django project settings
├── employees/                # Employee management app
├── attendance/               # Attendance tracking app
├── payroll/                  # Payroll processing app
├── reports/                  # Reports and analytics app
├── payroll-frontend/         # Next.js frontend
│   ├── src/
│   │   ├── components/       # React components
│   │   ├── contexts/         # React contexts
│   │   └── pages/            # Page components
│   └── public/               # Static assets
├── requirements.txt          # Python dependencies
└── README.md                 # This file
```

### Adding New Features

1. **Backend**: Create new Django apps or extend existing ones
2. **API**: Add new endpoints in `views.py` and `urls.py`
3. **Frontend**: Create new components in the appropriate directory
4. **Routing**: Update the navigation in `MainLayout.jsx`

### Code Style

- **Backend**: Follow PEP 8 Python style guide
- **Frontend**: Use ESLint and Prettier for consistent formatting
- **Components**: Use functional components with hooks
- **API**: Follow RESTful conventions

### Testing

```bash
# Backend tests
python manage.py test

# Frontend tests
cd payroll-frontend
pnpm test
```

## 🚀 Deployment

### Frontend Deployment

To deploy updates:

1. **Build the application:**
   ```bash
   cd payroll-frontend
   pnpm run build
   ```

2. **Deploy to production:**
   The build artifacts are automatically deployed to the permanent URL.

### Backend Deployment

The backend can be deployed to various platforms:

1. **Heroku**: Use the provided `Procfile` and requirements
2. **AWS**: Deploy using Elastic Beanstalk or EC2
3. **DigitalOcean**: Use App Platform or Droplets
4. **Docker**: Containerize using the provided Dockerfile

### Environment Variables

Set the following environment variables in production:

```bash
SECRET_KEY=your-production-secret-key
DEBUG=False
ALLOWED_HOSTS=your-domain.com
DATABASE_URL=your-database-url
CORS_ALLOWED_ORIGINS=https://your-frontend-domain.com
```

## 🤝 Contributing

We welcome contributions to improve the Payroll Management System! Please follow these guidelines:

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/new-feature`
3. **Make your changes** and add tests
4. **Commit your changes**: `git commit -m 'Add new feature'`
5. **Push to the branch**: `git push origin feature/new-feature`
6. **Submit a pull request**

### Development Setup

1. Follow the installation instructions above
2. Create a new branch for your feature
3. Make your changes and test thoroughly
4. Submit a pull request with a clear description

## 📄 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Django**: For the robust backend framework
- **Next.js**: For the modern frontend framework
- **shadcn/ui**: For the beautiful UI components
- **Tailwind CSS**: For the utility-first CSS framework

## 📞 Support

For support and questions:

- **Documentation**: Refer to this README and inline code comments
- **Issues**: Create an issue on the repository
- **Email**: Contact the development team

---
