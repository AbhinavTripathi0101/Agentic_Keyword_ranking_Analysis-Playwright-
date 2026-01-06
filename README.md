# Agentic Keyword Ranking System

A modular ranking agentic system that leverages **Playwright** for web scraping and **LangGraph** (powered by Groq AI) to track Google search rankings (Organic and Local Pack) and provide strategic SEO recommendations.



## 📂 Project Structure

- **`main.py`**: The central orchestrator. It defines the LangGraph state machine, nodes (Search, Insight, Save, and Mail), and handles the Excel I/O.
- **`ranking_engine.py`**: Contains the core logic for navigating Google Search, identifying organic positions, and extracting Local Pack (Google Maps) rankings.
- **`browser_utils.py`**: Manages the Playwright browser lifecycle, stealth settings, geolocation (set to Noida, India), and safe navigation.
- **`config.py`**: Global configuration file for API keys, email credentials, business identifiers, and file paths.
- **`requirements.txt`**: List of necessary Python libraries.
- **`.env`**: Private environment file for storing sensitive API keys and email passwords.

## 🚀 Features

- **Dual Rank Tracking**: Checks both traditional organic blue links and the Google Maps "Local Pack."
- **AI-Powered Analysis**: Uses the `llama-3.1-8b-instant` model via Groq to generate 3 actionable SEO tips per keyword.
- **Stealth Automation**: Uses custom User-Agents and geolocation to mimic real user behavior and avoid bot detection.
- **Stateful Workflow**: Built on LangGraph, allowing the script to handle errors gracefully and loop through large keyword lists.
- **Automated Emailing**: Sends the final Excel report to a designated recipient automatically upon completion.
- **Formatted Export**: Outputs results to an Excel file with professional "boxed" formatting, text wrapping, and borders.

## 🛠️ Setup Instructions

### 1. Installation
Clone the repository and install the dependencies:
```bash
pip install -r requirements.txt
playwright install chromium
```
##2. Configuration
```bash
Create a .env file in the root directory and add your credentials:
GROQ_API_KEY=your_groq_api_key
EMAIL_SENDER=your-email@gmail.com
EMAIL_PASSWORD=your-16-character-app-password
EMAIL_RECEIVER=target-email@gmail.com
```

##3. Prepare Input
```bash
Ensure you have an Excel file named ranking.xlsx in the directory. The script automatically looks for a column named "Local Keyword Ideas" and "Targeted Page".
```

🖥️ Usage
Run the project using:
```bash
python main.py
```
---
