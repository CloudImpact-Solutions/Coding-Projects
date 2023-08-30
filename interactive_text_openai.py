import openai
import time
import json

# Initialize OpenAI API key
openai.api_key = "your_openai_api_key_here"

# Initialize rate limits
daily_limit = 40000  # Replace with your daily token limit
tokens_used = 0

def analyze_text_with_openai(text, task):
    global tokens_used
    try:
        response = openai.Completion.create(
            model="text-davinci-002",  # Replace with your model
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

def main():
    global tokens_used
    while True:
        if tokens_used >= daily_limit:
            print("Daily limit reached. Locking terminal.")
            for i in range(86400):  # 24 hours in seconds
                print(f"Time remaining: {86400 - i} seconds", end='\r')
                time.sleep(1)
            tokens_used = 0  # Reset token count after 24 hours

        remaining_tokens = daily_limit - tokens_used
        print(f"Tokens used: {tokens_used}, Remaining tokens: {remaining_tokens}")

        user_input = input("Enter the text you want to analyze (or type 'exit' to quit): ")
        if user_input.lower() == 'exit':
            break

        task = "proofread and organize"
        result = analyze_text_with_openai(user_input, task)
        if result:
            print(f"Result: {result}")

if __name__ == "__main__":
    main()
