import tkinter as tk
from tkinter import scrolledtext, filedialog, messagebox
import sys
import io
import os

class PythonProjectInterpreterUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Python Project Interpreter")

        # Create a button to open the project entry file (main file)
        self.open_button = tk.Button(root, text="Open Python Main File", command=self.open_file)
        self.open_button.pack(pady=10)

        # Create an "Execute" button
        self.execute_button = tk.Button(root, text="Execute", state=tk.DISABLED, command=self.execute_code)
        self.execute_button.pack(pady=5)

        # Create a text box for output
        self.output_text = scrolledtext.ScrolledText(root, height=15, width=80, wrap=tk.WORD)
        self.output_text.pack(pady=10)

        self.file_path = None  # To store the selected main file path

    def open_file(self):
        # Open a file dialog to select the main Python file (e.g., main.py)
        self.file_path = filedialog.askopenfilename(
            title="Select Python Main File",
            filetypes=(("Python Files", "*.py"), ("All Files", "*.*"))
        )

        # If a file is selected, enable the "Execute" button
        if self.file_path:
            self.execute_button.config(state=tk.NORMAL)
        else:
            self.execute_button.config(state=tk.DISABLED)

    def execute_code(self):
        if not self.file_path:
            messagebox.showerror("Error", "No Python file selected")
            return

        # Clear the output area
        self.output_text.delete("1.0", tk.END)

        # Redirect stdout and stderr to capture print statements and errors
        old_stdout = sys.stdout
        old_stderr = sys.stderr
        redirected_output = io.StringIO()
        sys.stdout = redirected_output
        sys.stderr = redirected_output

        try:
            # Change the working directory to the directory containing the selected file
            # This is crucial for ensuring relative imports work
            script_dir = os.path.dirname(self.file_path)
            os.chdir(script_dir)

            # Read and execute the Python main file
            with open(self.file_path, "r") as file:
                code = file.read()
                exec(code, globals())  # Execute the code

        except Exception as e:
            # Capture and display any errors
            print(f"Error: {e}")

        # Get the output and display it in the output_text box
        output = redirected_output.getvalue()
        self.output_text.insert(tk.END, output)

        # Reset stdout and stderr
        sys.stdout = old_stdout
        sys.stderr = old_stderr


# Main application
root = tk.Tk()
app = PythonProjectInterpreterUI(root)
root.mainloop()
