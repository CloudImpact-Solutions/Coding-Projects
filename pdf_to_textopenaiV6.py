import PyPDF2
import openai
import time
from fpdf import FPDF
from docx import Document
import sys
import json
import random

# Initialize OpenAI API key
openai.api_key = "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"

# Initialize rate limits
daily_limit = 200
tokens_used = 0
requests_used = 0
max_retries = 5

# Function to convert PDF to text
def pdf_to_text(pdf_path):
    print("Reading PDF...")
    with open(pdf_path, 'rb') as pdf_file:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        text_content = ""
        for page_num in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_num]
            text_content += page.extract_text()
    print("PDF read successfully.")
    return text_content

# Function to analyze text with OpenAI API
def analyze_text_with_openai(text, task):
    global tokens_used, requests_used
    retries = 0
    while retries <= max_retries:
        print(f"Analyzing text with OpenAI... Section summary: {text[:50]}...")
        try:
            response = openai.Completion.create(
                engine="text-davinci-002",
                prompt=f"Please {task} the following text: {text}",
                max_tokens=100
            )
            tokens_used += response['usage']['total_tokens']
            requests_used += 1
            return response.choices[0].text.strip()
        except openai.error.RateLimitError:
            print("Rate limit reached, initiating exponential backoff.")
            sleep_time = (2 ** retries) + random.uniform(0, 0.2 * (2 ** retries))
            time.sleep(sleep_time)
            retries += 1
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

# Function to display a progress bar
def progress_bar(percentage):
    bar_length = 50
    block = int(round(bar_length * percentage))
    progress = "|" + "=" * block + "-" * (bar_length - block) + "|"
    sys.stdout.write(f"\r{progress} {percentage * 100:.2f}%")

# Main function
def main():
    global tokens_used, requests_used

    # PDF path
    pdf_path = "C:\\Users\\skell\\OneDrive\\Documents\\PDF parser\\CloudImpactBusinessDoc.pdf"
    text_content = pdf_to_text(pdf_path)

    # Split the text into sections
    sections = text_content.split('\n\n')
    total_sections = len(sections)
    organized_text = ""

    for i, section in enumerate(sections):
        if tokens_used >= daily_limit:
            print("Daily limit reached. Locking terminal.")
            time.sleep(86400)
            tokens_used = 0
            requests_used = 0

        proofread_section = analyze_text_with_openai(section, "proofread and organize")
        if proofread_section:
            organized_text += proofread_section + "\n\n"

        # Update progress bar
        percentage = (i + 1) / total_sections
        progress_bar(percentage)

    # Save to PDF and Word
    save_to_pdf(organized_text, "C:\\Users\\skell\\OneDrive\\Documents\\PDF parser\\PARSED\\final_document.pdf")
    save_to_word(organized_text, "C:\\Users\\skell\\OneDrive\\Documents\\PDF parser\\PARSED\\final_document.docx")

    print("\nProcessing complete. Saved to final_document.pdf and final_document.docx.")

if __name__ == "__main__":
    main()
