# Deepfake Detection Dashboard - Setup Guide

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
├── uploads/
│   ├── videos/
│   ├── audios/
│   └── results/
└── README.md
```

## Prerequisites

- Python 3.8+
- Node.js 18+
- npm

## Installation & Setup

### Step 1: Install Python Dependencies

Open PowerShell and navigate to the project directory:

```powershell
cd "c:\Users\nehah\OneDrive\Desktop\MAJOR PROJECT\A-Multimodal-Approach-for-Deepfake-Detection-"
```

Install required Python packages:

```powershell
pip install -r requirements.txt
```

Or manually install:

```powershell
pip install Flask==2.3.3 Flask-CORS==4.0.0 Werkzeug==2.3.7
```

### Step 2: Start the Backend Server

In the same PowerShell window, run:

```powershell
python app.py
```

You should see output like:
```
Starting Deepfake Detection Server...
Upload folder: c:\Users\nehah\OneDrive\Desktop\MAJOR PROJECT\A-Multimodal-Approach-for-Deepfake-Detection-\uploads
Max file size: 100MB
 * Serving Flask app 'app'
 * Debug mode: on
 * Running on http://localhost:5000
```

### Step 3: Install Frontend Dependencies

```powershell
npm install
```

### Step 4: Start React Frontend

```powershell
npm run dev
```

Open http://localhost:5173 in your browser.

## How to Use

### Uploading Files

1. **Drag and Drop** - Drag video/audio files into the upload areas
2. **Click Browse** - Click "Browse Files" to select from your computer

### Supported Formats

**Video Files:**
- MP4 (.mp4)
- AVI (.avi)
- MOV (.mov)
- WMV (.wmv)

**Audio Files:**
- WAV (.wav)
- MP3 (.mp3)
- M4A (.m4a)
- FLAC (.flac)

**File Size Limit:** 100MB per file

### Analysis

1. Upload one or both files
2. Click the **Analyze** button
3. Wait for analysis to complete (simulated 2-4 seconds)
4. View results including:
   - Authenticity score
   - Confidence level
   - Detection results for facial, audio, temporal, and artifact analysis
   - Detailed report (if requested)

### Download Results

- Click **Download Report** to save analysis as a text file
- Click **Analyze Another** to reset and analyze new files

## Backend API Endpoints

The Flask server provides the following endpoints:

### Health Check
```
GET /api/health
```

### Upload Endpoints
```
POST /api/upload/video        # Upload single video
POST /api/upload/audio        # Upload single audio
POST /api/upload/both         # Upload video and audio together
```

### File Management
```
GET /api/files/list           # List all uploaded files
POST /api/files/delete        # Delete a file
GET /api/files/<type>/<filename>  # Get file info
```

### Analysis & Stats
```
GET /api/stats                # Get upload statistics
POST /api/analyze             # Start analysis (placeholder)
```

## Troubleshooting

### Issue: "Failed to connect to server"
- Make sure Flask server is running (`python app.py`)
- Check that server is running on `http://localhost:5000`
- Verify no firewall is blocking port 5000

### Issue: "File upload fails"
- Check file format is supported
- Verify file size is under 100MB
- Ensure "uploads" folder exists and has write permissions

### Issue: "Port 5000 already in use"
- Another application is using port 5000
- Stop the conflicting application or change Flask port in app.py:
  ```python
  app.run(debug=True, host='localhost', port=5001)  # Change 5000 to 5001
  ```

### Issue: Python not found
- Ensure Python is installed and added to PATH
- Try using `python3` instead of `python`

## File Storage

Uploaded files are stored in:
- **Videos:** `uploads/videos/`
- **Audio:** `uploads/audios/`
- **Results:** `uploads/results/` (for future analysis results)

Files are automatically named with timestamps to prevent conflicts.

## Future Enhancements

To integrate your actual deepfake detection ML model:

1. Update the `/api/analyze` endpoint in `app.py`
2. Add ML model loading and prediction code
3. Return real analysis results instead of simulated ones
4. Store results in `uploads/results/`

Example integration:
```python
@app.route('/api/analyze', methods=['POST'])
def analyze_files():
    data = request.get_json()
    video_file = data.get('video')
    audio_file = data.get('audio')
    
    # Load your ML model
    # model = load_model()
    
    # Run analysis
    # results = model.predict(video_file, audio_file)
    
    return jsonify(results)
```

## Performance Notes

- File uploads are optimized for files up to 100MB
- Analysis is simulated (2-4 seconds) - replace with actual ML inference
- Server stores files locally - consider cloud storage for production
- No authentication - add user management for production use

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review Flask documentation: https://flask.palletsprojects.com/
3. Check browser console (F12) for JavaScript errors
4. Verify all files are in the correct directory

---

**Happy Detecting! 🎬🔍**
