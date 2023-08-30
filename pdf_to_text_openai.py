import PyPDF2
import openai
import time

# Function to convert PDF to text
def pdf_to_text(pdf_path):
    pdf_file = open(pdf_path, 'rb')
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    text = ""
    
    for page_num in range(len(pdf_reader.pages)):
        page = pdf_reader.pages[page_num]
        text += page.extract_text()
        
    pdf_file.close()
    return text

# Function to split text into sections
def split_text_into_sections(text, section_delimiter="\n\n"):
    return text.split(section_delimiter)

# Function to analyze text with OpenAI API
def analyze_text_with_openai(text, task):
    try:
        prompt = f"Please {task} the following text:\n{text}"
        response = openai.Completion.create(
            engine="text-davinci-002",
            prompt=prompt,
            max_tokens=300
        )
        return response.choices[0].text.strip()
    except openai.error.RateLimitError as e:  # Corrected this line
        print(f"OpenAI API error: {e}")
        if "rate limit" in str(e).lower():
            print("Rate limit exceeded, stopping further requests.")
            return None

# Main code
if __name__ == "__main__":
    pdf_path = r"C:\Users\skell\OneDrive\Documents\PDF parser\CloudImpactBusinessDoc.pdf"
    openai.api_key = "your key"
    
    # Convert PDF to text
    text_content = pdf_to_text(pdf_path)
    
    # Split text into sections
    sections = split_text_into_sections(text_content)
    
    # Initialize variables to hold final outputs
    organized_text = ""
    table_of_contents = "Table of Contents\n"
    list_of_changes = "List of Changes/Updates\n"
    
    # Analyze each section with OpenAI API
    for i, section in enumerate(sections):
        # Add a timeout to avoid hitting rate limits too quickly
        time.sleep(1)
        
        # Proofread and organize the section
        proofread_section = analyze_text_with_openai(section, "proofread and organize")
        if proofread_section is None:
            break
        organized_text += proofread_section + "\n\n"
        
        # Generate a title for this section for the table of contents
        section_title = analyze_text_with_openai(section, "generate a title for")
        if section_title is None:
            break
        table_of_contents += f"{i+1}. {section_title}\n"
        
        # Generate a list of changes/updates for this section
        changes = analyze_text_with_openai(section, "suggest changes or updates for")
        if changes is None:
            break
        list_of_changes += f"Section {i+1}:\n{changes}\n"
    
    # Combine everything and save it to a file
    with open("final_document.txt", "w") as f:
        f.write(table_of_contents + "\n")
        f.write(list_of_changes + "\n")
        f.write(organized_text)
