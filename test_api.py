#!/usr/bin/env python3
"""
Deepfake Detection API Test Script

This script tests the Flask backend API to ensure it's working correctly.
Run this after starting the Flask server with: python app.py
"""

import requests
import json
import time
import os
from pathlib import Path

# Configuration
API_BASE_URL = 'http://localhost:5000/api'
TEST_VIDEO_PATH = None
TEST_AUDIO_PATH = None

# Color codes for terminal output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'

def print_header(text):
    print(f"\n{Colors.BLUE}{'='*60}")
    print(f"{text}")
    print(f"{'='*60}{Colors.RESET}\n")

def print_success(text):
    print(f"{Colors.GREEN}✓ {text}{Colors.RESET}")

def print_error(text):
    print(f"{Colors.RED}✗ {text}{Colors.RESET}")

def print_warning(text):
    print(f"{Colors.YELLOW}⚠ {text}{Colors.RESET}")

def test_health():
    """Test health check endpoint"""
    print_header("Test 1: Health Check")
    try:
        response = requests.get(f'{API_BASE_URL}/health', timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"Status Code: {response.status_code}")
            print(f"Response: {json.dumps(data, indent=2)}")
            print_success("Health check passed!")
            return True
        else:
            print_error(f"Health check failed with status code: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print_error("Could not connect to server. Make sure Flask is running!")
        print_error("Start the server with: python app.py")
        return False
    except Exception as e:
        print_error(f"Error: {str(e)}")
        return False

def test_list_files():
    """Test list files endpoint"""
    print_header("Test 2: List Files")
    try:
        response = requests.get(f'{API_BASE_URL}/files/list')
        if response.status_code == 200:
            data = response.json()
            print(f"Status Code: {response.status_code}")
            print(f"Total Videos: {data.get('total_videos', 0)}")
            print(f"Total Audios: {data.get('total_audios', 0)}")
            print_success("List files endpoint working!")
            return True
        else:
            print_error(f"List files failed: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Error: {str(e)}")
        return False

def create_test_files():
    """Create dummy test files"""
    global TEST_VIDEO_PATH, TEST_AUDIO_PATH
    
    print_header("Creating Test Files")
    
    # Create a dummy video file (100 bytes)
    video_path = Path('test_video.mp4')
    if not video_path.exists():
        with open(video_path, 'wb') as f:
            f.write(b'\x00' * 1000)  # 1KB dummy file
        TEST_VIDEO_PATH = str(video_path)
        print_success(f"Created test video: {video_path}")
    else:
        TEST_VIDEO_PATH = str(video_path)
        print_warning(f"Using existing test video: {video_path}")
    
    # Create a dummy audio file (100 bytes)
    audio_path = Path('test_audio.mp3')
    if not audio_path.exists():
        with open(audio_path, 'wb') as f:
            f.write(b'\x00' * 1000)  # 1KB dummy file
        TEST_AUDIO_PATH = str(audio_path)
        print_success(f"Created test audio: {audio_path}")
    else:
        TEST_AUDIO_PATH = str(audio_path)
        print_warning(f"Using existing test audio: {audio_path}")

def test_upload_video():
    """Test video upload endpoint"""
    print_header("Test 3: Upload Video")
    
    if not TEST_VIDEO_PATH or not Path(TEST_VIDEO_PATH).exists():
        print_error("Test video file not found!")
        return False
    
    try:
        with open(TEST_VIDEO_PATH, 'rb') as f:
            files = {'video': (TEST_VIDEO_PATH, f, 'video/mp4')}
            data = {'originalName': TEST_VIDEO_PATH}
            response = requests.post(f'{API_BASE_URL}/upload/video', files=files, data=data)
        
        print(f"Status Code: {response.status_code}")
        result = response.json()
        print(f"Response: {json.dumps(result, indent=2)}")
        
        if response.status_code == 200 and result.get('success'):
            print_success("Video upload successful!")
            return result.get('file', {}).get('name')
        else:
            print_error("Video upload failed!")
            return False
    except Exception as e:
        print_error(f"Error: {str(e)}")
        return False

def test_upload_audio():
    """Test audio upload endpoint"""
    print_header("Test 4: Upload Audio")
    
    if not TEST_AUDIO_PATH or not Path(TEST_AUDIO_PATH).exists():
        print_error("Test audio file not found!")
        return False
    
    try:
        with open(TEST_AUDIO_PATH, 'rb') as f:
            files = {'audio': (TEST_AUDIO_PATH, f, 'audio/mpeg')}
            data = {'originalName': TEST_AUDIO_PATH}
            response = requests.post(f'{API_BASE_URL}/upload/audio', files=files, data=data)
        
        print(f"Status Code: {response.status_code}")
        result = response.json()
        print(f"Response: {json.dumps(result, indent=2)}")
        
        if response.status_code == 200 and result.get('success'):
            print_success("Audio upload successful!")
            return result.get('file', {}).get('name')
        else:
            print_error("Audio upload failed!")
            return False
    except Exception as e:
        print_error(f"Error: {str(e)}")
        return False

def test_get_stats():
    """Test stats endpoint"""
    print_header("Test 5: Get Statistics")
    try:
        response = requests.get(f'{API_BASE_URL}/stats')
        if response.status_code == 200:
            data = response.json()
            stats = data.get('stats', {})
            print(f"Status Code: {response.status_code}")
            print(f"Total Files: {stats.get('total_files', 0)}")
            print(f"Total Size: {stats.get('total_size_mb', 0)}MB")
            print(f"Videos: {stats.get('videos', {}).get('count', 0)}")
            print(f"Audios: {stats.get('audios', {}).get('count', 0)}")
            print_success("Statistics retrieved successfully!")
            return True
        else:
            print_error(f"Get stats failed: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Error: {str(e)}")
        return False

def test_delete_file(filename, file_type):
    """Test file delete endpoint"""
    print_header(f"Test 6: Delete {file_type.capitalize()}")
    
    if not filename:
        print_warning("No file to delete (upload test skipped)")
        return False
    
    try:
        response = requests.post(
            f'{API_BASE_URL}/files/delete',
            json={
                'filename': filename,
                'type': file_type
            }
        )
        
        print(f"Status Code: {response.status_code}")
        result = response.json()
        print(f"Response: {json.dumps(result, indent=2)}")
        
        if response.status_code == 200 and result.get('success'):
            print_success(f"{file_type.capitalize()} deleted successfully!")
            return True
        else:
            print_error(f"Delete {file_type} failed!")
            return False
    except Exception as e:
        print_error(f"Error: {str(e)}")
        return False

def cleanup_test_files():
    """Clean up test files"""
    print_header("Cleanup")
    
    if TEST_VIDEO_PATH and Path(TEST_VIDEO_PATH).exists():
        os.remove(TEST_VIDEO_PATH)
        print_success(f"Removed test video: {TEST_VIDEO_PATH}")
    
    if TEST_AUDIO_PATH and Path(TEST_AUDIO_PATH).exists():
        os.remove(TEST_AUDIO_PATH)
        print_success(f"Removed test audio: {TEST_AUDIO_PATH}")

def main():
    """Run all tests"""
    print(f"\n{Colors.BLUE}{'='*60}")
    print("Deepfake Detection API Test Suite")
    print(f"{'='*60}{Colors.RESET}\n")
    
    print(f"Testing API at: {API_BASE_URL}")
    print("Make sure Flask server is running: python app.py\n")
    
    # Run tests
    results = {}
    
    # Test 1: Health check
    results['Health Check'] = test_health()
    if not results['Health Check']:
        print_error("\nServer is not running. Please start it with: python app.py")
        return
    
    time.sleep(1)
    
    # Test 2: List files
    results['List Files'] = test_list_files()
    time.sleep(1)
    
    # Create test files
    create_test_files()
    time.sleep(1)
    
    # Test 3: Upload video
    video_filename = test_upload_video()
    results['Upload Video'] = bool(video_filename)
    time.sleep(1)
    
    # Test 4: Upload audio
    audio_filename = test_upload_audio()
    results['Upload Audio'] = bool(audio_filename)
    time.sleep(1)
    
    # Test 5: Get stats
    results['Get Stats'] = test_get_stats()
    time.sleep(1)
    
    # Test 6: Delete files
    if video_filename:
        results['Delete Video'] = test_delete_file(video_filename, 'video')
        time.sleep(1)
    
    if audio_filename:
        results['Delete Audio'] = test_delete_file(audio_filename, 'audio')
        time.sleep(1)
    
    # Print summary
    print_header("Test Summary")
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        if result:
            print_success(f"{test_name}")
        else:
            print_error(f"{test_name}")
    
    print(f"\nPassed: {passed}/{total}")
    
    if passed == total:
        print_success("\nAll tests passed! API is working correctly.")
    else:
        print_warning("\nSome tests failed. Check the output above for details.")
    
    # Cleanup
    cleanup_test_files()
    
    print(f"\n{Colors.BLUE}{'='*60}{Colors.RESET}\n")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user.")
    except Exception as e:
        print_error(f"Unexpected error: {str(e)}")
