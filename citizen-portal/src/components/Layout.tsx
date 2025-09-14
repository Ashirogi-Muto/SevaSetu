import { ReactNode } from "react";
import { Button } from "@/components/ui/button";
import { MapPin, User, FileText, LogOut } from "lucide-react";
import { useNavigate, useLocation } from "react-router-dom";

interface LayoutProps {
  children: ReactNode;
  showHeader?: boolean;
}

const Layout = ({ children, showHeader = true }: LayoutProps) => {
  const navigate = useNavigate();
  const location = useLocation();

  const isAuthenticated = !location.pathname.includes('/login') && !location.pathname.includes('/signup');

  const handleLogout = () => {
    // Clear authentication token
    localStorage.removeItem('authToken');
    navigate('/login'); // Navigate to login page on logout
  };

  return (
    <div className="min-h-screen bg-background">
      {showHeader && (
        <header className="border-b bg-card shadow-sm">
          <div className="container mx-auto px-4 py-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <img src="/favicon-32x32.png" alt="SEWASETU Logo" className="h-8 w-8" />
                <div>
                  <h1 className="text-xl font-bold text-foreground">SEWASETU</h1>
                  <p className="text-sm text-muted-foreground">Citizen Portal</p>
                </div>
              </div>

              {isAuthenticated && (
                <nav className="flex items-center space-x-4">
                  <Button
                    variant={location.pathname === '/home' ? 'default' : 'ghost'}
                    onClick={() => navigate('/home')} // Navigate to /home
                    className="flex items-center space-x-2"
                  >
                    <MapPin className="h-4 w-4" />
                    <span>Home</span>
                  </Button>
                  <Button
                    variant={location.pathname === '/my-reports' ? 'default' : 'ghost'}
                    onClick={() => navigate('/my-reports')}
                    className="flex items-center space-x-2"
                  >
                    <FileText className="h-4 w-4" />
                    <span>My Reports</span>
                  </Button>
                  <Button
                    variant="ghost"
                    onClick={handleLogout}
                    className="flex items-center space-x-2 text-destructive hover:text-destructive"
                  >
                    <LogOut className="h-4 w-4" />
                    <span>Logout</span>
                  </Button>
                </nav>
              )}
            </div>
          </div>
        </header>
      )}

      <main className="container mx-auto px-4 py-8">
        {children}
      </main>
    </div>
  );
};

export default Layout;