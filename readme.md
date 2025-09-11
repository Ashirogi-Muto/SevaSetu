# AI-Powered Civic Issue Reporting Platform

![Status](https://img.shields.io/badge/Status-Backend%20MVP%20Complete-brightgreen)
![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.116-blue?logo=fastapi)
![TensorFlow](https://img.shields.io/badge/TensorFlow-2.16-orange?logo=tensorflow)
![Supabase](https://img.shields.io/badge/Supabase-PostgreSQL-green?logo=supabase)

This repository contains the complete backend source code for the AI-Powered Civic Issue Reporting Platform. The system is designed to allow citizens to report issues, have them automatically classified by a real AI model, and routed to the correct municipal department.

## 🏛️ Project Architecture

The backend is built on a modern microservice architecture to ensure scalability and a clear separation of concerns. This is a professional setup that allows the core application and the AI model to be developed and deployed independently.



[Image of a microservice architecture diagram]


1.  **Main Backend API (Port 8000):** A robust FastAPI server responsible for handling all client requests, managing data in the PostgreSQL database, handling image uploads to Supabase Storage, and providing analytics.
2.  **AI Model Server (Port 8001):** A dedicated FastAPI server that hosts a real TensorFlow/Keras computer vision model (MobileNetV2). It exposes a single, specialized endpoint for classifying images.

---

## 💻 Technology Stack

### Main Backend API (`/backend`)
* **Framework:** Python 3.11+ with FastAPI
* **Database:** PostgreSQL (managed by Supabase)
* **Storage:** Supabase Storage for image uploads
* **Security:** API Key authentication for protected endpoints
* **Features:** Data validation (Enums), pagination, and filtering

### AI Model Server (`/ai_model_server`)
* **Framework:** Python 3.11+ with FastAPI
* **Machine Learning Library:** TensorFlow & Keras
* **Core Model:** MobileNetV2 (pre-trained on ImageNet)

---

## 🚀 Getting Started

Follow these instructions to get both backend services running on your local machine. **You will need two separate terminals.**

### Prerequisites
* Python 3.10+
* Git
* A Supabase account

### Step 1: Main Backend API (Terminal 1)

1.  **Navigate & Setup Environment:**
    ```bash
    cd F:\hackathon\backend
    python -m venv venv
    venv\Scripts\activate
    pip install -r requirements.txt
    ```
2.  **Configure Environment Variables:** Create a `.env` file in the `backend` folder and add your credentials:
    ```
    SUPABASE_URL=[https://your-project-url.supabase.co](https://your-project-url.supabase.co)
    SUPABASE_KEY=your-supabase-anon-key
    API_SECRET_KEY=a-very-secret-and-random-key-that-no-one-can-guess-12345
    AI_API_URL=[http://127.0.0.1:8001/api/classify](http://127.0.0.1:8001/api/classify)
    ```
3.  **Run the Server (Port 8000):**
    ```bash
    python -m uvicorn main:app --reload --port 8000
    ```
    *Keep this terminal running.*

### Step 2: AI Model Server (Terminal 2)

1.  **Navigate & Setup Environment:**
    ```bash
    # Open a NEW terminal
    cd F:\hackathon\ai_model_server
    python -m venv venv
    venv\Scripts\activate
    pip install -r requirements.txt
    ```
2.  **Run the Server (Port 8001):**
    ```bash
    python -m uvicorn main:app --reload --port 8001
    ```
    *The first time you run this, it will download the MobileNetV2 model. Keep this terminal running.*

---

## 🗺️ API Endpoints Overview

With both servers running, interact with the main backend at `http://127.0.0.1:8000`.

| Method | Endpoint                     | Description                                            | Secured? |
| :----- | :--------------------------- | :----------------------------------------------------- | :------- |
| `POST` | `/api/reports/`              | Submits a new report with images.                      | **Yes** |
| `GET`  | `/api/reports/`              | Retrieves a paginated and filterable list of reports.  | No       |
| `PUT`  | `/api/reports/{id}/status`   | Updates the status of a specific report.               | **Yes** |
| `GET`  | `/api/analytics/`            | Gets summary statistics for the admin dashboard.       | No       |

* **Interactive Docs:** [**http://127.0.0.1:8000/docs**](http://127.0.0.1:8000/docs)
* **Demo Map:** Open the `backend/admin_map.html` file in your browser.

---

## 🛣️ Project Roadmap

The backend is currently **feature-complete for the MVP demo**. The next major steps for the project are:

-   **Frontend Development:** Building the citizen reporting portal and a full admin dashboard in Next.js.
-   **AI Model Refinement:** The AI teammate will fine-tune the model and add the "translation layer" in `ai_model_server/main.py`.
-   **Deployment:** Deploying the backend services to a cloud host (e.g., Railway/Render) and setting up a CI/CD pipeline with GitHub Actions.