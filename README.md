# DiscountBot

**DiscountBot** — this is a Python bot for automatically generating and issuing discounts to customers.
It can handle promo codes and can be integrated into a loyalty system or online store.

---

## 📖 Description

DiscountBot — easy instrument for working with loyalty system:  

- Generation promo-codes
- Client management (for example, issuing a code upon first login to the bot)
---

## ⚙️ Install

1. Clone repo:

   ```bash
   git clone https://github.com/ManifoldCode/DiscountBot.git
   cd DiscountBot
   ```

2. Create virtual enviroment:

   ```bash
   python3 -m venv venv
   source venv/bin/activate 
   ```

3. Install requirements:

   ```bash
   pip install -r requirements.txt
   ```
---

## 🚀 Lounch

```bash
python app.py
```

---

## 💡 Using

- Ask the bot for a promo code – it will generate a unique value.
- The client can use it in a store or service. 
- The code can be checked for expiration date

---

## 📦 Modules

- **`app.py`** — the entry point to the application
- **`config.py`** — all project settings
- **`customer.py`** — working with clients and their data
- **`promo_code_generator.py`** — generating unique promo codes

---

## 🖥 Requirements

- Python 3.8+
- Dependencies from `requirements.txt`

---

