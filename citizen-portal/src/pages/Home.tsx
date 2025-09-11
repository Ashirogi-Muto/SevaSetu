import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Plus, MapPin, Calendar, AlertCircle } from "lucide-react";
import { useNavigate } from "react-router-dom";
import Layout from "@/components/Layout";
import ReportsMap from "@/components/Map"; // Import the new map component

// This mock data is still used for the "Recent Reports" section.
const mockReports = [
  {
    id: "1",
    description: "Broken streetlight on Main Street causing safety concerns",
    status: "Pending" as const,
    submittedDate: "2024-01-15T10:30:00Z",
    location: { latitude: 40.7128, longitude: -74.0060 }
  },
  {
    id: "2", 
    description: "Pothole near City Hall intersection affecting traffic",
    status: "In Progress" as const,
    submittedDate: "2024-01-12T14:15:00Z",
    location: { latitude: 40.7589, longitude: -73.9851 }
  },
  {
    id: "3",
    description: "Damaged park bench in Central Park needs repair",
    status: "Resolved" as const,
    submittedDate: "2024-01-10T09:45:00Z",
    location: { latitude: 40.7812, longitude: -73.9665 }
  }
];

const Home = () => {
  const navigate = useNavigate();

  const getStatusBadge = (status: string) => {
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
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  };

  return (
    <Layout>
      <div className="space-y-8">
        {/* Hero Banner */}
        <section className="gov-banner rounded-lg p-8 text-center">
          <h1 className="mb-4 text-4xl font-bold">Report Civic Issues in Your City</h1>
          <p className="mb-6 text-lg opacity-90">
            Help improve your community by reporting infrastructure problems, safety concerns, and public service issues.
          </p>
          <Button
            size="lg"
            variant="secondary"
            onClick={() => navigate('/report')}
            className="flex items-center space-x-2 bg-secondary text-secondary-foreground hover:bg-secondary/90"
          >
            <Plus className="h-5 w-5" />
            <span>Report an Issue</span>
          </Button>
        </section>

        {/* Replace the old map placeholder with the new ReportsMap component */}
        <section className="h-96 rounded-lg overflow-hidden shadow-md border">
          <ReportsMap />
        </section>

        {/* Recent Reports */}
        <section>
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-2xl font-semibold">Recent Reports</h2>
            <Button
              variant="outline"
              onClick={() => navigate('/my-reports')}
              className="flex items-center space-x-2"
            >
              <AlertCircle className="h-4 w-4" />
              <span>View All Reports</span>
            </Button>
          </div>
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
              {mockReports.slice(0, 3).map((report) => (
                <Card key={report.id} className="transition-shadow hover:shadow-md">
                  <CardContent className="pt-6">
                    <div className="flex items-start justify-between mb-2">
                        {getStatusBadge(report.status)}
                        <div className="flex items-center text-sm text-muted-foreground">
                          <Calendar className="h-4 w-4 mr-1" />
                          {formatDate(report.submittedDate)}
                        </div>
                      </div>
                    <p className="text-sm leading-relaxed font-medium">{report.description}</p>
                    <div className="mt-3 flex items-center text-xs text-muted-foreground">
                      <MapPin className="h-3 w-3 mr-1" />
                      <span>
                        {report.location.latitude.toFixed(4)}, {report.location.longitude.toFixed(4)}
                      </span>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
        </section>
      </div>
    </Layout>
  );
};

export default Home;