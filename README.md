# Digital Note Organiser

A Flask-based web application that allows users to create, manage, and store digital notes with optional PDF uploads.

---

## 🚀 Features

* User authentication (Sign up / Login / Logout)
* Create and manage notes
* Upload PDF files
* Simple and clean user interface
* Organized file storage

---

## 🛠️ Tech Stack

* Python (Flask)
* HTML / CSS / JavaScript
* SQLite (default Flask database)
* Jinja2 Templates

---

## 📁 Project Structure

```
Digital-Note-Organiser/
│
├── website/
│   ├── static/          # CSS & JS files
│   ├── templates/       # HTML templates
│   ├── auth.py          # Authentication routes
│   ├── models.py        # Database models
│   ├── views.py         # Main app routes
│   └── __init__.py
│
├── instance/            # Database files
├── uploads/             # Uploaded PDFs
├── main.py              # App entry point
├── requirements.txt     # Dependencies
└── README.md
```

---

## ⚙️ Installation

1. Clone the repository

```bash
git clone https://github.com/sitap902/Digital-Note-Organiser.git
cd Digital-Note-Organiser
```

2. Create and activate virtual environment

```bash
python3 -m venv venv
source venv/bin/activate   # Mac/Linux
venv\Scripts\activate      # Windows
```

3. Install dependencies

```bash
pip install -r requirements.txt
```

---

## ▶️ Running the App

```bash
python main.py
```

Open your browser and go to:

```
http://127.0.0.1:5000
```

---

## 📌 Usage

* Sign up for a new account
* Log in
* Add notes
* Upload PDF files
* Manage your saved notes

---

## 🧹 .gitignore (Recommended)

Make sure the following are ignored:

```
venv/
__pycache__/
instance/
uploads/
*.pyc
.env
```

---

## 🔮 Future Improvements

* Search and filter notes
* Edit and delete notes
* Better UI/UX design
* Cloud storage integration
* User profile management

---

## 👤 Author

* GitHub: https://github.com/sitap902

---

## 📄 License

This project is open-source and available for learning and personal use.

