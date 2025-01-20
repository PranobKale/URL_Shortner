# URL Shortener

A simple and robust URL shortener application that converts long URLs into short, manageable links. Includes features like expiration, analytics, and logging.

---

## Features

- Shorten long URLs with unique codes.
- Set expiration times for shortened URLs.
- Redirect users to original URLs.
- Track analytics (access count, timestamps, IP addresses).
- Handle invalid or expired URLs gracefully.

---

## Getting Started

Follow these steps to set up and run the URL Shortener project.

---

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/url-shortener.git
cd url-shortener

---



### 2. Set Up the Virtual Environment
bash
# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate



### 3. Install Dependencies
bash



-- pip install -r requirements.txt

### 4. Configure the Database
bash



# Apply migrations to set up the database schema
-- python manage.py makemigrations
-- python manage.py migrate



### 5. Run the Development Server
bash

Command :- python manage.py runserver
-- Access the application in your browser at: http://127.0.0.1:8000/



### How to Use
Shorten a URL:- 
-- Enter the original URL and an optional expiration time (in hours) on the homepage.
-- Click "Shorten URL" to generate a shortened link.
Redirect
-- Use the generated shortened link to access the original URL.
View Analytics
-- Click the "Analytics" button next to a shortened URL to view:
   1. Original URL
   2. Expiration timestamp
   3. Total access count
   4. Access logs (timestamps and IP addresses)


### Testing
Run the following command to execute the test suite:
python manage.py test


-- This version of the README is well-organized, clear, and properly formatted. Let me know if you'd like any additional details or tweaks!

