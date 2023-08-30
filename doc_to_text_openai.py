import openai
import time
import sys

# Initialize OpenAI API key
openai.api_key = "your_openai_api_key_here"

# Initialize rate limits
daily_limit = 40000  # Replace with your daily token limit
tokens_used = 0
requests_used = 0

def analyze_text_with_openai(text, task):
    global tokens_used, requests_used
    try:
        response = openai.Completion.create(
            model="text-davinci-002",  # Replace with your model
            prompt=f"Please {task} the following text: {text}",
            max_tokens=100
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

def progress_bar(percentage):
    bar_length = 50
    block = int(round(bar_length * percentage))
    progress = "|" + "=" * block + "-" * (bar_length - block) + "|"
    sys.stdout.write(f"\r{progress} {percentage * 100:.2f}%")

def main():
    global tokens_used, requests_used
    document = "Your document content here."  # Replace with your document content
    sections = document.split("\n")  # Split document into sections by newline
    total_sections = len(sections)
    processed_sections = []

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
            processed_sections.append(result)

        # Update progress bar
        percentage = (i + 1) / total_sections
        progress_bar(percentage)

    # Combine processed sections into a single string
    processed_document = "\n".join(processed_sections)
    print(f"\nProcessed Document:\n{processed_document}")

if __name__ == "__main__":
    main()
