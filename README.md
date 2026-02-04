# 🐍 Squama - The Python Code Editor

![Squama Banner](https://img.shields.io/badge/Squama-v1.0-blue?style=for-the-badge&logo=python) ![Status](https://img.shields.io/badge/Status-Stable-green?style=for-the-badge) ![Build](https://img.shields.io/badge/Build-PyInstaller-orange?style=for-the-badge)

**Squama** (Latin for *Scale*) is a lightweight, high-performance Python IDE built entirely from scratch. Unlike standard text widgets, Squama runs on a custom **Gap Buffer** engine for efficient memory management and features a custom-built **Time Travel (Undo/Redo)** state machine.

---

## 🎬 Demo Video

See Squama in action (Syntax Highlighting, Undo/Redo, and Internal Execution):

[![Watch the Demo](https://img.youtube.com/vi/4tXfDIrUp0c/0.jpg)](https://youtu.be/4tXfDIrUp0c)

> **[Click here to watch the full demo on YouTube](https://youtu.be/4tXfDIrUp0c)**

---

## 🚀 Key Features

### 🧠 Core Engineering
* **Custom Text Engine:** Built on a **Gap Buffer** data structure (O(1) insertions/deletions at cursor) instead of standard string concatenation.
* **Time Travel (Undo/Redo):** Implemented using **Dual Stacks (LIFO)**. Captures full state snapshots to allow infinite undo/redo capability.
* **Internal Execution:** Runs Python code *internally* using `exec()` and `contextlib`. Captures `stdout` in real-time without spawning external command prompt windows.

### 🎨 User Experience
* **Live Syntax Highlighting:** Real-time coloring for Python keywords (`def`, `class`), control flow (`if`, `return`), and built-ins.
* **Smart Indentation:** Auto-detects block starts (lines ending in `:`) and automatically indents the next line.
* **Smart Navigation:**
    * Translates 2D Mouse Clicks to 1D Linear memory indices.
    * **Block Deletion:** Support for highlighting text and deleting entire chunks.
* **Modern UI:** Dark mode interface built with `CustomTkinter`.

---

## 🛠️ Installation

### Option 1: The Easy Way (Windows Portable)
1.  Go to the **[Releases Page](../../releases)**.
2.  Download `Squama_v1.zip`.
3.  Unzip the folder.
4.  Double-click `Squama.exe`.
    * *No Python installation required.*

### Option 2: For Developers (Source Code)
If you want to modify the engine or run it from source:

```bash
# 1. Clone the repository
git clone [https://github.com/YourUsername/Squama.git](https://github.com/YourUsername/Squama.git)

# 2. Install dependencies
pip install customtkinter

# 3. Run the app
python main.py
## 🏗️ Architecture

Squama is not just a wrapper around a text box; it is a full engineering project designed for performance.

### 1. The Gap Buffer
Instead of moving all characters in memory every time you type (which is $O(N)$), Squama maintains a **"Gap"** (a list of `None` values) at the cursor position.

`[H, E, L, L, O, _, _, _, _, _, W, O, R, L, D]`
_— Gap starts at the cursor position —_

* **Efficiency:** When you type, we simply fill the gap.
* **Resizing:** When the gap is full, we double the buffer size using **Dynamic Array resizing**.

### 2. The Undo Stack
Every major action pushes a state snapshot to the `undo_stack`.

* **Undo:** Pop from `undo_stack` $\rightarrow$ Push to `redo_stack`.
* **Redo:** Pop from `redo_stack` $\rightarrow$ Push to `undo_stack`.
* **New Action:** Clears the `redo_stack` (Standard Branching Timeline Logic).

---

## 📜 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

---

**Built with ❤️ and Python by Dhruv.**
