import React, { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Textarea } from '@/components/ui/textarea';
import { Calendar } from '@/components/ui/calendar';
import { Popover, PopoverContent, PopoverTrigger } from '@/components/ui/popover';
import {
  Calendar as CalendarIcon,
  Plus,
  Search,
  Filter,
  Check,
  X,
  Clock,
  User,
  FileText,
  AlertCircle,
  CheckCircle,
  XCircle,
  MoreHorizontal,
  Download,
  Eye,
  Edit,
  Trash2
} from 'lucide-react';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { format, addDays, differenceInDays } from 'date-fns';

const LeaveManagement = () => {
  const { user, isAdmin, isHR } = useAuth();
  const [leaveRequests, setLeaveRequests] = useState([]);
  const [leaveTypes, setLeaveTypes] = useState([]);
  const [employees, setEmployees] = useState([]);
  const [loading, setLoading] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterStatus, setFilterStatus] = useState('all');
  const [filterType, setFilterType] = useState('all');
  const [filterEmployee, setFilterEmployee] = useState('all');
  const [isApplyDialogOpen, setIsApplyDialogOpen] = useState(false);
  const [isViewDialogOpen, setIsViewDialogOpen] = useState(false);
  const [selectedLeave, setSelectedLeave] = useState(null);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [formData, setFormData] = useState({
    leave_type: '',
    start_date: null,
    end_date: null,
    reason: '',
    emergency_contact: '',
    attachment: null
  });

  // Mock data
  const mockLeaveTypes = [
    { id: 1, name: 'Annual Leave', days_allowed: 25, color: 'bg-blue-100 text-blue-800' },
    { id: 2, name: 'Sick Leave', days_allowed: 10, color: 'bg-red-100 text-red-800' },
    { id: 3, name: 'Personal Leave', days_allowed: 5, color: 'bg-green-100 text-green-800' },
    { id: 4, name: 'Maternity Leave', days_allowed: 90, color: 'bg-purple-100 text-purple-800' },
    { id: 5, name: 'Emergency Leave', days_allowed: 3, color: 'bg-orange-100 text-orange-800' }
  ];

  const mockEmployees = [
    { id: 1, first_name: 'John', last_name: 'Doe', avatar: null },
    { id: 2, first_name: 'Jane', last_name: 'Smith', avatar: null },
    { id: 3, first_name: 'Mike', last_name: 'Johnson', avatar: null }
  ];

  const mockLeaveRequests = [
    {
      id: 1,
      employee: { id: 1, first_name: 'John', last_name: 'Doe', avatar: null },
      leave_type: { id: 1, name: 'Annual Leave', color: 'bg-blue-100 text-blue-800' },
      start_date: '2024-02-15',
      end_date: '2024-02-20',
      days_requested: 6,
      reason: 'Family vacation to Europe',
      status: 'pending',
      applied_date: '2024-01-20',
      approved_by: null,
      approved_date: null,
      emergency_contact: '+1-555-0199',
      attachment: null,
      comments: ''
    },
    {
      id: 2,
      employee: { id: 2, first_name: 'Jane', last_name: 'Smith', avatar: null },
      leave_type: { id: 2, name: 'Sick Leave', color: 'bg-red-100 text-red-800' },
      start_date: '2024-01-25',
      end_date: '2024-01-26',
      days_requested: 2,
      reason: 'Flu symptoms and fever',
      status: 'approved',
      applied_date: '2024-01-24',
      approved_by: { first_name: 'Admin', last_name: 'User' },
      approved_date: '2024-01-24',
      emergency_contact: '+1-555-0188',
      attachment: null,
      comments: 'Get well soon!'
    },
    {
      id: 3,
      employee: { id: 3, first_name: 'Mike', last_name: 'Johnson', avatar: null },
      leave_type: { id: 3, name: 'Personal Leave', color: 'bg-green-100 text-green-800' },
      start_date: '2024-02-01',
      end_date: '2024-02-01',
      days_requested: 1,
      reason: 'Personal appointment',
      status: 'rejected',
      applied_date: '2024-01-28',
      approved_by: { first_name: 'Admin', last_name: 'User' },
      approved_date: '2024-01-29',
      emergency_contact: '+1-555-0177',
      attachment: null,
      comments: 'Please reschedule for a less busy period.'
    }
  ];

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      // Mock implementation
      setLeaveRequests(mockLeaveRequests);
      setLeaveTypes(mockLeaveTypes);
      setEmployees(mockEmployees);
    } catch (error) {
      setError('Failed to load leave data');
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleDateChange = (name, date) => {
    setFormData(prev => ({
      ...prev,
      [name]: date
    }));
  };

  const handleSelectChange = (name, value) => {
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const resetForm = () => {
    setFormData({
      leave_type: '',
      start_date: null,
      end_date: null,
      reason: '',
      emergency_contact: '',
      attachment: null
    });
    setError('');
    setSuccess('');
  };

  const handleApplyLeave = async (e) => {
    e.preventDefault();
    try {
      if (!formData.start_date || !formData.end_date) {
        setError('Please select start and end dates');
        return;
      }

      const daysRequested = differenceInDays(formData.end_date, formData.start_date) + 1;
      
      const newLeaveRequest = {
        id: Date.now(),
        employee: {
          id: user?.id,
          first_name: user?.first_name,
          last_name: user?.last_name,
          avatar: user?.avatar
        },
        leave_type: leaveTypes.find(type => type.id === parseInt(formData.leave_type)),
        start_date: format(formData.start_date, 'yyyy-MM-dd'),
        end_date: format(formData.end_date, 'yyyy-MM-dd'),
        days_requested: daysRequested,
        reason: formData.reason,
        status: 'pending',
        applied_date: format(new Date(), 'yyyy-MM-dd'),
        approved_by: null,
        approved_date: null,
        emergency_contact: formData.emergency_contact,
        attachment: formData.attachment,
        comments: ''
      };

      setLeaveRequests(prev => [newLeaveRequest, ...prev]);
      setSuccess('Leave request submitted successfully!');
      setIsApplyDialogOpen(false);
      resetForm();
    } catch (error) {
      setError('Failed to submit leave request');
    }
  };

  const handleApproveLeave = async (leaveId) => {
    try {
      setLeaveRequests(prev => prev.map(leave => 
        leave.id === leaveId 
          ? {
              ...leave,
              status: 'approved',
              approved_by: { first_name: user?.first_name, last_name: user?.last_name },
              approved_date: format(new Date(), 'yyyy-MM-dd')
            }
          : leave
      ));
      setSuccess('Leave request approved successfully!');
    } catch (error) {
      setError('Failed to approve leave request');
    }
  };

  const handleRejectLeave = async (leaveId) => {
    try {
      setLeaveRequests(prev => prev.map(leave => 
        leave.id === leaveId 
          ? {
              ...leave,
              status: 'rejected',
              approved_by: { first_name: user?.first_name, last_name: user?.last_name },
              approved_date: format(new Date(), 'yyyy-MM-dd')
            }
          : leave
      ));
      setSuccess('Leave request rejected successfully!');
    } catch (error) {
      setError('Failed to reject leave request');
    }
  };

  const getStatusBadge = (status) => {
    switch (status) {
      case 'pending':
        return <Badge className="bg-yellow-100 text-yellow-800">Pending</Badge>;
      case 'approved':
        return <Badge className="bg-green-100 text-green-800">Approved</Badge>;
      case 'rejected':
        return <Badge variant="destructive">Rejected</Badge>;
      default:
        return <Badge variant="secondary">Unknown</Badge>;
    }
  };

  const getInitials = (firstName, lastName) => {
    return `${firstName?.[0] || ''}${lastName?.[0] || ''}`.toUpperCase();
  };

  const filteredRequests = leaveRequests.filter(request => {
    const matchesSearch = 
      request.employee.first_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      request.employee.last_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      request.reason.toLowerCase().includes(searchTerm.toLowerCase());
    
    const matchesStatus = filterStatus === 'all' || request.status === filterStatus;
    const matchesType = filterType === 'all' || request.leave_type.id.toString() === filterType;
    const matchesEmployee = filterEmployee === 'all' || request.employee.id.toString() === filterEmployee;
    
    // If not admin/HR, only show own requests
    const hasAccess = (isAdmin || isHR) || request.employee.id === user?.id;
    
    return matchesSearch && matchesStatus && matchesType && matchesEmployee && hasAccess;
  });

  const userLeaveBalance = {
    annual: { used: 8, total: 25 },
    sick: { used: 2, total: 10 },
    personal: { used: 1, total: 5 }
  };

  const leaveStats = {
    totalRequests: leaveRequests.length,
    pending: leaveRequests.filter(r => r.status === 'pending').length,
    approved: leaveRequests.filter(r => r.status === 'approved').length,
    rejected: leaveRequests.filter(r => r.status === 'rejected').length
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Leave Management</h1>
          <p className="text-muted-foreground">
            Manage leave requests and track leave balances
          </p>
        </div>
        <Dialog open={isApplyDialogOpen} onOpenChange={setIsApplyDialogOpen}>
          <DialogTrigger asChild>
            <Button onClick={resetForm}>
              <Plus className="mr-2 h-4 w-4" />
              Apply for Leave
            </Button>
          </DialogTrigger>
          <DialogContent className="max-w-2xl">
            <DialogHeader>
              <DialogTitle>Apply for Leave</DialogTitle>
              <DialogDescription>
                Submit a new leave request
              </DialogDescription>
            </DialogHeader>
            <form onSubmit={handleApplyLeave} className="space-y-4">
              {error && (
                <Alert variant="destructive">
                  <AlertDescription>{error}</AlertDescription>
                </Alert>
              )}
              
              <div>
                <Label htmlFor="leave_type">Leave Type</Label>
                <Select value={formData.leave_type} onValueChange={(value) => handleSelectChange('leave_type', value)}>
                  <SelectTrigger>
                    <SelectValue placeholder="Select leave type" />
                  </SelectTrigger>
                  <SelectContent>
                    {leaveTypes.map(type => (
                      <SelectItem key={type.id} value={type.id.toString()}>
                        {type.name} ({type.days_allowed} days allowed)
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label>Start Date</Label>
                  <Popover>
                    <PopoverTrigger asChild>
                      <Button
                        variant="outline"
                        className="w-full justify-start text-left font-normal"
                      >
                        <CalendarIcon className="mr-2 h-4 w-4" />
                        {formData.start_date ? format(formData.start_date, 'PPP') : 'Select date'}
                      </Button>
                    </PopoverTrigger>
                    <PopoverContent className="w-auto p-0">
                      <Calendar
                        mode="single"
                        selected={formData.start_date}
                        onSelect={(date) => handleDateChange('start_date', date)}
                        disabled={(date) => date < new Date()}
                        initialFocus
                      />
                    </PopoverContent>
                  </Popover>
                </div>
                <div>
                  <Label>End Date</Label>
                  <Popover>
                    <PopoverTrigger asChild>
                      <Button
                        variant="outline"
                        className="w-full justify-start text-left font-normal"
                      >
                        <CalendarIcon className="mr-2 h-4 w-4" />
                        {formData.end_date ? format(formData.end_date, 'PPP') : 'Select date'}
                      </Button>
                    </PopoverTrigger>
                    <PopoverContent className="w-auto p-0">
                      <Calendar
                        mode="single"
                        selected={formData.end_date}
                        onSelect={(date) => handleDateChange('end_date', date)}
                        disabled={(date) => date < (formData.start_date || new Date())}
                        initialFocus
                      />
                    </PopoverContent>
                  </Popover>
                </div>
              </div>

              {formData.start_date && formData.end_date && (
                <div className="p-3 bg-muted rounded-lg">
                  <p className="text-sm">
                    <strong>Duration:</strong> {differenceInDays(formData.end_date, formData.start_date) + 1} day(s)
                  </p>
                </div>
              )}

              <div>
                <Label htmlFor="reason">Reason for Leave</Label>
                <Textarea
                  id="reason"
                  name="reason"
                  value={formData.reason}
                  onChange={handleInputChange}
                  placeholder="Please provide a reason for your leave request..."
                  rows={3}
                  required
                />
              </div>

              <div>
                <Label htmlFor="emergency_contact">Emergency Contact</Label>
                <Input
                  id="emergency_contact"
                  name="emergency_contact"
                  value={formData.emergency_contact}
                  onChange={handleInputChange}
                  placeholder="Phone number for emergency contact"
                />
              </div>

              <div className="flex justify-end space-x-2">
                <Button type="button" variant="outline" onClick={() => setIsApplyDialogOpen(false)}>
                  Cancel
                </Button>
                <Button type="submit">Submit Request</Button>
              </div>
            </form>
          </DialogContent>
        </Dialog>
      </div>

      {/* Alerts */}
      {success && (
        <Alert>
          <CheckCircle className="h-4 w-4" />
          <AlertDescription>{success}</AlertDescription>
        </Alert>
      )}
      {error && (
        <Alert variant="destructive">
          <XCircle className="h-4 w-4" />
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      <Tabs defaultValue="requests" className="space-y-6">
        <TabsList>
          <TabsTrigger value="requests">Leave Requests</TabsTrigger>
          <TabsTrigger value="balance">My Leave Balance</TabsTrigger>
          {(isAdmin || isHR) && <TabsTrigger value="analytics">Analytics</TabsTrigger>}
        </TabsList>

        {/* Leave Requests Tab */}
        <TabsContent value="requests" className="space-y-6">
          {/* Stats Cards */}
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Total Requests</CardTitle>
                <FileText className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{leaveStats.totalRequests}</div>
                <p className="text-xs text-muted-foreground">
                  All time requests
                </p>
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Pending</CardTitle>
                <Clock className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-yellow-600">{leaveStats.pending}</div>
                <p className="text-xs text-muted-foreground">
                  Awaiting approval
                </p>
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Approved</CardTitle>
                <CheckCircle className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-green-600">{leaveStats.approved}</div>
                <p className="text-xs text-muted-foreground">
                  Successfully approved
                </p>
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Rejected</CardTitle>
                <XCircle className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-red-600">{leaveStats.rejected}</div>
                <p className="text-xs text-muted-foreground">
                  Declined requests
                </p>
              </CardContent>
            </Card>
          </div>

          <Card>
            <CardHeader>
              <CardTitle>Leave Requests</CardTitle>
              <CardDescription>
                {(isAdmin || isHR) ? 'Manage all employee leave requests' : 'Your leave request history'}
              </CardDescription>
            </CardHeader>
            <CardContent>
              {/* Filters */}
              <div className="flex flex-col md:flex-row gap-4 mb-6">
                <div className="flex-1">
                  <div className="relative">
                    <Search className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
                    <Input
                      placeholder="Search requests..."
                      value={searchTerm}
                      onChange={(e) => setSearchTerm(e.target.value)}
                      className="pl-8"
                    />
                  </div>
                </div>
                <Select value={filterStatus} onValueChange={setFilterStatus}>
                  <SelectTrigger className="w-[140px]">
                    <SelectValue placeholder="Status" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">All Status</SelectItem>
                    <SelectItem value="pending">Pending</SelectItem>
                    <SelectItem value="approved">Approved</SelectItem>
                    <SelectItem value="rejected">Rejected</SelectItem>
                  </SelectContent>
                </Select>
                <Select value={filterType} onValueChange={setFilterType}>
                  <SelectTrigger className="w-[160px]">
                    <SelectValue placeholder="Leave Type" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">All Types</SelectItem>
                    {leaveTypes.map(type => (
                      <SelectItem key={type.id} value={type.id.toString()}>
                        {type.name}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                {(isAdmin || isHR) && (
                  <Select value={filterEmployee} onValueChange={setFilterEmployee}>
                    <SelectTrigger className="w-[160px]">
                      <SelectValue placeholder="Employee" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="all">All Employees</SelectItem>
                      {employees.map(emp => (
                        <SelectItem key={emp.id} value={emp.id.toString()}>
                          {emp.first_name} {emp.last_name}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                )}
              </div>

              {/* Requests Table */}
              <div className="rounded-md border">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Employee</TableHead>
                      <TableHead>Leave Type</TableHead>
                      <TableHead>Duration</TableHead>
                      <TableHead>Applied Date</TableHead>
                      <TableHead>Status</TableHead>
                      <TableHead>Actions</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {filteredRequests.map((request) => (
                      <TableRow key={request.id}>
                        <TableCell>
                          <div className="flex items-center space-x-3">
                            <Avatar className="h-8 w-8">
                              <AvatarImage src={request.employee.avatar} />
                              <AvatarFallback>
                                {getInitials(request.employee.first_name, request.employee.last_name)}
                              </AvatarFallback>
                            </Avatar>
                            <div>
                              <div className="font-medium">
                                {request.employee.first_name} {request.employee.last_name}
                              </div>
                            </div>
                          </div>
                        </TableCell>
                        <TableCell>
                          <Badge className={request.leave_type.color}>
                            {request.leave_type.name}
                          </Badge>
                        </TableCell>
                        <TableCell>
                          <div>
                            <div className="font-medium">{request.days_requested} day(s)</div>
                            <div className="text-sm text-muted-foreground">
                              {format(new Date(request.start_date), 'MMM d')} - {format(new Date(request.end_date), 'MMM d, yyyy')}
                            </div>
                          </div>
                        </TableCell>
                        <TableCell>{format(new Date(request.applied_date), 'MMM d, yyyy')}</TableCell>
                        <TableCell>{getStatusBadge(request.status)}</TableCell>
                        <TableCell>
                          <div className="flex items-center space-x-2">
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => {
                                setSelectedLeave(request);
                                setIsViewDialogOpen(true);
                              }}
                            >
                              <Eye className="h-4 w-4" />
                            </Button>
                            {(isAdmin || isHR) && request.status === 'pending' && (
                              <>
                                <Button
                                  variant="ghost"
                                  size="sm"
                                  onClick={() => handleApproveLeave(request.id)}
                                  className="text-green-600 hover:text-green-700"
                                >
                                  <Check className="h-4 w-4" />
                                </Button>
                                <Button
                                  variant="ghost"
                                  size="sm"
                                  onClick={() => handleRejectLeave(request.id)}
                                  className="text-red-600 hover:text-red-700"
                                >
                                  <X className="h-4 w-4" />
                                </Button>
                              </>
                            )}
                          </div>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </div>

              {filteredRequests.length === 0 && (
                <div className="text-center py-8">
                  <FileText className="mx-auto h-12 w-12 text-muted-foreground" />
                  <h3 className="mt-2 text-sm font-semibold">No leave requests found</h3>
                  <p className="mt-1 text-sm text-muted-foreground">
                    No requests match your current filters.
                  </p>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Leave Balance Tab */}
        <TabsContent value="balance" className="space-y-6">
          <div className="grid gap-4 md:grid-cols-3">
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Annual Leave</CardTitle>
                <CardDescription>Vacation and personal time off</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span>Used</span>
                    <span>{userLeaveBalance.annual.used} / {userLeaveBalance.annual.total} days</span>
                  </div>
                  <div className="w-full bg-muted rounded-full h-2">
                    <div 
                      className="bg-blue-500 h-2 rounded-full"
                      style={{ width: `${(userLeaveBalance.annual.used / userLeaveBalance.annual.total) * 100}%` }}
                    ></div>
                  </div>
                  <p className="text-xs text-muted-foreground">
                    {userLeaveBalance.annual.total - userLeaveBalance.annual.used} days remaining
                  </p>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Sick Leave</CardTitle>
                <CardDescription>Medical and health-related leave</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span>Used</span>
                    <span>{userLeaveBalance.sick.used} / {userLeaveBalance.sick.total} days</span>
                  </div>
                  <div className="w-full bg-muted rounded-full h-2">
                    <div 
                      className="bg-red-500 h-2 rounded-full"
                      style={{ width: `${(userLeaveBalance.sick.used / userLeaveBalance.sick.total) * 100}%` }}
                    ></div>
                  </div>
                  <p className="text-xs text-muted-foreground">
                    {userLeaveBalance.sick.total - userLeaveBalance.sick.used} days remaining
                  </p>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Personal Leave</CardTitle>
                <CardDescription>Personal appointments and errands</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span>Used</span>
                    <span>{userLeaveBalance.personal.used} / {userLeaveBalance.personal.total} days</span>
                  </div>
                  <div className="w-full bg-muted rounded-full h-2">
                    <div 
                      className="bg-green-500 h-2 rounded-full"
                      style={{ width: `${(userLeaveBalance.personal.used / userLeaveBalance.personal.total) * 100}%` }}
                    ></div>
                  </div>
                  <p className="text-xs text-muted-foreground">
                    {userLeaveBalance.personal.total - userLeaveBalance.personal.used} days remaining
                  </p>
                </div>
              </CardContent>
            </Card>
          </div>

          <Card>
            <CardHeader>
              <CardTitle>Leave History</CardTitle>
              <CardDescription>Your recent leave requests and usage</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {leaveRequests
                  .filter(request => request.employee.id === user?.id)
                  .slice(0, 5)
                  .map((request) => (
                    <div key={request.id} className="flex items-center justify-between p-3 border rounded-lg">
                      <div className="flex items-center space-x-3">
                        <Badge className={request.leave_type.color}>
                          {request.leave_type.name}
                        </Badge>
                        <div>
                          <div className="font-medium">
                            {format(new Date(request.start_date), 'MMM d')} - {format(new Date(request.end_date), 'MMM d, yyyy')}
                          </div>
                          <div className="text-sm text-muted-foreground">
                            {request.days_requested} day(s) • {request.reason}
                          </div>
                        </div>
                      </div>
                      {getStatusBadge(request.status)}
                    </div>
                  ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Analytics Tab */}
        {(isAdmin || isHR) && (
          <TabsContent value="analytics" className="space-y-6">
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Avg. Leave Days</CardTitle>
                  <CalendarIcon className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">12.5</div>
                  <p className="text-xs text-muted-foreground">
                    Per employee this year
                  </p>
                </CardContent>
              </Card>
              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Most Used Type</CardTitle>
                  <FileText className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">Annual</div>
                  <p className="text-xs text-muted-foreground">
                    65% of all requests
                  </p>
                </CardContent>
              </Card>
              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Peak Month</CardTitle>
                  <CalendarIcon className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">December</div>
                  <p className="text-xs text-muted-foreground">
                    Holiday season
                  </p>
                </CardContent>
              </Card>
              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Approval Rate</CardTitle>
                  <CheckCircle className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">94%</div>
                  <p className="text-xs text-muted-foreground">
                    Requests approved
                  </p>
                </CardContent>
              </Card>
            </div>

            <div className="grid gap-4 md:grid-cols-2">
              <Card>
                <CardHeader>
                  <CardTitle>Leave Types Distribution</CardTitle>
                  <CardDescription>Breakdown of leave requests by type</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {leaveTypes.map((type, index) => {
                      const percentage = Math.random() * 40 + 10; // Mock data
                      return (
                        <div key={type.id} className="space-y-2">
                          <div className="flex justify-between text-sm">
                            <span className="font-medium">{type.name}</span>
                            <span>{percentage.toFixed(1)}%</span>
                          </div>
                          <div className="w-full bg-muted rounded-full h-2">
                            <div 
                              className="bg-primary h-2 rounded-full"
                              style={{ width: `${percentage}%` }}
                            ></div>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Monthly Trends</CardTitle>
                  <CardDescription>Leave requests over the past 12 months</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div className="grid grid-cols-6 gap-2 text-center">
                      {['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'].map((month, index) => (
                        <div key={month} className="space-y-2">
                          <div className="text-xs font-medium">{month}</div>
                          <div className="h-16 bg-muted rounded flex items-end justify-center">
                            <div 
                              className="bg-primary rounded-t w-full"
                              style={{ height: `${Math.random() * 80 + 20}%` }}
                            ></div>
                          </div>
                          <div className="text-xs text-muted-foreground">
                            {Math.floor(Math.random() * 20 + 5)}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>
        )}
      </Tabs>

      {/* View Leave Dialog */}
      <Dialog open={isViewDialogOpen} onOpenChange={setIsViewDialogOpen}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>Leave Request Details</DialogTitle>
            <DialogDescription>
              Complete information for this leave request
            </DialogDescription>
          </DialogHeader>
          {selectedLeave && (
            <div className="space-y-6">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-4">
                  <Avatar className="h-12 w-12">
                    <AvatarImage src={selectedLeave.employee.avatar} />
                    <AvatarFallback>
                      {getInitials(selectedLeave.employee.first_name, selectedLeave.employee.last_name)}
                    </AvatarFallback>
                  </Avatar>
                  <div>
                    <h3 className="text-lg font-semibold">
                      {selectedLeave.employee.first_name} {selectedLeave.employee.last_name}
                    </h3>
                    <Badge className={selectedLeave.leave_type.color}>
                      {selectedLeave.leave_type.name}
                    </Badge>
                  </div>
                </div>
                {getStatusBadge(selectedLeave.status)}
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label className="text-sm font-medium">Start Date</Label>
                  <p className="mt-1">{format(new Date(selectedLeave.start_date), 'PPPP')}</p>
                </div>
                <div>
                  <Label className="text-sm font-medium">End Date</Label>
                  <p className="mt-1">{format(new Date(selectedLeave.end_date), 'PPPP')}</p>
                </div>
                <div>
                  <Label className="text-sm font-medium">Duration</Label>
                  <p className="mt-1">{selectedLeave.days_requested} day(s)</p>
                </div>
                <div>
                  <Label className="text-sm font-medium">Applied Date</Label>
                  <p className="mt-1">{format(new Date(selectedLeave.applied_date), 'PPP')}</p>
                </div>
              </div>

              <div>
                <Label className="text-sm font-medium">Reason</Label>
                <p className="mt-1 p-3 bg-muted rounded-lg">{selectedLeave.reason}</p>
              </div>

              {selectedLeave.emergency_contact && (
                <div>
                  <Label className="text-sm font-medium">Emergency Contact</Label>
                  <p className="mt-1">{selectedLeave.emergency_contact}</p>
                </div>
              )}

              {selectedLeave.approved_by && (
                <div>
                  <Label className="text-sm font-medium">
                    {selectedLeave.status === 'approved' ? 'Approved By' : 'Reviewed By'}
                  </Label>
                  <p className="mt-1">
                    {selectedLeave.approved_by.first_name} {selectedLeave.approved_by.last_name} on{' '}
                    {format(new Date(selectedLeave.approved_date), 'PPP')}
                  </p>
                </div>
              )}

              {selectedLeave.comments && (
                <div>
                  <Label className="text-sm font-medium">Comments</Label>
                  <p className="mt-1 p-3 bg-muted rounded-lg">{selectedLeave.comments}</p>
                </div>
              )}

              {(isAdmin || isHR) && selectedLeave.status === 'pending' && (
                <div className="flex justify-end space-x-2">
                  <Button 
                    variant="outline" 
                    onClick={() => handleRejectLeave(selectedLeave.id)}
                    className="text-red-600 hover:text-red-700"
                  >
                    <X className="mr-2 h-4 w-4" />
                    Reject
                  </Button>
                  <Button 
                    onClick={() => handleApproveLeave(selectedLeave.id)}
                    className="bg-green-600 hover:bg-green-700"
                  >
                    <Check className="mr-2 h-4 w-4" />
                    Approve
                  </Button>
                </div>
              )}
            </div>
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default LeaveManagement;

