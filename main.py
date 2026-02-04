import customtkinter as ctk
from tkinter import filedialog
import sys
import io
import contextlib
import traceback
from text_engine import TextEngine

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

        # 4. Editor Display (The Upgrade)
        # We use CTkTextbox because it supports Scrolling and Color Tags
        self.display_area = ctk.CTkTextbox(
            self, 
            font=("Consolas", 16),
            fg_color="#1e1e1e",     # Background
            text_color="#d4d4d4",   # Default text color (Off-white)
            undo=False,             # We handle undo ourselves!
            wrap="none"             # No line wrapping for code
        )
        self.display_area.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        
        # KEY CHANGE: We must disable the user's ability to type directly into this box.
        # Why? Because we want our 'TextEngine' to handle the typing, not Tkinter.
        # We will briefly 'unlock' it only when we redraw.
        self.display_area.configure(state="disabled")
        # ... (after creating self.display_area) ...
        self.display_area.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        self.display_area.configure(state="disabled")

        # 5. Define Syntax Colors (Tags)
        # We act directly on the underlying Tkinter Text widget for tag configuration
        self.display_area.tag_config("keyword", foreground="#F97583")  # Orange/Red (def, class)
        self.display_area.tag_config("control", foreground="#B392F0")  # Purple (if, else)
        self.display_area.tag_config("builtin", foreground="#79B8FF")  # Blue (print, len)
        self.display_area.tag_config("string", foreground="#9ECBFF")   # Light Blue (Quotes) - optional

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

        # 0. Handle Shortcuts (Ctrl+Z / Ctrl+Y)
        # state=4 usually means Control is held down on Windows/Linux
        # On Mac it might be different, but let's try standard first.
        if (event.state & 4) or (event.state & 12): # Checks for Ctrl key
            if event.keysym.lower() == "z":
                self.engine.undo()
                self.redraw()
                return
            if event.keysym.lower() == "y":
                self.engine.redo()
                self.redraw()
                return

        # 1. Handle Backspace
        if event.keysym == "BackSpace":
            self.engine.delete_char()
            self.redraw()
            return
            
        # 2. Handle Return (Smart Indent)
        if event.keysym == "Return":
            # A. Get the text UP TO the cursor
            full_text = self.engine.get_text().replace("|", "")
            cursor_idx = self.engine.cursor_pos
            text_before = full_text[:cursor_idx]
            
            # B. Find the current line content
            # Split by newline and take the last chunk
            lines = text_before.split("\n")
            current_line = lines[-1] if lines else ""
            
            # C. Calculate Indentation (Count leading spaces)
            current_indent = 0
            for char in current_line:
                if char == " ":
                    current_indent += 1
                else:
                    break
            
            # D. Check for Colon (Start of block)
            # .strip() removes whitespace so "def foo():  " becomes "def foo():"
            if current_line.strip().endswith(":"):
                new_indent = current_indent + 4
            else:
                new_indent = current_indent

            # E. Insert Newline + Spaces
            self.engine.insert_char("\n")
            for _ in range(new_indent):
                self.engine.insert_char(" ")
            
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

        # 7. Bind Keys & Mouse
        self.bind("<Key>", self.handle_keypress)
        # Bind specifically to the text box widget
        self.display_area.bind("<Button-1>", self.handle_mouse_click)

    def redraw(self):
        full_text = self.engine.get_text()
        
        self.display_area.configure(state="normal")
        self.display_area.delete("1.0", "end")
        self.display_area.insert("1.0", full_text)
        
        # PAINT THE TEXT NOW
        self.highlight_syntax()
        
        self.display_area.configure(state="disabled")
    def open_file(self):
        # 1. Ask user for paths
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
        Runs the code internally using exec() and captures stdout.
        """
        # 1. Get code
        code = self.engine.get_text().replace("|", "")
        
        # 2. Update Console
        self.console_label.configure(text="Running...", text_color="yellow")
        self.update()

        # 3. Create a memory buffer to catch 'print' statements
        output_buffer = io.StringIO()
        
        try:
            # 4. Run the code while redirecting stdout to our buffer
            # We pass a fresh dictionary {} as globals to keep runs isolated
            with contextlib.redirect_stdout(output_buffer):
                exec(code, {'__name__': '__main__'})
            
            # 5. Success! Get the text from the buffer
            output = output_buffer.getvalue()
            if not output:
                output = "[Program finished with no output]"
                
            self.console_label.configure(text=f"✅ SUCCESS:\n{output}", text_color="#00FF00")

        except Exception:
            # 6. Error! Get the traceback (Error details)
            error_details = traceback.format_exc()
            self.console_label.configure(text=f"❌ ERROR:\n{error_details}", text_color="#FF5555")
        
        finally:
            output_buffer.close()

    def highlight_syntax(self):
        """
        Scans the text and applies colors to keywords.
        """
        # 1. Clear existing tags (clean slate)
        self.display_area.tag_remove("keyword", "1.0", "end")
        self.display_area.tag_remove("control", "1.0", "end")
        self.display_area.tag_remove("builtin", "1.0", "end")

        # 2. Define our Rules
        rules = [
            ("keyword", ["def", "class", "import", "from", "as", "global"]),
            ("control", ["if", "elif", "else", "while", "for", "in", "return", "try", "except", "break", "continue"]),
            ("builtin", ["print", "len", "range", "open", "str", "int", "bool", "True", "False", "None", "self"])
        ]

        # 3. Apply Tags
        # We loop through every word in our lists and search for it in the text box
        for tag_name, words in rules:
            for word in words:
                # Search from start ("1.0") to end
                start_pos = "1.0"
                while True:
                    # search(pattern, start_index, stop_index)
                    # count=count_var gives us the length of the match
                    start_pos = self.display_area.search(word, start_pos, stopindex="end")
                    
                    if not start_pos:
                        break # No more occurrences of this word
                    
                    # Calculate end position: start + length of word
                    # In Tkinter, "1.5 + 3 chars" logic is weird, so we construct it:
                    # We split "1.5" into line "1" and char "5"
                    line, char = start_pos.split(".")
                    end_pos = f"{line}.{int(char) + len(word)}"

                    # Apply the color tag
                    self.display_area.tag_add(tag_name, start_pos, end_pos)
                    
                    # Move to next char to keep searching
                    start_pos = end_pos

    def handle_mouse_click(self, event):
        """
        Translates a 2D mouse click into a 1D linear cursor position.
        """
        # 1. Ask Tkinter: "What text index is under this mouse coordinate?"
        # "@x,y" is the special syntax to query coordinates
        try:
            click_index = self.display_area.index(f"@{event.x},{event.y}")
            
            # 2. Parse "Line.Column" (e.g., "1.5")
            line_str, char_str = click_index.split(".")
            line_clicked = int(line_str)
            char_clicked = int(char_str)

            # 3. Convert to Linear Index
            # We have to sum up the lengths of all previous lines.
            full_text = self.engine.get_text().replace("|", "") # Raw text without cursor
            lines = full_text.split("\n")
            
            linear_pos = 0
            # Add length of all previous lines + 1 (for the \n character itself)
            for i in range(line_clicked - 1):
                if i < len(lines):
                    linear_pos += len(lines[i]) + 1 
            
            linear_pos += char_clicked

            # 4. Tell Engine to move there
            self.engine.set_cursor(linear_pos)
            self.redraw()
            
            # Return "break" to stop Tkinter from trying to focus the disabled widget
            return "break"
            
        except Exception as e:
            print(f"Click Error: {e}")


if __name__ == "__main__":
    app = CodeEditorApp()
    app.mainloop()