# enter your code below
from github import Github
from github_token import github_token 
import json
import requests as req

g = Github(github_token)

repo_ironhack = g.get_repo("Os-f-dev/datamex_082020").get_forks()

commits = 0

for repo in repo_ironhack:
    branches_req = g.get_repo(repo.full_name).get_branches()
    for branch in branches_req:
        commits_req = g.get_repo(repo.full_name).get_commits(branch.name)
        commits += len(list(commits_req))

print(commits)
