import pyautogui
import time
import os

# =========================
# OPEN CHROME
# =========================
def open_chrome():
    print("Opening Chrome...")

    pyautogui.hotkey('win', 'r')
    time.sleep(1)

    pyautogui.typewrite('chrome')
    pyautogui.press('enter')

    print("Chrome launched")
    time.sleep(5)  # wait for Chrome to open


# =========================
# CLOSE CHROME
# =========================
def close_chrome():
    print("Closing Chrome...")
    os.system("taskkill /f /im chrome.exe")
    print("Chrome closed")


# =========================
# MAIN FLOW
# =========================
if __name__ == "__main__":
    time.sleep(2)  # time to switch to screen if needed

    open_chrome()

    # wait 10 seconds as requested
    print("Waiting for 10 seconds...")
    time.sleep(10)

    close_chrome()