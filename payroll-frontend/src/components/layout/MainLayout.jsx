import React, { useState } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { Button } from '@/components/ui/button';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { Sheet, SheetContent, SheetTrigger } from '@/components/ui/sheet';
import {
  Users,
  Calendar,
  DollarSign,
  BarChart3,
  Settings,
  LogOut,
  Menu,
  Home,
  Clock,
  FileText,
  UserCheck,
  Building2
} from 'lucide-react';

// Import all page components
import Dashboard from '../dashboard/Dashboard';
import EmployeeManagement from '../employees/EmployeeManagement';
import AttendanceTracking from '../attendance/AttendanceTracking';
import LeaveManagement from '../leaves/LeaveManagement';
import PayrollProcessing from '../payroll/PayrollProcessing';

const MainLayout = () => {
  const { user, logout, isAdmin, isHR } = useAuth();
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [currentPage, setCurrentPage] = useState('dashboard');

  const navigationItems = [
    {
      name: 'Dashboard',
      key: 'dashboard',
      icon: Home,
      component: Dashboard,
    },
    {
      name: 'Employees',
      key: 'employees',
      icon: Users,
      component: EmployeeManagement,
      adminOnly: true,
    },
    {
      name: 'Departments',
      key: 'departments',
      icon: Building2,
      component: () => <div className="p-6">Departments page coming soon...</div>,
      adminOnly: true,
    },
    {
      name: 'Attendance',
      key: 'attendance',
      icon: UserCheck,
      component: AttendanceTracking,
    },
    {
      name: 'Leave Management',
      key: 'leaves',
      icon: Calendar,
      component: LeaveManagement,
    },
    {
      name: 'Payroll',
      key: 'payroll',
      icon: DollarSign,
      component: PayrollProcessing,
      hrOnly: true,
    },
    {
      name: 'Time Tracking',
      key: 'timetracking',
      icon: Clock,
      component: () => <div className="p-6">Time Tracking page coming soon...</div>,
    },
    {
      name: 'Reports',
      key: 'reports',
      icon: BarChart3,
      component: () => <div className="p-6">Reports page coming soon...</div>,
      hrOnly: true,
    },
    {
      name: 'Pay Slips',
      key: 'payslips',
      icon: FileText,
      component: () => <div className="p-6">Pay Slips page coming soon...</div>,
    },
  ];

  const filteredNavItems = navigationItems.filter(item => {
    if (item.adminOnly && !isAdmin) return false;
    if (item.hrOnly && !isHR && !isAdmin) return false;
    return true;
  });

  const handleLogout = () => {
    logout();
  };

  const getUserInitials = () => {
    if (user?.first_name && user?.last_name) {
      return `${user.first_name[0]}${user.last_name[0]}`.toUpperCase();
    }
    return user?.username?.[0]?.toUpperCase() || 'U';
  };

  const handleNavigation = (pageKey) => {
    setCurrentPage(pageKey);
    setSidebarOpen(false);
  };

  const getCurrentComponent = () => {
    const currentItem = navigationItems.find(item => item.key === currentPage);
    if (currentItem && currentItem.component) {
      const Component = currentItem.component;
      return <Component />;
    }
    return <Dashboard />;
  };

  const Sidebar = ({ mobile = false }) => (
    <div className={`flex flex-col h-full ${mobile ? 'w-full' : 'w-64'}`}>
      {/* Logo */}
      <div className="flex items-center justify-center h-16 px-4 border-b">
        <h1 className="text-xl font-bold text-primary">Payroll System</h1>
      </div>

      {/* Navigation */}
      <nav className="flex-1 px-4 py-6 space-y-2">
        {filteredNavItems.map((item) => {
          const Icon = item.icon;
          return (
            <button
              key={item.key}
              onClick={() => handleNavigation(item.key)}
              className={`w-full flex items-center px-3 py-2 text-sm font-medium rounded-md transition-colors ${
                currentPage === item.key
                  ? 'bg-primary text-primary-foreground'
                  : 'text-muted-foreground hover:bg-accent hover:text-accent-foreground'
              }`}
            >
              <Icon className="mr-3 h-5 w-5" />
              {item.name}
            </button>
          );
        })}
      </nav>

      {/* User info */}
      <div className="p-4 border-t">
        <div className="flex items-center space-x-3">
          <Avatar className="h-8 w-8">
            <AvatarImage src={user?.avatar} />
            <AvatarFallback>{getUserInitials()}</AvatarFallback>
          </Avatar>
          <div className="flex-1 min-w-0">
            <p className="text-sm font-medium truncate">
              {user?.first_name} {user?.last_name}
            </p>
            <p className="text-xs text-muted-foreground truncate">
              {user?.email}
            </p>
          </div>
        </div>
      </div>
    </div>
  );

  return (
    <div className="flex h-screen bg-background">
      {/* Desktop Sidebar */}
      <div className="hidden md:flex md:flex-shrink-0">
        <div className="flex flex-col w-64 border-r">
          <Sidebar />
        </div>
      </div>

      {/* Mobile Sidebar */}
      <Sheet open={sidebarOpen} onOpenChange={setSidebarOpen}>
        <SheetContent side="left" className="p-0 w-64">
          <Sidebar mobile />
        </SheetContent>
      </Sheet>

      {/* Main Content */}
      <div className="flex flex-col flex-1 overflow-hidden">
        {/* Top Navigation */}
        <header className="flex items-center justify-between px-6 py-4 bg-background border-b">
          <div className="flex items-center">
            <Sheet open={sidebarOpen} onOpenChange={setSidebarOpen}>
              <SheetTrigger asChild>
                <Button variant="ghost" size="sm" className="md:hidden">
                  <Menu className="h-5 w-5" />
                </Button>
              </SheetTrigger>
            </Sheet>
            <h2 className="ml-4 text-lg font-semibold md:ml-0">
              {filteredNavItems.find(item => item.key === currentPage)?.name || 'Dashboard'}
            </h2>
          </div>

          <div className="flex items-center space-x-4">
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="ghost" className="relative h-8 w-8 rounded-full">
                  <Avatar className="h-8 w-8">
                    <AvatarImage src={user?.avatar} />
                    <AvatarFallback>{getUserInitials()}</AvatarFallback>
                  </Avatar>
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent className="w-56" align="end" forceMount>
                <DropdownMenuLabel className="font-normal">
                  <div className="flex flex-col space-y-1">
                    <p className="text-sm font-medium leading-none">
                      {user?.first_name} {user?.last_name}
                    </p>
                    <p className="text-xs leading-none text-muted-foreground">
                      {user?.email}
                    </p>
                  </div>
                </DropdownMenuLabel>
                <DropdownMenuSeparator />
                <DropdownMenuItem onClick={() => handleNavigation('profile')}>
                  <Settings className="mr-2 h-4 w-4" />
                  <span>Profile Settings</span>
                </DropdownMenuItem>
                <DropdownMenuSeparator />
                <DropdownMenuItem onClick={handleLogout}>
                  <LogOut className="mr-2 h-4 w-4" />
                  <span>Log out</span>
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </div>
        </header>

        {/* Page Content */}
        <main className="flex-1 overflow-y-auto p-6">
          {getCurrentComponent()}
        </main>
      </div>
    </div>
  );
};

export default MainLayout;

