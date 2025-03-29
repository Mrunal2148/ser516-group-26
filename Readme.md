# Project Metrics Calculator

The **Project Metrics Calculator** is a web-based application designed to help developers analyze and improve their code quality by providing essential software quality metrics. It features a **React frontend** with **Java** and **Python backends**, containerized using **Docker** and orchestrated through **Docker Compose**.

## Features
- **Fog Index Metric:** Measures the readability of code comments.
- **Defects Removed Metric:** Evaluates how many defects have been fixed in the codebase.
- **Code Comment Coverage:** Calculates the percentage of commented code to ensure maintainability.

## Tech Stack
- **Frontend:** React.js
- **Backends:**  
  - Java (for core metric computations)  
  - Python (for repository analysis and comment coverage metrics)  
- **Containerization:** Docker & Docker Compose
- **Version Control:** GitHub

---

## Getting Started
### Prerequisites
- Docker & Docker Compose installed.
- A valid GitHub token for repository analysis.

### Environment Variables
GITHUB Token
To generate a GitHub personal access token (PAT) for developers, follow these steps:

Step 1: Log into GitHub
  Go to GitHub and log into your account.
Step 2: Navigate to Developer Settings
  Click on your profile picture (top-right corner).
  Select "Settings" from the dropdown.
  Scroll down and find "Developer settings" (on the left sidebar).
  Click "Personal access tokens", then choose "Tokens (classic)" (or "Fine-grained tokens" if you need more control).
Step 3: Generate a New Token
  Click "Generate new token", then choose:
  Classic token (widely used and easier to configure)
  Fine-grained token (for more specific permissions)
  Give your token a note/name for identification.
  Set Expiration (recommended for security).
Select Permissions:
![image](https://github.com/user-attachments/assets/cc2e48b4-d508-41cf-8617-8328aa794b99)
  For repository access, check repo.
  For GitHub Actions, check workflow.
  For Git operations (push/pull), check write:packages, read:packages.
  For Full access, check all necessary scopes.
  Click "Generate token".
Step 4: Copy and Store the Token
  Copy the token immediately and store it securely (e.g., in a password manager).

### Installation & Running
1. **Clone the repository:**
   ```bash
   git clone https://github.com/Mrunal2148/ser516-group-java-2.git
   cd app
   touch .env
   echo GITHUB_TOKEN=your_github_token_here >> .env
   ```

2. **Start the application:**
   ```bash
   docker-compose build --no-cache
   docker-compose up
   ```
3. **Access the application:**
   - Frontend: [http://localhost:3000](http://localhost:3000)  
   - Java Backend: [http://localhost:8080](http://localhost:8080)  
   - Python Backend: [http://localhost:5005](http://localhost:5005)  

---

## Project Structure
```
project-metrics-calculator/
├── frontend/           # React application
├── backend/
│   ├── Dockerfile      # Java backend Docker setup
│   └── python-backend/
│       ├── Dockerfile  # Python backend Docker setup
│       └── ...         # Python code for metrics
├── docker-compose.yml  # Docker orchestration file
└── .env                # Environment variables
```

## Team
- **Kaumudi Gulbarga** - Developer  
- **Mrunal Kapure** - Developer  
- **Parth Patel** - Developer  
- **Shreya Prakash** - Developer  


