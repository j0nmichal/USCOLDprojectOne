#!/bin/bash
# Double-click this file to launch the US Cold Admin panel.

DIR="$(cd "$(dirname "$0")" && pwd)"
PORT=8743

# Kill any previous instance on this port
lsof -ti tcp:$PORT | xargs kill -9 2>/dev/null

# Start server in background
cd "$DIR"
python3 -m http.server $PORT &
SERVER_PID=$!

# Wait briefly then open browser
sleep 0.4
open "http://localhost:$PORT/uscold-admin.html"

echo ""
echo "  US Cold Admin is running at http://localhost:$PORT/uscold-admin.html"
echo "  Close this window to shut down the server."
echo ""

# Keep running until window is closed
trap "kill $SERVER_PID 2>/dev/null" EXIT
wait $SERVER_PID
