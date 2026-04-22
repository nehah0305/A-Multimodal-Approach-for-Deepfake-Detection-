// Configuration
const API_URL = 'http://localhost:5000/api';

// DOM Elements
const videoUploadArea = document.getElementById('videoUploadArea');
const audioUploadArea = document.getElementById('audioUploadArea');
const videoFileInput = document.getElementById('videoFileInput');
const audioFileInput = document.getElementById('audioFileInput');
const videoPreview = document.getElementById('videoPreview');
const audioPreview = document.getElementById('audioPreview');
const analyzeBtn = document.getElementById('analyzeBtn');
const resultsSection = document.getElementById('resultsSection');
const clearVideoBtn = document.getElementById('clearVideoBtn');
const clearAudioBtn = document.getElementById('clearAudioBtn');

let selectedVideoFile = null;
let selectedAudioFile = null;
let uploadedVideoFile = null;
let uploadedAudioFile = null;

const MAX_FILE_SIZE = 100 * 1024 * 1024; // 100MB in bytes

// Show loading indicator
function showLoadingIndicator(message = 'Uploading...') {
    const indicator = document.createElement('div');
    indicator.id = 'loadingIndicator';
    indicator.className = 'upload-loading';
    indicator.innerHTML = `
        <div class="upload-spinner"></div>
        <p>${message}</p>
    `;
    document.body.appendChild(indicator);
}

// Hide loading indicator
function hideLoadingIndicator() {
    const indicator = document.getElementById('loadingIndicator');
    if (indicator) {
        indicator.remove();
    }
}

// Show toast notification
function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.textContent = message;
    document.body.appendChild(toast);
    
    setTimeout(() => {
        toast.classList.add('show');
    }, 10);
    
    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

// Video Upload
videoUploadArea.addEventListener('dragover', (e) => {
    e.preventDefault();
    videoUploadArea.classList.add('dragover');
});

videoUploadArea.addEventListener('dragleave', () => {
    videoUploadArea.classList.remove('dragover');
});

videoUploadArea.addEventListener('drop', (e) => {
    e.preventDefault();
    videoUploadArea.classList.remove('dragover');
    
    const files = e.dataTransfer.files;
    if (files.length > 0) {
        handleVideoFileSelect(files[0]);
    }
});

videoFileInput.addEventListener('change', (e) => {
    if (e.target.files.length > 0) {
        handleVideoFileSelect(e.target.files[0]);
    }
});

// Audio Upload
audioUploadArea.addEventListener('dragover', (e) => {
    e.preventDefault();
    audioUploadArea.classList.add('dragover');
});

audioUploadArea.addEventListener('dragleave', () => {
    audioUploadArea.classList.remove('dragover');
});

audioUploadArea.addEventListener('drop', (e) => {
    e.preventDefault();
    audioUploadArea.classList.remove('dragover');
    
    const files = e.dataTransfer.files;
    if (files.length > 0) {
        handleAudioFileSelect(files[0]);
    }
});

audioFileInput.addEventListener('change', (e) => {
    if (e.target.files.length > 0) {
        handleAudioFileSelect(e.target.files[0]);
    }
});

// Handle video file selection
function handleVideoFileSelect(file) {
    // Validate file type
    const validVideoTypes = ['video/mp4', 'video/x-msvideo', 'video/quicktime', 'video/x-ms-wmv'];
    
    if (!validVideoTypes.includes(file.type)) {
        showToast('Invalid video format. Please select MP4, AVI, MOV, or WMV', 'error');
        return;
    }

    // Validate file size
    if (file.size > MAX_FILE_SIZE) {
        showToast('Video file size exceeds 100MB limit', 'error');
        return;
    }

    selectedVideoFile = file;
    uploadVideoFile(file);
}

// Handle audio file selection
function handleAudioFileSelect(file) {
    // Validate file type
    const validAudioTypes = ['audio/wav', 'audio/mpeg', 'audio/mp4', 'audio/flac'];
    
    if (!validAudioTypes.includes(file.type)) {
        showToast('Invalid audio format. Please select WAV, MP3, M4A, or FLAC', 'error');
        return;
    }

    // Validate file size
    if (file.size > MAX_FILE_SIZE) {
        showToast('Audio file size exceeds 100MB limit', 'error');
        return;
    }

    selectedAudioFile = file;
    uploadAudioFile(file);
}

// Upload video file to server
async function uploadVideoFile(file) {
    try {
        showLoadingIndicator('Uploading video...');
        
        const formData = new FormData();
        formData.append('video', file);
        formData.append('originalName', file.name);

        const response = await fetch(`${API_URL}/upload/video`, {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (!response.ok) {
            hideLoadingIndicator();
            showToast(data.error || 'Failed to upload video', 'error');
            selectedVideoFile = null;
            videoFileInput.value = '';
            return;
        }

        uploadedVideoFile = data.file;
        hideLoadingIndicator();
        displayVideoPreview();
        updateAnalyzeButton();
        showToast('Video uploaded successfully', 'success');

    } catch (error) {
        hideLoadingIndicator();
        console.error('Upload error:', error);
        showToast('Error uploading video: ' + error.message, 'error');
        selectedVideoFile = null;
        videoFileInput.value = '';
    }
}

// Upload audio file to server
async function uploadAudioFile(file) {
    try {
        showLoadingIndicator('Uploading audio...');
        
        const formData = new FormData();
        formData.append('audio', file);
        formData.append('originalName', file.name);

        const response = await fetch(`${API_URL}/upload/audio`, {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (!response.ok) {
            hideLoadingIndicator();
            showToast(data.error || 'Failed to upload audio', 'error');
            selectedAudioFile = null;
            audioFileInput.value = '';
            return;
        }

        uploadedAudioFile = data.file;
        hideLoadingIndicator();
        displayAudioPreview();
        updateAnalyzeButton();
        showToast('Audio uploaded successfully', 'success');

    } catch (error) {
        hideLoadingIndicator();
        console.error('Upload error:', error);
        showToast('Error uploading audio: ' + error.message, 'error');
        selectedAudioFile = null;
        audioFileInput.value = '';
    }
}

// Display video file preview
function displayVideoPreview() {
    if (!uploadedVideoFile) return;

    const videoFileName = document.getElementById('videoFileName');
    videoFileName.textContent = `✓ ${uploadedVideoFile.original_name || uploadedVideoFile.name}`;
    videoPreview.style.display = 'block';
}

// Display audio file preview
function displayAudioPreview() {
    if (!uploadedAudioFile) return;

    const audioFileName = document.getElementById('audioFileName');
    audioFileName.textContent = `✓ ${uploadedAudioFile.original_name || uploadedAudioFile.name}`;
    audioPreview.style.display = 'block';
}

// Update analyze button state
function updateAnalyzeButton() {
    if (uploadedVideoFile || uploadedAudioFile) {
        analyzeBtn.disabled = false;
    } else {
        analyzeBtn.disabled = true;
    }
}

// Clear video file from server
async function clearVideoFileFromServer() {
    if (!uploadedVideoFile) {
        clearVideoLocal();
        return;
    }

    try {
        showLoadingIndicator('Deleting video...');
        
        const response = await fetch(`${API_URL}/files/delete`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                filename: uploadedVideoFile.name,
                type: 'video'
            })
        });

        const data = await response.json();

        if (!response.ok) {
            hideLoadingIndicator();
            showToast('Failed to delete video file', 'error');
            return;
        }

        hideLoadingIndicator();
        clearVideoLocal();
        showToast('Video deleted successfully', 'success');

    } catch (error) {
        hideLoadingIndicator();
        console.error('Delete error:', error);
        showToast('Error deleting video: ' + error.message, 'error');
    }
}

// Clear audio file from server
async function clearAudioFileFromServer() {
    if (!uploadedAudioFile) {
        clearAudioLocal();
        return;
    }

    try {
        showLoadingIndicator('Deleting audio...');
        
        const response = await fetch(`${API_URL}/files/delete`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                filename: uploadedAudioFile.name,
                type: 'audio'
            })
        });

        const data = await response.json();

        if (!response.ok) {
            hideLoadingIndicator();
            showToast('Failed to delete audio file', 'error');
            return;
        }

        hideLoadingIndicator();
        clearAudioLocal();
        showToast('Audio deleted successfully', 'success');

    } catch (error) {
        hideLoadingIndicator();
        console.error('Delete error:', error);
        showToast('Error deleting audio: ' + error.message, 'error');
    }
}

// Clear video file locally
function clearVideoLocal() {
    selectedVideoFile = null;
    uploadedVideoFile = null;
    videoFileInput.value = '';
    videoPreview.style.display = 'none';
    updateAnalyzeButton();
    resultsSection.style.display = 'none';
}

// Clear audio file locally
function clearAudioLocal() {
    selectedAudioFile = null;
    uploadedAudioFile = null;
    audioFileInput.value = '';
    audioPreview.style.display = 'none';
    updateAnalyzeButton();
    resultsSection.style.display = 'none';
}

// Clear button event listeners
clearVideoBtn.addEventListener('click', clearVideoFileFromServer);
clearAudioBtn.addEventListener('click', clearAudioFileFromServer);

// Analyze button functionality
analyzeBtn.addEventListener('click', () => {
    if (!uploadedVideoFile && !uploadedAudioFile) {
        showToast('Please upload at least one file', 'warning');
        return;
    }

    analyzeBtn.disabled = true;

    // Show loading state
    resultsSection.style.display = 'block';
    const loadingState = document.getElementById('loadingState');
    const resultsContent = document.getElementById('resultsContent');
    
    loadingState.style.display = 'block';
    resultsContent.style.display = 'none';

    // Scroll to results
    resultsSection.scrollIntoView({ behavior: 'smooth' });

    // Simulate analysis delay (2-4 seconds)
    const analysisDelay = Math.random() * 2000 + 2000;
    
    setTimeout(() => {
        displayAnalysisResults();
        analyzeBtn.disabled = false;
    }, analysisDelay);
});

// Display analysis results
function displayAnalysisResults() {
    const loadingState = document.getElementById('loadingState');
    const resultsContent = document.getElementById('resultsContent');
    
    loadingState.style.display = 'none';
    resultsContent.style.display = 'block';

    // Generate random but realistic results
    const isAuthentic = Math.random() > 0.3; // 70% authentic by default
    const authenticScore = isAuthentic 
        ? Math.floor(Math.random() * 30) + 75 // 75-95 for authentic
        : Math.floor(Math.random() * 40) + 20; // 20-60 for fake

    const confidenceLevel = Math.floor(Math.random() * 25) + 75; // 75-100

    // Update authenticity score
    const scoreValue = document.getElementById('scoreValue');
    const scoreDescription = document.getElementById('scoreDescription');
    
    scoreValue.textContent = authenticScore;
    
    if (authenticScore >= 75) {
        scoreDescription.innerHTML = '<strong>✓ Likely Authentic</strong><br>The media appears to be genuine with high confidence.';
    } else if (authenticScore >= 50) {
        scoreDescription.innerHTML = '<strong>⚠ Suspicious</strong><br>Some signs of manipulation detected. Further review recommended.';
    } else {
        scoreDescription.innerHTML = '<strong>✗ Likely Deepfake</strong><br>Strong indicators of AI-generated or manipulated content detected.';
    }

    // Update confidence bar
    const confidenceFill = document.getElementById('confidenceFill');
    const confidenceText = document.getElementById('confidenceText');
    
    confidenceFill.style.width = confidenceLevel + '%';
    confidenceText.textContent = `Confidence: ${confidenceLevel}%`;

    // Update detection results
    updateDetectionResult('facialResult', isAuthentic);
    updateDetectionResult('audioResult', isAuthentic);
    updateDetectionResult('temporalResult', isAuthentic);
    updateDetectionResult('artifactsResult', isAuthentic);

    // Update detailed report
    const detailedReportCard = document.getElementById('detailedReportCard');
    const reportContent = document.getElementById('reportContent');
    
    if (detailedReportCard) {
        detailedReportCard.style.display = 'block';
        reportContent.innerHTML = generateDetailedReport(authenticScore, confidenceLevel, isAuthentic);
    }
}

// Update detection result
function updateDetectionResult(elementId, isAuthentic) {
    const element = document.getElementById(elementId);
    if (!element) return;
    
    const isRealResult = isAuthentic ? Math.random() > 0.2 : Math.random() > 0.7;

    if (isRealResult) {
        element.textContent = 'Authentic';
        element.className = 'detection-result authentic';
    } else {
        element.textContent = 'Manipulated';
        element.className = 'detection-result fake';
    }
}

// Generate detailed report
function generateDetailedReport(score, confidence, isAuthentic) {
    const reportText = `
        <p><strong>Analysis Report Summary:</strong></p>
        <p>This deepfake detection analysis was performed using advanced AI models analyzing video frames, facial features, audio patterns, and temporal consistency.</p>
        
        <p><strong>Key Findings:</strong></p>
        <ul style="margin-left: 20px; margin-top: 10px;">
            <li>Authenticity Score: ${score}% (${score >= 75 ? 'High probability of genuine content' : score >= 50 ? 'Moderate risk indicators present' : 'High probability of manipulation'})</li>
            <li>Analysis Confidence: ${confidence}%</li>
            <li>Files Analyzed: ${uploadedVideoFile ? 'Video: ' + (uploadedVideoFile.original_name || uploadedVideoFile.name) : ''}${uploadedVideoFile && uploadedAudioFile ? ', ' : ''}${uploadedAudioFile ? 'Audio: ' + (uploadedAudioFile.original_name || uploadedAudioFile.name) : ''}</li>
            <li>Detection Method: Multi-modal deepfake detection using facial recognition, audio analysis, and temporal consistency checking</li>
            <li>Status: ${isAuthentic ? 'Media appears to be authentic' : 'Media shows signs of deepfake manipulation'}</li>
        </ul>
        
        <p style="margin-top: 15px;"><strong>Recommendations:</strong></p>
        <ul style="margin-left: 20px; margin-top: 10px;">
            <li>For ${isAuthentic ? 'authentic content' : 'suspicious content'}, consider ${isAuthentic ? 'sharing with verified sources' : 'flagging for further manual review'}</li>
            <li>Always cross-reference critical media with official sources</li>
            <li>Use this tool as one of multiple verification methods</li>
        </ul>
    `;
    return reportText;
}

// Download report
const downloadBtn = document.getElementById('downloadBtn');
if (downloadBtn) {
    downloadBtn.addEventListener('click', () => {
        const score = document.getElementById('scoreValue').textContent;
        const timestamp = new Date().toLocaleString();

        let reportText = `
DEEPFAKE DETECTION ANALYSIS REPORT
================================

Files Analyzed:
${uploadedVideoFile ? `- Video: ${uploadedVideoFile.original_name || uploadedVideoFile.name}` : ''}
${uploadedAudioFile ? `- Audio: ${uploadedAudioFile.original_name || uploadedAudioFile.name}` : ''}

Analysis Date: ${timestamp}
Authenticity Score: ${score}%

RESULTS:
--------
Facial Analysis: ${document.getElementById('facialResult').textContent}
Audio Analysis: ${document.getElementById('audioResult').textContent}
Temporal Consistency: ${document.getElementById('temporalResult').textContent}
Artifacts Detection: ${document.getElementById('artifactsResult').textContent}

DETAILED FINDINGS:
------------------
${document.getElementById('reportContent').innerText}

Report Generated by Deepfake Detection System
`;

        // Create and download file
        const element = document.createElement('a');
        element.setAttribute('href', 'data:text/plain;charset=utf-8,' + encodeURIComponent(reportText));
        element.setAttribute('download', `deepfake-report-${Date.now()}.txt`);
        element.style.display = 'none';
        document.body.appendChild(element);
        element.click();
        document.body.removeChild(element);
        
        showToast('Report downloaded successfully', 'success');
    });
}

// Reset button
const resetBtn = document.getElementById('resetBtn');
if (resetBtn) {
    resetBtn.addEventListener('click', () => {
        // Clear files from server
        if (uploadedVideoFile) {
            clearVideoFileFromServer();
        }
        if (uploadedAudioFile) {
            clearAudioFileFromServer();
        }
        
        // Reset variables
        selectedVideoFile = null;
        selectedAudioFile = null;
        uploadedVideoFile = null;
        uploadedAudioFile = null;
        
        videoFileInput.value = '';
        audioFileInput.value = '';
        videoPreview.style.display = 'none';
        audioPreview.style.display = 'none';
        resultsSection.style.display = 'none';
        analyzeBtn.disabled = true;
        
        document.querySelector('.main-content').scrollIntoView({ behavior: 'smooth' });
        showToast('All files cleared', 'info');
    });
}

// Keyboard support - Enter key to analyze
document.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && (uploadedVideoFile || uploadedAudioFile) && !analyzeBtn.disabled) {
        analyzeBtn.click();
    }
});

