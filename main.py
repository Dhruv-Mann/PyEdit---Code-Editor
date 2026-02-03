import customtkinter as ctk
from text_engine import TextEngine  # <--- IMPORT THE BRAIN
from tkinter import filedialog
import subprocess
import sys

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("dark-blue")


class CodeEditorApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # 1. Setup Window
        self.title("Squama - Python Code Editor")
        self.geometry("900x700") # Taller window for the console

        # Grid Layout: 
        # Column 0: Sidebar (Fixed)
        # Column 1: Editor/Console (Expandable)
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        
        # Row 0: Editor (Takes 80% space)
        # Row 1: Console (Takes 20% space)
        self.grid_rowconfigure(0, weight=4) 
        self.grid_rowconfigure(1, weight=1)

        self.engine = TextEngine()

        # 2. Sidebar Frame
        self.sidebar = ctk.CTkFrame(self, width=150, corner_radius=0)
        self.sidebar.grid(row=0, column=0, rowspan=2, sticky="nsew") # Spans both rows
        
        # 3. Sidebar Buttons
        self.btn_open = ctk.CTkButton(self.sidebar, text="Open File", command=self.open_file)
        self.btn_open.pack(pady=10, padx=10)

        self.btn_save = ctk.CTkButton(self.sidebar, text="Save File", command=self.save_file)
        self.btn_save.pack(pady=10, padx=10)
        
        # --- NEW RUN BUTTON ---
        self.btn_run = ctk.CTkButton(self.sidebar, text="▶ RUN", fg_color="green", hover_color="darkgreen", command=self.run_code)
        self.btn_run.pack(pady=20, padx=10)

        # 4. Editor Display (Row 0)
        self.display_label = ctk.CTkLabel(
            self, 
            text="Start typing...", 
            font=("Consolas", 16), 
            anchor="nw", 
            justify="left",
            fg_color="#1e1e1e",
            text_color="white"
        )
        self.display_label.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

        # 5. Console Display (Row 1) --- NEW ---
        self.console_label = ctk.CTkLabel(
            self,
            text="Console Output...",
            font=("Consolas", 12),
            anchor="nw",
            justify="left",
            fg_color="#000000", # Pure black for terminal feel
            text_color="#00FF00" # Matrix Green text
        )
        self.console_label.grid(row=1, column=1, padx=10, pady=(0, 10), sticky="nsew")

        # 6. Bind Keys
        self.bind("<Key>", self.handle_keypress)

    def handle_keypress(self, event):
        """
        Receives the key event, sends it to the engine, and updates the UI.
        """
        # DEBUG: See what is happening
        print(f"Key sym: {event.keysym}, Char: '{event.char}'")

        # 1. Handle Backspace
        if event.keysym == "BackSpace":
            self.engine.delete_char()
            self.redraw()
            return
            
        # 2. Handle Return (Enter)
        if event.keysym == "Return":
            self.engine.insert_char("\n")
            self.redraw()
            return

        # 3. Handle Left Arrow (MUST BE BEFORE empty char check)
        if event.keysym == "Left":
            new_pos = self.engine.cursor_pos - 1
            self.engine.set_cursor(new_pos)
            self.redraw()
            return

        # 4. Handle Right Arrow (MUST BE BEFORE empty char check)
        if event.keysym == "Right":
            new_pos = self.engine.cursor_pos + 1
            self.engine.set_cursor(new_pos)
            self.redraw()
            return

        # 5. NOW we can safely ignore modifiers (Shift, Ctrl, Alt)
        if event.char == "": 
            return
        
        # 6. Handle Normal Characters
        self.engine.insert_char(event.char)
        self.redraw()

    def redraw(self):
        """
        Gets the text from the engine and paints it on the label.
        """
        full_text = self.engine.get_text()
        self.display_label.configure(text=full_text)

    def open_file(self):
        # 1. Ask user for path
        filepath = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt"), ("Python Files", "*.py"), ("All Files", "*.*")])
        if not filepath:
            return # User cancelled

        # 2. Open and Read
        with open(filepath, "r") as f:
            content = f.read()

        # 3. Load into Engine
        self.engine.load_text(content)
        self.redraw()
        self.title(f"PyEdit - {filepath}")

    def save_file(self):
        # 1. Ask user for path
        filepath = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text Files", "*.txt"), ("Python Files", "*.py"), ("All Files", "*.*")])
        if not filepath:
            return # User cancelled

        # 2. Get text from Engine
        content = self.engine.get_text().replace("|", "") # Remove cursor before saving

        # 3. Write to file
        with open(filepath, "w") as f:
            f.write(content)
        
        self.title(f"PyEdit - {filepath}")

    def run_code(self):
        """
        Saves current code to a temp file and runs it.
        """
        # 1. Get code (remove the cursor pipe!)
        code = self.engine.get_text().replace("|", "")
        
        # 2. Save to a temp file (hidden file)
        temp_filename = ".temp_run.py"
        with open(temp_filename, "w") as f:
            f.write(code)
            
        # 3. Update Console to show we are working...
        self.console_label.configure(text="Running...", text_color="yellow")
        self.update() # Force UI update immediately

        try:
            # 4. Run the subprocess
            # 'python' might need to be 'python3' depending on your OS path
            result = subprocess.run(
                [sys.executable, temp_filename], # sys.executable finds YOUR current python
                capture_output=True,
                text=True,
                timeout=5 # Don't let infinite loops freeze the app!
            )
            
            # 5. Show Output
            if result.returncode == 0:
                # Success: Show stdout
                output = f"✅ SUCCESS:\n{result.stdout}"
                self.console_label.configure(text=output, text_color="#00FF00")
            else:
                # Error: Show stderr
                output = f"❌ ERROR:\n{result.stderr}"
                self.console_label.configure(text=output, text_color="#FF5555")

        except subprocess.TimeoutExpired:
            self.console_label.configure(text="❌ ERROR: Code took too long (Infinite Loop?)", text_color="#FF5555")
        except Exception as e:
            self.console_label.configure(text=f"❌ SYSTEM ERROR: {str(e)}", text_color="#FF5555")


if __name__ == "__main__":
    app = CodeEditorApp()
    app.mainloop()