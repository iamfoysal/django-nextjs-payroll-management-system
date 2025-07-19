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
import { Separator } from '@/components/ui/separator';
import {
  DollarSign,
  Calendar as CalendarIcon,
  Users,
  Calculator,
  FileText,
  Download,
  Eye,
  Edit,
  Trash2,
  Plus,
  Search,
  Filter,
  CheckCircle,
  XCircle,
  AlertCircle,
  MoreHorizontal,
  TrendingUp,
  TrendingDown,
  CreditCard,
  Receipt,
  Banknote
} from 'lucide-react';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { format, startOfMonth, endOfMonth, subMonths } from 'date-fns';

const PayrollProcessing = () => {
  const { user, isAdmin, isHR } = useAuth();
  const [payrollRecords, setPayrollRecords] = useState([]);
  const [employees, setEmployees] = useState([]);
  const [selectedPeriod, setSelectedPeriod] = useState(new Date());
  const [loading, setLoading] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterStatus, setFilterStatus] = useState('all');
  const [filterDepartment, setFilterDepartment] = useState('all');
  const [isGenerateDialogOpen, setIsGenerateDialogOpen] = useState(false);
  const [isViewPayslipOpen, setIsViewPayslipOpen] = useState(false);
  const [selectedPayroll, setSelectedPayroll] = useState(null);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [generateData, setGenerateData] = useState({
    pay_period_start: null,
    pay_period_end: null,
    employees: 'all'
  });

  // Mock data
  const mockEmployees = [
    { 
      id: 1, 
      first_name: 'John', 
      last_name: 'Doe', 
      department: { name: 'Engineering' },
      salary_type: 'fixed',
      base_salary: 75000,
      hourly_rate: null
    },
    { 
      id: 2, 
      first_name: 'Jane', 
      last_name: 'Smith', 
      department: { name: 'HR' },
      salary_type: 'fixed',
      base_salary: 85000,
      hourly_rate: null
    },
    { 
      id: 3, 
      first_name: 'Mike', 
      last_name: 'Johnson', 
      department: { name: 'Marketing' },
      salary_type: 'hourly',
      base_salary: null,
      hourly_rate: 35
    }
  ];

  const mockPayrollRecords = [
    {
      id: 1,
      employee: { id: 1, first_name: 'John', last_name: 'Doe', department: { name: 'Engineering' } },
      pay_period_start: '2024-01-01',
      pay_period_end: '2024-01-31',
      basic_salary: 6250.00,
      overtime_pay: 450.00,
      bonuses: 500.00,
      deductions: 1250.00,
      tax_deduction: 1875.00,
      net_salary: 4075.00,
      gross_salary: 7200.00,
      status: 'paid',
      generated_date: '2024-01-28',
      paid_date: '2024-01-31',
      hours_worked: 168,
      overtime_hours: 12,
      leave_days: 2,
      present_days: 20
    },
    {
      id: 2,
      employee: { id: 2, first_name: 'Jane', last_name: 'Smith', department: { name: 'HR' } },
      pay_period_start: '2024-01-01',
      pay_period_end: '2024-01-31',
      basic_salary: 7083.33,
      overtime_pay: 0.00,
      bonuses: 1000.00,
      deductions: 1416.67,
      tax_deduction: 2125.00,
      net_salary: 4541.66,
      gross_salary: 8083.33,
      status: 'generated',
      generated_date: '2024-01-28',
      paid_date: null,
      hours_worked: 160,
      overtime_hours: 0,
      leave_days: 1,
      present_days: 21
    },
    {
      id: 3,
      employee: { id: 3, first_name: 'Mike', last_name: 'Johnson', department: { name: 'Marketing' } },
      pay_period_start: '2024-01-01',
      pay_period_end: '2024-01-31',
      basic_salary: 5600.00,
      overtime_pay: 525.00,
      bonuses: 200.00,
      deductions: 1225.00,
      tax_deduction: 1530.00,
      net_salary: 3570.00,
      gross_salary: 6325.00,
      status: 'pending',
      generated_date: null,
      paid_date: null,
      hours_worked: 160,
      overtime_hours: 15,
      leave_days: 0,
      present_days: 22
    }
  ];

  const departments = ['Engineering', 'HR', 'Marketing', 'Finance', 'Operations'];

  useEffect(() => {
    fetchData();
  }, [selectedPeriod]);

  const fetchData = async () => {
    try {
      setLoading(true);
      // Mock implementation
      setPayrollRecords(mockPayrollRecords);
      setEmployees(mockEmployees);
    } catch (error) {
      setError('Failed to load payroll data');
    } finally {
      setLoading(false);
    }
  };

  const handleGeneratePayroll = async (e) => {
    e.preventDefault();
    try {
      setLoading(true);
      
      // Mock payroll generation
      const newPayrolls = mockEmployees.map(employee => {
        const basicSalary = employee.salary_type === 'fixed' 
          ? employee.base_salary / 12 
          : employee.hourly_rate * 160; // Assuming 160 hours per month
        
        const overtimePay = Math.random() * 500;
        const bonuses = Math.random() * 1000;
        const grossSalary = basicSalary + overtimePay + bonuses;
        const taxDeduction = grossSalary * 0.25; // 25% tax
        const otherDeductions = grossSalary * 0.15; // 15% other deductions
        const netSalary = grossSalary - taxDeduction - otherDeductions;

        return {
          id: Date.now() + employee.id,
          employee: employee,
          pay_period_start: format(generateData.pay_period_start, 'yyyy-MM-dd'),
          pay_period_end: format(generateData.pay_period_end, 'yyyy-MM-dd'),
          basic_salary: Math.round(basicSalary * 100) / 100,
          overtime_pay: Math.round(overtimePay * 100) / 100,
          bonuses: Math.round(bonuses * 100) / 100,
          deductions: Math.round(otherDeductions * 100) / 100,
          tax_deduction: Math.round(taxDeduction * 100) / 100,
          net_salary: Math.round(netSalary * 100) / 100,
          gross_salary: Math.round(grossSalary * 100) / 100,
          status: 'generated',
          generated_date: format(new Date(), 'yyyy-MM-dd'),
          paid_date: null,
          hours_worked: 160 + Math.floor(Math.random() * 20),
          overtime_hours: Math.floor(Math.random() * 20),
          leave_days: Math.floor(Math.random() * 3),
          present_days: 22 - Math.floor(Math.random() * 3)
        };
      });

      setPayrollRecords(prev => [...newPayrolls, ...prev]);
      setSuccess(`Payroll generated for ${newPayrolls.length} employees!`);
      setIsGenerateDialogOpen(false);
      resetGenerateForm();
    } catch (error) {
      setError('Failed to generate payroll');
    } finally {
      setLoading(false);
    }
  };

  const handleMarkAsPaid = async (payrollId) => {
    try {
      setPayrollRecords(prev => prev.map(record => 
        record.id === payrollId 
          ? { ...record, status: 'paid', paid_date: format(new Date(), 'yyyy-MM-dd') }
          : record
      ));
      setSuccess('Payroll marked as paid successfully!');
    } catch (error) {
      setError('Failed to update payroll status');
    }
  };

  const handleDeletePayroll = async (payrollId) => {
    if (window.confirm('Are you sure you want to delete this payroll record?')) {
      try {
        setPayrollRecords(prev => prev.filter(record => record.id !== payrollId));
        setSuccess('Payroll record deleted successfully!');
      } catch (error) {
        setError('Failed to delete payroll record');
      }
    }
  };

  const resetGenerateForm = () => {
    setGenerateData({
      pay_period_start: null,
      pay_period_end: null,
      employees: 'all'
    });
  };

  const getStatusBadge = (status) => {
    switch (status) {
      case 'pending':
        return <Badge className="bg-yellow-100 text-yellow-800">Pending</Badge>;
      case 'generated':
        return <Badge className="bg-blue-100 text-blue-800">Generated</Badge>;
      case 'paid':
        return <Badge className="bg-green-100 text-green-800">Paid</Badge>;
      default:
        return <Badge variant="secondary">Unknown</Badge>;
    }
  };

  const getInitials = (firstName, lastName) => {
    return `${firstName?.[0] || ''}${lastName?.[0] || ''}`.toUpperCase();
  };

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(amount || 0);
  };

  const filteredRecords = payrollRecords.filter(record => {
    const matchesSearch = 
      record.employee.first_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      record.employee.last_name.toLowerCase().includes(searchTerm.toLowerCase());
    
    const matchesStatus = filterStatus === 'all' || record.status === filterStatus;
    const matchesDepartment = filterDepartment === 'all' || 
      record.employee.department?.name === filterDepartment;
    
    return matchesSearch && matchesStatus && matchesDepartment;
  });

  const payrollStats = {
    totalRecords: payrollRecords.length,
    totalPaid: payrollRecords.filter(r => r.status === 'paid').reduce((sum, r) => sum + r.net_salary, 0),
    pending: payrollRecords.filter(r => r.status === 'pending').length,
    generated: payrollRecords.filter(r => r.status === 'generated').length,
    paid: payrollRecords.filter(r => r.status === 'paid').length
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Payroll Processing</h1>
          <p className="text-muted-foreground">
            Generate and manage employee payroll
          </p>
        </div>
        {(isAdmin || isHR) && (
          <Dialog open={isGenerateDialogOpen} onOpenChange={setIsGenerateDialogOpen}>
            <DialogTrigger asChild>
              <Button onClick={resetGenerateForm}>
                <Calculator className="mr-2 h-4 w-4" />
                Generate Payroll
              </Button>
            </DialogTrigger>
            <DialogContent className="max-w-lg">
              <DialogHeader>
                <DialogTitle>Generate Payroll</DialogTitle>
                <DialogDescription>
                  Generate payroll for selected pay period
                </DialogDescription>
              </DialogHeader>
              <form onSubmit={handleGeneratePayroll} className="space-y-4">
                {error && (
                  <Alert variant="destructive">
                    <AlertDescription>{error}</AlertDescription>
                  </Alert>
                )}
                
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label>Pay Period Start</Label>
                    <Popover>
                      <PopoverTrigger asChild>
                        <Button
                          variant="outline"
                          className="w-full justify-start text-left font-normal"
                        >
                          <CalendarIcon className="mr-2 h-4 w-4" />
                          {generateData.pay_period_start ? format(generateData.pay_period_start, 'PPP') : 'Select date'}
                        </Button>
                      </PopoverTrigger>
                      <PopoverContent className="w-auto p-0">
                        <Calendar
                          mode="single"
                          selected={generateData.pay_period_start}
                          onSelect={(date) => setGenerateData(prev => ({ ...prev, pay_period_start: date }))}
                          initialFocus
                        />
                      </PopoverContent>
                    </Popover>
                  </div>
                  <div>
                    <Label>Pay Period End</Label>
                    <Popover>
                      <PopoverTrigger asChild>
                        <Button
                          variant="outline"
                          className="w-full justify-start text-left font-normal"
                        >
                          <CalendarIcon className="mr-2 h-4 w-4" />
                          {generateData.pay_period_end ? format(generateData.pay_period_end, 'PPP') : 'Select date'}
                        </Button>
                      </PopoverTrigger>
                      <PopoverContent className="w-auto p-0">
                        <Calendar
                          mode="single"
                          selected={generateData.pay_period_end}
                          onSelect={(date) => setGenerateData(prev => ({ ...prev, pay_period_end: date }))}
                          disabled={(date) => date < (generateData.pay_period_start || new Date())}
                          initialFocus
                        />
                      </PopoverContent>
                    </Popover>
                  </div>
                </div>

                <div>
                  <Label>Employees</Label>
                  <Select 
                    value={generateData.employees} 
                    onValueChange={(value) => setGenerateData(prev => ({ ...prev, employees: value }))}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Select employees" />
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
                </div>

                <div className="flex justify-end space-x-2">
                  <Button type="button" variant="outline" onClick={() => setIsGenerateDialogOpen(false)}>
                    Cancel
                  </Button>
                  <Button type="submit" disabled={!generateData.pay_period_start || !generateData.pay_period_end}>
                    Generate Payroll
                  </Button>
                </div>
              </form>
            </DialogContent>
          </Dialog>
        )}
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

      <Tabs defaultValue="records" className="space-y-6">
        <TabsList>
          <TabsTrigger value="records">Payroll Records</TabsTrigger>
          <TabsTrigger value="summary">Summary</TabsTrigger>
          {!isAdmin && !isHR && <TabsTrigger value="payslips">My Payslips</TabsTrigger>}
        </TabsList>

        {/* Payroll Records Tab */}
        <TabsContent value="records" className="space-y-6">
          {/* Stats Cards */}
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Total Records</CardTitle>
                <FileText className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{payrollStats.totalRecords}</div>
                <p className="text-xs text-muted-foreground">
                  Payroll records
                </p>
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Total Paid</CardTitle>
                <DollarSign className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{formatCurrency(payrollStats.totalPaid)}</div>
                <p className="text-xs text-muted-foreground">
                  Net salary paid
                </p>
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Pending</CardTitle>
                <AlertCircle className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-yellow-600">{payrollStats.pending}</div>
                <p className="text-xs text-muted-foreground">
                  Awaiting generation
                </p>
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Generated</CardTitle>
                <CheckCircle className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-blue-600">{payrollStats.generated}</div>
                <p className="text-xs text-muted-foreground">
                  Ready for payment
                </p>
              </CardContent>
            </Card>
          </div>

          <Card>
            <CardHeader>
              <CardTitle>Payroll Records</CardTitle>
              <CardDescription>
                Manage employee payroll records and payments
              </CardDescription>
            </CardHeader>
            <CardContent>
              {/* Filters */}
              <div className="flex flex-col md:flex-row gap-4 mb-6">
                <div className="flex-1">
                  <div className="relative">
                    <Search className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
                    <Input
                      placeholder="Search employees..."
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
                    <SelectItem value="generated">Generated</SelectItem>
                    <SelectItem value="paid">Paid</SelectItem>
                  </SelectContent>
                </Select>
                <Select value={filterDepartment} onValueChange={setFilterDepartment}>
                  <SelectTrigger className="w-[160px]">
                    <SelectValue placeholder="Department" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">All Departments</SelectItem>
                    {departments.map(dept => (
                      <SelectItem key={dept} value={dept}>
                        {dept}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              {/* Records Table */}
              <div className="rounded-md border">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Employee</TableHead>
                      <TableHead>Pay Period</TableHead>
                      <TableHead>Gross Salary</TableHead>
                      <TableHead>Deductions</TableHead>
                      <TableHead>Net Salary</TableHead>
                      <TableHead>Status</TableHead>
                      <TableHead>Actions</TableHead>
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
                              <div className="text-sm text-muted-foreground">
                                {record.employee.department?.name}
                              </div>
                            </div>
                          </div>
                        </TableCell>
                        <TableCell>
                          <div className="text-sm">
                            {format(new Date(record.pay_period_start), 'MMM d')} - {format(new Date(record.pay_period_end), 'MMM d, yyyy')}
                          </div>
                        </TableCell>
                        <TableCell className="font-medium">{formatCurrency(record.gross_salary)}</TableCell>
                        <TableCell className="text-red-600">
                          -{formatCurrency(record.deductions + record.tax_deduction)}
                        </TableCell>
                        <TableCell className="font-medium text-green-600">
                          {formatCurrency(record.net_salary)}
                        </TableCell>
                        <TableCell>{getStatusBadge(record.status)}</TableCell>
                        <TableCell>
                          <div className="flex items-center space-x-2">
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => {
                                setSelectedPayroll(record);
                                setIsViewPayslipOpen(true);
                              }}
                            >
                              <Eye className="h-4 w-4" />
                            </Button>
                            {(isAdmin || isHR) && (
                              <>
                                {record.status === 'generated' && (
                                  <Button
                                    variant="ghost"
                                    size="sm"
                                    onClick={() => handleMarkAsPaid(record.id)}
                                    className="text-green-600 hover:text-green-700"
                                  >
                                    <CreditCard className="h-4 w-4" />
                                  </Button>
                                )}
                                <DropdownMenu>
                                  <DropdownMenuTrigger asChild>
                                    <Button variant="ghost" size="sm">
                                      <MoreHorizontal className="h-4 w-4" />
                                    </Button>
                                  </DropdownMenuTrigger>
                                  <DropdownMenuContent align="end">
                                    <DropdownMenuLabel>Actions</DropdownMenuLabel>
                                    <DropdownMenuItem>
                                      <Download className="mr-2 h-4 w-4" />
                                      Download Payslip
                                    </DropdownMenuItem>
                                    <DropdownMenuItem>
                                      <Edit className="mr-2 h-4 w-4" />
                                      Edit Record
                                    </DropdownMenuItem>
                                    <DropdownMenuSeparator />
                                    <DropdownMenuItem 
                                      onClick={() => handleDeletePayroll(record.id)}
                                      className="text-red-600"
                                    >
                                      <Trash2 className="mr-2 h-4 w-4" />
                                      Delete
                                    </DropdownMenuItem>
                                  </DropdownMenuContent>
                                </DropdownMenu>
                              </>
                            )}
                          </div>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </div>

              {filteredRecords.length === 0 && (
                <div className="text-center py-8">
                  <FileText className="mx-auto h-12 w-12 text-muted-foreground" />
                  <h3 className="mt-2 text-sm font-semibold">No payroll records found</h3>
                  <p className="mt-1 text-sm text-muted-foreground">
                    No records match your current filters.
                  </p>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Summary Tab */}
        <TabsContent value="summary" className="space-y-6">
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Monthly Payroll</CardTitle>
                <Banknote className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{formatCurrency(245000)}</div>
                <p className="text-xs text-muted-foreground">
                  <span className="text-green-600">+12%</span> from last month
                </p>
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Avg. Salary</CardTitle>
                <DollarSign className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{formatCurrency(6125)}</div>
                <p className="text-xs text-muted-foreground">
                  Per employee
                </p>
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Total Deductions</CardTitle>
                <Receipt className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{formatCurrency(98000)}</div>
                <p className="text-xs text-muted-foreground">
                  Tax + Other deductions
                </p>
              </CardContent>
            </Card>
          </div>

          <div className="grid gap-4 md:grid-cols-2">
            <Card>
              <CardHeader>
                <CardTitle>Department Wise Payroll</CardTitle>
                <CardDescription>Salary distribution by department</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {departments.map((dept, index) => {
                    const amount = Math.random() * 100000 + 50000;
                    const percentage = (amount / 500000) * 100;
                    return (
                      <div key={dept} className="space-y-2">
                        <div className="flex justify-between text-sm">
                          <span className="font-medium">{dept}</span>
                          <span>{formatCurrency(amount)}</span>
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
                <CardTitle>Payroll Trends</CardTitle>
                <CardDescription>Monthly payroll over the past 6 months</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="grid grid-cols-6 gap-2 text-center">
                    {['Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'].map((month, index) => (
                      <div key={month} className="space-y-2">
                        <div className="text-xs font-medium">{month}</div>
                        <div className="h-20 bg-muted rounded flex items-end justify-center">
                          <div 
                            className="bg-primary rounded-t w-full"
                            style={{ height: `${Math.random() * 80 + 20}%` }}
                          ></div>
                        </div>
                        <div className="text-xs text-muted-foreground">
                          {formatCurrency(Math.random() * 50000 + 200000)}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* My Payslips Tab */}
        {!isAdmin && !isHR && (
          <TabsContent value="payslips" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>My Payslips</CardTitle>
                <CardDescription>
                  Your salary history and payslip details
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {payrollRecords
                    .filter(record => record.employee.id === user?.id)
                    .map((record) => (
                      <div key={record.id} className="flex items-center justify-between p-4 border rounded-lg">
                        <div className="flex items-center space-x-4">
                          <div className="w-12 h-12 bg-primary/10 rounded-lg flex items-center justify-center">
                            <Receipt className="h-6 w-6 text-primary" />
                          </div>
                          <div>
                            <div className="font-medium">
                              {format(new Date(record.pay_period_start), 'MMMM yyyy')}
                            </div>
                            <div className="text-sm text-muted-foreground">
                              {format(new Date(record.pay_period_start), 'MMM d')} - {format(new Date(record.pay_period_end), 'MMM d, yyyy')}
                            </div>
                          </div>
                        </div>
                        <div className="text-right">
                          <div className="font-medium text-lg">{formatCurrency(record.net_salary)}</div>
                          <div className="text-sm text-muted-foreground">Net Salary</div>
                        </div>
                        <div className="flex items-center space-x-2">
                          {getStatusBadge(record.status)}
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => {
                              setSelectedPayroll(record);
                              setIsViewPayslipOpen(true);
                            }}
                          >
                            <Eye className="h-4 w-4" />
                          </Button>
                          <Button variant="ghost" size="sm">
                            <Download className="h-4 w-4" />
                          </Button>
                        </div>
                      </div>
                    ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        )}
      </Tabs>

      {/* View Payslip Dialog */}
      <Dialog open={isViewPayslipOpen} onOpenChange={setIsViewPayslipOpen}>
        <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>Payslip Details</DialogTitle>
            <DialogDescription>
              Detailed salary breakdown for {selectedPayroll?.employee.first_name} {selectedPayroll?.employee.last_name}
            </DialogDescription>
          </DialogHeader>
          {selectedPayroll && (
            <div className="space-y-6">
              {/* Header */}
              <div className="flex items-center justify-between p-4 bg-muted rounded-lg">
                <div className="flex items-center space-x-4">
                  <Avatar className="h-12 w-12">
                    <AvatarImage src={selectedPayroll.employee.avatar} />
                    <AvatarFallback>
                      {getInitials(selectedPayroll.employee.first_name, selectedPayroll.employee.last_name)}
                    </AvatarFallback>
                  </Avatar>
                  <div>
                    <h3 className="text-lg font-semibold">
                      {selectedPayroll.employee.first_name} {selectedPayroll.employee.last_name}
                    </h3>
                    <p className="text-sm text-muted-foreground">
                      {selectedPayroll.employee.department?.name}
                    </p>
                  </div>
                </div>
                <div className="text-right">
                  <div className="text-sm text-muted-foreground">Pay Period</div>
                  <div className="font-medium">
                    {format(new Date(selectedPayroll.pay_period_start), 'MMM d')} - {format(new Date(selectedPayroll.pay_period_end), 'MMM d, yyyy')}
                  </div>
                </div>
              </div>

              {/* Earnings */}
              <div>
                <h4 className="font-semibold mb-3">Earnings</h4>
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span>Basic Salary</span>
                    <span>{formatCurrency(selectedPayroll.basic_salary)}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Overtime Pay</span>
                    <span>{formatCurrency(selectedPayroll.overtime_pay)}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Bonuses</span>
                    <span>{formatCurrency(selectedPayroll.bonuses)}</span>
                  </div>
                  <Separator />
                  <div className="flex justify-between font-medium">
                    <span>Gross Salary</span>
                    <span>{formatCurrency(selectedPayroll.gross_salary)}</span>
                  </div>
                </div>
              </div>

              {/* Deductions */}
              <div>
                <h4 className="font-semibold mb-3">Deductions</h4>
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span>Tax Deduction</span>
                    <span className="text-red-600">-{formatCurrency(selectedPayroll.tax_deduction)}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Other Deductions</span>
                    <span className="text-red-600">-{formatCurrency(selectedPayroll.deductions)}</span>
                  </div>
                  <Separator />
                  <div className="flex justify-between font-medium">
                    <span>Total Deductions</span>
                    <span className="text-red-600">
                      -{formatCurrency(selectedPayroll.tax_deduction + selectedPayroll.deductions)}
                    </span>
                  </div>
                </div>
              </div>

              {/* Net Salary */}
              <div className="p-4 bg-green-50 rounded-lg">
                <div className="flex justify-between items-center">
                  <span className="text-lg font-semibold">Net Salary</span>
                  <span className="text-2xl font-bold text-green-600">
                    {formatCurrency(selectedPayroll.net_salary)}
                  </span>
                </div>
              </div>

              {/* Attendance Summary */}
              <div>
                <h4 className="font-semibold mb-3">Attendance Summary</h4>
                <div className="grid grid-cols-2 gap-4">
                  <div className="text-center p-3 bg-muted rounded-lg">
                    <div className="text-2xl font-bold">{selectedPayroll.present_days}</div>
                    <div className="text-sm text-muted-foreground">Present Days</div>
                  </div>
                  <div className="text-center p-3 bg-muted rounded-lg">
                    <div className="text-2xl font-bold">{selectedPayroll.leave_days}</div>
                    <div className="text-sm text-muted-foreground">Leave Days</div>
                  </div>
                  <div className="text-center p-3 bg-muted rounded-lg">
                    <div className="text-2xl font-bold">{selectedPayroll.hours_worked}h</div>
                    <div className="text-sm text-muted-foreground">Hours Worked</div>
                  </div>
                  <div className="text-center p-3 bg-muted rounded-lg">
                    <div className="text-2xl font-bold">{selectedPayroll.overtime_hours}h</div>
                    <div className="text-sm text-muted-foreground">Overtime Hours</div>
                  </div>
                </div>
              </div>

              {/* Status and Dates */}
              <div className="flex justify-between items-center">
                <div>
                  <div className="text-sm text-muted-foreground">Status</div>
                  {getStatusBadge(selectedPayroll.status)}
                </div>
                {selectedPayroll.generated_date && (
                  <div className="text-right">
                    <div className="text-sm text-muted-foreground">Generated Date</div>
                    <div className="text-sm">{format(new Date(selectedPayroll.generated_date), 'PPP')}</div>
                  </div>
                )}
                {selectedPayroll.paid_date && (
                  <div className="text-right">
                    <div className="text-sm text-muted-foreground">Paid Date</div>
                    <div className="text-sm">{format(new Date(selectedPayroll.paid_date), 'PPP')}</div>
                  </div>
                )}
              </div>

              <div className="flex justify-end space-x-2">
                <Button variant="outline">
                  <Download className="mr-2 h-4 w-4" />
                  Download PDF
                </Button>
                <Button variant="outline" onClick={() => setIsViewPayslipOpen(false)}>
                  Close
                </Button>
              </div>
            </div>
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default PayrollProcessing;

