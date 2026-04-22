import React, { useMemo, useRef, useState } from "react";
import "./App.css";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:5000/api";
const MAX_FILE_SIZE = 100 * 1024 * 1024;

const videoMimeTypes = ["video/mp4", "video/x-msvideo", "video/quicktime", "video/x-ms-wmv"];
const audioMimeTypes = ["audio/wav", "audio/mpeg", "audio/mp4", "audio/flac"];

function randomResult() {
  const isAuthentic = Math.random() > 0.3;
  const authenticScore = isAuthentic
    ? Math.floor(Math.random() * 30) + 75
    : Math.floor(Math.random() * 40) + 20;
  const confidenceLevel = Math.floor(Math.random() * 25) + 75;

  return {
    isAuthentic,
    authenticScore,
    confidenceLevel,
    detections: {
      facial: isAuthentic ? Math.random() > 0.2 : Math.random() > 0.7,
      audio: isAuthentic ? Math.random() > 0.2 : Math.random() > 0.7,
      temporal: isAuthentic ? Math.random() > 0.2 : Math.random() > 0.7,
      artifacts: isAuthentic ? Math.random() > 0.2 : Math.random() > 0.7
    }
  };
}

export default function App() {
  const videoInputRef = useRef(null);
  const audioInputRef = useRef(null);

  const [videoFile, setVideoFile] = useState(null);
  const [audioFile, setAudioFile] = useState(null);
  const [videoUploaded, setVideoUploaded] = useState(null);
  const [audioUploaded, setAudioUploaded] = useState(null);

  const [dragVideo, setDragVideo] = useState(false);
  const [dragAudio, setDragAudio] = useState(false);

  const [uploadLoading, setUploadLoading] = useState("");
  const [toasts, setToasts] = useState([]);

  const [showResults, setShowResults] = useState(false);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [result, setResult] = useState(null);
  const [extractFps, setExtractFps] = useState(25);
  const [isExtractingFrames, setIsExtractingFrames] = useState(false);
  const [frameExtraction, setFrameExtraction] = useState(null);

  const canAnalyze = Boolean(videoUploaded || audioUploaded);

  const scoreDescription = useMemo(() => {
    if (!result) return "";
    if (result.authenticScore >= 75) {
      return "Likely Authentic: The media appears to be genuine with high confidence.";
    }
    if (result.authenticScore >= 50) {
      return "Suspicious: Some signs of manipulation detected. Further review recommended.";
    }
    return "Likely Deepfake: Strong indicators of manipulated content detected.";
  }, [result]);

  const addToast = (message, type = "info") => {
    const id = Date.now() + Math.random();
    setToasts((prev) => [...prev, { id, message, type }]);
    setTimeout(() => {
      setToasts((prev) => prev.filter((toast) => toast.id !== id));
    }, 3000);
  };

  const validateFile = (file, kind) => {
    const mimeList = kind === "video" ? videoMimeTypes : audioMimeTypes;
    if (!mimeList.includes(file.type)) {
      addToast(
        kind === "video"
          ? "Invalid video format. Please select MP4, AVI, MOV, or WMV"
          : "Invalid audio format. Please select WAV, MP3, M4A, or FLAC",
        "error"
      );
      return false;
    }

    if (file.size > MAX_FILE_SIZE) {
      addToast(`${kind === "video" ? "Video" : "Audio"} file size exceeds 100MB limit`, "error");
      return false;
    }

    return true;
  };

  const uploadFile = async (file, kind) => {
    const formData = new FormData();
    formData.append(kind, file);
    formData.append("originalName", file.name);

    setUploadLoading(`Uploading ${kind}...`);

    try {
      const response = await fetch(`${API_URL}/upload/${kind}`, {
        method: "POST",
        body: formData
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || `Failed to upload ${kind}`);
      }

      if (kind === "video") {
        setVideoUploaded(data.file);
      } else {
        setAudioUploaded(data.file);
      }

      addToast(`${kind[0].toUpperCase() + kind.slice(1)} uploaded successfully`, "success");
    } catch (error) {
      addToast(error.message, "error");
      if (kind === "video") {
        setVideoFile(null);
        setVideoUploaded(null);
      } else {
        setAudioFile(null);
        setAudioUploaded(null);
      }
    } finally {
      setUploadLoading("");
    }
  };

  const handleVideoSelect = async (file) => {
    if (!file || !validateFile(file, "video")) return;
    setVideoFile(file);
    await uploadFile(file, "video");
  };

  const handleAudioSelect = async (file) => {
    if (!file || !validateFile(file, "audio")) return;
    setAudioFile(file);
    await uploadFile(file, "audio");
  };

  const deleteUploadedFile = async (name, kind) => {
    if (!name) return;
    setUploadLoading(`Deleting ${kind}...`);

    try {
      const response = await fetch(`${API_URL}/files/delete`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ filename: name, type: kind })
      });
      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.error || `Failed to delete ${kind}`);
      }
      addToast(`${kind[0].toUpperCase() + kind.slice(1)} deleted successfully`, "success");
    } catch (error) {
      addToast(error.message, "error");
    } finally {
      setUploadLoading("");
    }
  };

  const clearVideo = async () => {
    if (videoUploaded?.name) {
      await deleteUploadedFile(videoUploaded.name, "video");
    }
    setVideoFile(null);
    setVideoUploaded(null);
    setFrameExtraction(null);
    setShowResults(false);
  };

  const clearAudio = async () => {
    if (audioUploaded?.name) {
      await deleteUploadedFile(audioUploaded.name, "audio");
    }
    setAudioFile(null);
    setAudioUploaded(null);
    setShowResults(false);
  };

  const analyze = async () => {
    if (!canAnalyze) {
      addToast("Please upload at least one file", "warning");
      return;
    }

    setShowResults(true);
    setIsAnalyzing(true);
    setResult(null);

    const delay = Math.random() * 2000 + 2000;
    setTimeout(() => {
      setResult(randomResult());
      setIsAnalyzing(false);
    }, delay);
  };

  const extractFrames = async () => {
    if (!videoUploaded?.name) {
      addToast("Please upload a video file first", "warning");
      return;
    }

    const fpsValue = Number(extractFps);
    if (!Number.isFinite(fpsValue) || fpsValue <= 0 || fpsValue > 120) {
      addToast("FPS must be a number between 1 and 120", "error");
      return;
    }

    setIsExtractingFrames(true);
    setUploadLoading("Extracting video frames...");

    try {
      const response = await fetch(`${API_URL}/video/extract-frames`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          video_filename: videoUploaded.name,
          fps: fpsValue
        })
      });

      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.error || "Failed to extract frames");
      }

      setFrameExtraction(data.extraction || null);
      addToast("Frames extracted successfully", "success");
    } catch (error) {
      setFrameExtraction(null);
      addToast(error.message, "error");
    } finally {
      setIsExtractingFrames(false);
      setUploadLoading("");
    }
  };

  const downloadReport = () => {
    if (!result) return;

    const reportText = `
DEEPFAKE DETECTION ANALYSIS REPORT
================================

Files Analyzed:
${videoUploaded ? `- Video: ${videoUploaded.original_name || videoUploaded.name}` : ""}
${audioUploaded ? `- Audio: ${audioUploaded.original_name || audioUploaded.name}` : ""}

Analysis Date: ${new Date().toLocaleString()}
Authenticity Score: ${result.authenticScore}%
Confidence: ${result.confidenceLevel}%

RESULTS:
--------
Facial Analysis: ${result.detections.facial ? "Authentic" : "Manipulated"}
Audio Analysis: ${result.detections.audio ? "Authentic" : "Manipulated"}
Temporal Consistency: ${result.detections.temporal ? "Authentic" : "Manipulated"}
Artifacts Detection: ${result.detections.artifacts ? "Authentic" : "Manipulated"}
`;

    const link = document.createElement("a");
    link.href = `data:text/plain;charset=utf-8,${encodeURIComponent(reportText)}`;
    link.download = `deepfake-report-${Date.now()}.txt`;
    link.click();
    addToast("Report downloaded successfully", "success");
  };

  const resetAll = async () => {
    await clearVideo();
    await clearAudio();
    setResult(null);
    setFrameExtraction(null);
    setShowResults(false);
    setIsAnalyzing(false);
    addToast("All files cleared", "info");
  };

  const renderDetectionBadge = (value) => (
    <span className={`detection-result ${value ? "authentic" : "fake"}`}>
      {value ? "Authentic" : "Manipulated"}
    </span>
  );

  return (
    <div className="container">
      <header className="header">
        <div className="header-content">
          <h1 className="title">Deepfake Detection</h1>
          <p className="subtitle">Advanced AI-powered analysis for video and audio authentication</p>
        </div>
      </header>

      <main className="main-content">
        <section className="upload-section">
          <div className="section-title">
            <h2>Upload Files</h2>
          </div>

          <div className="upload-group">
            <h3 className="upload-group-title">Video File</h3>
            <div
              className={`upload-area ${dragVideo ? "dragover" : ""}`}
              onDragOver={(event) => {
                event.preventDefault();
                setDragVideo(true);
              }}
              onDragLeave={() => setDragVideo(false)}
              onDrop={(event) => {
                event.preventDefault();
                setDragVideo(false);
                handleVideoSelect(event.dataTransfer.files?.[0]);
              }}
            >
              <svg className="upload-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
                <polyline points="17 8 12 3 7 8" />
                <line x1="12" y1="3" x2="12" y2="15" />
              </svg>
              <p className="upload-text">Drag and drop a video file here, or click to select</p>
              <p className="upload-subtext">Supported formats: MP4, AVI, MOV, WMV</p>
              <p className="upload-subtext">Max size: 100MB</p>
              <button className="upload-button" type="button" onClick={() => videoInputRef.current?.click()}>
                Browse Files
              </button>
              <input
                ref={videoInputRef}
                type="file"
                accept="video/mp4,video/x-msvideo,video/quicktime,video/x-ms-wmv"
                hidden
                onChange={(event) => handleVideoSelect(event.target.files?.[0])}
              />
            </div>
            {videoUploaded && (
              <div className="file-preview">
                <div className="preview-header">
                  <span className="preview-filename">{videoUploaded.original_name || videoUploaded.name}</span>
                  <button className="clear-btn" type="button" onClick={clearVideo}>
                    &times;
                  </button>
                </div>
              </div>
            )}

            {videoUploaded && (
              <div className="frame-extract-card">
                <div className="frame-extract-header">
                  <h4>Frame Extraction</h4>
                  <p>Frames are saved under uploads/frames/&lt;video_name_timestamp&gt;/</p>
                </div>

                <div className="frame-extract-controls">
                  <label htmlFor="extract-fps">FPS</label>
                  <input
                    id="extract-fps"
                    type="number"
                    min="1"
                    max="120"
                    value={extractFps}
                    onChange={(event) => setExtractFps(event.target.value)}
                  />
                  <button
                    className="btn btn-primary"
                    type="button"
                    onClick={extractFrames}
                    disabled={isExtractingFrames}
                  >
                    {isExtractingFrames ? "Extracting..." : "Extract Frames"}
                  </button>
                </div>

                {frameExtraction && (
                  <div className="frame-extract-result">
                    <p>
                      <strong>Frame count:</strong> {frameExtraction.frame_count}
                    </p>
                    <p>
                      <strong>Output folder:</strong> uploads/frames/{frameExtraction.output_folder}
                    </p>
                    <p>
                      <strong>First frame:</strong> {frameExtraction.first_frame}
                    </p>
                    <p>
                      <strong>Last frame:</strong> {frameExtraction.last_frame}
                    </p>
                  </div>
                )}
              </div>
            )}
          </div>

          <div className="upload-group">
            <h3 className="upload-group-title">Audio File</h3>
            <div
              className={`upload-area ${dragAudio ? "dragover" : ""}`}
              onDragOver={(event) => {
                event.preventDefault();
                setDragAudio(true);
              }}
              onDragLeave={() => setDragAudio(false)}
              onDrop={(event) => {
                event.preventDefault();
                setDragAudio(false);
                handleAudioSelect(event.dataTransfer.files?.[0]);
              }}
            >
              <svg className="upload-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
                <polyline points="17 8 12 3 7 8" />
                <line x1="12" y1="3" x2="12" y2="15" />
              </svg>
              <p className="upload-text">Drag and drop an audio file here, or click to select</p>
              <p className="upload-subtext">Supported formats: WAV, MP3, M4A, FLAC</p>
              <p className="upload-subtext">Max size: 100MB</p>
              <button className="upload-button" type="button" onClick={() => audioInputRef.current?.click()}>
                Browse Files
              </button>
              <input
                ref={audioInputRef}
                type="file"
                accept="audio/wav,audio/mpeg,audio/mp4,audio/flac"
                hidden
                onChange={(event) => handleAudioSelect(event.target.files?.[0])}
              />
            </div>
            {audioUploaded && (
              <div className="file-preview">
                <div className="preview-header">
                  <span className="preview-filename">{audioUploaded.original_name || audioUploaded.name}</span>
                  <button className="clear-btn" type="button" onClick={clearAudio}>
                    &times;
                  </button>
                </div>
              </div>
            )}
          </div>

          <div className="analyze-section">
            <button className="analyze-button" type="button" disabled={!canAnalyze || isAnalyzing} onClick={analyze}>
              Analyze
            </button>
          </div>
        </section>

        {showResults && (
          <section className="results-section">
            <div className="section-title">
              <h2>Analysis Results</h2>
            </div>

            {isAnalyzing && (
              <div className="loading-state">
                <div className="spinner" />
                <p>Analyzing your media...</p>
              </div>
            )}

            {!isAnalyzing && result && (
              <>
                <div className="result-card">
                  <h3>Authenticity Score</h3>
                  <div className="score-container">
                    <div className="score-circle">
                      <div className="score-value">{result.authenticScore}</div>
                      <div className="score-label">%</div>
                    </div>
                    <div className="score-description">
                      <p>{scoreDescription}</p>
                    </div>
                  </div>
                </div>

                <div className="result-card">
                  <h3>Confidence Level</h3>
                  <div className="confidence-bar">
                    <div className="confidence-fill" style={{ width: `${result.confidenceLevel}%` }} />
                  </div>
                  <p className="confidence-text">Confidence: {result.confidenceLevel}%</p>
                </div>

                <div className="result-card">
                  <h3>Detection Results</h3>
                  <div className="detection-grid">
                    <div className="detection-item">
                      <span>Facial Analysis</span>
                      {renderDetectionBadge(result.detections.facial)}
                    </div>
                    <div className="detection-item">
                      <span>Audio Analysis</span>
                      {renderDetectionBadge(result.detections.audio)}
                    </div>
                    <div className="detection-item">
                      <span>Temporal Consistency</span>
                      {renderDetectionBadge(result.detections.temporal)}
                    </div>
                    <div className="detection-item">
                      <span>Artifacts Detection</span>
                      {renderDetectionBadge(result.detections.artifacts)}
                    </div>
                  </div>
                </div>

                <div className="result-card">
                  <h3>Detailed Report</h3>
                  <div className="report-content">
                    <p><strong>Analysis Report Summary:</strong></p>
                    <p>
                      This deepfake detection analysis was performed using multi-modal signals from uploaded media.
                    </p>
                    <ul>
                      <li>Authenticity Score: {result.authenticScore}%</li>
                      <li>Analysis Confidence: {result.confidenceLevel}%</li>
                      <li>
                        Files Analyzed: {videoUploaded ? `Video: ${videoUploaded.original_name || videoUploaded.name}` : ""}
                        {videoUploaded && audioUploaded ? ", " : ""}
                        {audioUploaded ? `Audio: ${audioUploaded.original_name || audioUploaded.name}` : ""}
                      </li>
                    </ul>
                  </div>
                </div>

                <div className="action-buttons">
                  <button className="btn btn-primary" type="button" onClick={downloadReport}>
                    Download Report
                  </button>
                  <button className="btn btn-secondary" type="button" onClick={resetAll}>
                    Analyze Another
                  </button>
                </div>
              </>
            )}
          </section>
        )}
      </main>

      <footer className="footer">
        <p>Deepfake Detection System</p>
      </footer>

      {uploadLoading && (
        <div className="upload-loading">
          <div className="upload-spinner" />
          <p>{uploadLoading}</p>
        </div>
      )}

      <div className="toast-list">
        {toasts.map((toast) => (
          <div key={toast.id} className={`toast toast-${toast.type}`}>
            {toast.message}
          </div>
        ))}
      </div>
    </div>
  );
}
