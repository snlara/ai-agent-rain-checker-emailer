import requests
import smtplib
from email.message import EmailMessage
import google.generativeai as genai

# --- Configuration ---
GEMINI_API_KEY = "YOUR_GEMINI_API_KEY"
WEATHER_API_KEY = "YOUR_GOOGLE_WEATHER_API_KEY"
EMAIL_ADDRESS = "your_email@gmail.com"
EMAIL_PASSWORD = "your_app_password" # Use a Google App Password here
RECIPIENT_EMAIL = "target_email@gmail.com"
LAT, LON = 37.6688, -122.0808  # Hayward, CA

def run_weather_check():
    # 1. Fetch data
    url = f"[https://weather.googleapis.com/v1/forecast/days:lookup?location.latitude=](https://weather.googleapis.com/v1/forecast/days:lookup?location.latitude=){LAT}&location.longitude={LON}&days=2&key={WEATHER_API_KEY}"
    response = requests.get(url)
    data = response.json()

    # 2. Ask Gemini to evaluate
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    prompt = (f"Review this Hayward weather data: {data}. "
              "If rain is expected today or tomorrow, reply with the word 'SEND_EMAIL' "
              "on the first line, followed by a concise email body. Otherwise, reply 'STAY_SILENT'.")
    
    # We use .strip() to remove any weird whitespace or hidden characters
    gemini_output = model.generate_content(prompt).text.strip()

    # 3. Conditional Email
    if "SEND_EMAIL" in gemini_output:
        # Remove the trigger word to get just the message
        clean_body = gemini_output.replace("SEND_EMAIL", "").strip()
        send_email(clean_body)
        print("Rain alert sent.")
    else:
        print("No rain expected, staying silent.")

def send_email(content):
    msg = EmailMessage()
    msg.set_content(content)
    msg['Subject'] = "Hayward Rain Alert"
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = RECIPIENT_EMAIL

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.send_message(msg)

if __name__ == "__main__":
    run_weather_check()