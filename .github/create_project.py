import os
import sys
import requests
from github import Github

GRAPHQL_API_URL = "https://api.github.com/graphql"


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


def get_training_plan(repo):
    file_contents = repo.get_contents("learn.md")
    markdown_content = file_contents.decoded_content.decode()
    training_plan = {}
    for line in markdown_content.splitlines():
        if line.startswith("##"):
            week_title = line[3:].strip()
            training_plan[week_title] = []
        elif line.startswith("###"):
            sub_section = line[4:].strip()
            training_plan[week_title].append(sub_section)
    return training_plan


def create_project(token, repo_name, training_plan):
    # Split repo_name into owner and repo_name
    owner, repo_name = repo_name.split("/")

    # Get the repository and its existing project
    query = """
    query($owner: String!, $repoName: String!) {
      repository(owner: $owner, name: $repoName) {
        id
        projects(first: 1, orderBy: {field: CREATED_AT, direction: DESC}) {
          edges {
            node {
              id
              columns(first: 10) {
                edges {
                  node {
                    id
                    name
                  }
                }
              }
            }
          }
        }
      }
    }
    """
    variables = {
        "owner": owner,
        "repoName": repo_name
    }
    data = graphql_request(token, query, variables)
    repo_id = data["repository"]["id"]
    project_id = data["repository"]["projects"]["edges"][0]["node"]["id"]
    column_ids = [edge["node"]["id"] for edge in data["repository"]["projects"]["edges"][0]["node"]["columns"]["edges"]]

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

    if not token or not repo_name:
        print("GITHUB_TOKEN or GITHUB_REPOSITORY not found in environment variables.")
        sys.exit(1)

    github = Github(token)
    repo = github.get_repo(repo_name)

    # Fetch and parse the training plan from learn.md
    training_plan = get_training_plan(repo)

    # Create a new repository project
    create_project(token, repo_name, training_plan)
