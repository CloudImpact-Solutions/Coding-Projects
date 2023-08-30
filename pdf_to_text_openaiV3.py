import PyPDF2
import openai
import time
from fpdf import FPDF
from docx import Document
import sys

# Initialize OpenAI API key
openai.api_key = "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"

# Initialize rate limits
daily_limit = 40000  # Replace with your daily token limit
tokens_used = 0
requests_used = 0

# Function to convert PDF to text
def pdf_to_text(pdf_path):
    print("Attempting to read PDF...")
    with open(pdf_path, 'rb') as pdf_file:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        text_content = ""
        for page_num in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_num]
            text_content += page.extract_text()
    print("PDF read successfully.")
    return text_content

# Function to analyze text with OpenAI API
def analyze_text_with_openai(text, task, max_tokens=4000):
    global tokens_used, requests_used
    print(f"Attempting to analyze text with OpenAI... Section summary: {text[:50]}...")
    try:
        response = openai.Completion.create(
            model="text-davinci-002",  # Replace with your model
            prompt=f"Please {task} the following text: {text}",
            max_tokens=max_tokens
        )
        tokens_used += response['usage']['total_tokens']
        requests_used += 1
        print(f"Tokens used: {tokens_used}, Remaining tokens: {daily_limit - tokens_used}")
        print(f"Requests used: {requests_used}")
        return response.choices[0].text.strip()
    except openai.error.RateLimitError:
        print("You exceeded your current quota, please check your plan and billing details.")
        return None
    except Exception as e:
        print(f"OpenAI API error: {e}")
        return None

# Function to save to PDF
def save_to_pdf(text, filename):
    print("Attempting to save to PDF...")
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, text)
    pdf.output(filename)
    print("PDF saved successfully.")

# Function to save to Word
def save_to_word(text, filename):
    print("Attempting to save to Word...")
    doc = Document()
    doc.add_paragraph(text)
    doc.save(filename)
    print("Word document saved successfully.")

# Function to display progress bar
def progress_bar(percentage):
    if percentage < 1.0:
        bar_length = 50
        block = int(round(bar_length * percentage))
        progress = "|" + "=" * block + "-" * (bar_length - block) + "|"
        sys.stdout.write(f"\r{progress} {percentage * 100:.2f}%")

# Main code
if __name__ == "__main__":
    print("Script started.")
    pdf_path = "C:\\Users\\skell\\OneDrive\\Documents\\PDF parser\\CloudImpactBusinessDoc.pdf"
    output_folder = "C:\\Users\\skell\\OneDrive\\Documents\\PDF parser\\PARSED\\"
    
    text_content = pdf_to_text(pdf_path)
    print(f"Text content length: {len(text_content)}")
    
    sections = text_content.split('\n\n')
    organized_text = ""
    total_sections = len(sections)
    
    for i, section in enumerate(sections):
        proofread_section = analyze_text_with_openai(section, "proofread and organize")
        if proofread_section:
            organized_text += proofread_section + "\n\n"

        if tokens_used >= daily_limit:
            print("Daily limit reached. Sleeping for 24 hours.")
            time.sleep(86400)
            tokens_used = 0  # Reset token count after 24 hours
            requests_used = 0  # Reset request count after 24 hours

        # Update progress bar
        percentage = (i + 1) / total_sections
        progress_bar(percentage)

    save_to_pdf(organized_text, output_folder + "final_document.pdf")
    save_to_word(organized_text, output_folder + "final_document.docx")

    print("\nProcessing complete. Saved to final_document.pdf and final_document.docx.")
