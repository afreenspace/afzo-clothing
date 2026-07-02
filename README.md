# AFZO Clothing

AFZO Clothing is a Flask-based fashion ecommerce demo with product browsing, collections, wishlist/cart flows, checkout, order history, customer feedback, an admin dashboard, dark mode, and an in-page styling chatbot.

## Features

- Responsive storefront with home, products, collections, offers, delivery, feedback, cart, wishlist, checkout, and order pages
- Product catalog with categories for tops, trousers, summer wear, jackets, blazers, ethnic wear, shoes, accessories, and unisex styles
- User registration, login, sessions, cart management, wishlist management, and order placement
- Checkout with cash-on-delivery and simulated card payment flow
- Admin dashboard with orders, users, customers, feedback, category detail, product detail, revenue charts, and low-stock views
- AI-style chatbot UI for outfit suggestions and quick styling prompts
- Dark mode, mobile drawer navigation, animations, hero video, and product image assets

## Tech Stack

- Python
- Flask
- SQLite
- HTML / CSS / JavaScript

## Project Structure

```text
afzo-clothing/
  app.py
  database.db
  static/
    css/
    images/
    js/
    videos/
  templates/
```

## Setup

1. Install Python 3.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Start the app:

```bash
cd afzo-clothing
python app.py
```

4. Open the website:

```text
http://localhost:5000
```

## Admin Access

Admin URL:

```text
http://localhost:5000/admin
```

Default local demo credentials:

```text
Email: admin@afzo.com
Password: afzo2024
```

For deployment, set these environment variables instead of relying on defaults:

```text
FLASK_SECRET_KEY
ADMIN_EMAIL
ADMIN_PASSWORD
DISCOUNT_CODE
```

## Notes

- `database.db` is included so the demo can run with its current local data.
- Product images are stored in `afzo-clothing/static/images/products/`.
- The hero video is stored at `afzo-clothing/static/videos/hero.mp4`.
