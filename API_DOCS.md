# Deepfake Detection API Documentation

## Base URL
```
http://localhost:5000/api
```

## Content Types
- **Request:** `application/json` or `multipart/form-data` (for file uploads)
- **Response:** `application/json`

---

## Endpoints

### 1. Health Check

**Endpoint:** `GET /api/health`

**Description:** Check if the server is running

**Response:**
```json
{
  "status": "healthy",
  "message": "Server is running"
}
```

---

### 2. Upload Video

**Endpoint:** `POST /api/upload/video`

**Description:** Upload a single video file

**Request:**
- **Content-Type:** `multipart/form-data`
- **Body:**
  - `video` (required): Video file (mp4, avi, mov, wmv)
  - `originalName` (optional): Original filename

**cURL Example:**
```bash
curl -X POST http://localhost:5000/api/upload/video \
  -F "video=@path/to/video.mp4" \
  -F "originalName=my-video.mp4"
```

**Response (Success):**
```json
{
  "success": true,
  "message": "Video uploaded successfully",
  "file": {
    "id": "20240422_120000_video",
    "name": "20240422_120000_video.mp4",
    "original_name": "my-video.mp4",
    "type": "video",
    "size": 52428800,
    "size_mb": 50.0,
    "uploaded_at": "2024-04-22T12:00:00"
  }
}
```

**Response (Error):**
```json
{
  "error": "Invalid video format. Allowed formats: mp4, avi, mov, wmv"
}
```

---

### 3. Upload Audio

**Endpoint:** `POST /api/upload/audio`

**Description:** Upload a single audio file

**Request:**
- **Content-Type:** `multipart/form-data`
- **Body:**
  - `audio` (required): Audio file (wav, mp3, m4a, flac)
  - `originalName` (optional): Original filename

**cURL Example:**
```bash
curl -X POST http://localhost:5000/api/upload/audio \
  -F "audio=@path/to/audio.mp3" \
  -F "originalName=my-audio.mp3"
```

**Response (Success):**
```json
{
  "success": true,
  "message": "Audio uploaded successfully",
  "file": {
    "id": "20240422_120000_audio",
    "name": "20240422_120000_audio.mp3",
    "original_name": "my-audio.mp3",
    "type": "audio",
    "size": 10485760,
    "size_mb": 10.0,
    "uploaded_at": "2024-04-22T12:00:00"
  }
}
```

---

### 4. Upload Both Video and Audio

**Endpoint:** `POST /api/upload/both`

**Description:** Upload video and audio files together

**Request:**
- **Content-Type:** `multipart/form-data`
- **Body:**
  - `video` (optional): Video file
  - `audio` (optional): Audio file
  - `videoName` (optional): Video original name
  - `audioName` (optional): Audio original name

**cURL Example:**
```bash
curl -X POST http://localhost:5000/api/upload/both \
  -F "video=@path/to/video.mp4" \
  -F "audio=@path/to/audio.mp3" \
  -F "videoName=my-video.mp4" \
  -F "audioName=my-audio.mp3"
```

**Response (Success):**
```json
{
  "success": true,
  "message": "Files uploaded successfully",
  "files": {
    "video": {
      "id": "20240422_120000_video",
      "name": "20240422_120000_video.mp4",
      "original_name": "my-video.mp4",
      "type": "video",
      "size": 52428800,
      "size_mb": 50.0,
      "uploaded_at": "2024-04-22T12:00:00"
    },
    "audio": {
      "id": "20240422_120000_audio",
      "name": "20240422_120000_audio.mp3",
      "original_name": "my-audio.mp3",
      "type": "audio",
      "size": 10485760,
      "size_mb": 10.0,
      "uploaded_at": "2024-04-22T12:00:00"
    }
  }
}
```

---

### 5. List All Files

**Endpoint:** `GET /api/files/list`

**Description:** Get list of all uploaded files

**Response:**
```json
{
  "success": true,
  "files": {
    "videos": [
      {
        "filename": "20240422_120000_video.mp4",
        "size": 52428800,
        "size_mb": 50.0,
        "created_at": "2024-04-22T12:00:00",
        "path": "/path/to/uploads/videos/20240422_120000_video.mp4"
      }
    ],
    "audios": [
      {
        "filename": "20240422_120000_audio.mp3",
        "size": 10485760,
        "size_mb": 10.0,
        "created_at": "2024-04-22T12:00:00",
        "path": "/path/to/uploads/audios/20240422_120000_audio.mp3"
      }
    ]
  },
  "total_videos": 1,
  "total_audios": 1
}
```

---

### 6. Delete File

**Endpoint:** `POST /api/files/delete`

**Description:** Delete an uploaded file

**Request:**
- **Content-Type:** `application/json`
- **Body:**
  ```json
  {
    "filename": "20240422_120000_video.mp4",
    "type": "video"
  }
  ```

**cURL Example:**
```bash
curl -X POST http://localhost:5000/api/files/delete \
  -H "Content-Type: application/json" \
  -d '{
    "filename": "20240422_120000_video.mp4",
    "type": "video"
  }'
```

**Response (Success):**
```json
{
  "success": true,
  "message": "Video file deleted successfully"
}
```

---

### 7. Get File Information

**Endpoint:** `GET /api/files/<file_type>/<filename>`

**Description:** Get information about a specific file

**Parameters:**
- `file_type` (path): `video` or `audio`
- `filename` (path): Name of the file

**Example:** `GET /api/files/video/20240422_120000_video.mp4`

**Response:**
```json
{
  "success": true,
  "file": {
    "filename": "20240422_120000_video.mp4",
    "size": 52428800,
    "size_mb": 50.0,
    "created_at": "2024-04-22T12:00:00",
    "path": "/path/to/uploads/videos/20240422_120000_video.mp4"
  }
}
```

---

### 8. Get Statistics

**Endpoint:** `GET /api/stats`

**Description:** Get upload statistics

**Response:**
```json
{
  "success": true,
  "stats": {
    "videos": {
      "count": 5,
      "total_size_bytes": 262144000,
      "total_size_mb": 250.0
    },
    "audios": {
      "count": 3,
      "total_size_bytes": 52428800,
      "total_size_mb": 50.0
    },
    "total_files": 8,
    "total_size_mb": 300.0
  }
}
```

---

### 9. Analyze Files

**Endpoint:** `POST /api/analyze`

**Description:** Start analysis of uploaded files (placeholder endpoint)

**Request:**
- **Content-Type:** `application/json`
- **Body:**
  ```json
  {
    "video": "20240422_120000_video.mp4",
    "audio": "20240422_120000_audio.mp3"
  }
  ```

**Response:**
```json
{
  "success": true,
  "message": "Analysis started",
  "analysis": {
    "status": "analyzing",
    "files_analyzed": {
      "video": "20240422_120000_video.mp4",
      "audio": "20240422_120000_audio.mp3"
    },
    "timestamp": "2024-04-22T12:00:00"
  }
}
```

---

## Error Responses

### 400 Bad Request
```json
{
  "error": "No video file provided"
}
```

### 404 Not Found
```json
{
  "error": "File not found"
}
```

### 413 Payload Too Large
```json
{
  "error": "File size exceeds 100MB limit"
}
```

### 500 Internal Server Error
```json
{
  "error": "Internal server error"
}
```

---

## File Size Limits

- **Per File:** 100MB
- **Total Storage:** Unlimited (depends on disk space)

## Supported Formats

### Video
- mp4, avi, mov, wmv

### Audio
- wav, mp3, m4a, flac

---

## JavaScript/Fetch Examples

### Upload Video
```javascript
const formData = new FormData();
formData.append('video', videoFile);
formData.append('originalName', videoFile.name);

fetch('http://localhost:5000/api/upload/video', {
  method: 'POST',
  body: formData
})
.then(response => response.json())
.then(data => console.log(data));
```

### List Files
```javascript
fetch('http://localhost:5000/api/files/list')
  .then(response => response.json())
  .then(data => console.log(data));
```

### Delete File
```javascript
fetch('http://localhost:5000/api/files/delete', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    filename: '20240422_120000_video.mp4',
    type: 'video'
  })
})
.then(response => response.json())
.then(data => console.log(data));
```

---

## Rate Limiting

Currently, no rate limiting is implemented. For production use, consider adding:
- Rate limiting per IP
- Authentication/API keys
- Request throttling

---

## Security Notes

1. **File Validation:** All files are validated by type and size
2. **Path Security:** Filenames are sanitized using `werkzeug.utils.secure_filename`
3. **CORS:** Enabled for local development (restrict in production)
4. **No Authentication:** Add authentication for production use

---

## Future Enhancements

1. Add real ML model integration to `/api/analyze`
2. Implement async task queue for long-running analysis
3. Add WebSocket support for real-time progress updates
4. Implement user authentication and file ownership
5. Add rate limiting and request validation
6. Support for batch processing
7. Cloud storage integration (AWS S3, Azure Blob, etc.)

---

For more information, see [SETUP.md](SETUP.md) and [README.md](README.md)
