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
import { Calendar } from '@/components/ui/calendar';
import { Popover, PopoverContent, PopoverTrigger } from '@/components/ui/popover';
import {
  Clock,
  Calendar as CalendarIcon,
  Users,
  CheckCircle,
  XCircle,
  AlertCircle,
  Timer,
  Play,
  Pause,
  Square,
  MapPin,
  Filter,
  Download,
  Upload,
  MoreHorizontal,
  TrendingUp,
  TrendingDown
} from 'lucide-react';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { format } from 'date-fns';

const AttendanceTracking = () => {
  const { user, isAdmin, isHR } = useAuth();
  const [currentTime, setCurrentTime] = useState(new Date());
  const [isCheckedIn, setIsCheckedIn] = useState(false);
  const [todayAttendance, setTodayAttendance] = useState(null);
  const [attendanceRecords, setAttendanceRecords] = useState([]);
  const [selectedDate, setSelectedDate] = useState(new Date());
  const [filterEmployee, setFilterEmployee] = useState('all');
  const [filterStatus, setFilterStatus] = useState('all');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  // Mock data for demonstration
  const mockAttendanceRecords = [
    {
      id: 1,
      employee: {
        id: 1,
        first_name: 'John',
        last_name: 'Doe',
        avatar: null
      },
      date: '2024-01-15',
      time_in: '09:00:00',
      time_out: '17:30:00',
      break_time: 60,
      total_hours: 7.5,
      overtime_hours: 0,
      status: 'present',
      location: 'Office',
      notes: ''
    },
    {
      id: 2,
      employee: {
        id: 2,
        first_name: 'Jane',
        last_name: 'Smith',
        avatar: null
      },
      date: '2024-01-15',
      time_in: '08:45:00',
      time_out: '18:00:00',
      break_time: 45,
      total_hours: 8.5,
      overtime_hours: 0.5,
      status: 'present',
      location: 'Remote',
      notes: 'Working from home'
    },
    {
      id: 3,
      employee: {
        id: 3,
        first_name: 'Mike',
        last_name: 'Johnson',
        avatar: null
      },
      date: '2024-01-15',
      time_in: null,
      time_out: null,
      break_time: 0,
      total_hours: 0,
      overtime_hours: 0,
      status: 'absent',
      location: null,
      notes: 'Sick leave'
    }
  ];

  const mockEmployees = [
    { id: 1, first_name: 'John', last_name: 'Doe' },
    { id: 2, first_name: 'Jane', last_name: 'Smith' },
    { id: 3, first_name: 'Mike', last_name: 'Johnson' }
  ];

  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentTime(new Date());
    }, 1000);

    fetchAttendanceData();
    checkTodayAttendance();

    return () => clearInterval(timer);
  }, []);

  const fetchAttendanceData = async () => {
    try {
      setLoading(true);
      // Mock implementation
      setAttendanceRecords(mockAttendanceRecords);
    } catch (error) {
      setError('Failed to load attendance data');
    } finally {
      setLoading(false);
    }
  };

  const checkTodayAttendance = async () => {
    try {
      // Mock implementation - check if user has checked in today
      const today = format(new Date(), 'yyyy-MM-dd');
      const userAttendance = mockAttendanceRecords.find(
        record => record.employee.id === user?.id && record.date === today
      );
      
      if (userAttendance) {
        setTodayAttendance(userAttendance);
        setIsCheckedIn(userAttendance.time_in && !userAttendance.time_out);
      }
    } catch (error) {
      console.error('Error checking today attendance:', error);
    }
  };

  const handleCheckIn = async () => {
    try {
      setLoading(true);
      const now = new Date();
      const timeString = format(now, 'HH:mm:ss');
      
      // Mock implementation
      const newAttendance = {
        id: Date.now(),
        employee: {
          id: user?.id,
          first_name: user?.first_name,
          last_name: user?.last_name,
          avatar: user?.avatar
        },
        date: format(now, 'yyyy-MM-dd'),
        time_in: timeString,
        time_out: null,
        break_time: 0,
        total_hours: 0,
        overtime_hours: 0,
        status: 'present',
        location: 'Office',
        notes: ''
      };

      setTodayAttendance(newAttendance);
      setIsCheckedIn(true);
      setSuccess('Successfully checked in!');
    } catch (error) {
      setError('Failed to check in');
    } finally {
      setLoading(false);
    }
  };

  const handleCheckOut = async () => {
    try {
      setLoading(true);
      const now = new Date();
      const timeString = format(now, 'HH:mm:ss');
      
      // Calculate total hours
      const timeIn = new Date(`${todayAttendance.date}T${todayAttendance.time_in}`);
      const timeOut = new Date(`${todayAttendance.date}T${timeString}`);
      const totalMinutes = (timeOut - timeIn) / (1000 * 60);
      const totalHours = (totalMinutes - todayAttendance.break_time) / 60;
      
      const updatedAttendance = {
        ...todayAttendance,
        time_out: timeString,
        total_hours: Math.round(totalHours * 100) / 100,
        overtime_hours: Math.max(0, totalHours - 8)
      };

      setTodayAttendance(updatedAttendance);
      setIsCheckedIn(false);
      setSuccess('Successfully checked out!');
    } catch (error) {
      setError('Failed to check out');
    } finally {
      setLoading(false);
    }
  };

  const getStatusBadge = (status) => {
    switch (status) {
      case 'present':
        return <Badge className="bg-green-100 text-green-800">Present</Badge>;
      case 'absent':
        return <Badge variant="destructive">Absent</Badge>;
      case 'late':
        return <Badge className="bg-yellow-100 text-yellow-800">Late</Badge>;
      case 'half_day':
        return <Badge className="bg-blue-100 text-blue-800">Half Day</Badge>;
      default:
        return <Badge variant="secondary">Unknown</Badge>;
    }
  };

  const getInitials = (firstName, lastName) => {
    return `${firstName?.[0] || ''}${lastName?.[0] || ''}`.toUpperCase();
  };

  const formatTime = (timeString) => {
    if (!timeString) return 'N/A';
    return format(new Date(`2000-01-01T${timeString}`), 'h:mm a');
  };

  const formatDuration = (hours) => {
    if (!hours) return '0h 0m';
    const h = Math.floor(hours);
    const m = Math.round((hours - h) * 60);
    return `${h}h ${m}m`;
  };

  const filteredRecords = attendanceRecords.filter(record => {
    const matchesEmployee = filterEmployee === 'all' || 
      record.employee.id.toString() === filterEmployee;
    
    const matchesStatus = filterStatus === 'all' || record.status === filterStatus;
    
    const recordDate = new Date(record.date);
    const selectedDateStr = format(selectedDate, 'yyyy-MM-dd');
    const matchesDate = record.date === selectedDateStr;
    
    return matchesEmployee && matchesStatus && matchesDate;
  });

  const todayStats = {
    totalEmployees: mockEmployees.length,
    present: attendanceRecords.filter(r => r.status === 'present' && r.date === format(new Date(), 'yyyy-MM-dd')).length,
    absent: attendanceRecords.filter(r => r.status === 'absent' && r.date === format(new Date(), 'yyyy-MM-dd')).length,
    late: attendanceRecords.filter(r => r.status === 'late' && r.date === format(new Date(), 'yyyy-MM-dd')).length,
    avgHours: 7.8
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Attendance Tracking</h1>
          <p className="text-muted-foreground">
            Track employee attendance and working hours
          </p>
        </div>
        <div className="text-right">
          <div className="text-2xl font-mono font-bold">
            {format(currentTime, 'HH:mm:ss')}
          </div>
          <div className="text-sm text-muted-foreground">
            {format(currentTime, 'EEEE, MMMM d, yyyy')}
          </div>
        </div>
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

      <Tabs defaultValue="clock" className="space-y-6">
        <TabsList>
          <TabsTrigger value="clock">Time Clock</TabsTrigger>
          <TabsTrigger value="records">Attendance Records</TabsTrigger>
          <TabsTrigger value="analytics">Analytics</TabsTrigger>
        </TabsList>

        {/* Time Clock Tab */}
        <TabsContent value="clock" className="space-y-6">
          {/* Personal Time Clock */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <Clock className="mr-2 h-5 w-5" />
                My Time Clock
              </CardTitle>
              <CardDescription>
                Clock in and out for your work day
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="flex items-center justify-between">
                <div className="space-y-2">
                  {todayAttendance ? (
                    <div className="space-y-1">
                      <div className="flex items-center space-x-2">
                        <span className="text-sm font-medium">Time In:</span>
                        <span className="text-sm">{formatTime(todayAttendance.time_in)}</span>
                      </div>
                      {todayAttendance.time_out && (
                        <div className="flex items-center space-x-2">
                          <span className="text-sm font-medium">Time Out:</span>
                          <span className="text-sm">{formatTime(todayAttendance.time_out)}</span>
                        </div>
                      )}
                      <div className="flex items-center space-x-2">
                        <span className="text-sm font-medium">Total Hours:</span>
                        <span className="text-sm">{formatDuration(todayAttendance.total_hours)}</span>
                      </div>
                      {todayAttendance.overtime_hours > 0 && (
                        <div className="flex items-center space-x-2">
                          <span className="text-sm font-medium">Overtime:</span>
                          <span className="text-sm text-orange-600">
                            {formatDuration(todayAttendance.overtime_hours)}
                          </span>
                        </div>
                      )}
                    </div>
                  ) : (
                    <p className="text-sm text-muted-foreground">
                      You haven't clocked in today yet.
                    </p>
                  )}
                </div>
                <div className="flex space-x-2">
                  {!isCheckedIn ? (
                    <Button 
                      onClick={handleCheckIn} 
                      disabled={loading}
                      className="bg-green-600 hover:bg-green-700"
                    >
                      <Play className="mr-2 h-4 w-4" />
                      Clock In
                    </Button>
                  ) : (
                    <Button 
                      onClick={handleCheckOut} 
                      disabled={loading}
                      variant="destructive"
                    >
                      <Square className="mr-2 h-4 w-4" />
                      Clock Out
                    </Button>
                  )}
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Today's Stats */}
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Total Employees</CardTitle>
                <Users className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{todayStats.totalEmployees}</div>
                <p className="text-xs text-muted-foreground">
                  Registered employees
                </p>
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Present Today</CardTitle>
                <CheckCircle className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-green-600">{todayStats.present}</div>
                <p className="text-xs text-muted-foreground">
                  {Math.round((todayStats.present / todayStats.totalEmployees) * 100)}% attendance rate
                </p>
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Absent Today</CardTitle>
                <XCircle className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-red-600">{todayStats.absent}</div>
                <p className="text-xs text-muted-foreground">
                  Employees not present
                </p>
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Avg. Hours</CardTitle>
                <Timer className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{todayStats.avgHours}h</div>
                <p className="text-xs text-muted-foreground">
                  Average working hours
                </p>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Attendance Records Tab */}
        <TabsContent value="records" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Attendance Records</CardTitle>
              <CardDescription>
                View and manage employee attendance records
              </CardDescription>
            </CardHeader>
            <CardContent>
              {/* Filters */}
              <div className="flex flex-col md:flex-row gap-4 mb-6">
                <div className="flex-1">
                  <Label>Date</Label>
                  <Popover>
                    <PopoverTrigger asChild>
                      <Button
                        variant="outline"
                        className="w-full justify-start text-left font-normal"
                      >
                        <CalendarIcon className="mr-2 h-4 w-4" />
                        {format(selectedDate, 'PPP')}
                      </Button>
                    </PopoverTrigger>
                    <PopoverContent className="w-auto p-0">
                      <Calendar
                        mode="single"
                        selected={selectedDate}
                        onSelect={setSelectedDate}
                        initialFocus
                      />
                    </PopoverContent>
                  </Popover>
                </div>
                {(isAdmin || isHR) && (
                  <>
                    <div>
                      <Label>Employee</Label>
                      <Select value={filterEmployee} onValueChange={setFilterEmployee}>
                        <SelectTrigger className="w-[180px]">
                          <SelectValue placeholder="All Employees" />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="all">All Employees</SelectItem>
                          {mockEmployees.map(emp => (
                            <SelectItem key={emp.id} value={emp.id.toString()}>
                              {emp.first_name} {emp.last_name}
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>
                    <div>
                      <Label>Status</Label>
                      <Select value={filterStatus} onValueChange={setFilterStatus}>
                        <SelectTrigger className="w-[140px]">
                          <SelectValue placeholder="All Status" />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="all">All Status</SelectItem>
                          <SelectItem value="present">Present</SelectItem>
                          <SelectItem value="absent">Absent</SelectItem>
                          <SelectItem value="late">Late</SelectItem>
                          <SelectItem value="half_day">Half Day</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                  </>
                )}
              </div>

              {/* Records Table */}
              <div className="rounded-md border">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Employee</TableHead>
                      <TableHead>Time In</TableHead>
                      <TableHead>Time Out</TableHead>
                      <TableHead>Total Hours</TableHead>
                      <TableHead>Overtime</TableHead>
                      <TableHead>Status</TableHead>
                      <TableHead>Location</TableHead>
                      {(isAdmin || isHR) && <TableHead>Actions</TableHead>}
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {filteredRecords.map((record) => (
                      <TableRow key={record.id}>
                        <TableCell>
                          <div className="flex items-center space-x-3">
                            <Avatar className="h-8 w-8">
                              <AvatarImage src={record.employee.avatar} />
                              <AvatarFallback>
                                {getInitials(record.employee.first_name, record.employee.last_name)}
                              </AvatarFallback>
                            </Avatar>
                            <div>
                              <div className="font-medium">
                                {record.employee.first_name} {record.employee.last_name}
                              </div>
                            </div>
                          </div>
                        </TableCell>
                        <TableCell>{formatTime(record.time_in)}</TableCell>
                        <TableCell>{formatTime(record.time_out)}</TableCell>
                        <TableCell>{formatDuration(record.total_hours)}</TableCell>
                        <TableCell>
                          {record.overtime_hours > 0 ? (
                            <span className="text-orange-600">
                              {formatDuration(record.overtime_hours)}
                            </span>
                          ) : (
                            '-'
                          )}
                        </TableCell>
                        <TableCell>{getStatusBadge(record.status)}</TableCell>
                        <TableCell>
                          <div className="flex items-center">
                            <MapPin className="mr-1 h-3 w-3 text-muted-foreground" />
                            {record.location || 'N/A'}
                          </div>
                        </TableCell>
                        {(isAdmin || isHR) && (
                          <TableCell>
                            <DropdownMenu>
                              <DropdownMenuTrigger asChild>
                                <Button variant="ghost" className="h-8 w-8 p-0">
                                  <MoreHorizontal className="h-4 w-4" />
                                </Button>
                              </DropdownMenuTrigger>
                              <DropdownMenuContent align="end">
                                <DropdownMenuLabel>Actions</DropdownMenuLabel>
                                <DropdownMenuItem>
                                  Edit Record
                                </DropdownMenuItem>
                                <DropdownMenuItem>
                                  Add Note
                                </DropdownMenuItem>
                                <DropdownMenuSeparator />
                                <DropdownMenuItem className="text-red-600">
                                  Delete Record
                                </DropdownMenuItem>
                              </DropdownMenuContent>
                            </DropdownMenu>
                          </TableCell>
                        )}
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </div>

              {filteredRecords.length === 0 && (
                <div className="text-center py-8">
                  <Clock className="mx-auto h-12 w-12 text-muted-foreground" />
                  <h3 className="mt-2 text-sm font-semibold">No records found</h3>
                  <p className="mt-1 text-sm text-muted-foreground">
                    No attendance records found for the selected criteria.
                  </p>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Analytics Tab */}
        <TabsContent value="analytics" className="space-y-6">
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Weekly Attendance</CardTitle>
                <TrendingUp className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">92.5%</div>
                <p className="text-xs text-muted-foreground">
                  <span className="text-green-600">+2.1%</span> from last week
                </p>
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Avg. Daily Hours</CardTitle>
                <Timer className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">7.8h</div>
                <p className="text-xs text-muted-foreground">
                  <span className="text-red-600">-0.2h</span> from last week
                </p>
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Total Overtime</CardTitle>
                <AlertCircle className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">23.5h</div>
                <p className="text-xs text-muted-foreground">
                  <span className="text-orange-600">+5.2h</span> from last week
                </p>
              </CardContent>
            </Card>
          </div>

          <Card>
            <CardHeader>
              <CardTitle>Attendance Trends</CardTitle>
              <CardDescription>
                Weekly attendance patterns and insights
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="grid grid-cols-7 gap-2 text-center">
                  {['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'].map((day, index) => (
                    <div key={day} className="space-y-2">
                      <div className="text-sm font-medium">{day}</div>
                      <div className="h-20 bg-muted rounded flex items-end justify-center">
                        <div 
                          className="bg-primary rounded-t w-full"
                          style={{ height: `${Math.random() * 80 + 20}%` }}
                        ></div>
                      </div>
                      <div className="text-xs text-muted-foreground">
                        {Math.floor(Math.random() * 20 + 80)}%
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </CardContent>
          </Card>

          <div className="grid gap-4 md:grid-cols-2">
            <Card>
              <CardHeader>
                <CardTitle>Top Performers</CardTitle>
                <CardDescription>
                  Employees with best attendance this month
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {[
                    { name: 'Jane Smith', rate: '98.5%', hours: '168h' },
                    { name: 'John Doe', rate: '96.2%', hours: '162h' },
                    { name: 'Mike Johnson', rate: '94.8%', hours: '159h' }
                  ].map((performer, index) => (
                    <div key={index} className="flex items-center justify-between">
                      <div className="flex items-center space-x-3">
                        <div className="w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center text-sm font-medium">
                          {index + 1}
                        </div>
                        <div>
                          <div className="font-medium">{performer.name}</div>
                          <div className="text-sm text-muted-foreground">{performer.hours}</div>
                        </div>
                      </div>
                      <Badge variant="outline">{performer.rate}</Badge>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Department Attendance</CardTitle>
                <CardDescription>
                  Attendance rates by department
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {[
                    { dept: 'Engineering', rate: 95.2, color: 'bg-blue-500' },
                    { dept: 'Marketing', rate: 92.8, color: 'bg-green-500' },
                    { dept: 'HR', rate: 98.1, color: 'bg-purple-500' },
                    { dept: 'Finance', rate: 89.5, color: 'bg-orange-500' }
                  ].map((dept, index) => (
                    <div key={index} className="space-y-2">
                      <div className="flex justify-between text-sm">
                        <span className="font-medium">{dept.dept}</span>
                        <span>{dept.rate}%</span>
                      </div>
                      <div className="w-full bg-muted rounded-full h-2">
                        <div 
                          className={`h-2 rounded-full ${dept.color}`}
                          style={{ width: `${dept.rate}%` }}
                        ></div>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default AttendanceTracking;

