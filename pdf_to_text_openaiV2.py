import PyPDF2
import openai
import time
import sys
from fpdf import FPDF
from docx import Document

# Initialize OpenAI API key
openai.api_key = "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"

# Initialize rate limits
daily_limit = 40000  # Replace with your daily token limit
tokens_used = 0
requests_used = 0

# Function to convert PDF to text
def pdf_to_text(pdf_path):
    with open(pdf_path, 'rb') as pdf_file:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        text_content = ""
        for page_num in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_num]
            text_content += page.extract_text()
    return text_content

# Function to analyze text with OpenAI API
def analyze_text_with_openai(text, task, max_tokens=100):
    global tokens_used, requests_used
    try:
        response = openai.Completion.create(
            model="text-davinci-002",  # Replace with your model
            prompt=f"Please {task} the following text: {text}",
            max_tokens=max_tokens
        )
        tokens_used += response['usage']['total_tokens']
        requests_used += 1
        return response.choices[0].text.strip()
    except openai.error.RateLimitError:
        print("You exceeded your current quota, please check your plan and billing details.")
        return None
    except Exception as e:
        print(f"OpenAI API error: {e}")
        return None

# Function to save to PDF
def save_to_pdf(text, filename):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, text)
    pdf.output(filename)

# Function to save to Word
def save_to_word(text, filename):
    doc = Document()
    doc.add_paragraph(text)
    doc.save(filename)

# Function to display progress bar
def progress_bar(percentage):
    bar_length = 50
    block = int(round(bar_length * percentage))
    progress = "|" + "=" * block + "-" * (bar_length - block) + "|"
    sys.stdout.write(f"\r{progress} {percentage * 100:.2f}%")

# Main code
if __name__ == "__main__":
    pdf_path = "C:\\Users\\skell\\OneDrive\\Documents\\PDF parser\\CloudImpactBusinessDoc.pdf"
    text_content = pdf_to_text(pdf_path)

    # Split the text into sections if it's too long
    sections = text_content.split('\n\n')
    total_sections = len(sections)
    organized_text = ""

    for i, section in enumerate(sections):
        if tokens_used >= daily_limit:
            print("\nDaily limit reached. Locking terminal.")
            for i in range(86400):  # 24 hours in seconds
                print(f"\rTime remaining: {86400 - i} seconds", end='')
                time.sleep(1)
            tokens_used = 0  # Reset token count after 24 hours
            requests_used = 0  # Reset request count after 24 hours

        remaining_tokens = daily_limit - tokens_used
        print(f"\nTokens used: {tokens_used}, Remaining tokens: {remaining_tokens}")
        print(f"Requests used: {requests_used}")

        task = "proofread and organize"
        result = analyze_text_with_openai(section, task)
        if result:
            organized_text += result + "\n\n"

        # Update progress bar
        percentage = (i + 1) / total_sections
        progress_bar(percentage)

    # Save to PDF and Word when done
    save_to_pdf(organized_text, "final_document.pdf")
    save_to_word(organized_text, "final_document.docx")

    print("\nProcessing complete. Saved to final_document.pdf and final_document.docx.")
