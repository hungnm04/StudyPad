# StudyPad

**StudyPad** is a modern note-taking application featuring a clean and intuitive interface, built with **Django** and **Tailwind CSS**.

---

## Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/hungnm04/StudyPad
cd StudyPad
```

### 2. Create and Activate Virtual Environment

```bash
python -m venv venv
```

**On macOS/Linux:**
```bash
source venv/bin/activate
```

**On Windows:**
```bash
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Navigate to the Project Directory

```bash
cd noteApp
```

### 5. Apply Migrations

```bash
python manage.py migrate
```

### 6. Create Superuser (Optional)

```bash
python manage.py createsuperuser
```

### 7. Start the Development Server

```bash
python manage.py runserver
```

Then visit: [http://localhost:8000](http://localhost:8000)

---

## Creating Test Users

You can register test accounts via the signup page or Django admin interface.

Suggested usernames:
- `test1`
- `test2`

---

## License

This project is licensed under the MIT License.

---

