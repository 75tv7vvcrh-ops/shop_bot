# 🛍 Shop Bot

A Telegram shop bot built with Python and Aiogram.

The project implements a complete basic e-commerce flow inside Telegram:

**Catalog → Product → Cart → Order → Order Status → Order History**

---

## ✨ Features

* 🛍 Product catalog
* 📦 Product details
* 📸 Product images
* 🛒 Shopping cart
* 📋 Order history
* 🔔 Order status notifications
* 👑 Admin panel
* ➕ Add products through Telegram
* 🚫 User ban system
* 🔓 User unban system
* 📝 User registration
* 💾 PostgreSQL database
* ⚡ Asynchronous architecture
* 🔐 Environment-based configuration
* 🛡 Global error handling

---

## 🧰 Tech Stack

* **Python**
* **Aiogram 3**
* **PostgreSQL**
* **asyncpg**
* **asyncio**
* **python-dotenv**

---

## 📁 Project Structure

```text
shop_bot/
│
├── callbacks/
│   ├── callback_data.py
│   └── __init__.py
│
├── handlers/
│   ├── admin.py
│   ├── cart.py
│   ├── catalog.py
│   ├── errors.py
│   ├── orders.py
│   ├── registration.py
│   ├── start.py
│   └── __init__.py
│
├── keyboards/
│   ├── keyboards.py
│   └── __init__.py
│
├── middlewares/
│   ├── ban.py
│   └── __init__.py
│
├── services/
│   ├── database.py
│   └── __init__.py
│
├── states/
│   ├── registration.py
│   └── __init__.py
│
├── bot.py
├── config.py
├── main.py
└── requirements.txt
```

---

## 🛍 How It Works

### 1. Start

The user launches the bot with `/start`.

The bot creates the user in the database if they don't exist yet.

### 2. Catalog

The user opens the catalog and sees available products.

Each product contains:

* name
* description
* price
* stock
* image

### 3. Cart

The user can add products to the cart.

The bot checks the available stock before increasing the quantity.

### 4. Order

When the user checks out:

* the order is created
* order items are saved
* stock is decreased
* the cart is cleared
* the administrator receives the order
* the user receives the order number

### 5. Order Status

The administrator can change the order status:

* ⏳ В обработке
* ✅ Выполнен
* ❌ Отменен

The user can see the current status in their order history.

---

## 👑 Admin Panel

The administrator has access to:

```text
/admin
```

The admin panel displays active orders and allows changing their status.

### Product Management

Products can be added directly through Telegram:

```text
/add_product
```

The bot asks for:

1. Product name
2. Description
3. Price
4. Stock quantity
5. Category
6. Product image

### User Management

Ban a user:

```text
/ban <user_id> [reason]
```

Unban a user:

```text
/unban <user_id>
```

Banned users are automatically blocked by middleware.

---

## 🗄 Database

The project uses **PostgreSQL**.

Main tables:

```text
users
products
cart
orders
order_items
banned_users
```

The database is initialized automatically when the bot starts.

---

## 🔐 Configuration

Create a local `codes.env` file in the project root.

```env
BOT_TOKEN=your_bot_token
ADMIN_ID=your_telegram_id

PG_USER=your_postgres_user
PG_PASSWORD=your_postgres_password
PG_DATABASE=your_database
PG_HOST=your_host
PG_PORT=5432
```

⚠️ Never commit `codes.env` to GitHub.

---

## 📦 Installation

Clone the repository:

```bash
git clone https://github.com/75tv7vvcrh-ops/shop_bot.git
```

Enter the project directory:

```bash
cd shop_bot
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create your `codes.env` file and add the required configuration.

Run the bot:

```bash
python main.py
```

---

## 🧠 What This Project Demonstrates

This project demonstrates practical backend development with Python.

It includes:

* asynchronous programming
* Telegram Bot API
* Aiogram routers
* FSM states
* callback queries
* middleware
* PostgreSQL
* asyncpg connection pool
* database transactions
* CRUD operations
* order management
* stock management
* environment variables
* error handling
* basic project architecture

---

## 🚀 Future Improvements

Possible future improvements:

* 💳 Online payments
* 🔎 Product search
* 🏷 Product filtering
* 📊 Admin statistics
* ✏️ Product editing
* 🗑 Product deletion
* 📦 Advanced inventory management
* 🐘 PostgreSQL production deployment
* 🌐 Web administration panel
* 🔑 Authentication for admin tools

---

## 📌 Project Status

The core shop functionality is implemented and tested.

The project is being developed as a practical Python backend project.

---

## 👨‍💻 Author

**Dokar**

Python Developer | Building useful software

GitHub:

https://github.com/75tv7vvcrh-ops
