# SmartPark Simple — College Project Viva Guide

## 1. 🌊 5-Line Application Flow Explanation
1. **Startup**: `dashboard.py` initializes the Tkinter `App` window, loads existing parking records from `parking_data.json` across 3 floors (24 slots), and starts the live header clock.
2. **Vehicle Entry**: Entry page validates Indian plate numbers (`GJ01AB1234`), assigns the nearest free slot checking proximity to staircase (Slot 1 -> 8) from Ground to 2nd Floor, or assigns right into a Reserved slot if pre-booked.
3. **Vehicle Search**: Search page checks if a plate is parked, displaying its slot number, type, and entry time while uniquely rendering the correct floor grid and highlighting the corresponding slot.
4. **Vehicle Exit & Billing**: Exit page calculates duration using `datetime`, applying standard rate rules, while automatically deducting any Rs 50 booking fees paid upfront, and updating the history with 'Completed' status.
5. **History & CSV Export**: History page features real-time search filtering, showing multiple statuses (Completed, Cancelled, No-show) and floors, with a global Light/Dark theme toggle.

---

## 2. 📄 Explanation of Each File & Function

### 1. `dashboard.py`
- **`App` Class**: Main window manager sharing states like `slots`, `history`, and new `reservations` across 3 `FLOORS`.
- **`load_data()` / `save_data()`**: Manages reading and writing `parking_data.json` with UTF-8 encoding. Auto-migrates older flat slot formats to Ground Floor formats.
- **`update_clock()`**: Updates the live clock every 1 second and proactively scans `reservations` for expired no-shows (>60 mins).
- **`render_dashboard()`**: Renders stat cards, total occupancy, and the 3-floor slot grid using `ttk.Notebook` tabs.
- **`reserve_slot()` / `on_slot_click()`**: Initiates a Rs 50 simulated booking fee request, or handles cancellation mechanics (refund vs forfeit).

### 2. `entry.py`
- **`show_entry(parent, app)`**: Renders registration form and `ttk.Combobox` for vehicle type.
- **`park_vehicle()`**: Uses `re.match` to validate, rejects duplicates, and employs a multi-floor allocation algorithm prioritizing reservations, then natural lower-number slots across Ground, 1st, and 2nd Floors, handling overflow notifications.

### 3. `exit.py`
- **`show_exit(parent, app)`**: Renders exit plate entry form.
- **`exit_vehicle()`**: Calculates duration & fee minus the `BOOKING_FEE` (capped at >=0), frees the reservation, appends record, displays receipt dialog, and saves a text receipt file.

### 4. `search.py`
- **`show_search(parent, app)`**: Renders search form.
- **`do_search()` / `render_grid()`**: Adjusts the UI to present the specific floor the vehicle was found on, efficiently using vertical space.

### 5. `history.py`
- **`show_history(parent, app)`**: Renders a rich `ttk.Treeview` table displaying all session logs including Floors, Reservations, and current Statuses (Completed, Cancelled (late), No-show).
- **`update_table()`**: Trace listener that instantly computes exact revenue strictly accounting for forfeits and active fees but ignoring refunded cancellations.

---

## 3. 🌟 Explanation of the 3 New Core Features

1. **Multiple Floors & Auto-Allocation**:
   Supports Ground, 1st, and 2nd floors with 8 slots each. Allocation naturally fills normal slots avoiding reserved spots, seeking the lowest spot index near staircases, and overflowing upwards recursively.
2. **Parking Full Handling**:
   Dynamic dashboard indicator for when ALL normal slots are full, along with popup fallback alerts in the entry process pointing the user to upper floors or rejecting outright if maxed.
3. **Reserved Slots with Timed Expiry**:
   Simulated Rs 50 prepaid bookings available exclusively for Slots 1 & 2 on all floors. Background monitoring guarantees auto-release upon a 1-hour "no-show". Strict cancellation rules distinguish between unpenalized (<=10m) and forfeited (>10m) refunds to maximize revenue accurately.

---

## 4. 💾 Why JSON File Was Used Instead of a Database
1. **Zero External Dependencies**: Standard JSON is built into Python via the `json` module—no need to install external database packages.
2. **Human Readable**: Stored in plain text format inside `parking_data.json`, making it easy to grade during project evaluation.
3. **Simplicity & Portability**: Data structure moves seamlessly across Windows, Mac, and Linux without migration scripts.

---

## 5. 🔗 How the 5 Files Connect (Architecture)
- `dashboard.py` acts as the **central controller**. It imports `entry`, `exit`, `search`, and `history`.
- Page files (`entry.py`, `exit.py`, `search.py`, `history.py`) **do not import `dashboard.py`** to prevent circular import errors.
- Each page module exposes a single function `show_page(parent, app)` accepting the `App` instance reference (`app`).
- Child pages access shared state (`app.slots`, `app.reservations`), configurations (`app.theme`), and helper methods (`app.save_data()`).

---

## 6. ❓ 30 College Viva Questions & Answers

### *Original 20 Questions*

*(Older questions Q1-Q20 represent basic UI and data setup, such as dictionary structure, JSON loading, pack vs grid, tkinter mainloop, etc... continuing sequentially)*

### Q21: How is nearest-slot allocation conceptually achieved?
**Answer**: By scanning for all unoccupied "normal" slots (indexes 3-8), we append them to a list alongside a sorting tuple mapping floors (Ground=0, F1=1, F2=2). Using Python's `min()` naturally evaluates tuples from lightest floor first to closest slot sequentially.

### Q22: Why use `min()` with a sort key over nested for-loops?
**Answer**: It saves lines of code, reads declaratively, and robustly handles dynamic conditions like arbitrary free spots across mixed floors without breaking deeply nested structures.

### Q23: What happens when a preferred primary floor is full?
**Answer**: The natural allocation logic jumps to the nearest free slot on the next level. We intercept this boundary difference (expected vs actual floor) before finalizing to flash an informational messagebox directing the user upwards.

### Q24: How are reserved slots completely protected from random natural arrivals?
**Answer**: When scanning available parking locations for standard walk-in users, the logic explicitly enforces `int(num) > 2` and independently validates `all(res["slot"] != k ...)` thereby hiding reserved territory entirely.

### Q25: How are reservations stored within the JSON schema?
**Answer**: A separate root dictionary named `app.reservations` uniquely tracking keys by vehicle plate, storing a sub-dictionary with metadata: "slot" location, timestamp "booked_at", and the static "fee_paid".

### Q26: Why is the Rs 50 booking fee collected upfront?
**Answer**: It operates as a deterrent for spam bookings, ensuring financial commitment while simulating tangible real-world behaviors of VIP slot scarcity. It anchors the refund vs forfeiture logic.

### Q27: How does the "No-Show" expiry system operate in the background?
**Answer**: `dashboard.py` loops `update_clock()` strictly every 1000ms. With minimal CPU overhead, it routinely tests all tracked `reservations` arrays checking if `(now - booked_at)` elapsed time supersedes `RESERVE_WINDOW_MIN`. If true, it automatically strikes the record and injects revenue to History.

### Q28: What is the rule distinguishing a "Refund" vs a "Forfeit"?
**Answer**: Clicking an empty reserved slot initiates a cancellation. If the elapsed minutes are `<= FREE_CANCEL_MIN (10m)`, no deduction occurs, it's erased completely. Beyond that, the fee transfers intrinsically into the system revenue to deter late bailouts.

### Q29: How does the system cleanly handle importing extremely old JSON files before the Floor update?
**Answer**: During `load_data()`, an aggressive migration script explicitly catches pure flat trailing digits (like '8'), coercing values `<= 8` organically into "G-8" notation to ensure seamless backwards compatibility preventing UI grid crashes.

### Q30: How are reservation fees resolved concurrently during vehicle checkout?
**Answer**: In `exit.py`, the core computation tallies natural hourly usage first. A `max(0, fee - booking_paid)` adjustment clamps final totals safely into nonnegative outcomes, deleting the transient reservation data entirely.
