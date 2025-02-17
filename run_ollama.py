import subprocess
import os

OLLAMA_MODEL = "codegemma"
ITERATIONS = 100

FIRST_PROMPT_TEMPLATE = (
    "Write a Python program that does: {user_input}\n"
    "# Everything output by the model will be treated as code.\n"
    "# Any explanatory text should be prefixed with '#'.\n"
    "# Ensure all generated output follows this format to prevent execution errors."
    "# Only output the program do not say anything else no verbosity at all.\n"
)

LOOP_PROMPT_TEMPLATE = (
    "We are improving a Python program designed to do: {user_input}\n"
    "# The current version of the program is provided below.\n"
    "# The execution output from the previous run is also included.\n"
    "# Everything output by the model will be treated as code.\n"
    "# Any explanatory text should be prefixed with '#'.\n"
    "# Ensure all generated output follows this format to prevent execution errors.\n"
    "# Improve the program based on its current state and execution results.\n"
    "# Only output the program do not say anything else no verbosity at all."
)

def run_ollama(prompt):
    """Run Ollama model with the given prompt and return the output."""
    print("Running Ollama with prompt:")
    print(prompt)
    result = subprocess.run(["ollama", "run", OLLAMA_MODEL, prompt], capture_output=True, text=True)
    print("Model output:")
    print(result.stdout)
    return result.stdout.strip()

def save_program(code):
    """Save generated code to program.py, cleaning unnecessary artifacts."""
    lines = code.split("\n")
    if lines and not lines[0].startswith("#"):
        lines = lines[1:]  # Remove the first line if it's not a comment
    
    # Replace '*' at the start of lines with '#'
    lines = [line if not line.startswith("*") else "#" + line[1:] for line in lines]
    
    
    # Remove trailing ``` and anything after it
    cleaned_lines = []
    for line in lines:
        if line.strip() == "```":
            break
        cleaned_lines.append(line)
    cleaned_lines = [line if not line.startswith("```") else "#" + line[1:] for line in cleaned_lines]
    cleaned_code = "\n".join(cleaned_lines)
    
    with open("program.py", "w", encoding="utf-8") as f:
        f.write(cleaned_code)
    print("Saved new program.py:")
    print(cleaned_code)

def run_program():
    """Run program.py and capture all output to stdout.txt."""
    print("Executing program.py...")
    with open("stdout.txt", "w", encoding="utf-8") as out:
        result = subprocess.run(["python", "program.py"], capture_output=True, text=True)
        out.write(result.stdout + "\n" + result.stderr)
    print("Program output:")
    print(result.stdout)
    print("Program errors:")
    print(result.stderr)

def main():
    #user_input = input("Enter prompt for the first run: ex. python program that will generate a colorful gioconda with ascii, the more beautiful the better. no hardcoded ascii if you can avoid it. the program will run without arguments: ")
    user_input = "Write a Python program that types the alphabet. the program will run without arguments nor user input, and it will be proven without any external information"
    first_prompt = FIRST_PROMPT_TEMPLATE.format(user_input=user_input)
    
    # First run
    code = run_ollama(first_prompt)
    save_program(code)
    run_program()
    
    # Loop
    for i in range(ITERATIONS):
        print(f"\nIteration {i+1}...")
        with open("program.py", "r", encoding="utf-8") as f:
            program_code = f.read()
        with open("stdout.txt", "r", encoding="utf-8") as f:
            stdout_content = f.read()
        
        loop_prompt = LOOP_PROMPT_TEMPLATE.format(user_input=user_input)
        loop_prompt += f"\nthis is the program code:\n{program_code}\nand this is the output:\n{stdout_content}"
        
        new_code = run_ollama(loop_prompt)
        save_program(new_code)
        run_program()
    
    print("Loop finished.")

if __name__ == "__main__":
    main()
