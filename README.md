<div align="center">

# ⚡️ SplitWatts (AC Bill Splitter Deluxe)

**The fairest way to split the electricity bill when your roommate refuses to use the AC.** 🥶
<img width="670" height="895" alt="clipboard_2026-10-08_19-51" src="https://github.com/user-attachments/assets/1771e640-e30f-4650-8afd-f5aad2100456" />
<img width="645" height="425" alt="clipboard_2026-10-08_19-53" src="https://github.com/user-attachments/assets/0f27b9d9-5192-45fc-b012-09db0a7004ef" />


A sleek, dark-mode desktop app built with Python and CustomTkinter to calculate EXACTLY how much the AC user owes based on tiered (SLAB) electricity rates.

[![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![CustomTkinter](https://img.shields.io/badge/UI-CustomTkinter-1f538d?style=for-the-badge)](https://github.com/TomSchimansky/CustomTkinter)

</div>

---

## 🤷‍♂️ The Problem

We've all been there: It's the middle of summer. You're blasting the AC at 18°C to survive, but your roommate insists that "the ceiling fan is fine." 

When the monthly electricity bill arrives, a simple 50/50 split feels unfair to them, but calculating exactly how much *you* owe for the AC is a nightmare because electricity is billed in **tiers (SLAB rates)**. The more you use, the more expensive each unit (KWH) gets. 

## 💡 The Solution: SplitWatts

I built this app for my personal use to solve this exact problem. **SplitWatts** calculates the exact cost of the AC usage by figuring out which pricing tier the AC consumption falls into. 

Instead of guessing, you just punch in the meter readings, and the app calculates exactly who owes what!

---

## ✨ Features

- 📅 **Smart Billing Cycles:** Handles single-month calculations AND multi-month overlaps (where the tiered rates reset on the 1st of the month).
- 🧮 **Tiered Rate Logic:** Automatically calculates costs based on customizable KWH SLAB rates.
- 🎨 **Gorgeous UI:** A beautiful, responsive dark-mode interface powered by `CustomTkinter`.
- 💸 **"What About Y?" Calculator:** Easily calculate your roommate's net cost if they paid the utility company directly.

---

## 🚀 How to Run It

### Prerequisites
Make sure you have Python installed, then install the required libraries:
```bash
pip install customtkinter tkcalendar
```

### Running the App
Just run the script directly:
```bash
python SplitWatts.py
```

---

## ⚙️ How It Works (The Math)

Let's say Person Y uses base appliances (lights, fridge), and Person X uses the AC. 

Person X's AC usage pushes the total household consumption into a higher, more expensive pricing tier. SplitWatts isolates Person X's AC consumption (using a separate sub-meter or estimated start/end readings) and calculates the cost at the highest tier rates triggered by that usage, ensuring Person Y only pays the base rate for their non-AC usage.

The SLAB configuration is built-in, but you can easily tweak it in the source code:
```python
TIERS_CONFIG = [
    {"id": 1, "rate": 4.35, "cumulative_max_kwh": 50},
    {"id": 2, "rate": 4.85, "cumulative_max_kwh": 75},
    {"id": 3, "rate": 6.63, "cumulative_max_kwh": 200},
    # ... and so on
]
```

---

## 📄 License

Do whatever you want with it! Feel free to fork it, change the rates for your own country/utility provider, and save your friendships. (MIT License)
