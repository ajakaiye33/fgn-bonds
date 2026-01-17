/**
 * FGN Savings Bond Admin Dashboard
 *
 * Enhanced admin interface with analytics, filtering, pagination,
 * and export capabilities.
 *
 * @author Hedgar Ajakaiye
 * @license MIT
 */

import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import { adminApi } from '../services/api';
import { Button, Input, Checkbox, Select } from '../components/ui';
import { ApplicationDetailModal } from '../components/admin';
import { formatCurrency } from '../lib/utils';
import { TENORS, MONTHS } from '../lib/constants';
import type { MonthlyReportSummary, DMOSubmission } from '../types/application';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  LineChart,
  Line,
} from 'recharts';

// Types
interface Summary {
  total_applications: number;
  total_value: number;
  average_value: number;
  this_month_count: number;
}

interface Analytics {
  by_applicant_type: { type: string; count: number; total_value: number }[];
  by_tenor: { tenor: string; count: number; total_value: number }[];
  by_month: { month: string; count: number; total_value: number }[];
  value_distribution: { range: string; count: number }[];
}

interface Application {
  id: number;
  submission_date: string;
  applicant_type: string;
  tenor: string;
  bond_value: number;
  full_name?: string;
  company_name?: string;
  email?: string;
  corp_email?: string;
  payment_status: string;
}

interface Filters {
  page: number;
  page_size: number;
  applicant_types: string[];
  tenors: string[];
  payment_statuses: string[];
  start_date: string;
  end_date: string;
  min_value: string;
  max_value: string;
  search: string;
}

const PAYMENT_STATUSES = [
  { value: 'pending', label: 'Pending', color: 'bg-gray-600/30 text-gray-400' },
  { value: 'paid', label: 'Paid', color: 'bg-yellow-900/30 text-yellow-400' },
  { value: 'verified', label: 'Verified', color: 'bg-green-900/30 text-green-400' },
  { value: 'rejected', label: 'Rejected', color: 'bg-red-900/30 text-red-400' },
];

const CHART_COLORS = ['#4CAF50', '#2196F3', '#FF9800', '#9C27B0', '#E91E63'];

export function AdminDashboard() {
  const { user, logout, isLoading: authLoading } = useAuth();
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState<'overview' | 'applications' | 'reports'>('overview');

  // Data state
  const [summary, setSummary] = useState<Summary | null>(null);
  const [analytics, setAnalytics] = useState<Analytics | null>(null);
  const [applications, setApplications] = useState<Application[]>([]);
  const [totalPages, setTotalPages] = useState(1);
  const [isLoading, setIsLoading] = useState(true);
  const [selectedApplicationId, setSelectedApplicationId] = useState<number | null>(null);

  // Reports state
  const [reportMonth, setReportMonth] = useState(MONTHS[new Date().getMonth()]);
  const [reportYear, setReportYear] = useState(new Date().getFullYear());
  const [reportSummary, setReportSummary] = useState<MonthlyReportSummary | null>(null);
  const [submissions, setSubmissions] = useState<DMOSubmission[]>([]);
  const [isLoadingReport, setIsLoadingReport] = useState(false);

  // Filter state
  const [filters, setFilters] = useState<Filters>({
    page: 1,
    page_size: 20,
    applicant_types: [],
    tenors: [],
    payment_statuses: [],
    start_date: '',
    end_date: '',
    min_value: '',
    max_value: '',
    search: '',
  });

  // Redirect if not authenticated
  useEffect(() => {
    if (!authLoading && !user) {
      navigate('/admin/login');
    }
  }, [user, authLoading, navigate]);

  // Fetch data
  useEffect(() => {
    if (user) {
      fetchData();
    }
  }, [user, filters.page]);

  const fetchData = async () => {
    setIsLoading(true);
    try {
      const [summaryData, analyticsData, applicationsData] = await Promise.all([
        adminApi.getSummary(),
        adminApi.getAnalytics(),
        adminApi.getApplications({
          page: filters.page - 1, // Convert to 0-indexed for API
          page_size: filters.page_size,
          applicant_types: filters.applicant_types.length > 0 ? filters.applicant_types : undefined,
          tenors: filters.tenors.length > 0 ? filters.tenors : undefined,
          payment_statuses: filters.payment_statuses.length > 0 ? filters.payment_statuses : undefined,
          start_date: filters.start_date || undefined,
          end_date: filters.end_date || undefined,
          min_value: filters.min_value ? parseFloat(filters.min_value) : undefined,
          max_value: filters.max_value ? parseFloat(filters.max_value) : undefined,
          search: filters.search || undefined,
        }),
      ]);

      setSummary(summaryData);
      setAnalytics(analyticsData);
      setApplications(applicationsData.items);
      setTotalPages(applicationsData.total_pages);
    } catch (error) {
      console.error('Failed to fetch data:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSearch = () => {
    setFilters((prev) => ({ ...prev, page: 1 }));
    fetchData();
  };

  const handleExportCsv = async () => {
    try {
      const blob = await adminApi.exportCsv(filters as unknown as Record<string, unknown>);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `fgn_bonds_export_${new Date().toISOString().split('T')[0]}.csv`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (error) {
      console.error('Export failed:', error);
    }
  };

  const handleExportExcel = async () => {
    try {
      const blob = await adminApi.exportExcel(filters as unknown as Record<string, unknown>);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `fgn_bonds_export_${new Date().toISOString().split('T')[0]}.xlsx`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (error) {
      console.error('Export failed:', error);
    }
  };

  // Reports functions
  const fetchReportData = async () => {
    setIsLoadingReport(true);
    try {
      const [summaryData, submissionsData] = await Promise.all([
        adminApi.getMonthlyReportSummary(reportMonth, reportYear),
        adminApi.getDmoSubmissions(),
      ]);
      setReportSummary(summaryData);
      setSubmissions(submissionsData);
    } catch (error) {
      console.error('Failed to fetch report data:', error);
    } finally {
      setIsLoadingReport(false);
    }
  };

  const handleExportDmoReport = async () => {
    try {
      const blob = await adminApi.exportDmoReportExcel(reportMonth, reportYear, false);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `DMO_Report_${reportMonth}_${reportYear}.xlsx`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (error) {
      console.error('Export failed:', error);
    }
  };

  const handleMarkAsSubmitted = async () => {
    if (!reportSummary || reportSummary.is_submitted) return;

    const notes = prompt('Enter any notes for this submission (optional):');

    try {
      await adminApi.markAsSubmittedToDmo({
        month_of_offer: reportMonth,
        year: reportYear,
        notes: notes || undefined,
      });
      fetchReportData();
    } catch (error) {
      console.error('Failed to mark as submitted:', error);
      alert('Failed to mark as submitted to DMO');
    }
  };

  // Fetch report data when reports tab is active
  useEffect(() => {
    if (activeTab === 'reports') {
      fetchReportData();
    }
  }, [activeTab, reportMonth, reportYear]);

  if (authLoading) {
    return (
      <div className="min-h-screen bg-dark-bg flex items-center justify-center">
        <div className="animate-spin w-8 h-8 border-4 border-primary-500 border-t-transparent rounded-full" />
      </div>
    );
  }

  if (!user) return null;

  return (
    <div className="min-h-screen bg-dark-bg">
      {/* Header */}
      <header className="bg-dark-surface border-b border-dark-border sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <div className="w-10 h-10 bg-primary-900 rounded-lg flex items-center justify-center">
              <span className="text-white font-bold">FGN</span>
            </div>
            <div>
              <h1 className="text-lg font-bold text-dark-text">Admin Dashboard</h1>
              <p className="text-xs text-dark-text-secondary">FGN Savings Bond</p>
            </div>
          </div>
          <div className="flex items-center gap-4">
            <span className="text-sm text-dark-text-secondary">
              Welcome, {user.username}
            </span>
            <Button variant="secondary" size="sm" onClick={logout}>
              Logout
            </Button>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 py-6">
        {/* Tabs */}
        <div className="flex gap-4 mb-6 border-b border-dark-border">
          <button
            className={`pb-3 px-2 text-sm font-medium transition-colors ${
              activeTab === 'overview'
                ? 'text-primary-500 border-b-2 border-primary-500'
                : 'text-dark-text-secondary hover:text-dark-text'
            }`}
            onClick={() => setActiveTab('overview')}
          >
            Overview
          </button>
          <button
            className={`pb-3 px-2 text-sm font-medium transition-colors ${
              activeTab === 'applications'
                ? 'text-primary-500 border-b-2 border-primary-500'
                : 'text-dark-text-secondary hover:text-dark-text'
            }`}
            onClick={() => setActiveTab('applications')}
          >
            Applications
          </button>
          <button
            className={`pb-3 px-2 text-sm font-medium transition-colors ${
              activeTab === 'reports'
                ? 'text-primary-500 border-b-2 border-primary-500'
                : 'text-dark-text-secondary hover:text-dark-text'
            }`}
            onClick={() => setActiveTab('reports')}
          >
            DMO Reports
          </button>
        </div>

        {activeTab === 'overview' && (
          <>
            {/* Summary Cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
              <SummaryCard
                title="Total Applications"
                value={summary?.total_applications?.toLocaleString() || '0'}
                icon="📝"
              />
              <SummaryCard
                title="Total Value"
                value={formatCurrency(summary?.total_value || 0)}
                icon="💰"
              />
              <SummaryCard
                title="Average Value"
                value={formatCurrency(summary?.average_value || 0)}
                icon="📊"
              />
              <SummaryCard
                title="This Month"
                value={summary?.this_month_count?.toLocaleString() || '0'}
                icon="📅"
              />
            </div>

            {/* Charts */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* By Applicant Type */}
              <div className="card">
                <h3 className="text-lg font-semibold text-dark-text mb-4">
                  By Applicant Type
                </h3>
                <div className="h-64">
                  <ResponsiveContainer width="100%" height="100%">
                    <PieChart>
                      <Pie
                        data={analytics?.by_applicant_type || []}
                        dataKey="count"
                        nameKey="type"
                        cx="50%"
                        cy="50%"
                        outerRadius={80}
                        label={(props) => `${props.name}: ${props.value}`}
                      >
                        {analytics?.by_applicant_type?.map((_, index) => (
                          <Cell
                            key={`cell-${index}`}
                            fill={CHART_COLORS[index % CHART_COLORS.length]}
                          />
                        ))}
                      </Pie>
                      <Tooltip />
                    </PieChart>
                  </ResponsiveContainer>
                </div>
              </div>

              {/* By Tenor */}
              <div className="card">
                <h3 className="text-lg font-semibold text-dark-text mb-4">
                  By Tenor
                </h3>
                <div className="h-64">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={analytics?.by_tenor || []}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#30363d" />
                      <XAxis dataKey="tenor" stroke="#8b949e" />
                      <YAxis stroke="#8b949e" />
                      <Tooltip
                        contentStyle={{
                          backgroundColor: '#21262d',
                          border: '1px solid #30363d',
                        }}
                      />
                      <Bar dataKey="count" fill="#4CAF50" />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </div>

              {/* Monthly Trend */}
              <div className="card lg:col-span-2">
                <h3 className="text-lg font-semibold text-dark-text mb-4">
                  Monthly Trend
                </h3>
                <div className="h-64">
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={analytics?.by_month || []}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#30363d" />
                      <XAxis dataKey="month" stroke="#8b949e" />
                      <YAxis yAxisId="left" stroke="#8b949e" />
                      <YAxis yAxisId="right" orientation="right" stroke="#8b949e" />
                      <Tooltip
                        contentStyle={{
                          backgroundColor: '#21262d',
                          border: '1px solid #30363d',
                        }}
                      />
                      <Line
                        yAxisId="left"
                        type="monotone"
                        dataKey="count"
                        stroke="#4CAF50"
                        name="Applications"
                      />
                      <Line
                        yAxisId="right"
                        type="monotone"
                        dataKey="total_value"
                        stroke="#2196F3"
                        name="Value (₦)"
                      />
                    </LineChart>
                  </ResponsiveContainer>
                </div>
              </div>
            </div>
          </>
        )}

        {activeTab === 'applications' && (
          <>
            {/* Filters */}
            <div className="card mb-6">
              <h3 className="text-lg font-semibold text-dark-text mb-4">Filters</h3>
              <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-4 gap-4">
                <Input
                  label="Search"
                  placeholder="Name, email, company..."
                  value={filters.search}
                  onChange={(e) =>
                    setFilters((prev) => ({ ...prev, search: e.target.value }))
                  }
                />
                <Input
                  type="date"
                  label="Start Date"
                  value={filters.start_date}
                  onChange={(e) =>
                    setFilters((prev) => ({ ...prev, start_date: e.target.value }))
                  }
                />
                <Input
                  type="date"
                  label="End Date"
                  value={filters.end_date}
                  onChange={(e) =>
                    setFilters((prev) => ({ ...prev, end_date: e.target.value }))
                  }
                />
                <Input
                  type="number"
                  label="Min Value"
                  placeholder="₦0"
                  value={filters.min_value}
                  onChange={(e) =>
                    setFilters((prev) => ({ ...prev, min_value: e.target.value }))
                  }
                />
                <Input
                  type="number"
                  label="Max Value"
                  placeholder="₦50,000,000"
                  value={filters.max_value}
                  onChange={(e) =>
                    setFilters((prev) => ({ ...prev, max_value: e.target.value }))
                  }
                />
                <div>
                  <label className="label">Tenors</label>
                  <div className="flex gap-4">
                    {TENORS.map((tenor) => (
                      <Checkbox
                        key={tenor}
                        label={tenor}
                        checked={filters.tenors.includes(tenor)}
                        onChange={(e) => {
                          if (e.target.checked) {
                            setFilters((prev) => ({
                              ...prev,
                              tenors: [...prev.tenors, tenor],
                            }));
                          } else {
                            setFilters((prev) => ({
                              ...prev,
                              tenors: prev.tenors.filter((t) => t !== tenor),
                            }));
                          }
                        }}
                      />
                    ))}
                  </div>
                </div>
                <div>
                  <label className="label">Payment Status</label>
                  <div className="flex flex-wrap gap-3">
                    {PAYMENT_STATUSES.map((status) => (
                      <Checkbox
                        key={status.value}
                        label={status.label}
                        checked={filters.payment_statuses.includes(status.value)}
                        onChange={(e) => {
                          if (e.target.checked) {
                            setFilters((prev) => ({
                              ...prev,
                              payment_statuses: [...prev.payment_statuses, status.value],
                            }));
                          } else {
                            setFilters((prev) => ({
                              ...prev,
                              payment_statuses: prev.payment_statuses.filter((s) => s !== status.value),
                            }));
                          }
                        }}
                      />
                    ))}
                  </div>
                </div>
              </div>
              <div className="flex gap-4 mt-4">
                <Button variant="primary" onClick={handleSearch}>
                  Search
                </Button>
                <Button variant="secondary" onClick={handleExportCsv}>
                  Export CSV
                </Button>
                <Button variant="secondary" onClick={handleExportExcel}>
                  Export Excel
                </Button>
              </div>
            </div>

            {/* Applications Table */}
            <div className="card overflow-hidden">
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="border-b border-dark-border">
                      <th className="text-left p-3 text-sm font-medium text-dark-text-secondary">
                        ID
                      </th>
                      <th className="text-left p-3 text-sm font-medium text-dark-text-secondary">
                        Date
                      </th>
                      <th className="text-left p-3 text-sm font-medium text-dark-text-secondary">
                        Name/Company
                      </th>
                      <th className="text-left p-3 text-sm font-medium text-dark-text-secondary">
                        Type
                      </th>
                      <th className="text-left p-3 text-sm font-medium text-dark-text-secondary">
                        Tenor
                      </th>
                      <th className="text-right p-3 text-sm font-medium text-dark-text-secondary">
                        Value
                      </th>
                      <th className="text-left p-3 text-sm font-medium text-dark-text-secondary">
                        Payment
                      </th>
                    </tr>
                  </thead>
                  <tbody>
                    {isLoading ? (
                      <tr>
                        <td colSpan={7} className="p-8 text-center text-dark-text-secondary">
                          Loading...
                        </td>
                      </tr>
                    ) : applications.length === 0 ? (
                      <tr>
                        <td colSpan={7} className="p-8 text-center text-dark-text-secondary">
                          No applications found
                        </td>
                      </tr>
                    ) : (
                      applications.map((app) => {
                        const paymentStatusConfig = PAYMENT_STATUSES.find(s => s.value === app.payment_status) || PAYMENT_STATUSES[0];
                        return (
                          <tr
                            key={app.id}
                            className="border-b border-dark-border/50 hover:bg-dark-elevated/50 cursor-pointer"
                            onClick={() => setSelectedApplicationId(app.id)}
                          >
                            <td className="p-3 text-sm text-dark-text">#{app.id}</td>
                            <td className="p-3 text-sm text-dark-text">
                              {new Date(app.submission_date.replace(/ [A-Z]{3,4}$/, '')).toLocaleDateString()}
                            </td>
                            <td className="p-3 text-sm text-dark-text">
                              {app.full_name || app.company_name || '-'}
                            </td>
                            <td className="p-3 text-sm">
                              <span
                                className={`px-2 py-1 rounded text-xs font-medium ${
                                  app.applicant_type === 'Individual'
                                    ? 'bg-blue-900/30 text-blue-400'
                                    : app.applicant_type === 'Joint'
                                    ? 'bg-purple-900/30 text-purple-400'
                                    : 'bg-orange-900/30 text-orange-400'
                                }`}
                              >
                                {app.applicant_type}
                              </span>
                            </td>
                            <td className="p-3 text-sm text-dark-text">{app.tenor}</td>
                            <td className="p-3 text-sm text-dark-text text-right">
                              {formatCurrency(app.bond_value)}
                            </td>
                            <td className="p-3 text-sm">
                              <span
                                className={`px-2 py-1 rounded text-xs font-medium ${paymentStatusConfig.color}`}
                              >
                                {paymentStatusConfig.label}
                              </span>
                            </td>
                          </tr>
                        );
                      })
                    )}
                  </tbody>
                </table>
              </div>

              {/* Pagination */}
              {totalPages > 1 && (
                <div className="flex items-center justify-between p-4 border-t border-dark-border">
                  <span className="text-sm text-dark-text-secondary">
                    Page {filters.page} of {totalPages}
                  </span>
                  <div className="flex gap-2">
                    <Button
                      variant="secondary"
                      size="sm"
                      onClick={() =>
                        setFilters((prev) => ({ ...prev, page: prev.page - 1 }))
                      }
                      disabled={filters.page === 1}
                    >
                      Previous
                    </Button>
                    <Button
                      variant="secondary"
                      size="sm"
                      onClick={() =>
                        setFilters((prev) => ({ ...prev, page: prev.page + 1 }))
                      }
                      disabled={filters.page === totalPages}
                    >
                      Next
                    </Button>
                  </div>
                </div>
              )}
            </div>
          </>
        )}

        {activeTab === 'reports' && (
          <>
            {/* Month/Year Selector */}
            <div className="card mb-6">
              <div className="flex flex-wrap items-end gap-4">
                <Select
                  label="Month of Offer"
                  options={MONTHS.map((m) => ({ value: m, label: m }))}
                  value={reportMonth}
                  onChange={(e) => setReportMonth(e.target.value)}
                />
                <Select
                  label="Year"
                  options={[
                    { value: String(new Date().getFullYear() - 1), label: String(new Date().getFullYear() - 1) },
                    { value: String(new Date().getFullYear()), label: String(new Date().getFullYear()) },
                    { value: String(new Date().getFullYear() + 1), label: String(new Date().getFullYear() + 1) },
                  ]}
                  value={String(reportYear)}
                  onChange={(e) => setReportYear(parseInt(e.target.value))}
                />
                <Button variant="primary" onClick={fetchReportData}>
                  Refresh
                </Button>
              </div>
            </div>

            {isLoadingReport ? (
              <div className="flex items-center justify-center py-12">
                <div className="animate-spin w-8 h-8 border-4 border-primary-500 border-t-transparent rounded-full" />
              </div>
            ) : reportSummary ? (
              <>
                {/* Summary Stats */}
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
                  <div className="card">
                    <h3 className="text-sm text-dark-text-secondary">Total Applications</h3>
                    <p className="text-2xl font-bold text-dark-text mt-1">
                      {reportSummary.total_applications}
                    </p>
                  </div>
                  <div className="card">
                    <h3 className="text-sm text-dark-text-secondary">Total Value</h3>
                    <p className="text-2xl font-bold text-primary-500 mt-1">
                      {formatCurrency(reportSummary.total_value)}
                    </p>
                  </div>
                  <div className="card">
                    <h3 className="text-sm text-dark-text-secondary">Verified</h3>
                    <p className="text-2xl font-bold text-green-400 mt-1">
                      {reportSummary.verified_count} ({formatCurrency(reportSummary.verified_value)})
                    </p>
                  </div>
                  <div className="card">
                    <h3 className="text-sm text-dark-text-secondary">Status</h3>
                    <p className={`text-xl font-bold mt-1 ${reportSummary.is_submitted ? 'text-green-400' : 'text-yellow-400'}`}>
                      {reportSummary.is_submitted ? 'Submitted to DMO' : 'Not Submitted'}
                    </p>
                  </div>
                </div>

                {/* Breakdown */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
                  <div className="card">
                    <h3 className="text-lg font-semibold text-dark-text mb-4">By Tenor</h3>
                    <div className="space-y-3">
                      <div className="flex justify-between items-center">
                        <span className="text-dark-text-secondary">2-Year Bonds</span>
                        <span className="text-dark-text">
                          {reportSummary.total_2year} apps ({formatCurrency(reportSummary.value_2year)})
                        </span>
                      </div>
                      <div className="flex justify-between items-center">
                        <span className="text-dark-text-secondary">3-Year Bonds</span>
                        <span className="text-dark-text">
                          {reportSummary.total_3year} apps ({formatCurrency(reportSummary.value_3year)})
                        </span>
                      </div>
                    </div>
                  </div>

                  <div className="card">
                    <h3 className="text-lg font-semibold text-dark-text mb-4">By Applicant Type</h3>
                    <div className="space-y-3">
                      <div className="flex justify-between items-center">
                        <span className="text-dark-text-secondary">Individual</span>
                        <span className="text-dark-text">{reportSummary.total_individual}</span>
                      </div>
                      <div className="flex justify-between items-center">
                        <span className="text-dark-text-secondary">Joint</span>
                        <span className="text-dark-text">{reportSummary.total_joint}</span>
                      </div>
                      <div className="flex justify-between items-center">
                        <span className="text-dark-text-secondary">Corporate</span>
                        <span className="text-dark-text">{reportSummary.total_corporate}</span>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Payment Status Breakdown */}
                <div className="card mb-6">
                  <h3 className="text-lg font-semibold text-dark-text mb-4">Payment Status</h3>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    <div className="bg-dark-elevated rounded-lg p-4">
                      <p className="text-xs text-dark-text-secondary">Pending</p>
                      <p className="text-lg font-semibold text-gray-400">{reportSummary.pending_count}</p>
                      <p className="text-sm text-dark-text-secondary">{formatCurrency(reportSummary.pending_value)}</p>
                    </div>
                    <div className="bg-dark-elevated rounded-lg p-4">
                      <p className="text-xs text-dark-text-secondary">Paid</p>
                      <p className="text-lg font-semibold text-yellow-400">{reportSummary.paid_count}</p>
                      <p className="text-sm text-dark-text-secondary">{formatCurrency(reportSummary.paid_value)}</p>
                    </div>
                    <div className="bg-dark-elevated rounded-lg p-4">
                      <p className="text-xs text-dark-text-secondary">Verified</p>
                      <p className="text-lg font-semibold text-green-400">{reportSummary.verified_count}</p>
                      <p className="text-sm text-dark-text-secondary">{formatCurrency(reportSummary.verified_value)}</p>
                    </div>
                    <div className="bg-dark-elevated rounded-lg p-4">
                      <p className="text-xs text-dark-text-secondary">Rejected</p>
                      <p className="text-lg font-semibold text-red-400">{reportSummary.rejected_count}</p>
                      <p className="text-sm text-dark-text-secondary">{formatCurrency(reportSummary.rejected_value)}</p>
                    </div>
                  </div>
                </div>

                {/* Actions */}
                <div className="card mb-6">
                  <h3 className="text-lg font-semibold text-dark-text mb-4">Actions</h3>
                  <div className="flex flex-wrap gap-4">
                    <Button variant="primary" onClick={handleExportDmoReport}>
                      Export DMO Report (Excel)
                    </Button>
                    {!reportSummary.is_submitted && reportSummary.verified_count > 0 && (
                      <Button variant="secondary" onClick={handleMarkAsSubmitted}>
                        Mark as Submitted to DMO
                      </Button>
                    )}
                  </div>
                  {reportSummary.is_submitted && reportSummary.submitted_at && (
                    <p className="text-sm text-dark-text-secondary mt-3">
                      Submitted on: {new Date(reportSummary.submitted_at).toLocaleString()}
                    </p>
                  )}
                </div>

                {/* Submission History */}
                <div className="card">
                  <h3 className="text-lg font-semibold text-dark-text mb-4">Submission History</h3>
                  {submissions.length > 0 ? (
                    <div className="overflow-x-auto">
                      <table className="w-full">
                        <thead>
                          <tr className="border-b border-dark-border">
                            <th className="text-left p-3 text-sm font-medium text-dark-text-secondary">Month</th>
                            <th className="text-left p-3 text-sm font-medium text-dark-text-secondary">Year</th>
                            <th className="text-right p-3 text-sm font-medium text-dark-text-secondary">Applications</th>
                            <th className="text-right p-3 text-sm font-medium text-dark-text-secondary">Total Value</th>
                            <th className="text-left p-3 text-sm font-medium text-dark-text-secondary">Submitted</th>
                            <th className="text-left p-3 text-sm font-medium text-dark-text-secondary">Notes</th>
                          </tr>
                        </thead>
                        <tbody>
                          {submissions.map((sub) => (
                            <tr key={sub.id} className="border-b border-dark-border/50">
                              <td className="p-3 text-sm text-dark-text">{sub.month_of_offer}</td>
                              <td className="p-3 text-sm text-dark-text">{sub.year}</td>
                              <td className="p-3 text-sm text-dark-text text-right">{sub.total_applications}</td>
                              <td className="p-3 text-sm text-dark-text text-right">{formatCurrency(sub.total_value)}</td>
                              <td className="p-3 text-sm text-dark-text">
                                {new Date(sub.submitted_at).toLocaleDateString()}
                              </td>
                              <td className="p-3 text-sm text-dark-text-secondary">{sub.notes || '-'}</td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  ) : (
                    <p className="text-dark-text-secondary text-center py-4">No submissions yet</p>
                  )}
                </div>
              </>
            ) : (
              <div className="card text-center py-12">
                <p className="text-dark-text-secondary">No data for selected period</p>
              </div>
            )}
          </>
        )}
      </main>

      {/* Application Detail Modal */}
      {selectedApplicationId && (
        <ApplicationDetailModal
          applicationId={selectedApplicationId}
          onClose={() => setSelectedApplicationId(null)}
          onPaymentUpdated={() => {
            fetchData();
          }}
        />
      )}
    </div>
  );
}

// Summary card component
function SummaryCard({
  title,
  value,
  icon,
}: {
  title: string;
  value: string;
  icon: string;
}) {
  return (
    <div className="card">
      <div className="flex items-center justify-between mb-2">
        <span className="text-2xl">{icon}</span>
      </div>
      <h3 className="text-sm text-dark-text-secondary">{title}</h3>
      <p className="text-2xl font-bold text-dark-text mt-1">{value}</p>
    </div>
  );
}
