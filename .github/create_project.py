import os
import sys
import base64
from github import Github

def get_training_plan(repo):
    # Fetch the content of the learn.md file
    try:
        learn_md = repo.get_contents("learn.md")
        content = base64.b64decode(learn_md.content).decode("utf-8")
    except Exception as e:
        print(f"Error fetching learn.md: {e}")
        sys.exit(1)

    # Parse the content of the learn.md file into a dictionary
    training_plan = {}
    current_week = None

    for line in content.splitlines():
        if line.startswith("## "):
            current_week = line[3:].strip()
            training_plan[current_week] = []
        elif line.startswith("### "):
            sub_section = line[4:].strip()
            if current_week:
                training_plan[current_week].append(sub_section)

    return training_plan

def create_project():
    token = os.environ.get("GITHUB_TOKEN")
    repo_name = os.environ.get("GITHUB_REPOSITORY")

    if not token or not repo_name:
        print("GITHUB_TOKEN or GITHUB_REPOSITORY not found in environment variables.")
        sys.exit(1)

    github = Github(token)
    repo = github.get_repo(repo_name)

    # Fetch and parse the training plan from learn.md
    training_plan = get_training_plan(repo)

    # Get the authenticated user
    user = github.get_user()

    # Create a new user-level project
    project = user.create_project("ELK Training Plan", body="A project to track progress in the ELK training plan.")
    
    # Add columns to the project
    todo_column = project.create_column("To Do")
    project.create_column("In Progress")
    project.create_column("Done")

    # Add weeks as tasks to the "To Do" column
    for week_title, sub_sections in training_plan.items():
        card_content = f"**{week_title}**\n\n" + "\n".join(f"- {sub_section}" for sub_section in sub_sections)
        todo_column.create_card(note=card_content)

if __name__ == "__main__":
    create_project()
