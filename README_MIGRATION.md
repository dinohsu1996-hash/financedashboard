# 🚀 Finance Dashboard Migration Guide

This project has been updated! It now uses **FastAPI** (Backend) and **Next.js** (Frontend).
Since you have another app on port 3000, we've configured the frontend to run on **port 3001**.

---

## 🛠️ Step 1: Setup the Backend (Python)

The backend powers the data and AI features.

1.  **Open a Terminal** and enter the backend folder:
    ```bash
    cd backend
    ```

2.  **Create a Virtual Environment** (Isolated Python space):
    ```bash
    # Windows
    python -m venv venv
    .\venv\Scripts\activate

    # Mac/Linux
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Install Libraries**:
    ```bash
    pip install -r requirements.txt
    playwright install chromium
    ```

4.  **Add API Keys**:
    Create a file named `.env` inside the `backend` folder and paste this (replace with your real keys):
    ```ini
    GEMINI_API_KEY=your_actual_gemini_key_here
    FRED_API_KEY=your_actual_fred_api_key_here
    ```

5.  **Start the Server**:
    ```bash
    uvicorn app.main:app --reload
    ```
    ✅ *Success if you see: "Uvicorn running on http://127.0.0.1:8000"*

---

## 💻 Step 2: Setup the Frontend (Website)

The frontend is what you see and interact with.

1.  **Open a New Terminal Window** (keep the backend running!) and enter the frontend folder:
    ```bash
    cd frontend
    ```

2.  **Install Dependencies**:
    ```bash
    npm install
    ```

3.  **Start the Website**:
    ```bash
    npm run dev
    ```
    ✅ *Success if you see: "Ready in ... on http://localhost:3001"*

---

## 🚀 Step 3: Open the Dashboard

Open your web browser and go to:
👉 **http://localhost:3001**

(Note: port is **3001**, not 3000)

---

## ❓ Troubleshooting

-   **"Failed to fetch" errors?**
    Make sure the **Backend** terminal is still running and shows no errors.
-   **Stock charts empty?**
    The app tries to connect to a local database first. If that fails, it uses Yahoo Finance. Check the backend terminal logs for details.
-   **Port 3001 already in use?**
    Edit `frontend/package.json` and change `-p 3001` to `-p 3002` (or any free port).
