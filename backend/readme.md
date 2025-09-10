AI-Powered Civic Issue Reporting Platform - Backend Setup
This guide provides detailed, step-by-step instructions to set up and run the initial FastAPI backend for our project.

Prerequisites
Before you begin, ensure you have Python 3.7 or newer installed on your system. You can check your Python version by running this command in your terminal:

python --version
# or
python3 --version

Step 1: Set Up Your Project Directory
First, create a dedicated folder for your backend project and navigate into it.

# Create a new directory for the project
mkdir civic-reporting-api

# Move into the newly created directory
cd civic-reporting-api

Place the main.py and requirements.txt files you received into this civic-reporting-api folder.

Step 2: Create and Activate a Virtual Environment
It's a best practice to use a virtual environment for every Python project. This isolates the project's dependencies from your global Python installation.

# Create a virtual environment named 'venv'
python3 -m venv venv

# Activate the virtual environment
# On macOS and Linux:
source venv/bin/activate

# On Windows (Command Prompt):
venv\Scripts\activate

After activation, you will see (venv) at the beginning of your terminal prompt. This indicates that the virtual environment is active.

Step 3: Install the Required Packages
Now, we'll install the packages listed in the requirements.txt file using pip, Python's package installer.

# The '-r' flag tells pip to install from a requirements file
pip install -r requirements.txt

This will install FastAPI, Uvicorn (our server), and Pydantic.

Step 4: Run the Development Server
With the dependencies installed, you can now start the API server.

# Command to run the server
uvicorn main:app --reload

Let's break down this command:

uvicorn: The ASGI server we installed.

main: Refers to the main.py file.

app: Refers to the FastAPI() instance we created inside main.py.

--reload: This is a helpful flag for development. It automatically restarts the server whenever you save changes to your code.

After running the command, you should see output in your terminal indicating that the server is running, usually on http://127.0.0.1:8000.

Step 5: Test the API Endpoint
FastAPI provides free, interactive API documentation right out of the box. This is the best way to test our new endpoint.

Open your web browser and navigate to: http://127.0.0.1:8000/docs

You will see the Swagger UI documentation. Find the POST /api/reports endpoint and click on it to expand it.

Click the "Try it out" button on the right. This will make the "Request body" editable.

You can now change the example JSON data. For instance, you could report a broken streetlight:

{
  "description": "The streetlight at the corner of Oak and Maple street is flickering and seems broken.",
  "latitude": 34.0522,
  "longitude": -118.2437,
  "category": "Broken Streetlight"
}

Click the blue "Execute" button.

Step 6: Check the Results
In your browser: Scroll down, and you will see the server's response. A 201 Created status code means it was successful. The response body will contain the confirmation message and the data you sent.

In your terminal: Look at the terminal where the uvicorn server is running. You should see the report details printed to the console, just as we programmed in main.py!

--- New Report Received ---
Description: The streetlight at the corner of Oak and Maple street is flickering and seems broken.
Location: (Lat: 34.0522, Lon: -118.2437)
Category: Broken Streetlight
--------------------------

Congratulations! You now have a working, validated API endpoint. This is the perfect foundation for our next steps.

Our next goal will be to connect this endpoint to a Supabase PostgreSQL database so we can persist the reports that are submitted. Let me know when you're ready to tackle that!