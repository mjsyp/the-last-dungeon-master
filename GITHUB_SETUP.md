# GitHub Setup Instructions

## Step 1: Create the Repository on GitHub

1. Go to [GitHub](https://github.com) and sign in with your account (mjsyp@umich.edu)
2. Click the **"+"** icon in the top right → **"New repository"**
3. Fill in the details:
   - **Repository name**: `the-last-dungeon-master` (or your preferred name)
   - **Description**: "A voice-driven Dungeon Master Virtual Assistant using LLMs"
   - **Visibility**: Choose Public or Private
   - **DO NOT** initialize with README, .gitignore, or license (we already have these)
4. Click **"Create repository"**

## Step 2: Push Your Code

After creating the repository, GitHub will show you commands. Use these:

```bash
# Add the remote (replace YOUR_USERNAME with your GitHub username)
git remote add origin https://github.com/YOUR_USERNAME/the-last-dungeon-master.git

# Push to GitHub
git branch -M main
git push -u origin main
```

Or if you prefer SSH:

```bash
git remote add origin git@github.com:YOUR_USERNAME/the-last-dungeon-master.git
git branch -M main
git push -u origin main
```

## Alternative: Use the Setup Script

You can also use the provided script:

```bash
./.github_setup.sh
```

This will prompt you for the repository URL and handle the push.

## Step 3: Verify

1. Visit your repository on GitHub
2. You should see all your files
3. Consider adding:
   - Repository description
   - Topics/tags (e.g., `python`, `llm`, `dnd`, `rag`, `tabletop-rpg`)
   - A LICENSE file (MIT, Apache 2.0, etc.)

## Current Git Configuration

- **Name**: Michael Sypniewski
- **Email**: mjsyp@umich.edu

This is set for this repository only. If you want to set it globally, use:

```bash
git config --global user.name "Michael Sypniewski"
git config --global user.email "mjsyp@umich.edu"
```

