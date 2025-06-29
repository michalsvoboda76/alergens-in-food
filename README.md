# Food Restriction Checker

This is a Python Flask web application that allows users to specify their food restrictions and check if a food product (by EAN code) is suitable for them.

## Features
- Set your food restrictions (e.g., allergens, dietary preferences)
- Enter or scan an EAN code to check if a product is suitable

## Getting Started

1. **Install dependencies** (already installed if you followed setup):
   ```bash
   pip install flask
   ```
2. **Run the application:**
   ```bash
   C:/g/github/svd/alergens-in-food/.venv/Scripts/python.exe app.py
   ```
3. **Open your browser and go to:**
   [http://127.0.0.1:5000/](http://127.0.0.1:5000/)

## Project Structure
- `app.py` - Main Flask application
- `templates/` - HTML templates
- `.github/copilot-instructions.md` - Copilot custom instructions

## Notes
- This is a demo with in-memory data. For production, use a database and secure session management.
