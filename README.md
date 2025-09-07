# Web Scraper Project

## 📌 Overview
This project consists of:
- **Backend**: Flask API that scrapes websites for emails, phone numbers, and social media links.
- **Frontend**: React + Vite + Tailwind app to interact with the API.

## 🚀 Backend Setup (Flask)
1. Navigate to backend folder:
   ```bash
   cd backend
   ```
2. Create a virtual environment and install dependencies:
   ```bash
   python -m venv venv
   source venv/bin/activate  # or venv\Scripts\activate on Windows
   pip install -r requirements.txt
   ```
3. Set environment variables:
   ```bash
   export API_KEY=your_api_key_here
   export LOGTAIL_SOURCE_TOKEN=your_logtail_source_token
   ```
4. Run locally:
   ```bash
   python app.py
   ```

### Render Deployment
- Push repo to GitHub
- Create new Web Service in Render
- Add environment variables in dashboard:
  - `API_KEY`
  - `LOGTAIL_SOURCE_TOKEN`
- Render auto-detects `requirements.txt` and `Procfile`

---

## 🎨 Frontend Setup (React + Vite)
1. Navigate to frontend folder:
   ```bash
   cd frontend
   ```
2. Install dependencies:
   ```bash
   npm install
   ```
3. Create `.env` file:
   ```
   VITE_API_URL=https://your-backend-service.onrender.com
   VITE_API_KEY=your_api_key_here
   ```
4. Run locally:
   ```bash
   npm run dev
   ```

### Deploy Frontend
- Build the app:
  ```bash
  npm run build
  ```
- Deploy `dist/` folder to Netlify, Vercel, or Render static site hosting.

---

## ✅ Summary
- Flask backend with Logtail logging
- React + Vite + Tailwind frontend
- Ready for deployment on Render + Netlify/Vercel
