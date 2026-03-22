#!/bin/bash
set -e

echo "🚀 Starting Novel Agent..."

# Check if Docker is available
if command -v docker &> /dev/null; then
    echo "📦 Using Docker Compose..."
    docker-compose up -d
    echo "✅ Services started!"
    echo ""
    echo "Services:"
    echo "  - Frontend: http://localhost:5173"
    echo "  - Backend:  http://localhost:8000"
    echo "  - API Docs: http://localhost:8000/docs"
    echo "  - MinIO:    http://localhost:9001"
    echo ""
    echo "MinIO credentials: minioadmin / minioadmin"
else
    echo "⚠️ Docker not found. Starting services directly..."
    
    # Start PostgreSQL and MinIO via Docker if available
    if command -v docker-compose &> /dev/null; then
        docker-compose up -d postgres minio minio-init
    fi
    
    # Start backend
    echo "Starting backend..."
    cd backend
    if ! command -v opencode &> /dev/null; then
        echo "Installing OpenCode CLI..."
        npm install -g opencode-ai@latest
    fi
    pip install -r requirements.txt -q
    uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 &
    BACKEND_PID=$!
    cd ..
    
    # Start frontend
    echo "Starting frontend..."
    cd frontend
    pnpm install
    pnpm dev &
    FRONTEND_PID=$!
    cd ..
    
    echo "✅ Services started!"
    echo ""
    echo "  - Frontend: http://localhost:5173"
    echo "  - Backend:  http://localhost:8000"
    echo ""
    echo "Press Ctrl+C to stop all services"
    
    # Wait for interrupt
    trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" INT TERM
    wait
fi
