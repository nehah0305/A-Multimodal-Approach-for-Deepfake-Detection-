# Deepfake Detection Dashboard (React + Flask)

This project is now fully converted to a React frontend (Vite) with a Flask backend API for video/audio upload.

## Stack

- Frontend: React 18 + Vite
- Backend: Flask
- API: REST endpoints under /api

## Project Structure

```
A-Multimodal-Approach-for-Deepfake-Detection-/
├── index.html
├── package.json
├── vite.config.js
├── src/
│   ├── App.jsx
│   ├── App.css
│   ├── main.jsx
│   └── index.css
├── app.py
├── requirements.txt
├── start-server.bat
├── API_DOCS.md
└── test_api.py
```

## Run Backend

1. Install Python dependencies:

```powershell
pip install -r requirements.txt
```

2. Start Flask API:

```powershell
python app.py
```

Backend runs at http://localhost:5000.

## Run Frontend

1. Install Node dependencies:

```powershell
npm install
```

2. Start React dev server:

```powershell
npm run dev
```

Frontend runs at http://localhost:5173.

## Environment (Optional)

To change API URL, set VITE_API_URL in a .env file:

```
VITE_API_URL=http://localhost:5000/api
```

## Features

- Separate video and audio upload zones
- File validation (format and max 100MB)
- Upload/delete via Flask API
- Simulated analysis result cards
- Downloadable report

## API

Core endpoints used by React:

- GET /api/health
- POST /api/upload/video
- POST /api/upload/audio
- POST /api/files/delete

See [API_DOCS.md](API_DOCS.md) for full backend endpoint details.
   - Rate limiting and API keys
   - Production-grade deployment

4. **Monitoring**
   - Analysis metrics dashboard
   - Performance statistics
   - Error tracking and logging

## 📊 Technology Stack

**Frontend:**
- HTML5
- CSS3 (Responsive Design)
- Vanilla JavaScript (ES6+)

**Backend:**
- Python 3.8+
- Flask 2.3.3
- Flask-CORS
- Werkzeug

## 📝 License

This project is part of the Multimodal Approach for Deepfake Detection research.

## 👥 Support & Contribution

For issues, suggestions, or improvements:
1. Review the [SETUP.md](SETUP.md) guide
2. Check [API_DOCS.md](API_DOCS.md) for API details
3. Run [test_api.py](test_api.py) to verify setup
4. Contact the development team

## 🎬 Getting Started

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Start server
python app.py

# 3. Open browser and navigate to index.html

# 4. Start analyzing!
```

---

**Happy Detecting! 🎬🔍**

For detailed setup instructions, see [SETUP.md](SETUP.md)  
For API documentation, see [API_DOCS.md](API_DOCS.md)
