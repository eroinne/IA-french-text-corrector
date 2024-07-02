from pynput import keyboard
import threading
from textblob import TextBlob
from AppKit import NSUserNotification, NSUserNotificationCenter, NSUserNotificationDefaultSoundName, NSImage
from Foundation import NSObject
import os 

class KeyLogger:
    def __init__(self):
        self.text = ""
        self.is_listening = False
        self.shift_pressed = False
        self.option_pressed = False
        self.control_pressed = False
        self.commande_pressed = False
        self.listener = keyboard.Listener(on_press=self.on_press, on_release=self.on_release)
        self.listener.start()

    # we looking at the key press to add space or sup content and enter to align
    def on_press(self, key):
        try:
            # Print key and listening state for debugging

            # Handle character keys
            if hasattr(key, 'char') and key.char is not None:
                if self.is_listening and not self.option_pressed and not self.commande_pressed and not self.commande_pressed:
                    if key == keyboard.Key.backspace and self.text == "":
                        return
                    self.text += key.char
            else:
                # Handle special keys
                if key == keyboard.Key.space and self.is_listening:
                    self.text += ' '
                elif key == keyboard.Key.backspace and self.is_listening:
                    self.text = self.text[:-1]
                elif key == keyboard.Key.enter and self.is_listening:
                    if self.text != "":
                        self.text += '\n'
                        self.store()
                elif key == keyboard.Key.shift:
                    self.shift_pressed = True
                elif key == keyboard.Key.alt_l:  # 'Option' key on macOS is mapped as 'alt_l' in pynput
                    self.option_pressed = True
                elif key == keyboard.Key.ctrl:  # Handle any control key for safety
                    self.control_pressed = True
                elif key == keyboard.Key.cmd:  # Handle any control key for safety
                    self.commande_pressed = True

                # Check for Option + Shift to toggle listening
                if self.option_pressed and self.shift_pressed:
                    self.is_listening = not self.is_listening
                    self.show_notification("Text Correction", "Listening" if self.is_listening else "Not Listening", self.is_listening)
                    print("Started" if self.is_listening else "Finish")
        except AttributeError as e:
            print(f"AttributeError: {e}")

    # we do the correction when the space bar is released and shift is pressed
    def on_release(self, key):
        if key == keyboard.Key.shift:
            self.shift_pressed = False
        elif key == keyboard.Key.alt_l:
            self.option_pressed = False
        elif key == keyboard.Key.ctrl:  # Handle any control key for safety
            self.control_pressed = False
        elif key == keyboard.Key.cmd:  # Handle any control key for safety
            self.commande_pressed = False
        elif key == keyboard.Key.space and self.shift_pressed and self.is_listening:
            self.correct_text()
            print("Corrected text")

    def correct_text(self):
        blob = TextBlob(self.text)
        corrected_text = blob.correct()
        print(f"Corrected Text: {corrected_text}")
        self.text = ""

    def store(self):
        with open("keystrokes.txt", "a") as f:
            f.write(self.text)
        self.text = ""

    def run(self):
        self.listener.join()

    def show_notification(self, title, message, listening):
        # Create notification instance
        notification = NSUserNotification.alloc().init()

        # Set notification properties
        notification.setTitle_(title)
        notification.setSubtitle_(message)
        if listening:
            notification.setSoundName_(NSUserNotificationDefaultSoundName)  # Add sound for listening state

        else:
            notification.setSoundName_(None)  # No sound for not listening
        
        notification_icon_path = os.path.join(os.path.dirname(__file__), "logo.png")
        notification_icon = NSImage.alloc().initWithContentsOfFile_(notification_icon_path)
        notification.setContentImage_(notification_icon)  

        # Deliver the notification
        NSUserNotificationCenter.defaultUserNotificationCenter().deliverNotification_(notification)


# Run the keylogger
keylogger = KeyLogger()
keylogger.run()
