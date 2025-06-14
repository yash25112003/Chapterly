# Chapterly: AI-Powered Book Writing Automation

**Automated Storytelling, Chapter by Chapter.**

Chapterly is an innovative project designed to automate the creative writing process of a book, generating content chapter by chapter and managing its progression directly within a GitHub repository. It leverages advanced AI agents to plan, write, and format chapters, ensuring a consistent and structured narrative.

## Project Description

In the realm of creative writing, consistency and iterative progress can be challenging. Chapterly addresses this by providing an automated solution that acts as a perpetual writing machine. It begins by formulating a book plan, including characters, outline, and chapter titles. Subsequently, it writes chapters daily, ensuring each new chapter builds upon the previous context. The entire process, from content generation to Markdown formatting and version control, is handled autonomously, pushing updates directly to a GitHub repository.

## 🌟 Features

* **Automated Book Planning**: Generates a comprehensive book concept, outline, character details, and a list of chapter titles using an AI planning agent.

* **Iterative Chapter Writing**: Writes new chapters daily, intelligently incorporating context from previously written chapters to maintain narrative flow.

* **AI-Powered Content Creation**: Utilizes advanced Large Language Models (LLMs) to craft detailed and engaging chapter content.

* **Automated Markdown Formatting**: Ensures all generated chapters are properly structured and formatted in Markdown for readability and version control.

* **GitHub Integration**: Automatically commits and pushes new chapters and updates to a specified GitHub repository daily, managing the book's progress.

* **Scalable Agentic Workflow**: Built with CrewAI, allowing for modular and extensible agent-based tasks for planning, writing, and formatting.

## 🛠️ Technical Implementation

### 🔍 Core Technologies

* **Python**: The primary programming language for the entire application.

* **CrewAI**: An AI agent framework used to orchestrate multi-agent workflows for planning, writing, and formatting tasks.

* **Groq LLM (e.g., `gemma2-9b-it`)**: High-performance Large Language Model integrated via `langchain-groq` for generating creative content efficiently.

* **Langchain-Groq**: Provides the interface to connect CrewAI agents with Groq's LLM services.

* **PyGithub**: Python library for interacting with the GitHub API to read existing files and commit new content.

* **`python-dotenv`**: For managing environment variables (API keys, etc.).

* **`requests`**: For making HTTP requests to the GitHub API.

* **GitHub Actions**: Automates the daily execution of the Python script and handles continuous integration and deployment (CI/CD) to the GitHub repository.

### 📂 Project Structure

```bash
chapterly/
├── main.py                   # Main script containing CrewAI agents, tasks, and GitHub logic
├── .github/
│   └── workflows/
│       └── temp.yaml         # GitHub Actions workflow file for daily automation
├── .env                      # Environment variables (API keys, etc.)
└── requirements.txt          # Python dependencies
```

## 🚀 Getting Started

Follow these steps to set up and run Chapterly on your local machine, and to configure its GitHub Actions automation.

### Prerequisites

* Python 3.9+

* `pip` package manager

* A GitHub repository where you want the book to be written.

### Installation

1.  **Clone the repository:**

    ```bash
    git clone <your-repository-url>
    cd chapterly
    ```

2.  **Create and activate a virtual environment:**

    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

3.  **Install Dependencies:**
    Create a `requirements.txt` file in your project root with the following content:

    ```
    crewai
    groq
    PyGithub
    python-dotenv
    requests
    langchain-groq
    ```

    Then, install them:

    ```bash
    pip install -r requirements.txt
    ```

### Configuration

1.  **Environment Variables (`.env` file):**
    Create a file named `.env` in the root of your project:

    ```
    GROQ_API_KEY="YOUR_GROQ_API_KEY"
    G_TOKEN="YOUR_GITHUB_PERSONAL_ACCESS_TOKEN"
    ```

    * **`GROQ_API_KEY`**: Obtain this from [Groq](https://groq.com/).

    * **`G_TOKEN`**: This is a GitHub Personal Access Token (PAT).

        * Go to your GitHub profile **Settings** > **Developer settings** > **Personal access tokens** > **Tokens (classic)**.

        * Click "Generate new token".

        * Give it a descriptive name (e.g., "Chapterly_Automation_PAT").

        * For **Scope**, select `repo` (full control of private repositories) if your book repository is private. If it's public, `public_repo` might suffice, but `repo` provides broader access and is safer for automation involving commits.

        * **Important**: Copy the generated token immediately. You won't see it again.

2.  **GitHub Repository Configuration (`main.py`):**
    Open `main.py` and ensure the following lines are configured correctly for your repository:

    ```
    GITHUB_USERNAME = "your_github_username"  # e.g., "yash25112003"
    REPO_OWNER = "your_repo_owner"            # e.g., "yash25112003"
    REPO_NAME_PART = "your_repo_name"         # e.g., "ai-book-writer"
    BRANCH = "main"                           # Or "master", "develop", etc.
    ```

## 🚀 Running the Automation (GitHub Actions)

To automate the daily chapter writing and pushing, you need to set up a GitHub Actions workflow.

1.  **Create the Workflow File:**
    In your GitHub repository, create the directory structure `.github/workflows/` and add a file named `temp.yaml` (or any `.yaml`/`.yml` name) inside it.

    Copy the following content into `.github/workflows/temp.yaml`:

    ```yaml
    # .github/workflows/temp.yaml

    name: Automate Chapterly Project

    on:
      schedule:
        - cron: "0 0 * * *"  # Runs daily at midnight UTC
      workflow_dispatch:  # Allows manual execution from GitHub Actions UI

    permissions:
      contents: write  # Grant write permissions to the GITHUB_TOKEN to commit changes

    jobs:
      run-chapterly-script:
        runs-on: ubuntu-latest
        
        steps:
          - name: ✅ Checkout Repository
            uses: actions/checkout@v3

          - name: 🐍 Set Up Python
            uses: actions/setup-python@v4
            with:
              python-version: '3.9' # Ensure this matches your project's Python version, adjust if needed

          - name: 📦 Install Dependencies
            run: |
              # Upgrade pip, setuptools, wheel to ensure latest versions
              pip install --upgrade pip setuptools wheel
              
              # Install dependencies from requirements.txt if it exists
              if [ -f requirements.txt ]; then pip install -r requirements.txt; fi
              
              # Install specific packages required by your project
              # Assuming crewai, groq, PyGithub are needed based on your main.py
              pip install --no-cache-dir crewai groq PyGithub python-dotenv requests

          - name: 🚀 Run Chapterly Python Script
            # Set environment variables from GitHub Secrets
            env:
              GROQ_API_KEY: ${{ secrets.GROQ_API_KEY }}
              G_TOKEN: ${{ secrets.G_TOKEN }} # Use G_TOKEN as defined in your main.py
            run: python main.py

          - name: ⬆️ Commit and Push Changes (if any)
            # GITHUB_TOKEN is automatically provided by GitHub Actions with `contents: write` permission
            env:
              GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
            run: |
              # Configure git user for commits
              git config user.name github-actions
              git config user.email github-actions@github.com
              
              # Stage all changes
              git add .
              
              # Check if there are any changes to commit, then commit them
              # `git diff --staged --quiet` returns 0 if no diffs, 1 if diffs
              git diff --staged --quiet || git commit -m "🔄 Auto-update: Chapterly Project progress"
              
              # Pull latest changes and rebase before pushing to avoid conflicts
              git pull --rebase
              
              # Push the changes to the repository
              git push
    ```

2.  **Add GitHub Secrets for Workflow:**
    For the GitHub Actions workflow to access your API keys, you need to add them as repository secrets:

    * In your GitHub repository, go to **Settings**.

    * In the left sidebar, click on **Secrets and variables** > **Actions**.

    * Click on **New repository secret**.

    * Add the following secrets:

        * **`GROQ_API_KEY`**: Paste your Groq API key (the same one from your `.env` file).

        * **`G_TOKEN`**: Paste your GitHub Personal Access Token (PAT) here.

### Usage

Once the GitHub Actions workflow is committed, it will automatically:

* **Run Daily**: At midnight UTC, the workflow will execute `main.py`.

* **Write/Format Chapter**: The script will determine the next chapter, generate its content, format it, and attempt to commit it to your repository.

* **Push Changes**: The workflow will push any new or updated chapter files to your `main` (or specified) branch.

You can also trigger the workflow manually at any time by going to the "Actions" tab in your GitHub repository, selecting "Automate Chapterly Project" from the workflows list, and clicking "Run workflow."

## Local Execution (for testing/development)

While the project is designed for automation via GitHub Actions, you can run `main.py` locally for testing or development:

```bash
source venv/bin/activate # Activate your virtual environment
python main.py
```

This will execute the script once and attempt to write/update a chapter, committing it to your local git history and then pushing it to GitHub. Ensure your `.env` file is correctly configured for local runs.

## Contributing

Contributions are welcome! If you have suggestions for improvements, new features, or bug fixes, please follow these steps:

1.  Fork the repository.
2.  Create a new branch (`git checkout -b feature/your-feature-name` or `bugfix/your-bug-fix`).
3.  Make your changes and ensure tests pass (if applicable).
4.  Commit your changes (`git commit -m 'Add new feature'`).
5.  Push to the branch (`git push origin feature/your-feature-name`).
6.  Open a Pull Request.
