import requests
import time

print("Waiting for Streamlit to initialize...")
time.sleep(3)

try:
    # Try to access the health endpoint
    response = requests.get("http://localhost:8501/healthz")
    print(f"Health check status code: {response.status_code}")
    print(f"Health check response: {response.text}")
    
    # Try to access the main app
    main_response = requests.get("http://localhost:8501")
    print(f"Main app status code: {main_response.status_code}")
    print(f"Main app response length: {len(main_response.text)}")
    
    if main_response.status_code == 200 and len(main_response.text) > 100:
        print("App is accessible and running!")
    else:
        print("App may be having issues.")
except Exception as e:
    print(f"Error accessing app: {str(e)}")