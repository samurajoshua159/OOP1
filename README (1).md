# Community Vaccination Tracker

**PROG211 – Object-Oriented Programming 1 | Individual Assignment: Real-World Solutions under DPG Standards**
**Domain:** Health  |  **System:** Vaccination Tracker
**Language:** Python 3 (standard library only – nothing to install)

A small, open-source Python program that helps community health workers record vaccine doses and protect people from missed or badly timed doses. It enforces the minimum waiting time between doses and gives each person a plain-language status: **Not started**, **In progress** or **Fully vaccinated**. It also shows when the next dose is due, lists overdue doses for follow-up, and produces a coverage report. It is built with Object-Oriented Programming and follows Digital Public Goods (DPG) standards. **No personal data is stored.**

> The vaccine schedules in this program are simplified examples for a programming assignment. They are not medical guidance.

---

## 1. The problem

Many people miss follow-up vaccine doses because paper records are lost, handwriting is unclear, or nobody remembers when the next dose is due. Multi-dose vaccines such as Hepatitis B depend on correct timing. A dose given too early may not protect fully, and a missed dose leaves a person only partly protected. This program keeps every dose in one place, refuses doses that are too early or not needed, and tells health workers exactly who needs to come back and when.

## 2. Features

| # | Menu option | What it does |
|---|---|---|
| 1 | Register a new recipient | Gives the person an automatic anonymous ID (R-001, R-002, ...) from their age group |
| 2 | Record a vaccine dose | Saves a dose given by a chosen health worker; too-early, extra and future-dated doses are refused |
| 3 | View one recipient | Shows a recipient's dose history, completion percentage, status per vaccine and next due date |
| 4 | View all recipients | A table of every recipient with their number of doses and completion |
| 5 | Vaccination coverage report | For every vaccine: how many people are fully vaccinated, with a text bar chart |
| 6 | **Delete a recipient** | Removes a recipient **and all of their dose records**, after typing YES to confirm |
| 7 | **Search by age group** | Lists every recipient in one age group |
| 8 | **Most protected recipient** | Shows the recipient with the highest percentage of all required doses |
| 9 | **Top health worker** | Shows every worker's dose count and the worker who has given the most doses |
| 10 | **Overdue doses** | A follow-up list of everyone whose next dose date has passed, and by how many days |
| 11 | System summary | Totals for recipients, vaccines, workers and dose records, plus every schedule |
| 0 | Exit | Closes the program |

## 3. Project files

```
community-vaccination-tracker/
├── vaccination_tracker.py   # The complete program, demo and unit tests (one file)
├── README.md                # This file
└── LICENSE                  # MIT open-source licence
```

The program is one file divided into clearly labelled sections:

| Section | Contents |
|---|---|
| 1 – Fixed data | `VALID_AGE_GROUPS`, `VACCINE_DEFINITIONS`, `STATUS_LABELS` (tuples) |
| 2 – Classes | `Vaccine`, `VaccinationRecord`, `HealthWorker`, `Recipient` |
| 3 – Registry functions | `add_record()`, `find_recipient()`, `delete_recipient()`, `display_all()`, `search_by_age_group()` |
| 4 – Sample data | `load_sample_data()` – fictional vaccines, workers, recipients and doses |
| 5 – Input helpers | `ask()`, `choose_from()` |
| 6 – Menu actions | One function per menu option |
| 7 – Menu and demo | `main()` and `run_demo()` |
| 8 – Unit tests | 15 tests using Python's built-in `unittest` module |

## 4. How to run

You only need Python 3.8 or newer.

```bash
git clone https://github.com/<your-username>/community-vaccination-tracker.git
cd community-vaccination-tracker

python vaccination_tracker.py           # interactive menu
python vaccination_tracker.py --demo    # scripted demo of every requirement
python vaccination_tracker.py --test    # run the 15 unit tests
```

## 5. How the assignment tasks are met

### Task 1 – Classes, attributes and objects (Lecture 1)

| Class | Attributes | Main methods |
|---|---|---|
| `Vaccine` | `name`, `dose_intervals` (tuple), `doses_required` (property), `total_vaccines` (class attribute) | `coverage()`, `from_text()` [class], `__str__()` |
| `VaccinationRecord` | `record_id`, `vaccine_name`, `dose_number`, `date_given`, `worker_code`, `total_records` (class attribute) | `get_total_records()` [class], `record_removal()` [class], `parse_date()` [static], `__str__()` |
| `HealthWorker` | `worker_code`, `clinic`, `doses_administered`, `total_workers` (class attribute) | `administer_dose()`, `display_info()`, `find_top_worker()` [static], `__str__()` |
| `Recipient` | `recipient_id`, `age_group`, `doses` (dictionary), `total_recipients` and `next_number` (class attributes) | `receive_dose()`, `doses_of()`, `last_dose_of()`, `next_dose_due()`, `is_overdue()`, `is_fully_vaccinated()`, `completion_percent()`, `status_for()`, `display_info()`, `create_with_next_id()` [class], `get_total_recipients()` [class], `record_removal()` [class], `is_valid_age_group()` [static], `find_most_protected()` [static] |

**How the objects interact:**
1. A `HealthWorker` object calls `administer_dose()` and passes in a `Recipient` and a `Vaccine`.
2. The worker asks the recipient to run `receive_dose()`, which checks the schedule rules using the vaccine's `dose_intervals`.
3. If the rules pass, the recipient creates a new `VaccinationRecord` object and stores it.
4. Only then does the worker increase its own `doses_administered` count.

If a dose is refused, nothing changes, so each object protects its own data.

```python
hep_b = Vaccine.from_text("Hepatitis B:28,150")
worker_one = HealthWorker("HW-01", "Community Health Post")
child = Recipient.create_with_next_id("5-17")
worker_one.administer_dose(child, hep_b, date(2026, 8, 3))
```

### Task 2 – Data structure (Lecture 2)

The program uses **one data structure, the dictionary**, to store multiple objects. The unique ID is always the key:

```python
registry = {"R-001": <Recipient>, "R-002": <Recipient>, ...}
workers  = {"HW-01": <HealthWorker>, "HW-02": <HealthWorker>}
vaccines = {"Polio": <Vaccine>, "Yellow Fever": <Vaccine>, ...}
recipient.doses = {"R-001-01": <VaccinationRecord>, ...}
```

A dictionary was chosen over a list for two reasons: looking a person up by ID is immediate, and duplicate IDs are impossible because keys are unique. Every collection of objects in the program is a dictionary, and no list or set is used to store objects.

Functions in Section 3:
- **Add:** `add_record()` adds an object and rejects duplicate IDs.
- **Find:** `find_recipient()` looks up a recipient in any case, e.g. `r-001`.
- **Delete:** `delete_recipient()` removes a recipient and their records.
- **Display:** `display_all()` prints every recipient.
- **Search:** `search_by_age_group()` lists recipients in one age group.

**Optional tuples (bonus):** tuples are used only for data that should never change after it is created:
- `Vaccine.dose_intervals`: the fixed waiting times, e.g. `(28, 150)`.
- `VALID_AGE_GROUPS = ("0-4", "5-17", "18-49", "50-64", "65+")`.
- `VACCINE_DEFINITIONS`: the vaccine schedules written as text.
- `STATUS_LABELS = ("Not started", "In progress", "Fully vaccinated")`, read with tuple unpacking.
- `Vaccine.coverage()` returns a `(fully_vaccinated, total, percent)` tuple.
- The menu labels and the sample doses.

### Task 3 – Methods (Lecture 3)

| Type | Method | What it does |
|---|---|---|
| Instance | `HealthWorker.administer_dose()` | Gives a dose to a recipient and updates the worker's count |
| Instance | `Recipient.receive_dose()` | Checks the schedule rules and records a new `VaccinationRecord` |
| Instance | `Recipient.next_dose_due()` | Calculates the earliest date for the next dose |
| Instance | `Recipient.is_overdue()` | True if the next dose date has already passed |
| Instance | `Recipient.status_for()` | Returns Not started, In progress or Fully vaccinated |
| Instance | `Recipient.completion_percent()` | Percentage of all required doses received |
| Instance | `Vaccine.coverage()` | How many recipients have completed one vaccine (returns a tuple) |
| Class | `Vaccine.from_text()` | Builds a vaccine from text such as `'Polio:28,28'` |
| Class | `Recipient.create_with_next_id()` | Creates a recipient with an automatic ID like R-001 (IDs are never reused after a delete) |
| Class | `Recipient.get_total_recipients()` | How many recipients exist, using the shared class attribute |
| Class | `Recipient.record_removal()` / `VaccinationRecord.record_removal()` | Update the counts when a recipient is deleted |
| Static | `Recipient.is_valid_age_group()` | Checks an age group without needing an object |
| Static | `VaccinationRecord.parse_date()` | Converts YYYY-MM-DD text to a date; refuses bad formats and future dates |
| Static | `Recipient.find_most_protected()` | Finds the recipient with the highest completion percentage |
| Static | `HealthWorker.find_top_worker()` | Finds the worker who has given the most doses |

## 6. How the solution meets DPG standards

| DPG principle | How this project meets it |
|---|---|
| **Open-source** | The full source code is in a public GitHub repository under the **MIT licence**. It uses only the Python standard library, so anyone can run, study, copy and improve it at no cost. |
| **Inclusive and accessible design** | Prompts use plain language and numbered choices, so no typing of long names is needed. Errors start with `Problem:` and explain how to fix the input (e.g. the date format, or the earliest allowed date). IDs work in upper or lower case. Text is ASCII-only, so it works in any terminal. The coverage chart is a `#` text bar, so nothing depends on colour. No internet, login or special hardware is needed. Deleting asks for confirmation. |
| **Privacy-respecting** | **No names, addresses, phone numbers, exact birth dates or national IDs are stored.** Recipients have only an anonymous ID and an age band. Health workers have only a work code and clinic. Deleting a recipient removes all of their dose records too. All sample data is fictional. |
| **Modular and reusable** | The program is organised into labelled sections for data, classes, registry functions, the user interface, the demo and the tests. Each feature is its own function. The classes can be reused in a web app or a database-backed system. Vaccine schedules are data (e.g. `'Polio:28,28'`), so a new vaccine can be added by adding one line to `VACCINE_DEFINITIONS`, without changing any code. |

## 7. Example usage (sample input and output)

### Registering a recipient (option 1)

```
  Choose an option: 1
  Age groups: 0-4, 5-17, 18-49, 50-64, 65+
  Enter the age group: 30
  Problem: Age group must be one of: 0-4, 5-17, 18-49, 50-64, 65+

  Choose an option: 1
  Age groups: 0-4, 5-17, 18-49, 50-64, 65+
  Enter the age group: 65+
  [OK] Registered. The anonymous ID is R-005.
```

### Recording a dose (option 2), and a dose given too early

```
  Choose an option: 2
  Recipient ID (e.g. R-001): R-003
  Vaccines:
    1. Hepatitis B (3 dose(s))
    2. Polio (3 dose(s))
    3. Measles-Rubella (2 dose(s))
    4. Yellow Fever (1 dose(s))
  Choose a number: 2
  Health workers:
    1. HW-01 (Community Health Post)
    2. HW-02 (District Hospital)
  Choose a number: 2
  Date given (YYYY-MM-DD): 2026-09-20
  [OK] Saved: R-003-02: Polio dose 1 on 2026-09-20 (by HW-02)

  Choose an option: 2
  Recipient ID (e.g. R-001): R-003
  ...
  Date given (YYYY-MM-DD): 2026-09-25
  Problem: Too early for dose 2 of Polio. Earliest allowed date is 2026-10-18.
```

### Viewing one recipient (option 3)

```
  Choose an option: 3
  Recipient ID (e.g. R-001): R-002

  Recipient ID : R-002
  Age group    : 18-49
  Doses given  : 1
    - R-002-01: Measles-Rubella dose 1 on 2026-09-02 (by HW-02)
  Completion   : 11% of all doses
    Hepatitis B     : Not started
    Polio           : Not started
    Measles-Rubella : In progress (1 of 2 doses, next due from 2026-09-30)  ** OVERDUE **
    Yellow Fever    : Not started
```

### Deleting a recipient (option 6)

```
  Choose an option: 6
  Recipient ID to delete: R-003
  Recipient ID : R-003
  Age group    : 0-4
  Doses given  : 1
    - R-003-01: Yellow Fever dose 1 on 2026-09-05 (by HW-02)
  Type YES to delete this recipient and all their records: YES
  [OK] Deleted R-003 and 1 dose record(s).
```

If anything other than YES is typed, the program shows `Cancelled - nothing was deleted.`

### Most protected recipient (option 8) and top health worker (option 9)

```
  MOST PROTECTED RECIPIENT (highest completion)
  ----------------------------------------------
  R-004 (age group 0-4) - 67% of all doses, 6 dose(s) given
    Hepatitis B     : Not started
    Polio           : Fully vaccinated
    Measles-Rubella : Fully vaccinated
    Yellow Fever    : Fully vaccinated

  HEALTH WORKER ACTIVITY
  ----------------------------------------------
  Worker HW-01 at Community Health Post: 6 dose(s) administered
  Worker HW-02 at District Hospital: 4 dose(s) administered
  Top health worker: HW-01 (6 doses)
```

### Coverage report (option 5) and overdue doses (option 10)

```
  VACCINATION COVERAGE REPORT
  ----------------------------------------------------
  Hepatitis B      0 of 4 fully vaccinated  [..........]   0%
  Polio            1 of 4 fully vaccinated  [##........]  25%
  Measles-Rubella  1 of 4 fully vaccinated  [##........]  25%
  Yellow Fever     2 of 4 fully vaccinated  [#####.....]  50%

  FOLLOW-UP LIST - OVERDUE DOSES (as of 2026-10-12)
  ----------------------------------------------------
  R-002  Measles-Rubella  dose 2 was due 2026-09-30 (12 days ago)
```

The overdue list is worked out from **today's date**, so the "days ago" number grows each day you run the program.

### Running the tests

```
$ python vaccination_tracker.py --test
...
----------------------------------------------------------------------
Ran 15 tests in 0.001s

OK
```

## 8. Testing

There are 15 unit tests written with Python's built-in `unittest` module. They check that:
- vaccines are built correctly from text, and bad text is rejected;
- invalid age groups, badly formatted dates and future dates are rejected;
- a two-dose schedule is completed correctly;
- a dose given too early is refused and does not change the worker's count, and extra doses are refused;
- the next due date and overdue status are calculated correctly;
- the class method counts recipients, and IDs are not reused after a delete;
- the completion percentage and the most protected recipient are correct;
- the registry rejects duplicates, finds recipients and deletes them;
- the top health worker is found correctly, and coverage returns the correct tuple.

## 9. Future improvements

- Save data to a JSON file or database so records last between sessions.
- Add more vaccines, and local-language prompts such as Krio.
- Build a web or mobile interface for health workers in the field.

## 10. Licence

Released under the MIT Licence – see [LICENSE](LICENSE).
