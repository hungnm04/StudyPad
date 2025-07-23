##  **About StudyPad**
StudyPad is a modern note-taking application with a clean, intuitive interface built using Django and Tailwind CSS. 
## **Setup Instructions**
### Installation
# Clone the repository
git clone https://github.com/hungnm04/StudyPad
cd StudyPad

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Navigate to project directory
cd noteApp

# Run migrations
python manage.py migrate

# Create superuser (optional)
python manage.py createsuperuser

# Start server
python manage.py runserver

### Creating Test Users
# Access the app at http://localhost:8000
# Suggested usernames: test1, test2
