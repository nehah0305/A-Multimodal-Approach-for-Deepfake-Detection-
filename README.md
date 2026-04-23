# Deepfake Detection Dashboard (React + Flask)

This project has a React frontend (Vite) and a Flask backend API for uploading media and running deepfake-analysis workflows.

## Goal

After cloning, anyone should be able to run the project with one command.

## Tech Stack

- Frontend: React 18 + Vite
- Backend: Flask
- API Base: `http://localhost:5000/api`

## Prerequisites

- Python 3.8+
- Node.js 18+
- npm
- Optional: FFmpeg (required only for frame extraction endpoint)

## Quick Start (Recommended)

### Windows

```powershell
git clone <repo-url>
cd A-Multimodal-Approach-for-Deepfake-Detection-
python run_project.py
```

or double-click:

```powershell
start-server.bat
```

### macOS/Linux

```bash
git clone <repo-url>
cd A-Multimodal-Approach-for-Deepfake-Detection-
python3 run_project.py
```

or:

```bash
chmod +x start-project.sh
./start-project.sh
```

The launcher will:

1. Verify prerequisites
2. Install Python dependencies from `requirements.txt`
3. Install Node dependencies from `package.json`
4. Start backend on `http://localhost:5000`
5. Start frontend on `http://localhost:5173`

Press `Ctrl+C` to stop both services.

## Optional Environment Configuration

Copy `.env.example` to `.env` and edit if needed:

```bash
VITE_API_URL=http://localhost:5000/api
```

## Manual Start (If Needed)

```bash
pip install -r requirements.txt
npm install
python app.py
```

In a second terminal:

```bash
npm run dev
```

## API and Testing

- API reference: `API_DOCS.md`
- Basic API verification script: `test_api.py`

Run API tests after the backend is running:

```bash
python test_api.py
```

## Troubleshooting

- `python` not found:
   - Windows: install Python and enable "Add Python to PATH"
   - macOS/Linux: use `python3`
- `npm` not found: install Node.js 18+
- Port already in use:
   - Backend default: `5000`
   - Frontend default: `5173`
- Frame extraction fails: install FFmpeg and ensure it is available in PATH
