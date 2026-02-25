# Social Media API 🚀

A full-featured RESTful API for a social media platform, built with Django REST Framework.  

## Tech Stack
* **Language:** Python 3.13
* **Framework:** Django & Django REST Framework (DRF)
* **Database:** PostgreSQL
* **Task Queue:** Celery + Redis
* **Authentication:** JSON Web Tokens (JWT)
* **Documentation:** Swagger
* **Infrastructure:** Docker & Docker Compose

## Key Features
* **User Authentication:** Secure registration and login using JWT.
* **Social Graph:** Follow and unfollow other users to customize your feed.
* **Posts & Interactions:** Create posts (with text, hashtags, and images), leave comments, and like posts.
* **News Feed:** View a personalized feed containing only posts from followed users.
* **Scheduled Posting:** Users can specify a `scheduled_time` to publish posts in the future. Handled asynchronously by Celery and Redis.
* **Database Optimization:** Prevented N+1 query problems using `select_related`, `prefetch_related`, and Django's `Count` annotation for likes and comments.

## How to Run Locally

1. **Clone the repository:**
   ```bash
   git clone <https://github.com/nastyagst/Social-Media-API.git>
   cd Social-Media-API

2. **Build and start the containers:**
   ```bash
    docker-compose up --build -d

3. **Apply database migrations:**
   ```bash
    docker-compose exec web python manage.py migrate

4. **Create a superuser (optional, for admin panel access):**
   ```bash
    docker-compose exec web python manage.py createsuperuser

## API Documentation
Once the server is running, you can explore and test the API endpoints using the interactive documentation
* **Swagger UI**: http://127.0.0.1:8000/api/docs/

To test protected endpoints, register a new user, log in to get the JWT access token, and click the Authorize button in Swagger UI.
