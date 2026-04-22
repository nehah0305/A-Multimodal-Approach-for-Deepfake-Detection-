from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os
import json
from datetime import datetime
from pathlib import Path
import mimetypes

app = Flask(__name__)
CORS(app)

# Configuration
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
ALLOWED_VIDEO_EXTENSIONS = {'mp4', 'avi', 'mov', 'wmv', 'mkv'}
ALLOWED_AUDIO_EXTENSIONS = {'wav', 'mp3', 'm4a', 'flac', 'aac'}
MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB

# Create upload folder if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(os.path.join(UPLOAD_FOLDER, 'videos'), exist_ok=True)
os.makedirs(os.path.join(UPLOAD_FOLDER, 'audios'), exist_ok=True)
os.makedirs(os.path.join(UPLOAD_FOLDER, 'results'), exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE


def allowed_file(filename, file_type):
    """Check if file is allowed based on extension and type"""
    if '.' not in filename:
        return False
    
    ext = filename.rsplit('.', 1)[1].lower()
    
    if file_type == 'video':
        return ext in ALLOWED_VIDEO_EXTENSIONS
    elif file_type == 'audio':
        return ext in ALLOWED_AUDIO_EXTENSIONS
    
    return False


def get_file_info(filepath):
    """Get file information"""
    if not os.path.exists(filepath):
        return None
    
    file_size = os.path.getsize(filepath)
    created_time = datetime.fromtimestamp(os.path.getctime(filepath))
    
    return {
        'filename': os.path.basename(filepath),
        'size': file_size,
        'size_mb': round(file_size / (1024 * 1024), 2),
        'created_at': created_time.isoformat(),
        'path': filepath
    }


@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'message': 'Server is running'}), 200


@app.route('/api/upload/video', methods=['POST'])
def upload_video():
    """Handle video file upload"""
    try:
        # Check if file is present in request
        if 'video' not in request.files:
            return jsonify({'error': 'No video file provided'}), 400
        
        file = request.files['video']
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Validate file
        if not allowed_file(file.filename, 'video'):
            return jsonify({
                'error': f'Invalid video format. Allowed formats: {", ".join(ALLOWED_VIDEO_EXTENSIONS)}'
            }), 400
        
        # Check file size
        if len(file.read()) > MAX_FILE_SIZE:
            return jsonify({'error': f'File size exceeds {MAX_FILE_SIZE / (1024*1024):.0f}MB limit'}), 413
        
        file.seek(0)  # Reset file pointer
        
        # Save file
        filename = secure_filename(file.filename)
        # Add timestamp to filename to avoid conflicts
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_')
        filename = timestamp + filename
        
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], 'videos', filename)
        file.save(filepath)
        
        # Get file info
        file_info = get_file_info(filepath)
        
        return jsonify({
            'success': True,
            'message': 'Video uploaded successfully',
            'file': {
                'id': filename.replace('.', '_'),
                'name': filename,
                'original_name': request.form.get('originalName', file.filename),
                'type': 'video',
                'size': file_info['size'],
                'size_mb': file_info['size_mb'],
                'uploaded_at': file_info['created_at']
            }
        }), 200
    
    except Exception as e:
        return jsonify({'error': f'Upload failed: {str(e)}'}), 500


@app.route('/api/upload/audio', methods=['POST'])
def upload_audio():
    """Handle audio file upload"""
    try:
        # Check if file is present in request
        if 'audio' not in request.files:
            return jsonify({'error': 'No audio file provided'}), 400
        
        file = request.files['audio']
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Validate file
        if not allowed_file(file.filename, 'audio'):
            return jsonify({
                'error': f'Invalid audio format. Allowed formats: {", ".join(ALLOWED_AUDIO_EXTENSIONS)}'
            }), 400
        
        # Check file size
        if len(file.read()) > MAX_FILE_SIZE:
            return jsonify({'error': f'File size exceeds {MAX_FILE_SIZE / (1024*1024):.0f}MB limit'}), 413
        
        file.seek(0)  # Reset file pointer
        
        # Save file
        filename = secure_filename(file.filename)
        # Add timestamp to filename to avoid conflicts
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_')
        filename = timestamp + filename
        
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], 'audios', filename)
        file.save(filepath)
        
        # Get file info
        file_info = get_file_info(filepath)
        
        return jsonify({
            'success': True,
            'message': 'Audio uploaded successfully',
            'file': {
                'id': filename.replace('.', '_'),
                'name': filename,
                'original_name': request.form.get('originalName', file.filename),
                'type': 'audio',
                'size': file_info['size'],
                'size_mb': file_info['size_mb'],
                'uploaded_at': file_info['created_at']
            }
        }), 200
    
    except Exception as e:
        return jsonify({'error': f'Upload failed: {str(e)}'}), 500


@app.route('/api/upload/both', methods=['POST'])
def upload_both():
    """Handle both video and audio file upload"""
    try:
        uploaded_files = {}
        
        # Handle video upload
        if 'video' in request.files and request.files['video'].filename != '':
            video = request.files['video']
            
            if not allowed_file(video.filename, 'video'):
                return jsonify({
                    'error': f'Invalid video format. Allowed formats: {", ".join(ALLOWED_VIDEO_EXTENSIONS)}'
                }), 400
            
            video_data = video.read()
            if len(video_data) > MAX_FILE_SIZE:
                return jsonify({'error': f'Video file size exceeds {MAX_FILE_SIZE / (1024*1024):.0f}MB limit'}), 413
            
            video.seek(0)
            filename = secure_filename(video.filename)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_')
            filename = timestamp + filename
            
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], 'videos', filename)
            video.save(filepath)
            
            file_info = get_file_info(filepath)
            uploaded_files['video'] = {
                'id': filename.replace('.', '_'),
                'name': filename,
                'original_name': request.form.get('videoName', video.filename),
                'type': 'video',
                'size': file_info['size'],
                'size_mb': file_info['size_mb'],
                'uploaded_at': file_info['created_at']
            }
        
        # Handle audio upload
        if 'audio' in request.files and request.files['audio'].filename != '':
            audio = request.files['audio']
            
            if not allowed_file(audio.filename, 'audio'):
                return jsonify({
                    'error': f'Invalid audio format. Allowed formats: {", ".join(ALLOWED_AUDIO_EXTENSIONS)}'
                }), 400
            
            audio_data = audio.read()
            if len(audio_data) > MAX_FILE_SIZE:
                return jsonify({'error': f'Audio file size exceeds {MAX_FILE_SIZE / (1024*1024):.0f}MB limit'}), 413
            
            audio.seek(0)
            filename = secure_filename(audio.filename)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_')
            filename = timestamp + filename
            
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], 'audios', filename)
            audio.save(filepath)
            
            file_info = get_file_info(filepath)
            uploaded_files['audio'] = {
                'id': filename.replace('.', '_'),
                'name': filename,
                'original_name': request.form.get('audioName', audio.filename),
                'type': 'audio',
                'size': file_info['size'],
                'size_mb': file_info['size_mb'],
                'uploaded_at': file_info['created_at']
            }
        
        if not uploaded_files:
            return jsonify({'error': 'No files were uploaded'}), 400
        
        return jsonify({
            'success': True,
            'message': 'Files uploaded successfully',
            'files': uploaded_files
        }), 200
    
    except Exception as e:
        return jsonify({'error': f'Upload failed: {str(e)}'}), 500


@app.route('/api/files/list', methods=['GET'])
def list_files():
    """List all uploaded files"""
    try:
        files = {'videos': [], 'audios': []}
        
        # List videos
        video_folder = os.path.join(app.config['UPLOAD_FOLDER'], 'videos')
        if os.path.exists(video_folder):
            for filename in os.listdir(video_folder):
                filepath = os.path.join(video_folder, filename)
                if os.path.isfile(filepath):
                    file_info = get_file_info(filepath)
                    files['videos'].append(file_info)
        
        # List audios
        audio_folder = os.path.join(app.config['UPLOAD_FOLDER'], 'audios')
        if os.path.exists(audio_folder):
            for filename in os.listdir(audio_folder):
                filepath = os.path.join(audio_folder, filename)
                if os.path.isfile(filepath):
                    file_info = get_file_info(filepath)
                    files['audios'].append(file_info)
        
        return jsonify({
            'success': True,
            'files': files,
            'total_videos': len(files['videos']),
            'total_audios': len(files['audios'])
        }), 200
    
    except Exception as e:
        return jsonify({'error': f'Failed to list files: {str(e)}'}), 500


@app.route('/api/files/delete', methods=['POST'])
def delete_file():
    """Delete a file"""
    try:
        data = request.get_json()
        filename = data.get('filename')
        file_type = data.get('type')  # 'video' or 'audio'
        
        if not filename or not file_type:
            return jsonify({'error': 'filename and type are required'}), 400
        
        if file_type not in ['video', 'audio']:
            return jsonify({'error': 'Invalid file type'}), 400
        
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file_type + 's', filename)
        
        if not os.path.exists(filepath):
            return jsonify({'error': 'File not found'}), 404
        
        os.remove(filepath)
        
        return jsonify({
            'success': True,
            'message': f'{file_type.capitalize()} file deleted successfully'
        }), 200
    
    except Exception as e:
        return jsonify({'error': f'Failed to delete file: {str(e)}'}), 500


@app.route('/api/files/<file_type>/<filename>', methods=['GET'])
def get_file(file_type, filename):
    """Retrieve file information"""
    try:
        if file_type not in ['video', 'audio']:
            return jsonify({'error': 'Invalid file type'}), 400
        
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file_type + 's', filename)
        
        if not os.path.exists(filepath):
            return jsonify({'error': 'File not found'}), 404
        
        file_info = get_file_info(filepath)
        return jsonify({
            'success': True,
            'file': file_info
        }), 200
    
    except Exception as e:
        return jsonify({'error': f'Failed to retrieve file: {str(e)}'}), 500


@app.route('/api/analyze', methods=['POST'])
def analyze_files():
    """Analyze uploaded files (placeholder for ML model integration)"""
    try:
        data = request.get_json()
        video_file = data.get('video')
        audio_file = data.get('audio')
        
        if not video_file and not audio_file:
            return jsonify({'error': 'No files to analyze'}), 400
        
        # This is a placeholder for actual ML model integration
        # You can integrate your deepfake detection model here
        results = {
            'status': 'analyzing',
            'files_analyzed': {
                'video': video_file,
                'audio': audio_file
            },
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify({
            'success': True,
            'message': 'Analysis started',
            'analysis': results
        }), 200
    
    except Exception as e:
        return jsonify({'error': f'Analysis failed: {str(e)}'}), 500


@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get upload statistics"""
    try:
        video_folder = os.path.join(app.config['UPLOAD_FOLDER'], 'videos')
        audio_folder = os.path.join(app.config['UPLOAD_FOLDER'], 'audios')
        
        total_video_size = 0
        total_audio_size = 0
        video_count = 0
        audio_count = 0
        
        if os.path.exists(video_folder):
            for filename in os.listdir(video_folder):
                filepath = os.path.join(video_folder, filename)
                if os.path.isfile(filepath):
                    total_video_size += os.path.getsize(filepath)
                    video_count += 1
        
        if os.path.exists(audio_folder):
            for filename in os.listdir(audio_folder):
                filepath = os.path.join(audio_folder, filename)
                if os.path.isfile(filepath):
                    total_audio_size += os.path.getsize(filepath)
                    audio_count += 1
        
        return jsonify({
            'success': True,
            'stats': {
                'videos': {
                    'count': video_count,
                    'total_size_bytes': total_video_size,
                    'total_size_mb': round(total_video_size / (1024 * 1024), 2)
                },
                'audios': {
                    'count': audio_count,
                    'total_size_bytes': total_audio_size,
                    'total_size_mb': round(total_audio_size / (1024 * 1024), 2)
                },
                'total_files': video_count + audio_count,
                'total_size_mb': round((total_video_size + total_audio_size) / (1024 * 1024), 2)
            }
        }), 200
    
    except Exception as e:
        return jsonify({'error': f'Failed to get stats: {str(e)}'}), 500


@app.errorhandler(413)
def request_entity_too_large(error):
    """Handle file too large error"""
    return jsonify({'error': f'File size exceeds {MAX_FILE_SIZE / (1024*1024):.0f}MB limit'}), 413


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({'error': 'Endpoint not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return jsonify({'error': 'Internal server error'}), 500


if __name__ == '__main__':
    print("Starting Deepfake Detection Server...")
    print(f"Upload folder: {UPLOAD_FOLDER}")
    print(f"Max file size: {MAX_FILE_SIZE / (1024*1024):.0f}MB")
    app.run(debug=True, host='localhost', port=5000)
