#!/usr/bin/env bash
set -e

# Step 0: Move into Rust API folder (relative to script location)
cd "$(dirname "$0")/rust-chat-actix"

# Step 1: Ensure Rust is installed
if ! command -v cargo &> /dev/null
then
    echo "Rust is not installed. Please install Rust: https://www.rust-lang.org/tools/install"
    exit 1
fi

# Step 2: Clean and build the project
echo "Building Actix Messaging..."
cargo clean
cargo build --release

# Step 3: Set environment variables
export RUST_LOG=info
export RUST_BACKTRACE=1

# Step 4: Run the server in background with logs
echo "Starting Actix Messaging Server in background..."
nohup cargo run --release > ../server.log 2>&1 &

echo "Server started! Logs are being written to server.log"

cd ..
cd "$(dirname "$0")/flask-auth-api"
python app.py
