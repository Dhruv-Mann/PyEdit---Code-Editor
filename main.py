import customtkinter as ctk
from text_engine import TextEngine  # <--- IMPORT THE BRAIN

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("dark-blue")

class CodeEditorApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # 1. Initialize Window
        self.title("PyEdit - Python Code Editor")
        self.geometry("800x600")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # 2. Initialize the Engine
        self.engine = TextEngine()

        # 3. Create the Display Area
        # We use a Label for now just to see the text.
        # anchor="nw" means 'North West' (Top Left) alignment.
        self.display_label = ctk.CTkLabel(
            self, 
            text="Start typing...", 
            font=("Consolas", 16), 
            anchor="nw", 
            justify="left",
            width=780,
            height=580,
            fg_color="#1e1e1e",
            text_color="white"  # <--- ADD THIS LINE
        )
        self.display_label.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        # 4. Bind Keyboard Events
        # "<Key>" catches ALL standard keys (letters, numbers, symbols)
        self.bind("<Key>", self.handle_keypress)

    def handle_keypress(self, event):
        """
        Receives the key event, sends it to the engine, and updates the UI.
        """
        # A. Filter out special keys for now (Shift, Ctrl, Alt, etc.)
        # If event.char is empty, it's a modifier key.
        print(f"Key pressed: '{event.char}'")
        if event.char == "": 
            return

        # B. Handle Backspace (Tkinter sends \x08 for backspace)
        # We haven't implemented delete yet, so we ignore it or print a warning
        # B. Handle Backspace
        if event.keysym == "BackSpace":
            self.engine.delete_char()  # <--- CALL THE NEW FUNCTION
            self.redraw()              # <--- Update screen immediately
            return
            
        # C. Handle Return (Enter)
        if event.keysym == "Return":
            self.engine.insert_char("\n")
        
        # D. Handle Normal Characters
        else:
            self.engine.insert_char(event.char)

        # E. Update the UI
        self.redraw()

    def redraw(self):
        """
        Gets the text from the engine and paints it on the label.
        """
        full_text = self.engine.get_text()
        self.display_label.configure(text=full_text)

if __name__ == "__main__":
    app = CodeEditorApp()
    app.mainloop()