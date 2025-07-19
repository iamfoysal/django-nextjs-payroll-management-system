from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Count, Sum, Avg, Q, F
from django.utils import timezone
from datetime import datetime, timedelta, date
from decimal import Decimal
import calendar
from .serializers import (
    ReportFilterSerializer, WorkingHoursReportSerializer, OvertimeReportSerializer,
    LeaveReportSerializer, PayrollSummaryReportSerializer, EmployeePerformanceReportSerializer,
    DepartmentAnalyticsSerializer, CompanyAnalyticsSerializer, ReportExportSerializer,
    CustomReportSerializer, ReportMetadataSerializer
)
from employees.models import Employee, Department
from employees.permissions import CanViewReports, CanGenerateReports
from attendance.models import AttendanceRecord, LeaveApplication, LeaveType
from payroll.models import Payroll, PayrollPeriod


class ReportsViewSet(viewsets.ViewSet):
    """Main ViewSet for all reporting functionality"""
    
    permission_classes = [CanViewReports]
    
    def get_date_range(self, request):
        """Get date range from request parameters"""
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        if start_date:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        else:
            # Default to current month
            today = timezone.now().date()
            start_date = today.replace(day=1)
        
        if end_date:
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        else:
            # Default to end of current month
            today = timezone.now().date()
            _, last_day = calendar.monthrange(today.year, today.month)
            end_date = today.replace(day=last_day)
        
        return start_date, end_date
    
    def get_filtered_employees(self, request):
        """Get filtered employees based on request parameters"""
        employees = Employee.objects.filter(is_active=True)
        
        employee_ids = request.query_params.getlist('employee_ids')
        if employee_ids:
            employees = employees.filter(id__in=employee_ids)
        
        department_ids = request.query_params.getlist('department_ids')
        if department_ids:
            employees = employees.filter(department_id__in=department_ids)
        
        return employees
    
    @action(detail=False, methods=['get'])
    def working_hours(self, request):
        """Generate working hours report"""
        start_date, end_date = self.get_date_range(request)
        employees = self.get_filtered_employees(request)
        
        report_data = []
        
        for employee in employees:
            # Get attendance records for the period
            attendance_records = AttendanceRecord.objects.filter(
                employee=employee,
                date__gte=start_date,
                date__lte=end_date
            )
            
            # Calculate metrics
            total_days = (end_date - start_date).days + 1
            working_days = self.calculate_working_days(start_date, end_date)
            present_days = attendance_records.filter(status='PRESENT').count()
            absent_days = attendance_records.filter(status='ABSENT').count()
            leave_days = attendance_records.filter(status='LEAVE').count()
            
            # Calculate hours
            total_hours = attendance_records.aggregate(
                total=Sum('total_hours')
            )['total'] or Decimal('0.00')
            
            regular_hours = attendance_records.aggregate(
                total=Sum('regular_hours')
            )['total'] or Decimal('0.00')
            
            overtime_hours = attendance_records.aggregate(
                total=Sum('overtime_hours')
            )['total'] or Decimal('0.00')
            
            # Calculate rates
            attendance_rate = (present_days / working_days * 100) if working_days > 0 else 0
            late_days = attendance_records.filter(is_late=True).count()
            punctuality_rate = ((present_days - late_days) / present_days * 100) if present_days > 0 else 0
            
            average_daily_hours = total_hours / present_days if present_days > 0 else Decimal('0.00')
            
            # Daily breakdown (optional)
            daily_breakdown = []
            if request.query_params.get('include_daily') == 'true':
                for record in attendance_records.order_by('date'):
                    daily_breakdown.append({
                        'date': record.date,
                        'status': record.status,
                        'time_in': record.time_in,
                        'time_out': record.time_out,
                        'total_hours': record.total_hours,
                        'overtime_hours': record.overtime_hours,
                        'is_late': record.is_late
                    })
            
            employee_data = {
                'employee_id': employee.employee_id,
                'employee_name': employee.get_full_name(),
                'department': employee.department.name if employee.department else 'N/A',
                'total_days': total_days,
                'working_days': working_days,
                'present_days': present_days,
                'absent_days': absent_days,
                'leave_days': leave_days,
                'total_hours': total_hours,
                'regular_hours': regular_hours,
                'overtime_hours': overtime_hours,
                'average_daily_hours': average_daily_hours,
                'attendance_rate': round(attendance_rate, 2),
                'punctuality_rate': round(punctuality_rate, 2),
                'daily_breakdown': daily_breakdown
            }
            
            report_data.append(employee_data)
        
        serializer = WorkingHoursReportSerializer(report_data, many=True)
        return Response({
            'report_type': 'working_hours',
            'period': {
                'start_date': start_date,
                'end_date': end_date
            },
            'data': serializer.data,
            'summary': self.calculate_working_hours_summary(report_data)
        })
    
    @action(detail=False, methods=['get'])
    def overtime(self, request):
        """Generate overtime report"""
        start_date, end_date = self.get_date_range(request)
        employees = self.get_filtered_employees(request)
        
        report_data = []
        
        for employee in employees:
            # Get attendance records with overtime
            overtime_records = AttendanceRecord.objects.filter(
                employee=employee,
                date__gte=start_date,
                date__lte=end_date,
                overtime_hours__gt=0
            )
            
            # Calculate overtime metrics
            total_overtime_hours = overtime_records.aggregate(
                total=Sum('overtime_hours')
            )['total'] or Decimal('0.00')
            
            overtime_days = overtime_records.count()
            average_overtime_per_day = (
                total_overtime_hours / overtime_days if overtime_days > 0 else Decimal('0.00')
            )
            
            # Calculate overtime amount (assuming 1.5x regular rate)
            hourly_rate = employee.hourly_rate or Decimal('0.00')
            if employee.salary_type == 'FIXED' and employee.base_salary:
                # Calculate hourly rate from monthly salary
                monthly_hours = Decimal('160.00')  # Assuming 160 hours per month
                hourly_rate = employee.base_salary / monthly_hours
            
            overtime_rate = hourly_rate * Decimal('1.5')
            overtime_amount = total_overtime_hours * overtime_rate
            
            # Weekly breakdown
            weekly_breakdown = []
            current_date = start_date
            while current_date <= end_date:
                week_end = min(current_date + timedelta(days=6), end_date)
                week_overtime = overtime_records.filter(
                    date__gte=current_date,
                    date__lte=week_end
                ).aggregate(total=Sum('overtime_hours'))['total'] or Decimal('0.00')
                
                if week_overtime > 0:
                    weekly_breakdown.append({
                        'week_start': current_date,
                        'week_end': week_end,
                        'overtime_hours': week_overtime,
                        'overtime_amount': week_overtime * overtime_rate
                    })
                
                current_date = week_end + timedelta(days=1)
            
            # Monthly breakdown
            monthly_breakdown = []
            current_month = start_date.replace(day=1)
            while current_month <= end_date:
                month_end = (current_month.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)
                month_end = min(month_end, end_date)
                
                month_overtime = overtime_records.filter(
                    date__gte=current_month,
                    date__lte=month_end
                ).aggregate(total=Sum('overtime_hours'))['total'] or Decimal('0.00')
                
                if month_overtime > 0:
                    monthly_breakdown.append({
                        'month': current_month.strftime('%Y-%m'),
                        'overtime_hours': month_overtime,
                        'overtime_amount': month_overtime * overtime_rate
                    })
                
                # Move to next month
                if current_month.month == 12:
                    current_month = current_month.replace(year=current_month.year + 1, month=1)
                else:
                    current_month = current_month.replace(month=current_month.month + 1)
            
            employee_data = {
                'employee_id': employee.employee_id,
                'employee_name': employee.get_full_name(),
                'department': employee.department.name if employee.department else 'N/A',
                'total_overtime_hours': total_overtime_hours,
                'overtime_days': overtime_days,
                'average_overtime_per_day': average_overtime_per_day,
                'overtime_amount': overtime_amount,
                'weekly_breakdown': weekly_breakdown,
                'monthly_breakdown': monthly_breakdown
            }
            
            report_data.append(employee_data)
        
        serializer = OvertimeReportSerializer(report_data, many=True)
        return Response({
            'report_type': 'overtime',
            'period': {
                'start_date': start_date,
                'end_date': end_date
            },
            'data': serializer.data,
            'summary': self.calculate_overtime_summary(report_data)
        })
    
    @action(detail=False, methods=['get'])
    def leave(self, request):
        """Generate leave report"""
        start_date, end_date = self.get_date_range(request)
        employees = self.get_filtered_employees(request)
        
        report_data = []
        
        for employee in employees:
            # Get leave applications for the period
            leave_applications = LeaveApplication.objects.filter(
                employee=employee,
                start_date__gte=start_date,
                end_date__lte=end_date
            )
            
            # Calculate leave metrics
            total_leaves_taken = leave_applications.filter(
                status='APPROVED'
            ).aggregate(total=Sum('total_days'))['total'] or 0
            
            # Leave breakdown by type
            leave_type_breakdown = []
            leave_types = LeaveType.objects.filter(is_active=True)
            
            for leave_type in leave_types:
                type_leaves = leave_applications.filter(
                    leave_type=leave_type,
                    status='APPROVED'
                ).aggregate(total=Sum('total_days'))['total'] or 0
                
                leave_type_breakdown.append({
                    'leave_type': leave_type.name,
                    'days_taken': type_leaves,
                    'max_allowed': leave_type.max_days_per_year
                })
            
            # Application status breakdown
            pending_applications = leave_applications.filter(status='PENDING').count()
            approved_applications = leave_applications.filter(status='APPROVED').count()
            rejected_applications = leave_applications.filter(status='REJECTED').count()
            
            # Monthly breakdown
            monthly_breakdown = []
            current_month = start_date.replace(day=1)
            while current_month <= end_date:
                month_end = (current_month.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)
                month_end = min(month_end, end_date)
                
                month_leaves = leave_applications.filter(
                    start_date__gte=current_month,
                    end_date__lte=month_end,
                    status='APPROVED'
                ).aggregate(total=Sum('total_days'))['total'] or 0
                
                monthly_breakdown.append({
                    'month': current_month.strftime('%Y-%m'),
                    'leaves_taken': month_leaves
                })
                
                # Move to next month
                if current_month.month == 12:
                    current_month = current_month.replace(year=current_month.year + 1, month=1)
                else:
                    current_month = current_month.replace(month=current_month.month + 1)
            
            employee_data = {
                'employee_id': employee.employee_id,
                'employee_name': employee.get_full_name(),
                'department': employee.department.name if employee.department else 'N/A',
                'annual_leave_balance': employee.annual_leave_balance,
                'sick_leave_balance': employee.sick_leave_balance,
                'casual_leave_balance': employee.casual_leave_balance,
                'total_leaves_taken': total_leaves_taken,
                'annual_leaves_taken': leave_applications.filter(
                    leave_type__name='Annual Leave',
                    status='APPROVED'
                ).aggregate(total=Sum('total_days'))['total'] or 0,
                'sick_leaves_taken': leave_applications.filter(
                    leave_type__name='Sick Leave',
                    status='APPROVED'
                ).aggregate(total=Sum('total_days'))['total'] or 0,
                'casual_leaves_taken': leave_applications.filter(
                    leave_type__name='Casual Leave',
                    status='APPROVED'
                ).aggregate(total=Sum('total_days'))['total'] or 0,
                'leave_type_breakdown': leave_type_breakdown,
                'pending_applications': pending_applications,
                'approved_applications': approved_applications,
                'rejected_applications': rejected_applications,
                'monthly_breakdown': monthly_breakdown
            }
            
            report_data.append(employee_data)
        
        serializer = LeaveReportSerializer(report_data, many=True)
        return Response({
            'report_type': 'leave',
            'period': {
                'start_date': start_date,
                'end_date': end_date
            },
            'data': serializer.data,
            'summary': self.calculate_leave_summary(report_data)
        })
    
    @action(detail=False, methods=['get'])
    def payroll_summary(self, request):
        """Generate payroll summary report"""
        period_id = request.query_params.get('period_id')
        
        if period_id:
            try:
                payroll_period = PayrollPeriod.objects.get(id=period_id)
            except PayrollPeriod.DoesNotExist:
                return Response(
                    {'error': 'Payroll period not found.'},
                    status=status.HTTP_404_NOT_FOUND
                )
        else:
            # Get current period
            today = timezone.now().date()
            payroll_period = PayrollPeriod.objects.filter(
                start_date__lte=today,
                end_date__gte=today
            ).first()
            
            if not payroll_period:
                return Response(
                    {'error': 'No active payroll period found.'},
                    status=status.HTTP_404_NOT_FOUND
                )
        
        # Get payrolls for the period
        payrolls = Payroll.objects.filter(payroll_period=payroll_period)
        employees = self.get_filtered_employees(request)
        payrolls = payrolls.filter(employee__in=employees)
        
        # Calculate summary metrics
        total_employees = payrolls.count()
        active_employees = employees.count()
        
        totals = payrolls.aggregate(
            total_gross=Sum('gross_salary'),
            total_net=Sum('net_salary'),
            total_deductions=Sum('total_deductions'),
            total_bonuses=Sum('total_bonuses'),
            total_overtime=Sum('overtime_amount'),
            total_tax=Sum('tax_amount'),
            avg_gross=Avg('gross_salary'),
            avg_net=Avg('net_salary')
        )
        
        # Department breakdown
        department_breakdown = list(
            payrolls.values('employee__department__name')
            .annotate(
                department=F('employee__department__name'),
                employee_count=Count('id'),
                total_gross=Sum('gross_salary'),
                total_net=Sum('net_salary'),
                avg_salary=Avg('net_salary')
            )
            .order_by('-total_gross')
        )
        
        # Status breakdown
        status_breakdown = list(
            payrolls.values('status')
            .annotate(count=Count('id'))
            .order_by('-count')
        )
        
        report_data = {
            'period_name': payroll_period.name,
            'start_date': payroll_period.start_date,
            'end_date': payroll_period.end_date,
            'total_employees': total_employees,
            'active_employees': active_employees,
            'total_gross_salary': totals['total_gross'] or Decimal('0.00'),
            'total_net_salary': totals['total_net'] or Decimal('0.00'),
            'total_deductions': totals['total_deductions'] or Decimal('0.00'),
            'total_bonuses': totals['total_bonuses'] or Decimal('0.00'),
            'total_overtime': totals['total_overtime'] or Decimal('0.00'),
            'total_tax': totals['total_tax'] or Decimal('0.00'),
            'average_gross_salary': totals['avg_gross'] or Decimal('0.00'),
            'average_net_salary': totals['avg_net'] or Decimal('0.00'),
            'department_breakdown': department_breakdown,
            'status_breakdown': status_breakdown
        }
        
        serializer = PayrollSummaryReportSerializer(report_data)
        return Response({
            'report_type': 'payroll_summary',
            'data': serializer.data
        })
    
    @action(detail=False, methods=['get'])
    def employee_performance(self, request):
        """Generate employee performance insights report"""
        start_date, end_date = self.get_date_range(request)
        employees = self.get_filtered_employees(request)
        
        report_data = []
        
        for employee in employees:
            # Get performance metrics
            attendance_records = AttendanceRecord.objects.filter(
                employee=employee,
                date__gte=start_date,
                date__lte=end_date
            )
            
            working_days = self.calculate_working_days(start_date, end_date)
            days_present = attendance_records.filter(status='PRESENT').count()
            days_late = attendance_records.filter(is_late=True).count()
            
            # Calculate scores (0-100)
            attendance_reliability_score = (days_present / working_days * 100) if working_days > 0 else 0
            punctuality_score = ((days_present - days_late) / days_present * 100) if days_present > 0 else 0
            
            # Overtime efficiency (subjective metric)
            total_overtime = attendance_records.aggregate(
                total=Sum('overtime_hours')
            )['total'] or Decimal('0.00')
            overtime_efficiency_score = min(100, max(0, 100 - float(total_overtime) * 2))  # Penalty for excessive overtime
            
            # Leave utilization score
            leaves_taken = LeaveApplication.objects.filter(
                employee=employee,
                start_date__gte=start_date,
                end_date__lte=end_date,
                status='APPROVED'
            ).aggregate(total=Sum('total_days'))['total'] or 0
            
            max_leaves = employee.annual_leave_balance + employee.sick_leave_balance + employee.casual_leave_balance
            leave_utilization_score = 100 - (leaves_taken / max_leaves * 100) if max_leaves > 0 else 100
            
            # Overall performance score (weighted average)
            overall_performance_score = (
                attendance_reliability_score * 0.3 +
                punctuality_score * 0.3 +
                overtime_efficiency_score * 0.2 +
                leave_utilization_score * 0.2
            )
            
            # Generate recommendations
            recommendations = []
            if attendance_reliability_score < 80:
                recommendations.append("Improve attendance consistency")
            if punctuality_score < 80:
                recommendations.append("Focus on punctuality")
            if total_overtime > 40:
                recommendations.append("Consider workload optimization")
            if leaves_taken > max_leaves * 0.8:
                recommendations.append("Monitor leave usage patterns")
            
            employee_data = {
                'employee_id': employee.employee_id,
                'employee_name': employee.get_full_name(),
                'department': employee.department.name if employee.department else 'N/A',
                'role': employee.role.title if employee.role else 'N/A',
                'attendance_reliability_score': round(attendance_reliability_score, 2),
                'punctuality_score': round(punctuality_score, 2),
                'overtime_efficiency_score': round(overtime_efficiency_score, 2),
                'leave_utilization_score': round(leave_utilization_score, 2),
                'overall_performance_score': round(overall_performance_score, 2),
                'total_working_days': working_days,
                'days_present': days_present,
                'days_late': days_late,
                'total_overtime_hours': total_overtime,
                'leaves_taken': leaves_taken,
                'recommendations': recommendations
            }
            
            report_data.append(employee_data)
        
        # Sort by overall performance score
        report_data.sort(key=lambda x: x['overall_performance_score'], reverse=True)
        
        serializer = EmployeePerformanceReportSerializer(report_data, many=True)
        return Response({
            'report_type': 'employee_performance',
            'period': {
                'start_date': start_date,
                'end_date': end_date
            },
            'data': serializer.data,
            'summary': self.calculate_performance_summary(report_data)
        })
    
    def calculate_working_days(self, start_date, end_date):
        """Calculate working days between two dates (excluding weekends)"""
        working_days = 0
        current_date = start_date
        
        while current_date <= end_date:
            if current_date.weekday() < 5:  # Monday to Friday
                working_days += 1
            current_date += timedelta(days=1)
        
        return working_days
    
    def calculate_working_hours_summary(self, report_data):
        """Calculate summary for working hours report"""
        if not report_data:
            return {}
        
        total_employees = len(report_data)
        total_hours = sum(float(emp['total_hours']) for emp in report_data)
        total_overtime = sum(float(emp['overtime_hours']) for emp in report_data)
        avg_attendance_rate = sum(emp['attendance_rate'] for emp in report_data) / total_employees
        
        return {
            'total_employees': total_employees,
            'total_hours_worked': total_hours,
            'total_overtime_hours': total_overtime,
            'average_attendance_rate': round(avg_attendance_rate, 2),
            'top_performer': max(report_data, key=lambda x: x['attendance_rate'])['employee_name']
        }
    
    def calculate_overtime_summary(self, report_data):
        """Calculate summary for overtime report"""
        if not report_data:
            return {}
        
        total_overtime_hours = sum(float(emp['total_overtime_hours']) for emp in report_data)
        total_overtime_cost = sum(float(emp['overtime_amount']) for emp in report_data)
        employees_with_overtime = len([emp for emp in report_data if float(emp['total_overtime_hours']) > 0])
        
        return {
            'total_overtime_hours': total_overtime_hours,
            'total_overtime_cost': total_overtime_cost,
            'employees_with_overtime': employees_with_overtime,
            'average_overtime_per_employee': total_overtime_hours / len(report_data) if report_data else 0
        }
    
    def calculate_leave_summary(self, report_data):
        """Calculate summary for leave report"""
        if not report_data:
            return {}
        
        total_leaves_taken = sum(emp['total_leaves_taken'] for emp in report_data)
        total_pending = sum(emp['pending_applications'] for emp in report_data)
        avg_leaves_per_employee = total_leaves_taken / len(report_data) if report_data else 0
        
        return {
            'total_leaves_taken': total_leaves_taken,
            'total_pending_applications': total_pending,
            'average_leaves_per_employee': round(avg_leaves_per_employee, 2),
            'total_employees': len(report_data)
        }
    
    def calculate_performance_summary(self, report_data):
        """Calculate summary for performance report"""
        if not report_data:
            return {}
        
        avg_performance = sum(emp['overall_performance_score'] for emp in report_data) / len(report_data)
        top_performers = [emp for emp in report_data if emp['overall_performance_score'] >= 90]
        needs_improvement = [emp for emp in report_data if emp['overall_performance_score'] < 70]
        
        return {
            'average_performance_score': round(avg_performance, 2),
            'top_performers_count': len(top_performers),
            'needs_improvement_count': len(needs_improvement),
            'total_employees_evaluated': len(report_data)
        }

