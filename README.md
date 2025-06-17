# Crime City

Crime City is a web-based game inspired by Torn City, built with Python and Django. Players can engage in combat, manage properties, buy and sell items on the market, and explore different locations in the city.

## Features

- **Player Management**: Create and customize your criminal character
- **Combat System**: Fight against other players to earn cash and experience
- **Locations**: Explore different areas of the city, each with unique opportunities
- **Properties**: Purchase and manage properties to generate passive income
- **Inventory**: Collect, use, and trade items
- **Market**: Buy and sell items with other players

## Tech Stack

- **Backend**: Python 3.9+, Django 4.2
- **Database**: SQLite (development), PostgreSQL (production)
- **Real-time Communication**: Django Channels, WebSockets
- **Task Queue**: Celery with Redis
- **Frontend**: HTML, CSS, JavaScript, Bootstrap 5

## Setup Guide

### Prerequisites

- Python 3.9 or higher
- Redis (for Celery and Django Channels)
- Git

### Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/crime-city.git
   cd crime-city
   ```

2. Create and activate a virtual environment:
   ```
   python -m venv venv
   # On Windows
   venv\Scripts\activate
   # On macOS/Linux
   source venv/bin/activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Apply migrations:
   ```
   python manage.py migrate
   ```

5. Create initial data for the game:
   ```
   python manage.py loaddata initial_data
   ```

6. Create a superuser (admin):
   ```
   python manage.py createsuperuser
   ```

7. Run the development server:
   ```
   python manage.py runserver
   ```

8. In a separate terminal, start Redis and Celery:
   ```
   # Start Redis (if not running as a service)
   redis-server
   
   # Start Celery worker
   celery -A crime_city worker --loglevel=info
   ```

9. Access the site at http://127.0.0.1:8000/

### Running in PyCharm

1. Open the project in PyCharm
2. Configure the Python interpreter to use the virtual environment
3. Create a new Django Server run configuration:
   - Set the working directory to the project root
   - Set the host to 127.0.0.1 and port to 8000
4. Create a separate run configuration for Celery:
   - Program: path to celery in your venv (e.g., `venv/bin/celery` or `venv\Scripts\celery.exe`)
   - Parameters: `-A crime_city worker --loglevel=info`
   - Working directory: project root

## Project Structure

```
crime_city/
├── crime_city/              # Main project folder
│   ├── __init__.py
│   ├── settings.py          # Django settings
│   ├── urls.py              # Main URL routing
│   ├── asgi.py              # ASGI config (for WebSockets)
│   └── wsgi.py              # WSGI config
├── game/                    # Main game application
│   ├── __init__.py
│   ├── admin.py             # Django admin configuration
│   ├── apps.py              # App configuration
│   ├── consumers.py         # WebSocket consumers
│   ├── forms.py             # Form definitions
│   ├── middleware.py        # Custom middleware
│   ├── models/              # Database models
│   ├── services/            # Business logic
│   ├── tasks.py             # Scheduled tasks (Celery)
│   ├── templates/           # HTML templates
│   ├── templatetags/        # Custom template tags
│   ├── tests/               # Unit tests
│   ├── urls.py              # App-specific URL routing
│   └── views/               # View controllers
├── static/                  # Static files
├── manage.py                # Django management script
├── requirements.txt         # Python dependencies
└── README.md
```

## Development

### Creating Initial Data

To create initial game data (locations, items, etc.), you can:

1. Access the Django admin interface at http://127.0.0.1:8000/admin/
2. Add locations, items, property types, etc.
3. Export the data as a fixture:
   ```
   python manage.py dumpdata game.Location game.ItemType game.Item game.PropertyType --indent 4 > game/fixtures/initial_data.json
   ```

### Running Tests

```
python manage.py test
```

## License

This project is licensed under the MIT License.
