import type { Report } from "@/types";

// These types match the Zod schemas in your form components
type RegisterPayload = { name: string; email: string; password: string };
type LoginPayload = { email: string; password: string };
type ReportPayload = { description: string; latitude: number; longitude: number; file?: FileList };

const API_URL = import.meta.env.VITE_PUBLIC_API_URL || 'http://127.0.0.1:8000';

// A helper to get the JWT from local storage
const getToken = () => {
    return localStorage.getItem('authToken');
};

// --- Authentication Functions ---

export const registerUser = async (userData: RegisterPayload) => {
    const response = await fetch(`${API_URL}/api/auth/register`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(userData),
    });
    if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Registration failed');
    }
    return response.json();
};

export const loginUser = async (credentials: LoginPayload) => {
    const response = await fetch(`${API_URL}/api/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(credentials),
    });
    if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Login failed');
    }
    const data = await response.json();
    // Save the token to local storage for future requests
    if (data.access_token) {
        localStorage.setItem('authToken', data.access_token);
    }
    return data;
};

// --- Report Functions ---

export const fetchReports = async (): Promise<Report[]> => {
    const token = getToken();
    if (!token) {
        // Return empty array if not authenticated
        return []; 
    }

    try {
        const response = await fetch(`${API_URL}/api/reports`, {
            headers: {
                'Authorization': `Bearer ${token}`,
            },
        });

        if (!response.ok) {
            if (response.status === 401) {
                // Remove invalid token
                localStorage.removeItem('authToken');
                throw new Error('Authentication failed. Please log in again.');
            }
            throw new Error(`Failed to fetch reports: ${response.status}`);
        }
        
        const data = await response.json();
        
        // Validate and clean the data
        if (!Array.isArray(data)) {
            throw new Error('Invalid response format: expected array');
        }
        
        // Ensure each report has the required properties
        const validReports = data.map((report: any) => ({
            id: report.id || 'unknown',
            description: report.description || 'No description',
            status: ['Pending', 'In Progress', 'Resolved'].includes(report.status) 
                ? report.status 
                : 'Pending',
            submittedDate: report.submittedDate || new Date().toISOString(),
            imageUrl: report.imageUrl,
            location: report.location && 
                     typeof report.location.latitude === 'number' && 
                     typeof report.location.longitude === 'number'
                ? report.location 
                : undefined
        }));
        
        return validReports;
    } catch (error) {
        if (error instanceof Error) {
            throw error;
        }
        throw new Error('Network error: Failed to fetch reports');
    }
};

export const submitNewReport = async (values: ReportPayload) => {
    const token = getToken();
    if (!token) {
        throw new Error('You must be logged in to submit a report.');
    }

    const formData = new FormData();
    const reportDetails = {
      description: values.description,
      latitude: values.latitude,
      longitude: values.longitude,
    };
    formData.append('report_data_json', JSON.stringify(reportDetails));

    // The form gives a FileList, so we append the first file if it exists
    if (values.file && values.file.length > 0) {
        formData.append('images', values.file[0]);
    }

    const response = await fetch(`${API_URL}/api/reports`, {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${token}`,
            // NOTE: Do not set 'Content-Type' for multipart/form-data.
        },
        body: formData,
    });

    if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to submit report');
    }
    return response.json();
};

// --- Public Report Functions ---

// Fetches ALL reports for the public map view
export const fetchAllReports = async (): Promise<Report[]> => {
    // Note: We use the /all endpoint here
    const response = await fetch(`${API_URL}/api/reports/all`); 

    if (!response.ok) {
        throw new Error('Failed to fetch reports for map');
    }
    return response.json();
};