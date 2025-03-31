#pip install ollama faiss-cpu numpy sentence-transformers tkinter
#model atleast need 6-gb ram

import ollama  # AI Model (Mistral)
import os  # File handling
import faiss # Vector search for large text
import numpy as np  # Numerical processing
from sentence_transformers import SentenceTransformer  # Converts text to vectors
import tkinter as tk
from tkinter import filedialog, scrolledtext, messagebox

# Load the embedding model
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

class AITextAnalyzerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("AI Text Analyzer")

        # File Selection
        self.label = tk.Label(root, text="Upload a Text File:", font=("Arial", 12))
        self.label.pack(pady=5)

        self.upload_button = tk.Button(root, text="Upload File", command=self.load_text, font=("Arial", 12))
        self.upload_button.pack(pady=5)

        # Question Entry
        self.question_label = tk.Label(root, text="Enter your question:", font=("Arial", 12))
        self.question_label.pack(pady=5)

        self.question_entry = tk.Entry(root, width=50, font=("Arial", 12))
        self.question_entry.pack(pady=5)

        self.ask_button = tk.Button(root, text="Ask", command=self.ask_question, font=("Arial", 12))
        self.ask_button.pack(pady=5)

        # Answer Display
        self.answer_text = scrolledtext.ScrolledText(root, width=60, height=10, font=("Arial", 12))
        self.answer_text.pack(pady=10)

        # Variables to store file content
        self.text_chunks = []
        self.index = None
        self.use_vector_search = False

    def load_text(self):
        """Opens a file dialog to select a text file and processes it."""
        file_path = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt")])
        if not file_path:
            return  # User canceled the file selection

        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                text = file.read()
        except UnicodeDecodeError:
            messagebox.showerror("Error", "Unable to read the file due to encoding issues.")
            return

        # Process text into chunks
        self.text_chunks = self.split_text_into_chunks(text)
        
        # Decide method based on file size
        self.use_vector_search = len(self.text_chunks) > 5  # Use vector search if more than 5 chunks

        if self.use_vector_search:
            self.index, self.text_chunks = self.create_vector_store(self.text_chunks)

        messagebox.showinfo("Success", "Text file loaded successfully!")

    def split_text_into_chunks(self, text, chunk_size=500):
        """Splits text into chunks of a specified word count."""
        words = text.split()
        return [" ".join(words[i:i + chunk_size]) for i in range(0, len(words), chunk_size)]

    def embed_text(self, text):
        """Converts text into a vector embedding."""
        return embedding_model.encode(text)

    def create_vector_store(self, text_chunks):
        """Creates a FAISS vector store for efficient text search."""
        dimension = 384  # Embedding size for MiniLM
        index = faiss.IndexFlatL2(dimension)
        vectors = np.array([self.embed_text(chunk) for chunk in text_chunks], dtype=np.float32)
        index.add(vectors)
        return index, text_chunks

    def find_relevant_text(self, query):
        """Finds the most relevant text chunk using FAISS."""
        query_vector = np.array([self.embed_text(query)], dtype=np.float32)
        _, idx = self.index.search(query_vector, 1)
        return self.text_chunks[idx[0][0]]

    def find_relevant_chunk_simple(self, question):
        """Finds the most relevant chunk using keyword matching."""
        for chunk in self.text_chunks:
            if any(word.lower() in chunk.lower() for word in question.split()):
                return chunk
        return self.text_chunks[0]  # Default to the first chunk if no match

    def ask_question(self):
        """Processes the user's question and sends it to the AI model."""
        question = self.question_entry.get().strip()
        if not question:
            messagebox.showwarning("Warning", "Please enter a question.")
            return

        if self.use_vector_search:
            relevant_text = self.find_relevant_text(question)
        else:
            relevant_text = self.find_relevant_chunk_simple(question)

        # Construct AI prompt
        prompt = (
            "You are an AI that answers questions based ONLY on the given text.\n"
            "If the answer is not in the text, say 'I don't know.'\n\n"
            f"Text:\n{relevant_text}\n\n"
            f"Question: {question}"
        )

        try:
            response = ollama.chat(model="mistral", messages=[{"role": "user", "content": prompt}])
            answer = response.get('message', {}).get('content', "Error: No response from the model.")
        except Exception as e:
            answer = f"Error: {e}"

        # Display answer in the text box
        self.answer_text.delete("1.0", tk.END)
        self.answer_text.insert(tk.END, answer)

# Create and run the Tkinter app
if __name__ == "__main__":
    root = tk.Tk()
    app = AITextAnalyzerApp(root)
    root.mainloop()
