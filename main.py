import os
import json
from datetime import datetime
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
    api_key=os.getenv("GEMINI_API_KEY"),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

LOG_FILE = "refactor_logs.txt"

def log_code(original: str, refactored: str):
    """
    Salva o código original e o refatorado no log.
    """
    timestamp = datetime.now().isoformat()
    with open(LOG_FILE, "a") as f:
        f.write(f"\n=== {timestamp} ===\n")
        f.write("ORIGINAL CODE:\n")
        f.write(original + "\n\n")
        f.write("REFACTORED CODE:\n")
        f.write(refactored + "\n")
        f.write("="*50 + "\n")

def generate_refactored_code(code_snippet: str) -> str:
    """
    Envia o código para a LLM e recebe o código refatorado.
    """
    with open("post-examples.json", "r") as f:
        examples = json.load(f)

    examples_str = ""
    for i, example in enumerate(examples, 1):
        examples_str += f"""
<example-{i}>
<topic>
{example['topic']}
</topic>

<generated-post>
{example['post']}
</generated-post>
</example-{i}>
"""

    prompt = f"""
You are a senior software engineer and code quality expert.  
You excel at analyzing and refactoring code to make it cleaner, more readable, and more efficient — without changing its behavior.

Task: Refactor the code provided by the user.

Guidelines:
- Preserve the original functionality.  
- Improve readability and maintainability (naming, formatting, structure).  
- Apply best practices and idiomatic style for the language used.  
- Simplify complex or redundant logic where possible.  
- Add concise inline comments only where they improve clarity.  
- Do not add extra explanations outside the code block.  

User code:
<code>
{code_snippet}
</code>

Examples:
<examples>
{examples_str}
</examples>

Only output the refactored code inside a properly formatted code block.
"""

    response = client.chat.completions.create(
        model="gemini-2.5-flash",
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": code_snippet}
        ]
    )

    refactored_code = response.choices[0].message.content.strip() or "Could not generate refactored code."
    
    # Salva log automaticamente
    log_code(code_snippet, refactored_code)
    
    return refactored_code

def main():
    print("=== Refatorador de Código LLM ===")
    print("Cole o código que deseja refatorar. Digite 'END' em uma linha separada para finalizar.\n")

    lines = []
    while True:
        line = input()
        if line.strip().upper() == "END":
            break
        lines.append(line)

    user_code = "\n".join(lines)
    refactored = generate_refactored_code(user_code)

    print("\n=== Código Refatorado ===\n")
    print(refactored)
    print(f"\nO código original e o refatorado foram salvos em {LOG_FILE}")

if __name__ == "__main__":
    main()
