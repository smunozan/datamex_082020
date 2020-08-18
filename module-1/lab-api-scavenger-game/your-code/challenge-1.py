# enter your code below
from github import Github
from gh_token import github_token 
import json
import requests as req

g = Github(github_token)

repo_ironhack = g.get_repo("Os-f-dev/datamex_082020").get_forks()

languages = []

for repo in repo_ironhack:
    languages_req = g.get_repo(repo.full_name).get_languages()
    for item in languages_req:
        if item not in languages:
            languages.append(item)
        
print(languages)