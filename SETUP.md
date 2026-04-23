# Setup Guide

## Prerequisites

- Python 3.8+
- Node.js 18+
- npm
- Optional: FFmpeg (needed for `/api/video/extract-frames`)

## Recommended Setup and Run

From project root:

### Windows

```powershell
python run_project.py
```

or:

```powershell
start-server.bat
```

### macOS/Linux

```bash
python3 run_project.py
```

or:

```bash
chmod +x start-project.sh
./start-project.sh
```

This command will install all dependencies and start both services.

- Backend: `http://localhost:5000`
- Frontend: `http://localhost:5173`

## Setup Only

If you only want to install dependencies:

```bash
python run_project.py --setup-only
```

Skip installation and start directly:

```bash
python run_project.py --skip-install
```

## Manual Mode

```bash
pip install -r requirements.txt
npm install
python app.py
```

In a second terminal:

```bash
npm run dev
```

## Environment Configuration

Use `.env.example` as a template:

```bash
VITE_API_URL=http://localhost:5000/api
```

## Verify the API

Run once backend is active:

```bash
python test_api.py
```

## Troubleshooting

- Python command missing:
  - Windows: install Python and add to PATH
  - macOS/Linux: use `python3`
- npm missing: install Node.js 18+
- Ports in use (`5000` or `5173`): stop conflicting process or update port configuration
- Frame extraction errors: install FFmpeg and add it to PATH
