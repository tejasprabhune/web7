from pyngrok import ngrok
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get the ngrok authtoken from the environment
authtoken = os.environ.get("NGROK_AUTH_TOKEN")
if not authtoken:
    print("Error: NGROK_AUTHTOKEN not found.")
    print("Please add your ngrok authtoken to the .env file.")
    exit()

# Set the ngrok authtoken
ngrok.set_auth_token(authtoken)

# Open a tunnel to the local server on port 8000
http_tunnel = ngrok.connect(8000)

print(f"Ngrok tunnel established at: {http_tunnel.public_url}")
print("Press Ctrl+C to stop the tunnel.")

# Keep the script running to maintain the tunnel
try:
    # Block until CTRL-C or some other process kill event
    ngrok_process = ngrok.get_ngrok_process()
    ngrok_process.proc.wait()
except KeyboardInterrupt:
    print(" Shutting down ngrok.")
    ngrok.kill() 