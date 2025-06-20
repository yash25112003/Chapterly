import os
import re
import base64
import requests
import traceback
from crewai import Agent, Task, Crew  # your crewai agents and related modules
from github import Github
from langchain_groq import ChatGroq
from dotenv import load_dotenv

load_dotenv() 

# ===================================================
# Environment & GitHub Configuration (update as needed)
# ===================================================

# Define LLM Model
llm = ChatGroq(
    temperature=0,
    model_name="gemma2-9b-it",
    api_key=os.getenv('GROQ_API_KEY'),
)

# Set your GitHub token in an environment variable or here:
GITHUB_TOKEN = os.getenv('G_TOKEN')
GITHUB_USERNAME = "GITHUB_USERNAME"
REPO_OWNER = "REPO_OWNER_NAME"
REPO_NAME_PART = "ai-book-writer"
REPO_FULL_NAME = f"{REPO_OWNER}/{REPO_NAME_PART}"
BRANCH = "main"  # Change if using a different branch
BASE_URL = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME_PART}/contents"


# ===================================================
# Define CrewAI Agents
# ===================================================

planning_agent = Agent(
    role="Planning Agent",
    goal="Develop the book's concept, outline, characters, world details, and generate a list of 4 chapter titles in a proper markdown format for making it readable. Use all markdown format structuring for heading and paragraphs to make it readable",
    backstory="An experienced author specializing in planning and structuring novels.",
    verbose=True,
    allow_delegation=False,  # Disable delegation to avoid format issues
    llm=llm  # ✅ Use Groq model
)

writing_agent = Agent(
    role="Writing Agent",
    goal="Write detailed chapters based on the provided outline and chapter titles. Each chapter should be at least 300 words. Use all markdown format structuring for heading and paragraphs to make it readable",
    backstory="A creative writer adept at bringing stories to life.",
    verbose=True,
    allow_delegation=False,  # Disable delegation to avoid format issues
    llm=llm  # ✅ Use Groq model
)

formatting_agent = Agent(
    role="Markdown Formatting Agent",
    goal="Format and structure the text into a well-structured Markdown document with proper headings, spacing, and readability improvements.",
    backstory="A skilled editor who ensures content is properly formatted for GitHub Markdown preview.",
    verbose=True,
    allow_delegation=False,  # Disable delegation to avoid format issues
    llm=llm  # ✅ Use Groq model
)

# ===================================================
# Define CrewAI Tasks (With expected_output)
# ===================================================
plan_book_task = Task(
    description=(
        "Develop a book concept, outline, characters, and generate 4 chapter titles in a structured way. "
        "The final chapter (Chapter 4) should clearly indicate the conclusion of the story, with a relevant title such as 'The Final Resolution', 'The Journey's End', or 'Conclusion'. "
        "Use proper Markdown structuring for headings and paragraphs to make it readable."
    ),
    agent=planning_agent,
    expected_output="A structured book outline with 11 clearly numbered chapter titles, where Chapter 11 is the final chapter."
)


write_chapter_task = Task(
    description="Write a detailed chapter based on the given title and previous chapters' context.",
    agent=writing_agent,
    expected_output="A well-structured 300-word chapter continuing the story."
)

format_markdown_task = Task(
    description="Format the chapter content to ensure correct Markdown headings, paragraphs, lists, and readability improvements.",
    agent=formatting_agent,
    expected_output="A fully formatted Markdown document with improved structure and readability."
)

# ===================================================
# GitHub Functions
# ===================================================
def github_commit(repo_name, file_content, filename, commit_message):
    """
    Commit a file to GitHub.
    """
    try:
        g = Github(GITHUB_TOKEN)
        repo = g.get_repo(repo_name)

        try:
            contents = repo.get_contents(filename, ref=BRANCH)
            repo.update_file(contents.path, commit_message, file_content, contents.sha, branch=BRANCH)
            print(f"Updated {filename} successfully.")
        except:
            repo.create_file(filename, commit_message, file_content, branch=BRANCH)
            print(f"Created {filename} successfully.")

    except Exception as e:
        print(f"Error committing {filename}: {e}")
        traceback.print_exc()
        
def list_files(path=""):
    """
    List files in the GitHub repository path.
    """
    url = f"{BASE_URL}/{path}?ref={BRANCH}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    response = requests.get(url, headers=headers)
    return response.json() if response.status_code == 200 else None

def read_file(file_path):
    """
    Read and decode a file from GitHub.
    """
    url = f"{BASE_URL}/{file_path}?ref={BRANCH}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return base64.b64decode(response.json()["content"]).decode("utf-8")
    return None
    
def extract_content(crew_result):
    """
    Safely extract content from CrewAI result.
    """
    try:
        # If result is a list-like object
        if hasattr(crew_result, '__iter__') and not isinstance(crew_result, str):
            return "\n".join(str(item) for item in crew_result)
        
        # If result is a string
        return str(crew_result)
    except Exception as e:
        print(f"Error extracting crew result: {e}")
        return ""

# ===================================================
# Main Daily Runner
# ===================================================
def extract_number(fname):
    match = re.search(r"chapter(\d+)_", fname)
    return int(match.group(1)) if match else 0
    
def main():
    plan_filename = "book_plan.md"
    plan_content = read_file(plan_filename)

    if plan_content is None:
        print("Day 1: Creating book plan and first chapter...")

        # Run planning task using CrewAI
        crew = Crew(agents=[planning_agent], tasks=[plan_book_task])
        plan_result = crew.kickoff()
        plan_text = extract_content(plan_result)

        github_commit(REPO_FULL_NAME, plan_text, plan_filename, "Added book plan")
        chapter_titles = [line.split(".", 1)[1].strip() for line in plan_text.splitlines() if "." in line]
    else:
        print("Continuing book writing...")
        chapter_titles = [line.split(".", 1)[1].strip() for line in plan_content.splitlines() if "." in line]

    files = list_files()
    chapter_files = [file["name"] for file in files if file["name"].startswith("chapter") and file["name"].endswith(".md")]
    chapter_files_sorted = sorted(chapter_files, key=extract_number)
    current_chapter_count = len(chapter_files_sorted)

    if current_chapter_count >= 4:
        print("All 4 chapters are written. Process complete.")
        return

    next_chapter_number = current_chapter_count + 1
    if next_chapter_number == 4:
      next_chapter_title = "The Grand Finale"
    else:
      next_chapter_title = chapter_titles[next_chapter_number - 1] if next_chapter_number - 1 < len(chapter_titles) else f"Chapter {next_chapter_number}"

    context_text = "\n".join(
        [f"Excerpt from {fname}: " + read_file(fname)[:300] for fname in chapter_files_sorted[-3:]]
    )

    # Run writing task using CrewAI
    write_chapter_task.description = f"Write Chapter {next_chapter_number}: {next_chapter_title}. Context: {context_text}"
    crew = Crew(agents=[writing_agent], tasks=[write_chapter_task])
    chapter_result = extract_content(crew.kickoff())

    # Run formatting task using CrewAI
    format_markdown_task.description = f"Format the following chapter content to ensure correct Markdown structure: {chapter_result}"
    crew = Crew(agents=[formatting_agent], tasks=[format_markdown_task])
    formatted_chapter = extract_content(crew.kickoff())

    chapter_filename = f"chapter{next_chapter_number}_{next_chapter_title.replace(' ', '_')}.md"
    github_commit(REPO_FULL_NAME, formatted_chapter, chapter_filename, f"Added {chapter_filename}")
    print(f"Day {next_chapter_number} completed: {chapter_filename} committed.")


if __name__ == "__main__":
    main()