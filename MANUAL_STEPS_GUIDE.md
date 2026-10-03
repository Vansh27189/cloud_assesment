# Step-by-Step Manual Actions Guide 📋

This guide provides the simple, step-by-step actions for you to push the project to your GitHub, deploy it, and submit the assessment.

---

## 🛠️ Step 1: Initialize Git and Create a Public GitHub Repository

1. Open your browser and go to [GitHub.com](https://github.com/) (log in to your account).
2. Click the **`+`** icon at the top right and select **New repository**.
3. Set:
   - **Repository name**: `cloudpulse-microservice` (or any name you prefer)
   - **Visibility**: **Public** (required by assessment)
   - Do **NOT** check "Add a README" or ".gitignore" (we have already created them for you).
4. Click **Create repository**.
5. Copy your new repository HTTPS URL (e.g., `https://github.com/Vansh27189/cloud_assesment.git`).

---

## 🚀 Step 2: Push the Code from Your Machine to GitHub

Open **PowerShell** or your terminal inside `d:\cloud_assement` and run the following commands:

```powershell
# 1. Navigate to the project directory
cd d:\cloud_assement

# 2. Initialize Git
git init

# 3. Add all files to staging
git add .

# 4. Commit the project
git commit -m "feat: Initial commit of CloudPulse containerized microservice with CI/CD"

# 5. Rename default branch to main
git branch -M main

# 6. Add your GitHub remote (replace with your actual GitHub URL from Step 1)
git remote add origin https://github.com/Vansh27189/cloud_assesment.git

# 7. Push to GitHub
git push -u origin main
```

---

## 🛡️ Step 3: Verify GitHub Actions CI/CD Pipeline

1. Go to your GitHub repository in your browser.
2. Click on the **Actions** tab at the top.
3. You will see the **CI/CD Pipeline - CloudPulse Microservice** running:
   - It will run `flake8` lint checks.
   - It will execute all **8 automated Pytest test cases**.
   - It will build the Docker container and verify the `/health` probe.
   - You will see a green checkmark **`✔ Run Unit & Integration Tests (Quality Gate)`**.

> [!TIP]
> **To test that pushing fails if tests fail (as required by assessment):**
> Break a test intentionally (e.g., change `assert response.status_code == 200` to `201` in `tests/test_health.py`), commit, and push. GitHub Actions will fail and block the build! Then change it back and push to restore green status.

---

## ☁️ Step 4: Show Your Running Deployed Project

The assessment requires: *"Show your running deployed project."* You have two great options:

### 🌟 Option A: 100% Free Cloud Deployment on Render (Takes 2 minutes)
If you want an instant, zero-cost, publicly accessible HTTPS URL to show in class or submit in the spreadsheet:
1. Go to [Render.com](https://render.com/) and sign up / log in with your GitHub account.
2. Click **New +** -> **Web Service**.
3. Connect your GitHub repository `cloudpulse-microservice`.
4. Render will automatically detect the `Dockerfile` and `render.yaml`.
5. Click **Deploy Web Service**.
6. In ~2 minutes, Render gives you a live public URL (e.g. `https://cloudpulse-microservice.onrender.com`).
7. Open that URL to see your live dashboard, `/docs`, and `/health`!

---

### ☁️ Option B: Deploy to Amazon Web Services (AWS EC2)
If you prefer AWS deployment:
1. Log in to the [AWS Management Console](https://console.aws.amazon.com/).
2. Navigate to **EC2** -> **Launch Instance**.
3. Configure:
   - **Name**: `cloudpulse-microservice`
   - **OS Image**: **Ubuntu Server 22.04 LTS** (Free Tier eligible)
   - **Instance Type**: `t2.micro`
   - **Key Pair**: Select or create an SSH key pair (or proceed without one if using browser EC2 Instance Connect).
   - **Network Settings**: Check **Allow HTTP traffic from the internet** (Port 80).
   - Under **Advanced Details** -> Scroll down to **User Data** -> Paste the entire contents of [`deploy/ec2-userdata.sh`](file:///d:/cloud_assement/deploy/ec2-userdata.sh).
4. Click **Launch Instance**.
5. Wait 2-3 minutes for the instance to initialize.
6. Copy the **Public IPv4 address** from the EC2 dashboard and open in your browser: `http://YOUR_EC2_PUBLIC_IP/`.

---

## 📝 Step 5: Submit the Assessment

1. Open the submission link from your assessment PDF:
   [Submission Google Sheet](https://docs.google.com/spreadsheets/d/158n95p7F09XiKvoSxIewYPQMSZ8hdg1U5dR02I_Bx3U/edit?usp=sharing)
2. Enter your details:
   - **Name / Roll Number**
   - **GitHub Public Repository URL**: `https://github.com/Vansh27189/cloud_assesment`
   - **Live Deployed URL**: Your Render URL or EC2 Public IP (`http://<IP>/` or `https://<render-url>/`)
   - **Project Chosen**: Option 1: Containerized microservice on AWS with Load Balancing & CI/CD.

---

## 🎤 Step 6: Presenting in Class (2-3 Minutes)
When presenting in class or to an interviewer, open [`PRESENTATION_SCRIPT.md`](file:///d:/cloud_assement/PRESENTATION_SCRIPT.md) and read or follow the exact 3-minute talk track provided.
