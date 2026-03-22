# ⚡ BrainSpark — Math & English Game

An adaptive educational game for students up to Grade 7, built with Python and Streamlit.

## Features

- **Math Mode** — Randomly generated mental arithmetic questions, from Grade 3 addition to Grade 7 algebra and order of operations
- **English Mode** — Three rotating question types: Vocabulary, Grammar Check, and Sentence Classification
- **Adaptive difficulty** — Gets harder every 3 correct answers (Grade 3 → Grade 7)
- **3-lives system** — Session ends after 3 wrong answers
- **Persistent high scores** — Saved between sessions via a local JSON file
- **Reset scores** — Reset your Math or English high score independently from the main menu

## How to Run

**1. Clone the repo**
```bash
git clone https://github.com/YOUR_USERNAME/brainspark.git
cd brainspark
```

**2. Install dependencies**
```bash
pip install -r requirements.txt
```

**3. Run the app**
```bash
streamlit run app.py
```

The app will open automatically in your browser at `http://localhost:8501`.

> **Windows users:** If `streamlit` is not recognised, use:
> ```bash
> python -m streamlit run app.py
> ```

## Tech Stack

- **Python 3.9+**
- **Streamlit** — UI framework for Python web apps

## Project Structure

```
brainspark/
├── app.py            # Main application (all game logic)
├── requirements.txt  # Python dependencies
├── highscores.json   # Auto-created when you first play
└── README.md
```
