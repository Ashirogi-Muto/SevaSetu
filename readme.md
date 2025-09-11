# AI-Powered Civic Issue Reporting & Resolution Platform

This repository contains the complete source code for the AI-Powered Civic Issue Reporting Platform, a full-stack application designed to streamline the process of reporting, classifying, and resolving municipal issues.

## Project Architecture

The backend is built on a modern microservice architecture to ensure scalability and separation of concerns:

1.  **Main Backend API (on Port 8000):** A robust FastAPI server responsible for handling all user requests, managing data in the database, storing images, and providing analytics.
2.  **AI Model Server (on Port 8001):** A dedicated FastAPI server that hosts the real TensorFlow/Keras computer vision model (MobileNetV2). It exposes a single endpoint for classifying images, allowing the AI logic to be updated independently.



[Image of a microservice architecture diagram]


---

## Getting Started

Follow these instructions to get both backend services up and running on your local machine for development and testing.

### Prerequisites

* Python 3.10+
* Git
* A Supabase account for the database and file storage.

---

## 🚀 Step 1: Main Backend API Setup

This is the core application that manages all data.

1.  **Navigate to the Backend Directory:**
    Open your first terminal and navigate to the backend folder:
    ```bash
    cd F:\hackathon\backend
    ```

2.  **Create and Activate Virtual Environment:**
    ```bash
    # Create the environment
    python -m venv venv

    # Activate on Windows
    venv\Scripts\activate
    ```

3.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure Environment Variables:**
    Create a new file named `.env` in the `F:\hackathon\backend` directory. Copy the content below and fill in your actual credentials from Supabase.
    ```
    SUPABASE_URL=[https://your-project-url.supabase.co](https://your-project-url.supabase.co)
    SUPABASE_KEY=your-supabase-anon-key
    API_SECRET_KEY=a-very-secret-and-random-key-that-no-one-can-guess-12345
    AI_API_URL=[http://127.0.0.1:8001/api/classify](http://127.0.0.1:8001/api/classify)
    ```

5.  **Run the Server:**
    Your main backend will run on port **8000**.
    ```bash
    python -m uvicorn main:app --reload --port 8000
    ```
    Keep this terminal running.

---

## 🧠 Step 2: AI Model Server Setup

This service provides the intelligence for image classification.

1.  **Navigate to the AI Server Directory:**
    **Open a second, new terminal** and navigate to the AI server folder:
    ```bash
    cd F:\hackathon\ai_model_server
    ```

2.  **Create and Activate Virtual Environment:**
    ```bash
    # Create the environment
    python -m venv venv

    # Activate on Windows
    venv\Scripts\activate
    ```

3.  **Install Dependencies:**
    *Note: This step may take several minutes as TensorFlow is a large library.*
    ```bash
    pip install -r requirements.txt
    ```

4.  **Run the Server:**
    Your AI server will run on port **8001**.
    ```bash
    python -m uvicorn main:app --reload --port 8001
    ```
    The first time you run this, it will download the MobileNetV2 model weights. You will see "Model loaded successfully" when it's ready. Keep this second terminal running.

---

## 🧪 Testing the Application

With both servers running, you can now interact with the main backend API.

* **Interactive API Docs:** Open your browser to [**http://127.0.0.1:8000/docs**](http://127.0.0.1:8000/docs)
* **Admin Map:** Open the `admin_map.html` file in your browser to see a live map of all reported issues.

Remember to use the **Authorize** button in the docs and provide your `API_SECRET_KEY` to test the protected `POST` and `PUT` endpoints.

## 💻 Technology Stack

* **Backend API:** Python, FastAPI, API Key Security
* **AI Service:** Python, FastAPI, TensorFlow/Keras, MobileNetV2
* **Database & Storage:** PostgreSQL & File Storage via Supabase
* **Admin Map Demo:** HTML5, Leaflet.js, JavaScript