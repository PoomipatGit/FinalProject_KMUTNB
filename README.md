# FinalProject_KMUTNB
# 1. Create a README file with the project title as the first heading
echo "# FinalProject_KMUTNB" >> README.md

# 2. Turn this local folder into a Git repository
git init

# 3. Stage the README file (tells Git to track it). Swap with 'git add .' to add everything in the folder.
git add README.md

# 4. Save your staged changes into the local history with a descriptive message
git commit -m "first commit"

# 5. Rename your default local branch to 'main' to match modern GitHub naming
git branch -M main

# 6. Point your local repository to the remote repository hosted on GitHub
git remote add origin git@github.com:PoomipatGit/FinalProject_KMUTNB.git

# 7. Upload your local 'main' branch to GitHub and remember this link for future pushes
git push -u origin main

# 8. Pull
git pull origin main

# Undo a specific commit by its ID, creating a new "undo" commit (keeps history clean for teams)
git revert <commit-id>