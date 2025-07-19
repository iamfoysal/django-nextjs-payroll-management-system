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
import {
  Users,
  Plus,
  Search,
  Filter,
  Edit,
  Trash2,
  Eye,
  Mail,
  Phone,
  MapPin,
  Calendar,
  DollarSign,
  Building2,
  UserCheck,
  MoreHorizontal,
  Download,
  Upload
} from 'lucide-react';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import axios from 'axios';

const EmployeeManagement = () => {
  const { user, isAdmin, isHR } = useAuth();
  const [employees, setEmployees] = useState([]);
  const [departments, setDepartments] = useState([]);
  const [roles, setRoles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterDepartment, setFilterDepartment] = useState('all');
  const [filterStatus, setFilterStatus] = useState('all');
  const [selectedEmployee, setSelectedEmployee] = useState(null);
  const [isAddDialogOpen, setIsAddDialogOpen] = useState(false);
  const [isEditDialogOpen, setIsEditDialogOpen] = useState(false);
  const [isViewDialogOpen, setIsViewDialogOpen] = useState(false);
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    first_name: '',
    last_name: '',
    phone_number: '',
    address: '',
    date_of_birth: '',
    hire_date: '',
    department: '',
    role: '',
    salary_type: 'fixed',
    base_salary: '',
    hourly_rate: '',
    is_active: true
  });
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  // Mock data for demonstration
  const mockEmployees = [
    {
      id: 1,
      username: 'john.doe',
      email: 'john.doe@company.com',
      first_name: 'John',
      last_name: 'Doe',
      phone_number: '+1-555-0123',
      address: '123 Main St, City, State 12345',
      date_of_birth: '1990-05-15',
      hire_date: '2022-01-15',
      department: { id: 1, name: 'Engineering' },
      role: { id: 1, name: 'Software Engineer' },
      salary_type: 'fixed',
      base_salary: 75000,
      hourly_rate: null,
      is_active: true,
      avatar: null
    },
    {
      id: 2,
      username: 'jane.smith',
      email: 'jane.smith@company.com',
      first_name: 'Jane',
      last_name: 'Smith',
      phone_number: '+1-555-0124',
      address: '456 Oak Ave, City, State 12345',
      date_of_birth: '1988-08-22',
      hire_date: '2021-03-10',
      department: { id: 2, name: 'Human Resources' },
      role: { id: 2, name: 'HR Manager' },
      salary_type: 'fixed',
      base_salary: 85000,
      hourly_rate: null,
      is_active: true,
      avatar: null
    },
    {
      id: 3,
      username: 'mike.johnson',
      email: 'mike.johnson@company.com',
      first_name: 'Mike',
      last_name: 'Johnson',
      phone_number: '+1-555-0125',
      address: '789 Pine St, City, State 12345',
      date_of_birth: '1992-12-03',
      hire_date: '2023-06-01',
      department: { id: 3, name: 'Marketing' },
      role: { id: 3, name: 'Marketing Specialist' },
      salary_type: 'hourly',
      base_salary: null,
      hourly_rate: 35,
      is_active: true,
      avatar: null
    }
  ];

  const mockDepartments = [
    { id: 1, name: 'Engineering' },
    { id: 2, name: 'Human Resources' },
    { id: 3, name: 'Marketing' },
    { id: 4, name: 'Finance' },
    { id: 5, name: 'Operations' }
  ];

  const mockRoles = [
    { id: 1, name: 'Software Engineer' },
    { id: 2, name: 'HR Manager' },
    { id: 3, name: 'Marketing Specialist' },
    { id: 4, name: 'Financial Analyst' },
    { id: 5, name: 'Operations Manager' },
    { id: 6, name: 'Admin' }
  ];

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      // For now, use mock data
      setEmployees(mockEmployees);
      setDepartments(mockDepartments);
      setRoles(mockRoles);
    } catch (error) {
      console.error('Error fetching data:', error);
      setError('Failed to load employee data');
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
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
      username: '',
      email: '',
      first_name: '',
      last_name: '',
      phone_number: '',
      address: '',
      date_of_birth: '',
      hire_date: '',
      department: '',
      role: '',
      salary_type: 'fixed',
      base_salary: '',
      hourly_rate: '',
      is_active: true
    });
    setError('');
    setSuccess('');
  };

  const handleAddEmployee = async (e) => {
    e.preventDefault();
    try {
      // Mock implementation
      const newEmployee = {
        id: employees.length + 1,
        ...formData,
        department: departments.find(d => d.id === parseInt(formData.department)),
        role: roles.find(r => r.id === parseInt(formData.role)),
        base_salary: formData.base_salary ? parseFloat(formData.base_salary) : null,
        hourly_rate: formData.hourly_rate ? parseFloat(formData.hourly_rate) : null,
        avatar: null
      };
      
      setEmployees(prev => [...prev, newEmployee]);
      setSuccess('Employee added successfully!');
      setIsAddDialogOpen(false);
      resetForm();
    } catch (error) {
      setError('Failed to add employee');
    }
  };

  const handleEditEmployee = async (e) => {
    e.preventDefault();
    try {
      // Mock implementation
      const updatedEmployee = {
        ...selectedEmployee,
        ...formData,
        department: departments.find(d => d.id === parseInt(formData.department)),
        role: roles.find(r => r.id === parseInt(formData.role)),
        base_salary: formData.base_salary ? parseFloat(formData.base_salary) : null,
        hourly_rate: formData.hourly_rate ? parseFloat(formData.hourly_rate) : null,
      };
      
      setEmployees(prev => prev.map(emp => 
        emp.id === selectedEmployee.id ? updatedEmployee : emp
      ));
      setSuccess('Employee updated successfully!');
      setIsEditDialogOpen(false);
      resetForm();
      setSelectedEmployee(null);
    } catch (error) {
      setError('Failed to update employee');
    }
  };

  const handleDeleteEmployee = async (employeeId) => {
    if (window.confirm('Are you sure you want to delete this employee?')) {
      try {
        setEmployees(prev => prev.filter(emp => emp.id !== employeeId));
        setSuccess('Employee deleted successfully!');
      } catch (error) {
        setError('Failed to delete employee');
      }
    }
  };

  const openEditDialog = (employee) => {
    setSelectedEmployee(employee);
    setFormData({
      username: employee.username,
      email: employee.email,
      first_name: employee.first_name,
      last_name: employee.last_name,
      phone_number: employee.phone_number,
      address: employee.address,
      date_of_birth: employee.date_of_birth,
      hire_date: employee.hire_date,
      department: employee.department?.id?.toString() || '',
      role: employee.role?.id?.toString() || '',
      salary_type: employee.salary_type,
      base_salary: employee.base_salary?.toString() || '',
      hourly_rate: employee.hourly_rate?.toString() || '',
      is_active: employee.is_active
    });
    setIsEditDialogOpen(true);
  };

  const openViewDialog = (employee) => {
    setSelectedEmployee(employee);
    setIsViewDialogOpen(true);
  };

  const filteredEmployees = employees.filter(employee => {
    const matchesSearch = 
      employee.first_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      employee.last_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      employee.email.toLowerCase().includes(searchTerm.toLowerCase()) ||
      employee.username.toLowerCase().includes(searchTerm.toLowerCase());
    
    const matchesDepartment = filterDepartment === 'all' || 
      employee.department?.id?.toString() === filterDepartment;
    
    const matchesStatus = filterStatus === 'all' || 
      (filterStatus === 'active' && employee.is_active) ||
      (filterStatus === 'inactive' && !employee.is_active);
    
    return matchesSearch && matchesDepartment && matchesStatus;
  });

  const getInitials = (firstName, lastName) => {
    return `${firstName?.[0] || ''}${lastName?.[0] || ''}`.toUpperCase();
  };

  const formatSalary = (employee) => {
    if (employee.salary_type === 'fixed') {
      return `$${employee.base_salary?.toLocaleString() || 0}/year`;
    } else {
      return `$${employee.hourly_rate || 0}/hour`;
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto mb-4"></div>
          <p className="text-muted-foreground">Loading employees...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Employee Management</h1>
          <p className="text-muted-foreground">
            Manage your organization's employees and their information
          </p>
        </div>
        {(isAdmin || isHR) && (
          <Dialog open={isAddDialogOpen} onOpenChange={setIsAddDialogOpen}>
            <DialogTrigger asChild>
              <Button onClick={resetForm}>
                <Plus className="mr-2 h-4 w-4" />
                Add Employee
              </Button>
            </DialogTrigger>
            <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
              <DialogHeader>
                <DialogTitle>Add New Employee</DialogTitle>
                <DialogDescription>
                  Fill in the employee information below
                </DialogDescription>
              </DialogHeader>
              <form onSubmit={handleAddEmployee} className="space-y-4">
                {error && (
                  <Alert variant="destructive">
                    <AlertDescription>{error}</AlertDescription>
                  </Alert>
                )}
                
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label htmlFor="first_name">First Name</Label>
                    <Input
                      id="first_name"
                      name="first_name"
                      value={formData.first_name}
                      onChange={handleInputChange}
                      required
                    />
                  </div>
                  <div>
                    <Label htmlFor="last_name">Last Name</Label>
                    <Input
                      id="last_name"
                      name="last_name"
                      value={formData.last_name}
                      onChange={handleInputChange}
                      required
                    />
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label htmlFor="username">Username</Label>
                    <Input
                      id="username"
                      name="username"
                      value={formData.username}
                      onChange={handleInputChange}
                      required
                    />
                  </div>
                  <div>
                    <Label htmlFor="email">Email</Label>
                    <Input
                      id="email"
                      name="email"
                      type="email"
                      value={formData.email}
                      onChange={handleInputChange}
                      required
                    />
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label htmlFor="phone_number">Phone Number</Label>
                    <Input
                      id="phone_number"
                      name="phone_number"
                      value={formData.phone_number}
                      onChange={handleInputChange}
                    />
                  </div>
                  <div>
                    <Label htmlFor="date_of_birth">Date of Birth</Label>
                    <Input
                      id="date_of_birth"
                      name="date_of_birth"
                      type="date"
                      value={formData.date_of_birth}
                      onChange={handleInputChange}
                    />
                  </div>
                </div>

                <div>
                  <Label htmlFor="address">Address</Label>
                  <Textarea
                    id="address"
                    name="address"
                    value={formData.address}
                    onChange={handleInputChange}
                    rows={2}
                  />
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label htmlFor="department">Department</Label>
                    <Select value={formData.department} onValueChange={(value) => handleSelectChange('department', value)}>
                      <SelectTrigger>
                        <SelectValue placeholder="Select department" />
                      </SelectTrigger>
                      <SelectContent>
                        {departments.map(dept => (
                          <SelectItem key={dept.id} value={dept.id.toString()}>
                            {dept.name}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                  <div>
                    <Label htmlFor="role">Role</Label>
                    <Select value={formData.role} onValueChange={(value) => handleSelectChange('role', value)}>
                      <SelectTrigger>
                        <SelectValue placeholder="Select role" />
                      </SelectTrigger>
                      <SelectContent>
                        {roles.map(role => (
                          <SelectItem key={role.id} value={role.id.toString()}>
                            {role.name}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label htmlFor="hire_date">Hire Date</Label>
                    <Input
                      id="hire_date"
                      name="hire_date"
                      type="date"
                      value={formData.hire_date}
                      onChange={handleInputChange}
                      required
                    />
                  </div>
                  <div>
                    <Label htmlFor="salary_type">Salary Type</Label>
                    <Select value={formData.salary_type} onValueChange={(value) => handleSelectChange('salary_type', value)}>
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="fixed">Fixed Salary</SelectItem>
                        <SelectItem value="hourly">Hourly Rate</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>

                {formData.salary_type === 'fixed' ? (
                  <div>
                    <Label htmlFor="base_salary">Annual Salary ($)</Label>
                    <Input
                      id="base_salary"
                      name="base_salary"
                      type="number"
                      value={formData.base_salary}
                      onChange={handleInputChange}
                      placeholder="75000"
                    />
                  </div>
                ) : (
                  <div>
                    <Label htmlFor="hourly_rate">Hourly Rate ($)</Label>
                    <Input
                      id="hourly_rate"
                      name="hourly_rate"
                      type="number"
                      step="0.01"
                      value={formData.hourly_rate}
                      onChange={handleInputChange}
                      placeholder="25.00"
                    />
                  </div>
                )}

                <div className="flex justify-end space-x-2">
                  <Button type="button" variant="outline" onClick={() => setIsAddDialogOpen(false)}>
                    Cancel
                  </Button>
                  <Button type="submit">Add Employee</Button>
                </div>
              </form>
            </DialogContent>
          </Dialog>
        )}
      </div>

      {/* Alerts */}
      {success && (
        <Alert>
          <AlertDescription>{success}</AlertDescription>
        </Alert>
      )}
      {error && (
        <Alert variant="destructive">
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {/* Stats Cards */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Employees</CardTitle>
            <Users className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{employees.length}</div>
            <p className="text-xs text-muted-foreground">
              Active employees in system
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Active</CardTitle>
            <UserCheck className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {employees.filter(emp => emp.is_active).length}
            </div>
            <p className="text-xs text-muted-foreground">
              Currently active
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Departments</CardTitle>
            <Building2 className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{departments.length}</div>
            <p className="text-xs text-muted-foreground">
              Active departments
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">New This Month</CardTitle>
            <Calendar className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">3</div>
            <p className="text-xs text-muted-foreground">
              Recent hires
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Filters and Search */}
      <Card>
        <CardHeader>
          <CardTitle>Employee Directory</CardTitle>
          <CardDescription>
            Search and filter employees by various criteria
          </CardDescription>
        </CardHeader>
        <CardContent>
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
            <Select value={filterDepartment} onValueChange={setFilterDepartment}>
              <SelectTrigger className="w-[180px]">
                <SelectValue placeholder="Department" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Departments</SelectItem>
                {departments.map(dept => (
                  <SelectItem key={dept.id} value={dept.id.toString()}>
                    {dept.name}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            <Select value={filterStatus} onValueChange={setFilterStatus}>
              <SelectTrigger className="w-[140px]">
                <SelectValue placeholder="Status" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Status</SelectItem>
                <SelectItem value="active">Active</SelectItem>
                <SelectItem value="inactive">Inactive</SelectItem>
              </SelectContent>
            </Select>
          </div>

          {/* Employee Table */}
          <div className="rounded-md border">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Employee</TableHead>
                  <TableHead>Department</TableHead>
                  <TableHead>Role</TableHead>
                  <TableHead>Salary</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {filteredEmployees.map((employee) => (
                  <TableRow key={employee.id}>
                    <TableCell>
                      <div className="flex items-center space-x-3">
                        <Avatar className="h-8 w-8">
                          <AvatarImage src={employee.avatar} />
                          <AvatarFallback>
                            {getInitials(employee.first_name, employee.last_name)}
                          </AvatarFallback>
                        </Avatar>
                        <div>
                          <div className="font-medium">
                            {employee.first_name} {employee.last_name}
                          </div>
                          <div className="text-sm text-muted-foreground">
                            {employee.email}
                          </div>
                        </div>
                      </div>
                    </TableCell>
                    <TableCell>
                      <Badge variant="outline">
                        {employee.department?.name || 'N/A'}
                      </Badge>
                    </TableCell>
                    <TableCell>{employee.role?.name || 'N/A'}</TableCell>
                    <TableCell>{formatSalary(employee)}</TableCell>
                    <TableCell>
                      <Badge variant={employee.is_active ? 'default' : 'secondary'}>
                        {employee.is_active ? 'Active' : 'Inactive'}
                      </Badge>
                    </TableCell>
                    <TableCell>
                      <DropdownMenu>
                        <DropdownMenuTrigger asChild>
                          <Button variant="ghost" className="h-8 w-8 p-0">
                            <MoreHorizontal className="h-4 w-4" />
                          </Button>
                        </DropdownMenuTrigger>
                        <DropdownMenuContent align="end">
                          <DropdownMenuLabel>Actions</DropdownMenuLabel>
                          <DropdownMenuItem onClick={() => openViewDialog(employee)}>
                            <Eye className="mr-2 h-4 w-4" />
                            View Details
                          </DropdownMenuItem>
                          {(isAdmin || isHR) && (
                            <>
                              <DropdownMenuItem onClick={() => openEditDialog(employee)}>
                                <Edit className="mr-2 h-4 w-4" />
                                Edit
                              </DropdownMenuItem>
                              <DropdownMenuSeparator />
                              <DropdownMenuItem 
                                onClick={() => handleDeleteEmployee(employee.id)}
                                className="text-red-600"
                              >
                                <Trash2 className="mr-2 h-4 w-4" />
                                Delete
                              </DropdownMenuItem>
                            </>
                          )}
                        </DropdownMenuContent>
                      </DropdownMenu>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>

          {filteredEmployees.length === 0 && (
            <div className="text-center py-8">
              <Users className="mx-auto h-12 w-12 text-muted-foreground" />
              <h3 className="mt-2 text-sm font-semibold">No employees found</h3>
              <p className="mt-1 text-sm text-muted-foreground">
                Try adjusting your search or filter criteria.
              </p>
            </div>
          )}
        </CardContent>
      </Card>

      {/* View Employee Dialog */}
      <Dialog open={isViewDialogOpen} onOpenChange={setIsViewDialogOpen}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>Employee Details</DialogTitle>
            <DialogDescription>
              Complete information for {selectedEmployee?.first_name} {selectedEmployee?.last_name}
            </DialogDescription>
          </DialogHeader>
          {selectedEmployee && (
            <div className="space-y-6">
              <div className="flex items-center space-x-4">
                <Avatar className="h-16 w-16">
                  <AvatarImage src={selectedEmployee.avatar} />
                  <AvatarFallback className="text-lg">
                    {getInitials(selectedEmployee.first_name, selectedEmployee.last_name)}
                  </AvatarFallback>
                </Avatar>
                <div>
                  <h3 className="text-lg font-semibold">
                    {selectedEmployee.first_name} {selectedEmployee.last_name}
                  </h3>
                  <p className="text-muted-foreground">{selectedEmployee.role?.name}</p>
                  <Badge variant={selectedEmployee.is_active ? 'default' : 'secondary'}>
                    {selectedEmployee.is_active ? 'Active' : 'Inactive'}
                  </Badge>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label className="text-sm font-medium">Email</Label>
                  <div className="flex items-center mt-1">
                    <Mail className="mr-2 h-4 w-4 text-muted-foreground" />
                    <span>{selectedEmployee.email}</span>
                  </div>
                </div>
                <div>
                  <Label className="text-sm font-medium">Phone</Label>
                  <div className="flex items-center mt-1">
                    <Phone className="mr-2 h-4 w-4 text-muted-foreground" />
                    <span>{selectedEmployee.phone_number || 'N/A'}</span>
                  </div>
                </div>
                <div>
                  <Label className="text-sm font-medium">Department</Label>
                  <div className="flex items-center mt-1">
                    <Building2 className="mr-2 h-4 w-4 text-muted-foreground" />
                    <span>{selectedEmployee.department?.name || 'N/A'}</span>
                  </div>
                </div>
                <div>
                  <Label className="text-sm font-medium">Salary</Label>
                  <div className="flex items-center mt-1">
                    <DollarSign className="mr-2 h-4 w-4 text-muted-foreground" />
                    <span>{formatSalary(selectedEmployee)}</span>
                  </div>
                </div>
                <div>
                  <Label className="text-sm font-medium">Hire Date</Label>
                  <div className="flex items-center mt-1">
                    <Calendar className="mr-2 h-4 w-4 text-muted-foreground" />
                    <span>{new Date(selectedEmployee.hire_date).toLocaleDateString()}</span>
                  </div>
                </div>
                <div>
                  <Label className="text-sm font-medium">Date of Birth</Label>
                  <div className="flex items-center mt-1">
                    <Calendar className="mr-2 h-4 w-4 text-muted-foreground" />
                    <span>{selectedEmployee.date_of_birth ? new Date(selectedEmployee.date_of_birth).toLocaleDateString() : 'N/A'}</span>
                  </div>
                </div>
              </div>

              {selectedEmployee.address && (
                <div>
                  <Label className="text-sm font-medium">Address</Label>
                  <div className="flex items-start mt-1">
                    <MapPin className="mr-2 h-4 w-4 text-muted-foreground mt-0.5" />
                    <span>{selectedEmployee.address}</span>
                  </div>
                </div>
              )}
            </div>
          )}
        </DialogContent>
      </Dialog>

      {/* Edit Employee Dialog */}
      <Dialog open={isEditDialogOpen} onOpenChange={setIsEditDialogOpen}>
        <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>Edit Employee</DialogTitle>
            <DialogDescription>
              Update employee information
            </DialogDescription>
          </DialogHeader>
          <form onSubmit={handleEditEmployee} className="space-y-4">
            {error && (
              <Alert variant="destructive">
                <AlertDescription>{error}</AlertDescription>
              </Alert>
            )}
            
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label htmlFor="edit_first_name">First Name</Label>
                <Input
                  id="edit_first_name"
                  name="first_name"
                  value={formData.first_name}
                  onChange={handleInputChange}
                  required
                />
              </div>
              <div>
                <Label htmlFor="edit_last_name">Last Name</Label>
                <Input
                  id="edit_last_name"
                  name="last_name"
                  value={formData.last_name}
                  onChange={handleInputChange}
                  required
                />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label htmlFor="edit_username">Username</Label>
                <Input
                  id="edit_username"
                  name="username"
                  value={formData.username}
                  onChange={handleInputChange}
                  required
                />
              </div>
              <div>
                <Label htmlFor="edit_email">Email</Label>
                <Input
                  id="edit_email"
                  name="email"
                  type="email"
                  value={formData.email}
                  onChange={handleInputChange}
                  required
                />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label htmlFor="edit_phone_number">Phone Number</Label>
                <Input
                  id="edit_phone_number"
                  name="phone_number"
                  value={formData.phone_number}
                  onChange={handleInputChange}
                />
              </div>
              <div>
                <Label htmlFor="edit_date_of_birth">Date of Birth</Label>
                <Input
                  id="edit_date_of_birth"
                  name="date_of_birth"
                  type="date"
                  value={formData.date_of_birth}
                  onChange={handleInputChange}
                />
              </div>
            </div>

            <div>
              <Label htmlFor="edit_address">Address</Label>
              <Textarea
                id="edit_address"
                name="address"
                value={formData.address}
                onChange={handleInputChange}
                rows={2}
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label htmlFor="edit_department">Department</Label>
                <Select value={formData.department} onValueChange={(value) => handleSelectChange('department', value)}>
                  <SelectTrigger>
                    <SelectValue placeholder="Select department" />
                  </SelectTrigger>
                  <SelectContent>
                    {departments.map(dept => (
                      <SelectItem key={dept.id} value={dept.id.toString()}>
                        {dept.name}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <div>
                <Label htmlFor="edit_role">Role</Label>
                <Select value={formData.role} onValueChange={(value) => handleSelectChange('role', value)}>
                  <SelectTrigger>
                    <SelectValue placeholder="Select role" />
                  </SelectTrigger>
                  <SelectContent>
                    {roles.map(role => (
                      <SelectItem key={role.id} value={role.id.toString()}>
                        {role.name}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label htmlFor="edit_hire_date">Hire Date</Label>
                <Input
                  id="edit_hire_date"
                  name="hire_date"
                  type="date"
                  value={formData.hire_date}
                  onChange={handleInputChange}
                  required
                />
              </div>
              <div>
                <Label htmlFor="edit_salary_type">Salary Type</Label>
                <Select value={formData.salary_type} onValueChange={(value) => handleSelectChange('salary_type', value)}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="fixed">Fixed Salary</SelectItem>
                    <SelectItem value="hourly">Hourly Rate</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>

            {formData.salary_type === 'fixed' ? (
              <div>
                <Label htmlFor="edit_base_salary">Annual Salary ($)</Label>
                <Input
                  id="edit_base_salary"
                  name="base_salary"
                  type="number"
                  value={formData.base_salary}
                  onChange={handleInputChange}
                  placeholder="75000"
                />
              </div>
            ) : (
              <div>
                <Label htmlFor="edit_hourly_rate">Hourly Rate ($)</Label>
                <Input
                  id="edit_hourly_rate"
                  name="hourly_rate"
                  type="number"
                  step="0.01"
                  value={formData.hourly_rate}
                  onChange={handleInputChange}
                  placeholder="25.00"
                />
              </div>
            )}

            <div className="flex items-center space-x-2">
              <input
                type="checkbox"
                id="edit_is_active"
                name="is_active"
                checked={formData.is_active}
                onChange={handleInputChange}
                className="rounded border-gray-300"
              />
              <Label htmlFor="edit_is_active">Active Employee</Label>
            </div>

            <div className="flex justify-end space-x-2">
              <Button type="button" variant="outline" onClick={() => setIsEditDialogOpen(false)}>
                Cancel
              </Button>
              <Button type="submit">Update Employee</Button>
            </div>
          </form>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default EmployeeManagement;

