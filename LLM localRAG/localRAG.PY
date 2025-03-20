import ollama
import os

def load_text():
    """Prompt the user to enter a file path and read the file content."""
    file_path = input("Enter the path of the text file: ").strip()

    if not os.path.exists(file_path):
        print("Error: File does not exist. Please enter a valid file path.")
        return None

    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except UnicodeDecodeError:
        print("Error: Unable to read the file due to encoding issues.")
        return None

def ask_question(context, question):
    """Sends the context and question to the local LLM and handles errors."""
    if not context.strip():
        return "Error: The text file is empty."

    prompt = (
        "You are an AI that answers questions based ONLY on the given text.\n"
        "If the answer is not in the text, say 'I don't know.'\n\n"
        f"Text:\n{context}\n\n"
        f"Question: {question}"
    )

    try:
        response = ollama.chat(model='mistral', messages=[{"role": "user", "content": prompt}])
        return response.get('message', {}).get('content', "Error: No response from the model.")
    except Exception as e:
        return f"Error: {e}"

if __name__ == "__main__":
    context = load_text()
    
    if context:
        print("\nText file loaded successfully!\n")
        while True:
            question = input("Ask a question (or type 'exit' to quit): ").strip()
            if question.lower() == "exit":
                print("Exiting...")
                break
            answer = ask_question(context, question)
            print("\nAnswer:", answer, "\n")
