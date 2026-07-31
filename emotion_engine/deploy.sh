#!/bin/bash
# Glennian Emotion Engine — Deployment Script
# AI_OS3 — Commit #1013 / #1102
set -e
echo "=== DEPLOYING EMOTION ENGINE v3 ==="
echo "Building Docker image..."
docker build -t glennian-emotion-engine:3.0.0 .
echo "Starting container..."
docker-compose up -d
echo "Waiting for health check..."
sleep 5
curl -s http://localhost:5000/health | python3 -m json.tool
echo ""
echo "=== DEPLOYMENT COMPLETE ==="
echo "  Endpoints:"
echo "    POST http://localhost:5000/process"
echo "    GET  http://localhost:5000/state"
echo "    GET  http://localhost:5000/health"
echo "    GET  http://localhost:5000/metrics"
echo "    GET  http://localhost:5000/receipt"
echo ""
echo "  ~76))) ~75))) ~74)))"
