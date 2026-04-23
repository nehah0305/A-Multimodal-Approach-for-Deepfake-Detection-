from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os
import json
from datetime import datetime
from pathlib import Path
import mimetypes
import subprocess
import shutil

from inference_service import analyze_video

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
os.makedirs(os.path.join(UPLOAD_FOLDER, 'frames'), exist_ok=True)

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


def ffmpeg_available():
    """Check if ffmpeg binary is available in PATH."""
    return resolve_ffmpeg_binary() is not None


def resolve_ffmpeg_binary():
    """Resolve ffmpeg binary path from env, PATH, or common WinGet location."""
    env_binary = os.getenv('FFMPEG_BINARY')
    if env_binary and os.path.isfile(env_binary):
        return env_binary

    for binary_name in ('ffmpeg', 'ffmpeg.exe'):
        resolved = shutil.which(binary_name)
        if resolved:
            return resolved

    local_app_data = os.getenv('LOCALAPPDATA')
    if local_app_data:
        winget_packages_dir = Path(local_app_data) / 'Microsoft' / 'WinGet' / 'Packages'
        if winget_packages_dir.exists():
            candidates = sorted(
                winget_packages_dir.glob('Gyan.FFmpeg_*/*/bin/ffmpeg.exe'),
                key=lambda path: path.stat().st_mtime,
                reverse=True
            )
            if candidates:
                return str(candidates[0])

    return None


def clear_directory_contents(directory_path, keep_gitkeep=True):
    """Delete all files and subfolders inside a directory."""
    deleted_files = 0
    deleted_dirs = 0

    if not os.path.exists(directory_path):
        return {'files_deleted': deleted_files, 'directories_deleted': deleted_dirs}

    with os.scandir(directory_path) as entries:
        for entry in entries:
            if keep_gitkeep and entry.name == '.gitkeep':
                continue

            if entry.is_file() or entry.is_symlink():
                os.remove(entry.path)
                deleted_files += 1
            elif entry.is_dir():
                shutil.rmtree(entry.path)
                deleted_dirs += 1

    return {'files_deleted': deleted_files, 'directories_deleted': deleted_dirs}


@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint"""
    video_folder = os.path.join(app.config['UPLOAD_FOLDER'], 'videos')
    audio_folder = os.path.join(app.config['UPLOAD_FOLDER'], 'audios')

    return jsonify({
        'status': 'healthy',
        'message': 'Server is running',
        'ffmpeg_available': ffmpeg_available(),
        'video_count': len([name for name in os.listdir(video_folder) if os.path.isfile(os.path.join(video_folder, name))]) if os.path.exists(video_folder) else 0,
        'audio_count': len([name for name in os.listdir(audio_folder) if os.path.isfile(os.path.join(audio_folder, name))]) if os.path.exists(audio_folder) else 0
    }), 200


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


@app.route('/api/files/cleanup/video-and-frames', methods=['POST'])
def cleanup_video_and_frames():
    """Delete all uploaded videos and extracted frame outputs."""
    try:
        video_folder = os.path.join(app.config['UPLOAD_FOLDER'], 'videos')
        frames_folder = os.path.join(app.config['UPLOAD_FOLDER'], 'frames')

        cleaned_videos = clear_directory_contents(video_folder)
        cleaned_frames = clear_directory_contents(frames_folder)

        return jsonify({
            'success': True,
            'message': 'Uploaded videos and extracted frames cleaned successfully',
            'cleaned': {
                'videos': cleaned_videos,
                'frames': cleaned_frames
            }
        }), 200

    except Exception as e:
        return jsonify({'error': f'Failed to clean videos and frames: {str(e)}'}), 500


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
    """Analyze uploaded video using the trained baseline model."""
    try:
        data = request.get_json() or {}
        video_file = data.get('video')

        if not video_file:
            return jsonify({'error': 'A video file is required for analysis'}), 400

        video_path = os.path.join(app.config['UPLOAD_FOLDER'], 'videos', video_file)
        if not os.path.exists(video_path):
            return jsonify({'error': 'Uploaded video was not found on the server'}), 404

        results = analyze_video(video_path)

        return jsonify({
            'success': True,
            'message': 'Analysis completed',
            'analysis': results['analysis']
        }), 200
    
    except Exception as e:
        return jsonify({'error': f'Analysis failed: {str(e)}'}), 500


@app.route('/api/video/extract-frames', methods=['POST'])
def extract_video_frames():
    """Extract PNG frames from an uploaded video using FFmpeg at fixed FPS."""
    try:
        data = request.get_json() or {}
        video_filename = data.get('video_filename')
        fps = data.get('fps', 25)

        if not video_filename:
            return jsonify({'error': 'video_filename is required'}), 400

        try:
            fps = float(fps)
        except (TypeError, ValueError):
            return jsonify({'error': 'fps must be a valid number'}), 400

        if fps <= 0:
            return jsonify({'error': 'fps must be greater than 0'}), 400

        # Limit to practical extraction range to avoid accidental overload.
        if fps > 120:
            return jsonify({'error': 'fps must be less than or equal to 120'}), 400

        ffmpeg_binary = resolve_ffmpeg_binary()
        if not ffmpeg_binary:
            return jsonify({
                'error': 'FFmpeg is not installed or not available in PATH'
            }), 500

        video_path = os.path.join(app.config['UPLOAD_FOLDER'], 'videos', video_filename)
        if not os.path.exists(video_path):
            return jsonify({'error': 'Video file not found'}), 404

        video_stem = Path(video_filename).stem
        run_id = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_folder_name = f"{video_stem}_{run_id}"
        output_dir = os.path.join(app.config['UPLOAD_FOLDER'], 'frames', output_folder_name)
        os.makedirs(output_dir, exist_ok=True)

        output_pattern = os.path.join(output_dir, 'frame_%06d.png')

        # Keep spatial features intact by avoiding scale/crop filters.
        # PNG is lossless, so quality is preserved frame-by-frame.
        ffmpeg_cmd = [
            ffmpeg_binary,
            '-hide_banner',
            '-loglevel', 'error',
            '-i', video_path,
            '-vf', f'fps={fps}',
            '-start_number', '0',
            output_pattern
        ]

        run = subprocess.run(ffmpeg_cmd, capture_output=True, text=True)
        if run.returncode != 0:
            return jsonify({
                'error': 'FFmpeg frame extraction failed',
                'details': run.stderr.strip() or 'Unknown FFmpeg error'
            }), 500

        frames = sorted(
            [name for name in os.listdir(output_dir) if name.lower().endswith('.png')]
        )

        if not frames:
            return jsonify({
                'error': 'No frames were extracted. Check input video and ffmpeg setup.'
            }), 500

        return jsonify({
            'success': True,
            'message': 'Frames extracted successfully',
            'extraction': {
                'video_filename': video_filename,
                'fps': fps,
                'format': 'png',
                'frame_count': len(frames),
                'output_folder': output_folder_name,
                'output_path': output_dir,
                'first_frame': frames[0],
                'last_frame': frames[-1]
            }
        }), 200

    except Exception as e:
        return jsonify({'error': f'Frame extraction failed: {str(e)}'}), 500


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
