# Academic E-Library

Academic E-Library is a web-based application built using Django that allows faculty to upload academic notes and students to view and download them based on branch, batch, year, semester, and subject.

## Features
- Role-based authentication for Faculty and Students
- Faculty can upload, edit, and delete notes
- Students can view and download notes
- Dynamic filtering by batch, year, semester, and subject
- Password reset functionality using email
- Secure handling of uploaded files

## Tech Stack
- Backend: Django (Python)
- Frontend: HTML, CSS, Bootstrap
- Database: SQLite (development)
- Tools: Git, GitHub

## Project Structure
- `simply_notes/` – Core application logic
- `templates/` – HTML templates
- `static/` – CSS and frontend assets
- `manage.py` – Django project entry point

## Setup Instructions (Local)
1. Clone the repository
2. Create and activate a virtual environment
3. Install Django
4. Run migrations
5. Start the server
6. Open the application in the browser

## Security Notes
- Sensitive data such as email credentials are managed using environment variables
- Database and uploaded media files are excluded from version control

## What I Learned
- Django project structure and URL routing
- Role-based access control
- Backend and frontend integration
- Secure file upload handling
- Using environment variables for sensitive data
