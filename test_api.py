import subprocess
import json
import time
import os

def test_sidecar():
    # Path to api.py
    api_path = os.path.join(os.getcwd(), 'python', 'api.py')
    
    print(f"Testing Sidecar at: {api_path}")
    
    # Start process
    process = subprocess.Popen(
        ['python3', api_path],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1
    )
    
    # 1. Test Ping
    print("\n[Test 1] Sending Ping...")
    process.stdin.write(json.dumps({"command": "ping"}) + "\n")
    process.stdin.flush()
    
    output = process.stdout.readline()
    print(f"Response: {output.strip()}")
    
    if "pong" in output:
        print("✅ Ping Successful")
    else:
        print("❌ Ping Failed")
        err = process.stderr.read()
        print(f"Stderr: {err}")
    
    # Close
    process.terminate()

if __name__ == "__main__":
    test_sidecar()
