import { useQuery } from "@tanstack/react-query";
import { Card, CardContent, CardHeader } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { Calendar, MapPin, Plus, FileText, ArrowLeft, Image as ImageIcon, AlertTriangle, LogIn } from "lucide-react";
import { useNavigate } from "react-router-dom";
import Layout from "@/components/Layout";
import { fetchReports } from "@/lib/api";
import type { Report } from "@/types";

const MyReports = () => {
  const navigate = useNavigate();

  // Check if user is authenticated
  const token = localStorage.getItem('authToken');
  
  // Use React Query to fetch, cache, and manage the state of your reports
  const { data: reports, isLoading, isError, error } = useQuery({
    queryKey: ['userReports'], // A unique key for this data
    queryFn: fetchReports,    // The function that fetches the data
    enabled: !!token, // Only run query if user is authenticated
  });

  // Check authentication first
  if (!token) {
    return (
      <Layout>
        <div className="min-h-[60vh] flex items-center justify-center">
          <Card className="w-full max-w-md">
            <CardContent className="flex flex-col items-center justify-center py-12">
              <LogIn className="h-12 w-12 text-muted-foreground mb-4" />
              <h3 className="text-lg font-semibold mb-2">Login Required</h3>
              <p className="text-muted-foreground text-center mb-4">
                Please log in to view your reports.
              </p>
              <Button onClick={() => navigate('/login')} className="flex items-center space-x-2">
                <LogIn className="h-4 w-4" />
                <span>Go to Login</span>
              </Button>
            </CardContent>
          </Card>
        </div>
      </Layout>
    );
  }

  const getStatusBadge = (status: Report['status']) => {
    switch (status) {
      case 'Pending':
        return <Badge className="status-badge status-pending">Pending</Badge>;
      case 'In Progress':
        return <Badge className="status-badge status-in-progress">In Progress</Badge>;
      case 'Resolved':
        return <Badge className="status-badge status-resolved">Resolved</Badge>;
      default:
        return <Badge variant="outline">{status}</Badge>;
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric', month: 'long', day: 'numeric',
      hour: '2-digit', minute: '2-digit'
    });
  };

  // This function now uses the fetched data
  const getStatusCount = (status: Report['status']) => {
    if (isLoading || !reports) return <Skeleton className="h-6 w-8 inline-block" />;
    return reports.filter(report => report.status === status).length;
  };

  const renderReportList = () => {
    if (isLoading) {
      return (
        <div className="space-y-4">
          {[...Array(3)].map((_, i) => (
            <Card key={i}>
              <CardHeader><Skeleton className="h-6 w-1/4" /></CardHeader>
              <CardContent className="space-y-2">
                <Skeleton className="h-4 w-full" />
                <Skeleton className="h-4 w-3/4" />
              </CardContent>
            </Card>
          ))}
        </div>
      );
    }

    if (isError) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to load reports';
      const isAuthError = errorMessage.includes('Authentication failed');
      
      return (
        <Card>
          <CardContent className="flex flex-col items-center justify-center py-12">
            <AlertTriangle className="h-12 w-12 text-destructive mb-4" />
            <h3 className="text-lg font-semibold mb-2">
              {isAuthError ? 'Authentication Required' : 'Failed to load reports'}
            </h3>
            <p className="text-muted-foreground text-center mb-4">
              {isAuthError ? 'Please log in again to view your reports.' : errorMessage}
            </p>
            <div className="flex gap-2">
              {isAuthError ? (
                <Button onClick={() => navigate('/login')} className="flex items-center space-x-2">
                  <LogIn className="h-4 w-4" />
                  <span>Go to Login</span>
                </Button>
              ) : (
                <Button onClick={() => window.location.reload()} className="flex items-center space-x-2">
                  <ArrowLeft className="h-4 w-4" />
                  <span>Refresh Page</span>
                </Button>
              )}
            </div>
          </CardContent>
        </Card>
      );
    }

    if (!reports || reports.length === 0) {
      return (
        <Card>
          <CardContent className="flex flex-col items-center justify-center py-12">
            <FileText className="h-12 w-12 text-muted-foreground mb-4" />
            <h3 className="text-lg font-semibold mb-2">No Reports Yet</h3>
            <p className="text-muted-foreground text-center mb-4">
              You haven't submitted any reports yet. Start by reporting your first civic issue.
            </p>
            <Button onClick={() => navigate('/report')}>
              <Plus className="h-4 w-4 mr-2" />
              Report Your First Issue
            </Button>
          </CardContent>
        </Card>
      );
    }

    return (
      <div className="space-y-4">
        {reports.map((report) => (
          <Card key={report.id} className="transition-shadow hover:shadow-md">
            <CardHeader className="pb-4">
              <div className="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-3">
                <div className="flex items-center space-x-3">
                  {getStatusBadge(report.status)}
                  <div className="flex items-center text-sm text-muted-foreground">
                    <Calendar className="h-4 w-4 mr-1" />
                    <span>Submitted {formatDate(report.submittedDate)}</span>
                  </div>
                </div>
                {report.imageUrl && (
                  <div className="flex items-center text-sm text-muted-foreground">
                    <ImageIcon className="h-4 w-4 mr-1" />
                    <span>Photo attached</span>
                  </div>
                )}
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <p className="text-sm leading-relaxed">{report.description}</p>
                <div className="flex items-center justify-between pt-3 border-t">
                  <div className="flex items-center text-xs text-muted-foreground">
                    <MapPin className="h-3 w-3 mr-1" />
                    <span>
                      {report.location && report.location.latitude && report.location.longitude
                        ? `${report.location.latitude.toFixed(4)}, ${report.location.longitude.toFixed(4)}`
                        : 'Location not available'
                      }
                    </span>
                  </div>
                  <div className="text-xs text-muted-foreground">
                    Report ID: {report.id}
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    );
  };

  return (
    <Layout>
      <div className="space-y-6">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <div>
            <Button
              variant="ghost"
              onClick={() => navigate('/home')}
              className="flex items-center space-x-2 mb-4"
            >
              <ArrowLeft className="h-4 w-4" />
              <span>Back to Home</span>
            </Button>
            <h1 className="text-3xl font-bold">My Reports</h1>
            <p className="text-muted-foreground mt-2">
              Track the status of all your submitted civic issue reports
            </p>
          </div>
          <Button
            onClick={() => navigate('/report')}
            className="flex items-center space-x-2"
          >
            <Plus className="h-4 w-4" />
            <span>Report New Issue</span>
          </Button>
        </div>

        {/* Status Summary */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <Card>
            <CardContent className="flex items-center justify-between p-6">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Pending</p>
                <div className="text-2xl font-bold text-primary">{getStatusCount('Pending')}</div>
              </div>
              <div className="p-2 bg-primary/10 rounded-full">
                <FileText className="h-6 w-6 text-primary" />
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="flex items-center justify-between p-6">
              <div>
                <p className="text-sm font-medium text-muted-foreground">In Progress</p>
                <div className="text-2xl font-bold text-warning">{getStatusCount('In Progress')}</div>
              </div>
              <div className="p-2 bg-warning/10 rounded-full">
                <FileText className="h-6 w-6 text-warning" />
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="flex items-center justify-between p-6">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Resolved</p>
                <div className="text-2xl font-bold text-success">{getStatusCount('Resolved')}</div>
              </div>
              <div className="p-2 bg-success/10 rounded-full">
                <FileText className="h-6 w-6 text-success" />
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Reports List */}
        {renderReportList()}
      </div>
    </Layout>
  );
};

export default MyReports;