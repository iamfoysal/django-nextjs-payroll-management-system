import React from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import {
  Users,
  Calendar,
  DollarSign,
  Clock,
  TrendingUp,
  CheckCircle,
  AlertCircle,
  XCircle
} from 'lucide-react';

const Dashboard = () => {
  const { user, isAdmin, isHR } = useAuth();

  // Mock data - in a real app, this would come from API calls
  const stats = {
    totalEmployees: 156,
    presentToday: 142,
    onLeave: 8,
    pendingLeaves: 5,
    totalPayroll: 2450000,
    avgSalary: 15705,
    overtimeHours: 234,
    attendanceRate: 91.2
  };

  const recentActivities = [
    {
      id: 1,
      type: 'leave_approved',
      message: 'Leave application approved for John Doe',
      time: '2 hours ago',
      icon: CheckCircle,
      color: 'text-green-600'
    },
    {
      id: 2,
      type: 'payroll_processed',
      message: 'Monthly payroll processed for December 2024',
      time: '5 hours ago',
      icon: DollarSign,
      color: 'text-blue-600'
    },
    {
      id: 3,
      type: 'attendance_alert',
      message: 'Late arrival alert for 3 employees',
      time: '1 day ago',
      icon: AlertCircle,
      color: 'text-yellow-600'
    },
    {
      id: 4,
      type: 'leave_rejected',
      message: 'Leave application rejected for Jane Smith',
      time: '2 days ago',
      icon: XCircle,
      color: 'text-red-600'
    }
  ];

  const StatCard = ({ title, value, description, icon: Icon, trend }) => (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-sm font-medium">{title}</CardTitle>
        <Icon className="h-4 w-4 text-muted-foreground" />
      </CardHeader>
      <CardContent>
        <div className="text-2xl font-bold">{value}</div>
        <p className="text-xs text-muted-foreground">
          {description}
          {trend && (
            <span className={`ml-1 ${trend > 0 ? 'text-green-600' : 'text-red-600'}`}>
              {trend > 0 ? '+' : ''}{trend}%
            </span>
          )}
        </p>
      </CardContent>
    </Card>
  );

  return (
    <div className="space-y-6">
      {/* Welcome Section */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">
            Welcome back, {user?.first_name || user?.username}!
          </h1>
          <p className="text-muted-foreground">
            Here's what's happening with your payroll system today.
          </p>
        </div>
        <Badge variant="outline" className="text-sm">
          {user?.role?.name || 'Employee'}
        </Badge>
      </div>

      {/* Stats Grid */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <StatCard
          title="Total Employees"
          value={stats.totalEmployees}
          description="Active employees"
          icon={Users}
          trend={2.5}
        />
        <StatCard
          title="Present Today"
          value={stats.presentToday}
          description={`${stats.attendanceRate}% attendance rate`}
          icon={CheckCircle}
          trend={1.2}
        />
        <StatCard
          title="On Leave"
          value={stats.onLeave}
          description={`${stats.pendingLeaves} pending approvals`}
          icon={Calendar}
        />
        <StatCard
          title="Overtime Hours"
          value={stats.overtimeHours}
          description="This month"
          icon={Clock}
          trend={-5.2}
        />
      </div>

      {/* Additional Stats for HR/Admin */}
      {(isHR || isAdmin) && (
        <div className="grid gap-4 md:grid-cols-2">
          <StatCard
            title="Total Payroll"
            value={`$${stats.totalPayroll.toLocaleString()}`}
            description="Monthly payroll cost"
            icon={DollarSign}
            trend={3.1}
          />
          <StatCard
            title="Average Salary"
            value={`$${stats.avgSalary.toLocaleString()}`}
            description="Per employee"
            icon={TrendingUp}
            trend={1.8}
          />
        </div>
      )}

      {/* Recent Activities */}
      <div className="grid gap-4 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Recent Activities</CardTitle>
            <CardDescription>
              Latest updates and notifications
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {recentActivities.map((activity) => {
                const Icon = activity.icon;
                return (
                  <div key={activity.id} className="flex items-start space-x-3">
                    <Icon className={`h-5 w-5 mt-0.5 ${activity.color}`} />
                    <div className="flex-1 space-y-1">
                      <p className="text-sm font-medium">{activity.message}</p>
                      <p className="text-xs text-muted-foreground">{activity.time}</p>
                    </div>
                  </div>
                );
              })}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Quick Actions</CardTitle>
            <CardDescription>
              Common tasks and shortcuts
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              <button className="w-full text-left p-3 rounded-lg border hover:bg-accent transition-colors">
                <div className="font-medium">Mark Attendance</div>
                <div className="text-sm text-muted-foreground">Clock in/out for today</div>
              </button>
              <button className="w-full text-left p-3 rounded-lg border hover:bg-accent transition-colors">
                <div className="font-medium">Apply for Leave</div>
                <div className="text-sm text-muted-foreground">Submit a new leave request</div>
              </button>
              {(isHR || isAdmin) && (
                <>
                  <button className="w-full text-left p-3 rounded-lg border hover:bg-accent transition-colors">
                    <div className="font-medium">Process Payroll</div>
                    <div className="text-sm text-muted-foreground">Generate monthly payroll</div>
                  </button>
                  <button className="w-full text-left p-3 rounded-lg border hover:bg-accent transition-colors">
                    <div className="font-medium">View Reports</div>
                    <div className="text-sm text-muted-foreground">Access analytics and reports</div>
                  </button>
                </>
              )}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default Dashboard;

