# 🧠🚀 Space-Themed Mental Health Chatbot

A space-inspired mental health analysis chatbot web application built using **Flask**. It guides users through a conversational interface to gather basic details, analyze mood, and provide personalized feedback. The data is stored securely in per-user CSV files, and users can view visual summaries on their dashboard.

---

## 🌌 Features

- 🌠 **Space-Themed UI/UX**: Beautifully styled with Bootstrap and cosmic fonts.
- 🧑‍💼 **User Authentication**: Secure login and signup pages.
- 🤖 **Conversational Chatbot**:
  - Collects user info (Name, Age, Occupation)
  - Asks about past mental health diagnosis (Yes/No)
  - Captures current mood (with options and "Other" analysis)
- 📊 **Dashboard**:
  - Displays personalized mood analysis over time
  - Includes pie charts, bar graphs, and line charts (via Chart.js)
- 📁 **CSV Storage**: Each user's responses are stored in `username.csv` files.

---

## 🚀 How to Run

### 🔧 Prerequisites

- Python 3.8+
- pip

### 📦 Install Dependencies

```bash
pip install -r requirements.txt

▶️ Run the App
python app.py

Tested and working fine with MAC AIR M2 Sequoia 15.5 and windows 10 