import openai
import time
import json
import PyPDF2
from fpdf import FPDF
from docx import Document
import random
import sys

# Initialize OpenAI API key
openai.api_key = "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"

# Initialize rate limits
daily_limit = 40000
tokens_used = 0

def analyze_text_with_openai(text, task):
    global tokens_used
    try:
        response = openai.Completion.create(
            model="text-davinci-002",
            prompt=f"Please {task} the following text: {text}",
            max_tokens=100
        )
        tokens_used += response['usage']['total_tokens']
        return response.choices[0].text.strip()
    except openai.error.RateLimitError:
        print("You exceeded your current quota, please check your plan and billing details.")
        return None
    except Exception as e:
        print(f"OpenAI API error: {e}")
        return None

def pdf_to_text(pdf_path):
    with open(pdf_path, 'rb') as pdf_file:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        text_content = ""
        for page_num in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_num]
            text_content += page.extract_text()
    return text_content

def save_to_pdf(text, filename):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, text)
    pdf.output(filename)

def save_to_word(text, filename):
    doc = Document()
    doc.add_paragraph(text)
    doc.save(filename)

def main():
    global tokens_used
    while True:
        if tokens_used >= daily_limit:
            print("Daily limit reached. Locking terminal.")
            time.sleep(86400)
            tokens_used = 0

        remaining_tokens = daily_limit - tokens_used
        print(f"Tokens used: {tokens_used}, Remaining tokens: {remaining_tokens}")

        print("Choose an operation:")
        print("1. Analyze text")
        print("2. Process PDF")
        print("3. Exit")

        choice = input("Your choice: ")
        if choice == "3":
            break
        elif choice == "1":
            user_input = input("Enter the text you want to analyze: ")
            task = "proofread and organize"
            result = analyze_text_with_openai(user_input, task)
            if result:
                print(f"Result: {result}")
        elif choice == "2":
            pdf_path = input("Enter the full path to your PDF: ")
            text_content = pdf_to_text(pdf_path)
            sections = text_content.split('\n\n')
            organized_text = ""
            for section in sections:
                proofread_section = analyze_text_with_openai(section, "proofread and organize")
                if proofread_section:
                    organized_text += proofread_section + "\n\n"
            pdf_save_path = input("Enter the path where you want to save the processed PDF: ")
            word_save_path = input("Enter the path where you want to save the processed Word document: ")
            save_to_pdf(organized_text, pdf_save_path)
            save_to_word(organized_text, word_save_path)
            print("Processing complete. Saved processed files.")

if __name__ == "__main__":
    main()
