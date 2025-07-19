from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from employees.models import Employee, Department, Role
from attendance.models import LeaveType
from decimal import Decimal


class Command(BaseCommand):
    help = 'Set up the payroll system with default groups, permissions, and sample data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--create-admin',
            action='store_true',
            help='Create a default admin user',
        )
        parser.add_argument(
            '--admin-username',
            type=str,
            default='admin',
            help='Username for the admin user (default: admin)',
        )
        parser.add_argument(
            '--admin-email',
            type=str,
            default='admin@payroll.com',
            help='Email for the admin user (default: admin@payroll.com)',
        )
        parser.add_argument(
            '--admin-password',
            type=str,
            default='admin123',
            help='Password for the admin user (default: admin123)',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Setting up payroll system...'))
        
        # Create default groups
        self.create_default_groups()
        
        # Create default departments
        self.create_default_departments()
        
        # Create default leave types
        self.create_default_leave_types()
        
        # Create admin user if requested
        if options['create_admin']:
            self.create_admin_user(
                username=options['admin_username'],
                email=options['admin_email'],
                password=options['admin_password']
            )
        
        self.stdout.write(
            self.style.SUCCESS('Payroll system setup completed successfully!')
        )

    def create_default_groups(self):
        """Create default user groups with appropriate permissions"""
        self.stdout.write('Creating default groups...')
        
        groups_data = [
            {
                'name': 'Admin',
                'description': 'System administrators with full access'
            },
            {
                'name': 'HR',
                'description': 'Human Resources personnel'
            },
            {
                'name': 'Manager',
                'description': 'Department managers and team leads'
            },
            {
                'name': 'Finance',
                'description': 'Finance and accounting personnel'
            },
            {
                'name': 'Employee',
                'description': 'Regular employees'
            }
        ]
        
        for group_data in groups_data:
            group, created = Group.objects.get_or_create(
                name=group_data['name']
            )
            if created:
                self.stdout.write(f'  Created group: {group.name}')
            else:
                self.stdout.write(f'  Group already exists: {group.name}')

    def create_default_departments(self):
        """Create default departments and roles"""
        self.stdout.write('Creating default departments and roles...')
        
        departments_data = [
            {
                'name': 'Human Resources',
                'description': 'Human Resources Department',
                'roles': [
                    {'title': 'HR Manager', 'base_salary': Decimal('80000.00')},
                    {'title': 'HR Specialist', 'base_salary': Decimal('55000.00')},
                    {'title': 'Recruiter', 'base_salary': Decimal('50000.00')},
                ]
            },
            {
                'name': 'Information Technology',
                'description': 'IT Department',
                'roles': [
                    {'title': 'IT Manager', 'base_salary': Decimal('90000.00')},
                    {'title': 'Senior Developer', 'base_salary': Decimal('75000.00')},
                    {'title': 'Junior Developer', 'base_salary': Decimal('55000.00')},
                    {'title': 'System Administrator', 'base_salary': Decimal('65000.00')},
                ]
            },
            {
                'name': 'Finance',
                'description': 'Finance and Accounting Department',
                'roles': [
                    {'title': 'Finance Manager', 'base_salary': Decimal('85000.00')},
                    {'title': 'Accountant', 'base_salary': Decimal('60000.00')},
                    {'title': 'Financial Analyst', 'base_salary': Decimal('65000.00')},
                ]
            },
            {
                'name': 'Sales',
                'description': 'Sales Department',
                'roles': [
                    {'title': 'Sales Manager', 'base_salary': Decimal('75000.00')},
                    {'title': 'Sales Representative', 'base_salary': Decimal('45000.00')},
                    {'title': 'Account Executive', 'base_salary': Decimal('55000.00')},
                ]
            },
            {
                'name': 'Marketing',
                'description': 'Marketing Department',
                'roles': [
                    {'title': 'Marketing Manager', 'base_salary': Decimal('70000.00')},
                    {'title': 'Marketing Specialist', 'base_salary': Decimal('50000.00')},
                    {'title': 'Content Creator', 'base_salary': Decimal('45000.00')},
                ]
            }
        ]
        
        for dept_data in departments_data:
            department, created = Department.objects.get_or_create(
                name=dept_data['name'],
                defaults={'description': dept_data['description']}
            )
            
            if created:
                self.stdout.write(f'  Created department: {department.name}')
            else:
                self.stdout.write(f'  Department already exists: {department.name}')
            
            # Create roles for this department
            for role_data in dept_data['roles']:
                role, created = Role.objects.get_or_create(
                    title=role_data['title'],
                    department=department,
                    defaults={
                        'base_salary': role_data['base_salary'],
                        'description': f'{role_data["title"]} in {department.name}'
                    }
                )
                
                if created:
                    self.stdout.write(f'    Created role: {role.title}')

    def create_default_leave_types(self):
        """Create default leave types"""
        self.stdout.write('Creating default leave types...')
        
        leave_types_data = [
            {
                'name': 'Annual Leave',
                'description': 'Yearly vacation leave',
                'max_days_per_year': 21,
                'is_paid': True,
                'requires_approval': True,
                'advance_notice_days': 7
            },
            {
                'name': 'Sick Leave',
                'description': 'Medical leave for illness',
                'max_days_per_year': 10,
                'is_paid': True,
                'requires_approval': False,
                'advance_notice_days': 0
            },
            {
                'name': 'Casual Leave',
                'description': 'Short-term personal leave',
                'max_days_per_year': 5,
                'is_paid': True,
                'requires_approval': True,
                'advance_notice_days': 1
            },
            {
                'name': 'Maternity Leave',
                'description': 'Maternity leave for new mothers',
                'max_days_per_year': 90,
                'is_paid': True,
                'requires_approval': True,
                'advance_notice_days': 30
            },
            {
                'name': 'Paternity Leave',
                'description': 'Paternity leave for new fathers',
                'max_days_per_year': 14,
                'is_paid': True,
                'requires_approval': True,
                'advance_notice_days': 14
            },
            {
                'name': 'Emergency Leave',
                'description': 'Emergency personal leave',
                'max_days_per_year': 3,
                'is_paid': False,
                'requires_approval': True,
                'advance_notice_days': 0
            }
        ]
        
        for leave_data in leave_types_data:
            leave_type, created = LeaveType.objects.get_or_create(
                name=leave_data['name'],
                defaults=leave_data
            )
            
            if created:
                self.stdout.write(f'  Created leave type: {leave_type.name}')
            else:
                self.stdout.write(f'  Leave type already exists: {leave_type.name}')

    def create_admin_user(self, username, email, password):
        """Create an admin user"""
        self.stdout.write('Creating admin user...')
        
        # Check if admin user already exists
        if Employee.objects.filter(username=username).exists():
            self.stdout.write(f'  Admin user "{username}" already exists')
            return
        
        # Get HR department and HR Manager role
        hr_dept = Department.objects.filter(name='Human Resources').first()
        hr_manager_role = Role.objects.filter(title='HR Manager').first()
        
        # Create admin user
        admin_user = Employee.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name='System',
            last_name='Administrator',
            employee_id='EMP0000',
            is_staff=True,
            is_superuser=True,
            department=hr_dept,
            role=hr_manager_role,
            employment_type='FULL_TIME',
            salary_type='FIXED',
            base_salary=Decimal('100000.00') if hr_manager_role else None
        )
        
        # Add to Admin and HR groups
        admin_group = Group.objects.get(name='Admin')
        hr_group = Group.objects.get(name='HR')
        admin_user.groups.add(admin_group, hr_group)
        
        self.stdout.write(
            self.style.SUCCESS(f'  Created admin user: {username}')
        )
        self.stdout.write(f'    Email: {email}')
        self.stdout.write(f'    Password: {password}')
        self.stdout.write(
            self.style.WARNING('    Please change the default password after first login!')
        )

