﻿import sys
from git import Repo, GitCommandError

def check_brackets(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    stack = []
    for i, char in enumerate(content):
        if char == '{':
            stack.append(i)
        elif char == '}':
            if not stack:
                print(f"Unmatched closing bracket at position {i} in file {file_path}")
                return False
            stack.pop()
    
    if stack:
        for pos in stack:
            print(f"Unmatched opening bracket at position {pos} in file {file_path}")
        return False
    
    print(f"All brackets are properly closed in file {file_path}.")
    return True

def get_changed_resx_files(repo_path, source_branch='main'):
    repo = Repo(repo_path)
    
    # Fetch the branches to ensure they are available locally
    try:
        repo.git.fetch('origin', source_branch)
        repo.git.fetch('origin', repo.active_branch.name)
    except GitCommandError as e:
        print(f"Error fetching branches: {e}")
        sys.exit(1)
    
    try:
        current_branch = repo.active_branch.name
    except TypeError:
        # Handle detached HEAD state
        current_branch = repo.git.rev_parse('--abbrev-ref', 'HEAD')
        if current_branch == 'HEAD':
            current_branch = repo.head.commit.hexsha

    # Get the diff between the current branch and the source branch
    try:
        diff = repo.git.diff(f'origin/{source_branch}...{current_branch}', name_only=True)
    except GitCommandError as e:
        print(f"Error running git diff: {e}")
        sys.exit(1)
    
    # Filter the diff to include only .resx files
    changed_files = [file for file in diff.split('\n') if file.endswith('.resx')]
    return changed_files

def main(repo_path, source_branch='main'):
    changed_resx_files = get_changed_resx_files(repo_path, source_branch)
    if not changed_resx_files:
        print("No .resx files changed.")
        return
    
    all_files_valid = True
    for file_path in changed_resx_files:
        if not check_brackets(file_path):
            all_files_valid = False
    
    if not all_files_valid:
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python check_brackets.py <repo_path> [<source_branch>]")
        sys.exit(1)
    
    repo_path = sys.argv[1]
    source_branch = sys.argv[2] if len(sys.argv) > 2 else 'main'
    main(repo_path, source_branch)