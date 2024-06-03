import git
import os
import yaml

def check_submodule_status(repo_path, submodule_path):
    try:
        # Load the main repository
        repo = git.Repo(repo_path)
        
        #   Ensure the repository is not bare
        if repo.bare:
            print(f"The repository at {repo_path} is bare.")
            return False

        submodulepath = submodule_path
        # Load the submodule
        submodule = repo.submodule(submodulepath)

        # Check if the submodule is up to date
        submodule_module = submodule.module()
        current_commit = submodule_module.head.commit
        latest_commit = submodule_module.remotes.origin.fetch()[0].commit

        if current_commit == latest_commit:
            print(f"The DBC Files at {submodulepath} are up to date.")
            return True
        else:
            print(f"The DBC Files at {submodulepath} are not up to date.")
            return False
    
    except Exception as e:
        print(f"An error occurred: {e}")
        return False

def update_submodule(repo_path, submodule_path):
    try:
        # Load the main repository
        repo = git.Repo(repo_path)
        # Load and update the submodule
        submodule = repo.submodule(submodule_path)
        repo.git.submodule('update', '--remote', submodule_path)
        print(f"The DBC Files at {submodule_path} have been updated.")
    
    except Exception as e:
        print(f"An error occurred during the update: {e}")
