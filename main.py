import customtkinter as ctk

# 1. Theme Configuration
# 'System' uses the OS preference (Dark/Light). 'Dark-Blue' is the color theme.
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("dark-blue")

class CodeEditorApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # 2. Window Setup
        self.title("PyEdit - Python Code Editor")
        self.geometry("800x600") # Start with a reasonable size
        
        # 3. Grid Layout Configuration
        # We want the editor to expand when we resize the window.
        # This tells column 0 and row 0 to take up 100% of the weight.
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # 4. Placeholder UI (Proof of Life)
        # We add a temporary label just to see something on screen.
        self.label = ctk.CTkLabel(self, text="PyEdit is Running!", font=("Arial", 20))
        self.label.grid(row=0, column=0, padx=20, pady=20)

# 5. The Entry Point
if __name__ == "__main__":
    app = CodeEditorApp()
    app.mainloop() # This starts the infinite event loop