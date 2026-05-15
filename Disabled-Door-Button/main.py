# This is basic sample code to that just sends a basic API request but the import can be used for other projects as well.

from rf_button import RFButtonListener, RFFrame
import requests

url = "xxxx"


def send_api_request(frame: RFFrame):
    try:
        response = requests.post(url)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"API request failed: {e}")


def main():
    listener = RFButtonListener(target_suffix="F4BAD8BB8", on_press=send_api_request, debug=False)
    listener.listen()

if __name__ == "__main__":
    main()