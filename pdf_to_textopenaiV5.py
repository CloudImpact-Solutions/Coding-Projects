import PyPDF2
import openai
import time
import sys
import json

# Initialize OpenAI API key
openai.api_key = "your_openai_api_key_here"

# Initialize rate limits based on your subscription
daily_limit = 200  # Replace with your daily request limit
tokens_per_minute = 150000  # Replace with your tokens per minute limit

# Initialize counters
requests_made = 0
tokens_used = 0

# Initialize exponential backoff settings
max_retries = 3
backoff_factor = 1.5

# Function to display a progress bar
def progress_bar(percentage):
    bar_length = 50
    block = int(round(bar_length * percentage))
    progress = "|" + "=" * block + "-" * (bar_length - block) + "|"
    sys.stdout.write(f"\r{progress} {percentage * 100:.2f}%")

# Function to analyze text with OpenAI API
def analyze_text_with_openai(text, task, section_summary):
    global requests_made, tokens_used
    retries = 0

    while retries <= max_retries:
        if requests_made >= daily_limit:
            print("\nDaily limit reached. Locking terminal.")
            time.sleep(86400)  # Sleep for 24 hours
            requests_made = 0  # Reset counters

        try:
            response = openai.Completion.create(
                engine="text-davinci-002",  # Replace with your engine
                prompt=f"Please {task} the following text: {text}",
                max_tokens=100
            )
            tokens_used += response['usage']['total_tokens']
            requests_made += 1
            return response.choices[0].text.strip()

        except openai.error.RateLimitError:
            print(f"Rate limit reached, initiating exponential backoff. Section summary: {section_summary}")
            time.sleep(backoff_factor ** retries)
            retries += 1

        except Exception as e:
            print(f"OpenAI API error: {e}")
            return None

# Main function
def main():
    global requests_made, tokens_used

    # Load the last processed section index if exists
    try:
        with open("last_processed_section.json", "r") as f:
            last_processed_section = json.load(f)["last_processed_section"]
    except FileNotFoundError:
        last_processed_section = 0

    # Your PDF path
    pdf_path = "C:\\Users\\skell\\OneDrive\\Documents\\PDF parser\\CloudImpactBusinessDoc.pdf"

    # Convert PDF to text
    pdf_reader = PyPDF2.PdfReader(open(pdf_path, "rb"))
    total_pages = len(pdf_reader.pages)
    text_content = ""

    for page_num in range(total_pages):
        page = pdf_reader.pages[page_num]
        text_content += page.extract_text()

    # Split the text into sections
    sections = text_content.split("\n\n")
    total_sections = len(sections)

    # Process each section
    for i, section in enumerate(sections[last_processed_section:], start=last_processed_section):
        section_summary = section[:50]  # First 50 characters as summary
        print(f"Attempting to analyze text with OpenAI... Section summary: {section_summary}")

        task = "proofread and organize"
        result = analyze_text_with_openai(section, task, section_summary)

        if result:
            # Save the processed section (you can save it to a file or database)
            print(f"Processed section: {result}")

        # Update progress bar
        progress = (i + 1) / total_sections
        progress_bar(progress)

        # Save the last processed section index
        with open("last_processed_section.json", "w") as f:
            json.dump({"last_processed_section": i}, f)

if __name__ == "__main__":
    main()
