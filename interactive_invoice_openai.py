import openai
import time
import json
import PyPDF2
from fpdf import FPDF
from docx import Document
import random
import re
import sys

# Initialize OpenAI API key
openai.api_key = "your_openai_api_key_here"

# Initialize rate limits
daily_limit = 40000
tokens_used = 0

# Function to analyze text with OpenAI API
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

# Function to convert PDF to text
def pdf_to_text(pdf_path):
    with open(pdf_path, 'rb') as pdf_file:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        text_content = ""
        for page_num in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_num]
            text_content += page.extract_text()
    return text_content

# Function to parse invoice for various attributes
def parse_invoice(text):
    part_numbers = re.findall(r'Part No: (\w+)', text)
    fulfillment_plants = re.findall(r'Fulfillment Plant: (\w+)', text)
    shipping_methods = re.findall(r'Shipping Method: (\w+)', text)
    vendor_numbers = re.findall(r'Vendor No: (\w+)', text)
    customer_numbers = re.findall(r'Customer No: (\w+)', text)
    purchase_order_numbers = re.findall(r'PO No: (\w+)', text)

    print(f"Part Numbers: {part_numbers}")
    print(f"Fulfillment Plants: {fulfillment_plants}")
    print(f"Shipping Methods: {shipping_methods}")
    print(f"Vendor Numbers: {vendor_numbers}")
    print(f"Customer Numbers: {customer_numbers}")
    print(f"Purchase Order Numbers: {purchase_order_numbers}")

# Main function
def main():
    global tokens_used
    while True:
        if tokens_used >= daily_limit:
            print("Daily limit reached. Locking terminal.")
            time.sleep(86400)
            tokens_used = 0

        remaining_tokens = daily_limit - tokens_used
        print(f"Tokens used: {tokens_used}, Remaining tokens: {remaining_tokens}")

        print("\nChoose an operation:")
        print("1. Analyze text")
        print("2. Process PDF")
        print("3. Invoice Operations")
        print("4. Exit")

        choice = input("Your choice: ")
        if choice == "4":
            break
        elif choice == "1":
            user_input = input("Enter the text you want to analyze: ")
            task = input("Enter the task (e.g., 'proofread and organize'): ")
            result = analyze_text_with_openai(user_input, task)
            if result:
                print(f"Result: {result}")
        elif choice == "2":
            pdf_path = input("Enter the full path to your PDF: ")
            text_content = pdf_to_text(pdf_path)
            task = "proofread and organize"
            organized_text = analyze_text_with_openai(text_content, task)
            if organized_text:
                save_to_pdf(organized_text, "processed_pdf.pdf")
                save_to_word(organized_text, "processed_word.docx")
                print("Processing complete. Saved processed files.")
        elif choice == "3":
            invoice_text = input("Paste the invoice text here: ")
            parse_invoice(invoice_text)

if __name__ == "__main__":
    main()
