import ollama
import os
import tkinter as tk
from tkinter import filedialog, scrolledtext, messagebox

# Function to load the text file
def load_text():
    file_path = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt")])
    
    if not file_path:
        messagebox.showwarning("Warning", "No file selected!")
        return None

    if not os.path.exists(file_path):
        messagebox.showerror("Error", "File does not exist!")
        return None

    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except UnicodeDecodeError:
        messagebox.showerror("Error", "Unable to read the file due to encoding issues!")
        return None

# Function to ask the question
def ask_question():
    question = question_entry.get().strip()
    
    if not context_text.get("1.0", tk.END).strip():
        messagebox.showerror("Error", "No text file loaded!")
        return

    if not question:
        messagebox.showwarning("Warning", "Please enter a question!")
        return

    prompt = (
        "You are an AI that answers questions based ONLY on the given text.\n"
        "If the answer is not in the text, say 'I don't know.'\n\n"
        f"Text:\n{context_text.get('1.0', tk.END).strip()}\n\n"
        f"Question: {question}"
    )

    try:
        response = ollama.chat(model='gemma:2b', messages=[{"role": "user", "content": prompt}])
        answer_text.config(state=tk.NORMAL)
        answer_text.delete("1.0", tk.END)
        answer_text.insert(tk.END, response.get('message', {}).get('content', "No response from model."))
        answer_text.config(state=tk.DISABLED)
    except Exception as e:
        messagebox.showerror("Error", f"AI Error: {e}")

# Function to load a file and display content
def load_file():
    text = load_text()
    if text:
        context_text.config(state=tk.NORMAL)
        context_text.delete("1.0", tk.END)
        context_text.insert(tk.END, text)
        context_text.config(state=tk.DISABLED)

# GUI Setup
root = tk.Tk()
root.title("AI Text Analyzer")
root.geometry("600x500")

# Load File Button
load_button = tk.Button(root, text="Load Text File", command=load_file)
load_button.pack(pady=5)

# Display loaded text
context_text = scrolledtext.ScrolledText(root, height=10, wrap=tk.WORD)
context_text.pack(pady=5)
context_text.config(state=tk.DISABLED)

# Question Entry
question_label = tk.Label(root, text="Enter your question:")
question_label.pack()
question_entry = tk.Entry(root, width=50)
question_entry.pack(pady=5)

# Ask Question Button
ask_button = tk.Button(root, text="Ask", command=ask_question)
ask_button.pack(pady=5)

# Answer Display
answer_label = tk.Label(root, text="Answer:")
answer_label.pack()
answer_text = scrolledtext.ScrolledText(root, height=5, wrap=tk.WORD)
answer_text.pack(pady=5)
answer_text.config(state=tk.DISABLED)

# Run GUI
root.mainloop()
