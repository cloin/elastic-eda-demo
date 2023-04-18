import os
import sys
import base64
import requests
from github import Github

GRAPHQL_API_URL = "https://api.github.com/graphql"

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

def graphql_request(token, query, variables=None):
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    response = requests.post(GRAPHQL_API_URL, json={"query": query, "variables": variables}, headers=headers)
    response.raise_for_status()
    json_response = response.json()
    if 'data' not in json_response:
        print(f"Error in GraphQL response: {json_response}")
        sys.exit(1)
    return json_response["data"]


def create_project(token, repo_name, training_plan):
    # Fetch repository information using GraphQL
    query = """
    query($repoName: String!, $repoOwner: String!) {
        repository(name: $repoName, owner: $repoOwner) {
            id
            owner {
                id
            }
        }
    }
    """
    variables = {
        "repoName": repo_name_split,
        "repoOwner": repo_owner_split
    }
    data = graphql_request(token, query, variables)
    print(data)

    # Create a new repository project
    mutation = """
    mutation($ownerId: ID!, $repoId: ID!, $name: String!) {
        createProjectV2(input: {ownerId: $ownerId, repositoryId: $repoId, title: $name}) {
            projectV2 {
                number
            }
        }
    }
    """
    variables = {
        "ownerId": data["repository"]["owner"]["id"],
        "repoId": data["repository"]["id"],
        "name": "ELK Training Plan",
    }
    data = graphql_request(token, mutation, variables)
    print(data)
    project_id = data["createProjectV2"]["project"]["number"]

    # Create columns for the new project
    column_names = ["To Do", "In Progress", "Done"]
    column_ids = []

    for column_name in column_names:
        mutation = """
        mutation($projectId: ID!, $name: String!) {
            createProjectColumn(input: {projectId: $projectId, name: $name}) {
                projectColumn {
                    id
                }
            }
        }
        """
        variables = {
            "projectId": project_id,
            "name": column_name
        }
        data = graphql_request(token, mutation, variables)
        print(data)
        column_ids.append(data["createProjectColumn"]["projectColumn"]["id"])

    # Add weeks as tasks to the "To Do" column
    todo_column_id = column_ids[0]

    for week_title, sub_sections in training_plan.items():
        card_content = f"**{week_title}**\n\n" + "\n".join(f"- {sub_section}" for sub_section in sub_sections)

    # Add weeks as tasks to the "To Do" column
    todo_column_id = column_ids[0]

    for week_title, sub_sections in training_plan.items():
        card_content = f"**{week_title}**\n\n" + "\n".join(f"- {sub_section}" for sub_section in sub_sections)

        # Create a new issue for the week
        issue = repo.create_issue(title=week_title, body=card_content)

        # Add the issue as a card in the "To Do" column
        mutation = """
        mutation($columnId: ID!, $contentId: ID!) {
            addProjectCard(input: {projectColumnId: $columnId, contentId: $contentId}) {
                projectCard {
                    id
                }
            }
        }
        """
        variables = {
            "columnId": todo_column_id,
            "contentId": f"Issue:{issue.id}"
        }
        graphql_request(token, mutation, variables)

if __name__ == "__main__":
    token = os.environ.get("GITHUB_TOKEN")
    repo_name = os.environ.get("GITHUB_REPOSITORY")
    repo_owner_split, repo_name_split = repo_name.split("/")

    if not token or not repo_name:
        print("GITHUB_TOKEN or GITHUB_REPOSITORY not found in environment variables.")
        sys.exit(1)

    github = Github(token)
    repo = github.get_repo(repo_name)

    # Fetch and parse the training plan from learn.md
    training_plan = get_training_plan(repo)

    # Create a new repository project
    create_project(token, repo_name, training_plan)
