# SmartPark Simple — Smart Parking Management System

A short, beginner-friendly desktop application for managing a smart parking lot. Built using pure **Python**, standard **Tkinter** / **TTK**, and local **JSON** storage. Designed specifically for college project viva explanations.

---

## 🚀 How to Run

```bash
cd SmartPark_Simple
python dashboard.py
```

---

## 🌟 Key Features & Extras

1. **Multiple Floors (3 Levels)**: Supports Ground, 1st, and 2nd Floors with notebook tabs parsing dynamically sized visual grids spanning 24 discrete spots. Auto-assigns nearest stairs space across all domains recursively. 
2. **Reserved Slot Economics**: Enables simulated pre-booking of prime spots (Slots 1 & 2 per floor) collecting Rs 50 upfront fees safely adjusting remaining exit billing totals. Supports auto-forfeiture (No-show >1hr expiry) directly pumping unrefunded revenues into backend logs automatically while filtering transparently.
3. **Parking Full Handling**: Robust warning notifications natively catching capacity limits (red indicators, warning prompts gracefully bypassing assignment flow).
4. **Regex Vehicle Validation**: Enforces Indian plate format (`GJ01AB1234`) using `re.match` gracefully across both Reservation and standard Entry processes.
5. **Vehicle Types & Differential Rates**: `Car` (Rs 30 + Rs 20/hr) vs `Bike` (Rs 15 + Rs 10/hr) via `ttk.Combobox`.
6. **Live Header Clock**: Real-time non-blocking clock using `after(1000)` handling dynamic background calculations for active no-show mechanics silently.
7. **History Search & CSV Export**: Real-time table filtering displaying Floor, Status, Reservation flags natively alongside exporting to `parking_history.csv` via `csv.writer`.
8. **Light / Dark Theme Toggle**: Global theme switching across all views explicitly recoloring designated premium tabs simultaneously.

---

## 📁 File Structure

- **`dashboard.py`** — Main window manager, live clock, no-show expiry daemon routines, multi-floor tab grid renderer, reservation flow handler, and JSON persistence.
- **`entry.py`** — Vehicle entry form resolving nearest free physical lot placement across 3 floors efficiently bypassing prepurchased VIP spaces.
- **`exit.py`** — Exit processing, dynamically adjusted reservation fee mechanics capping naturally, generating unified receipts text files.
- **`search.py`** — Vehicle search collapsing entire architecture into a single targeted floor visualization intelligently isolating queries horizontally.
- **`history.py`** — Multi-column enriched history tables distinctly summarizing raw aggregate revenues bypassing cancelled artifacts selectively.
- **`VIVA_NOTES.md`** — Comprehensive viva guide containing application flow, deep file explanations, extra features walkthrough, and 30 exhaustive Q&A natively exploring newly added features and edge case behaviors systematically.
