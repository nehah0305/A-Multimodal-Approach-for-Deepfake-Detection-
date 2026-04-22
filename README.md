# Deepfake Detection Dashboard

A modern, interactive web-based dashboard with full backend support for analyzing video and audio files to detect deepfakes and manipulated content.

## 🎯 Key Features

✨ **Full-Stack Application**
- Frontend: Interactive HTML/CSS/JavaScript dashboard
- Backend: Python Flask REST API
- Real file upload and storage
- Complete API documentation

📁 **Media Upload & Management**
- Drag-and-drop file upload (both separate and combined)
- Support for multiple video formats (MP4, AVI, MOV, WMV)
- Support for multiple audio formats (MP3, WAV, M4A, FLAC)
- File size validation (max 100MB per file)
- Automatic file organization and timestamping
- File listing and deletion endpoints

🔍 **Analysis Features**
- Authenticity score with visual indicators
- Confidence level bar
- Multi-factor detection results:
  - Facial Analysis
  - Audio Analysis
  - Temporal Consistency
  - Artifacts Detection
- Detailed analysis reports
- Downloadable results

🚀 **Backend API**
- RESTful API with comprehensive endpoints
- File upload/download management
- Statistics and monitoring
- CORS-enabled for frontend integration
- Error handling and validation
- Ready for ML model integration

## 📋 Quick Start

### Prerequisites
- Python 3.8+ ([Download](https://www.python.org/))
- Any modern web browser

### Installation (5 minutes)

1. **Install Dependencies**
   ```powershell
   cd "path/to/project"
   pip install -r requirements.txt
   ```

2. **Start Backend Server**
   ```powershell
   python app.py
   ```
   Or use the quick start script:
   ```powershell
   .\start-server.bat
   ```

3. **Open Dashboard**
   - Double-click `index.html` or
   - Open in browser: `file:///path/to/index.html`

4. **Start Analyzing!**
   - Upload video/audio files
   - Click Analyze
   - View results and download reports

## 📂 Project Structure

```
A-Multimodal-Approach-for-Deepfake-Detection-/
├── index.html              # Frontend dashboard
├── styles.css              # Styling (responsive design)
├── script.js               # Frontend JavaScript (with API integration)
├── app.py                  # Backend Flask server
├── requirements.txt        # Python dependencies
├── start-server.bat        # Quick start script (Windows)
├── test_api.py            # API testing script
├── uploads/               # File storage (auto-created)
│   ├── videos/           # Uploaded video files
│   ├── audios/           # Uploaded audio files
│   └── results/          # Analysis results
├── README.md             # This file
├── SETUP.md              # Detailed setup guide
└── API_DOCS.md           # API documentation
```

## 🎮 How to Use

### Uploading Files

1. **Video Upload**
   - Click the video upload area or drag a video file
   - Supported formats: MP4, AVI, MOV, WMV
   - Max size: 100MB

2. **Audio Upload**
   - Click the audio upload area or drag an audio file
   - Supported formats: MP3, WAV, M4A, FLAC
   - Max size: 100MB

### Running Analysis

1. Upload one or both files (video/audio)
2. Click the **Analyze** button
3. Wait for analysis to complete
4. View comprehensive results

### Results Display

- **Authenticity Score**: Percentage-based genuineness indicator
- **Confidence Level**: How confident the analysis is
- **Detection Results**: Individual metrics for different analysis types
- **Detailed Report**: In-depth findings and recommendations

### Download & Export

- Download analysis as text report
- Clear and analyze another file
- File history is maintained on server

## 🔌 API Endpoints

All endpoints are documented in [API_DOCS.md](API_DOCS.md)

### Core Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/health` | Health check |
| `POST` | `/api/upload/video` | Upload video |
| `POST` | `/api/upload/audio` | Upload audio |
| `POST` | `/api/upload/both` | Upload both |
| `GET` | `/api/files/list` | List all files |
| `POST` | `/api/files/delete` | Delete file |
| `GET` | `/api/stats` | Get statistics |
| `POST` | `/api/analyze` | Start analysis |

See [API_DOCS.md](API_DOCS.md) for detailed endpoint documentation.

## 🧪 Testing

Run the API test suite to verify everything is working:

```powershell
python test_api.py
```

This will test all endpoints and verify the API is functioning correctly.

## 📚 Documentation

- **[SETUP.md](SETUP.md)** - Detailed installation and setup guide
- **[API_DOCS.md](API_DOCS.md)** - Complete API reference
- **[README.md](README.md)** - This file

## 🎨 User Interface

- Modern gradient design with purple/pink color scheme
- Fully responsive (desktop, tablet, mobile)
- Smooth animations and transitions
- Toast notifications for user feedback
- Loading indicators for file uploads
- Real-time file preview

## ⚙️ Supported Formats

### Video
- MP4 (.mp4)
- AVI (.avi)  
- MOV (.mov)
- WMV (.wmv)

### Audio
- MP3 (.mp3)
- WAV (.wav)
- M4A (.m4a)
- FLAC (.flac)

**File Size Limit:** 100MB per file

## 🚧 Troubleshooting

### Server Connection Issues
- Ensure Flask is running: `python app.py`
- Check server is on `http://localhost:5000`
- Verify no firewall blocking port 5000

### File Upload Fails
- Verify file format is supported
- Check file size is under 100MB
- Ensure `uploads` folder exists with write permissions

### Python Not Found
- Install Python from [python.org](https://www.python.org/)
- Add to PATH during installation
- Restart terminal after installation

See [SETUP.md](SETUP.md) for more troubleshooting tips.

## 🔮 Future Enhancements

1. **ML Model Integration**
   - Integrate your deepfake detection ML models
   - Real-time analysis results
   - Custom model selection

2. **Advanced Features**
   - User authentication
   - File history and analytics
   - Batch processing
   - Real-time progress updates (WebSocket)

3. **Infrastructure**
   - Cloud storage integration (AWS S3, Azure)
   - Database for results storage
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
