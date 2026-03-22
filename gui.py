import customtkinter as ctk
import threading
import sys
import jarvis

# --- 1. SET UP MODERN THEME ---
ctk.set_appearance_mode("dark")  # Force dark mode
ctk.set_default_color_theme("blue")

# --- 2. THE MAIN WINDOW ---
root = ctk.CTk()
root.title("Strawhat AI")
root.geometry("600x700")

# --- 3. BUILD UI ELEMENTS ---
# Main container frame with rounded corners
frame = ctk.CTkFrame(master=root, corner_radius=20, fg_color="#111111")
frame.pack(pady=20, padx=20, fill="both", expand=True)

# Holographic Title
title_label = ctk.CTkLabel(master=frame, text="The Thousand Sunny", font=("Roboto", 45, "bold"), text_color="#FF0000")
title_label.pack(pady=(30, 5))

# Tech Subtitle
status_label = ctk.CTkLabel(master=frame, text="READY FOR ADVENTURE!", font=("Consolas", 14), text_color="#FFA500")
status_label.pack(pady=(0, 20))

# The Modern Output Terminal
log_area = ctk.CTkTextbox(master=frame, width=500, height=450, corner_radius=10, 
                          fg_color="#050505", text_color="#FF4500", font=("Consolas", 13))
log_area.pack(pady=10, padx=20, fill="both", expand=True)

# A Pulse Button for visual flair
def clear_logs():
    # Erases all text from the UI box
    log_area.delete("0.0", "end")
    print("\n[SYSTEM] Logs cleared.")

pulse_button = ctk.CTkButton(master=frame, text="CLEAR LOGS", font=("Roboto", 14, "bold"), 
                             fg_color="#880000", hover_color="#AA0000", corner_radius=30, 
                             height=40, command=clear_logs)
pulse_button.pack(pady=25)

# --- 4. OVERRIDE PRINT() TO TARGET THE TEXTBOX ---
class RedirectText:
    def __init__(self, text_widget):
        self.text_widget = text_widget

    def write(self, string):
        # Insert text and scroll down automatically
        self.text_widget.insert("end", string)
        self.text_widget.see("end")
        
    def flush(self):
        pass

# Point standard print() commands into the CustomTkinter textbox
sys.stdout = RedirectText(log_area)

# --- 5. START JARVIS ---
def run_backend():
    # Launch JARVIS's brain
    jarvis.run_assistant()
    # Kill the UI if JARVIS naturally exits
    try:
        root.quit()
    except Exception:
        pass

jarvis_thread = threading.Thread(target=run_backend, daemon=True)
jarvis_thread.start()

# --- 6. LAUNCH THE INTERFACE ---
root.mainloop()
