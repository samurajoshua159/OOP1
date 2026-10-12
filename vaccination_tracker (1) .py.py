"""
===============================================================
 COMMUNITY VACCINATION TRACKER
 PROG211 Object-Oriented Programming 1 - Individual Assignment
 Real-World Solutions under DPG Standards | Domain: Health
===============================================================

Run the interactive menu:   python vaccination_tracker.py
Run the automatic demo:     python vaccination_tracker.py --demo
Run the built-in tests:     python vaccination_tracker.py --test

The whole program is in this ONE file, organised into sections:

    SECTION 1 - Fixed data (tuples)
    SECTION 2 - Classes: Vaccine, VaccinationRecord, HealthWorker, Recipient
    SECTION 3 - Registry functions (the dictionary data structure)
    SECTION 4 - Sample data
    SECTION 5 - Input helpers
    SECTION 6 - Menu actions
    SECTION 7 - Menu and demo
    SECTION 8 - Unit tests

PRIVACY BY DESIGN (DPG): no names, addresses, phone numbers, exact
birth dates or national ID numbers are stored. A recipient is only an
anonymous code (e.g. R-001) and an age group. A health worker is only
a work code (e.g. HW-01) and a clinic name.

NOTE: the vaccine schedules are simplified examples for this
assignment. They are not medical guidance.
"""

import sys
import unittest
from datetime import date, timedelta


# ===============================================================
# SECTION 1 - FIXED DATA (TUPLES)
# Tuples are used because these values must NEVER change while the
# program runs. A tuple is immutable, so nothing can edit them by mistake.
# ===============================================================

# Allowed age groups (age bands are used instead of exact birth dates)
VALID_AGE_GROUPS = ("0-4", "5-17", "18-49", "50-64", "65+")

# Vaccine schedules written as text: "Name:gap1,gap2"
# The numbers are the minimum days between doses. No numbers = single dose.
VACCINE_DEFINITIONS = (
    "Hepatitis B:28,150",
    "Polio:28,28",
    "Measles-Rubella:28",
    "Yellow Fever:",
)

# (label when no doses, label when some doses, label when complete)
STATUS_LABELS = ("Not started", "In progress", "Fully vaccinated")


# ===============================================================
# SECTION 2 - CLASSES
# ===============================================================

class Vaccine:
    """A vaccine and its dosing schedule.

    dose_intervals is a TUPLE of minimum gaps (in days) between doses.
    Example: (28, 150) means three doses: dose 2 at least 28 days after
    dose 1, and dose 3 at least 150 days after dose 2.
    An empty tuple means a single-dose vaccine.
    """

    total_vaccines = 0   # class attribute shared by all Vaccine objects

    def __init__(self, name, dose_intervals=()):
        if not name or not name.strip():
            raise ValueError("Vaccine name cannot be empty.")
        for days in dose_intervals:
            if days <= 0:
                raise ValueError("Dose intervals must be positive numbers of days.")
        self.name = name.strip()
        self.dose_intervals = tuple(dose_intervals)
        Vaccine.total_vaccines += 1

    @property
    def doses_required(self):
        """Total number of doses needed to be fully vaccinated."""
        return len(self.dose_intervals) + 1

    # ---------- Instance method ----------
    def coverage(self, registry):
        """
        Work out how many recipients have completed this vaccine.
        Returns a TUPLE: (fully vaccinated, total recipients, percentage)
        """
        fully = 0
        for recipient in registry.values():
            if recipient.is_fully_vaccinated(self):
                fully += 1
        total = len(registry)
        percent = round(fully / total * 100) if total else 0
        return fully, total, percent

    # ---------- Class method ----------
    @classmethod
    def from_text(cls, text):
        """Build a Vaccine from simple text such as 'Polio:28,28'.

        The part before ':' is the name; the numbers after it are the
        gaps in days between doses. 'Yellow Fever:' means a single dose.
        """
        name, _, gaps = text.partition(":")
        try:
            intervals = tuple(int(g) for g in gaps.split(",") if g.strip())
        except ValueError:
            raise ValueError("Dose gaps must be whole numbers, e.g. 'Polio:28,28'.")
        return cls(name, intervals)

    def __str__(self):
        return f"{self.name} ({self.doses_required} dose(s))"


class VaccinationRecord:
    """One dose given to one recipient (anonymous)."""

    total_records = 0   # class attribute: how many records currently exist

    def __init__(self, record_id, vaccine_name, dose_number, date_given, worker_code):
        self.record_id = record_id
        self.vaccine_name = vaccine_name
        self.dose_number = dose_number
        self.date_given = date_given
        self.worker_code = worker_code
        VaccinationRecord.total_records += 1

    # ---------- Class methods ----------
    @classmethod
    def get_total_records(cls):
        """Return how many dose records currently exist."""
        return cls.total_records

    @classmethod
    def record_removal(cls, count=1):
        """Reduce the record count when records are deleted."""
        cls.total_records -= count

    # ---------- Static method ----------
    @staticmethod
    def parse_date(text):
        """Turn 'YYYY-MM-DD' text into a date. Future dates are refused."""
        try:
            given = date.fromisoformat(text.strip())
        except ValueError:
            raise ValueError("Please enter the date as YYYY-MM-DD, e.g. 2026-09-30.")
        if given > date.today():
            raise ValueError("The date cannot be in the future.")
        return given

    def __str__(self):
        return (f"{self.record_id}: {self.vaccine_name} dose {self.dose_number} "
                f"on {self.date_given.isoformat()} (by {self.worker_code})")


class HealthWorker:
    """A vaccinator, identified only by a work code and clinic (no personal data)."""

    total_workers = 0

    def __init__(self, worker_code, clinic):
        self.worker_code = worker_code
        self.clinic = clinic
        self.doses_administered = 0
        HealthWorker.total_workers += 1

    # ---------- Instance methods ----------
    def administer_dose(self, recipient, vaccine, date_given):
        """Give a dose to a recipient (object interaction).

        The worker asks the Recipient object to record the dose, then
        updates their own count ONLY if the dose was accepted.
        """
        record = recipient.receive_dose(vaccine, self.worker_code, date_given)
        self.doses_administered += 1
        return record

    def display_info(self):
        print(f"  Worker {self.worker_code} at {self.clinic}: "
              f"{self.doses_administered} dose(s) administered")

    def __str__(self):
        return f"{self.worker_code} ({self.clinic})"

    # ---------- Static method ----------
    @staticmethod
    def find_top_worker(workers):
        """Return the health worker who has given the most doses (or None)."""
        top = None
        for worker in workers.values():
            if top is None or worker.doses_administered > top.doses_administered:
                top = worker
        return top


class Recipient:
    """A person receiving vaccines, stored anonymously."""

    total_recipients = 0   # class attribute: how many recipients currently exist
    next_number = 1        # used for automatic IDs (never reused after a delete)

    def __init__(self, recipient_id, age_group):
        if not Recipient.is_valid_age_group(age_group):
            raise ValueError("Age group must be one of: " + ", ".join(VALID_AGE_GROUPS))
        self.recipient_id = recipient_id
        self.age_group = age_group
        # Dictionary of this person's doses: {record_id: VaccinationRecord}
        self.doses = {}
        Recipient.total_recipients += 1

    # ---------- Class methods ----------
    @classmethod
    def create_with_next_id(cls, age_group):
        """Create a Recipient with an automatic anonymous code like R-001."""
        recipient = cls(f"R-{cls.next_number:03d}", age_group)
        cls.next_number += 1
        return recipient

    @classmethod
    def get_total_recipients(cls):
        """Return how many recipients currently exist."""
        return cls.total_recipients

    @classmethod
    def record_removal(cls):
        """Reduce the count when a recipient is deleted."""
        cls.total_recipients -= 1

    # ---------- Static methods ----------
    @staticmethod
    def is_valid_age_group(value):
        """Check an age group without needing an object."""
        return value in VALID_AGE_GROUPS

    @staticmethod
    def find_most_protected(registry, vaccines):
        """Return the recipient with the highest completion percentage (or None)."""
        top = None
        for recipient in registry.values():
            if top is None or recipient.completion_percent(vaccines) > top.completion_percent(vaccines):
                top = recipient
        return top

    # ---------- Instance methods ----------
    def doses_of(self, vaccine_name):
        """Return a dictionary of this recipient's records for one vaccine."""
        matches = {}
        for record_id, record in self.doses.items():
            if record.vaccine_name == vaccine_name:
                matches[record_id] = record
        return matches

    def last_dose_of(self, vaccine_name):
        """Return the most recent record for one vaccine, or None."""
        last = None
        for record in self.doses_of(vaccine_name).values():
            if last is None or record.date_given > last.date_given:
                last = record
        return last

    def receive_dose(self, vaccine, worker_code, date_given):
        """Record a new dose after checking the schedule rules."""
        count = len(self.doses_of(vaccine.name))
        if count >= vaccine.doses_required:
            raise ValueError(f"{self.recipient_id} has already completed {vaccine.name}.")
        if count > 0:
            earliest = self.next_dose_due(vaccine)
            if date_given < earliest:
                raise ValueError(f"Too early for dose {count + 1} of {vaccine.name}. "
                                 f"Earliest allowed date is {earliest.isoformat()}.")
        record_id = f"{self.recipient_id}-{len(self.doses) + 1:02d}"
        record = VaccinationRecord(record_id, vaccine.name, count + 1, date_given, worker_code)
        self.doses[record_id] = record
        return record

    def next_dose_due(self, vaccine):
        """Earliest date for the next dose, or None if not started / already complete."""
        count = len(self.doses_of(vaccine.name))
        if count == 0 or count >= vaccine.doses_required:
            return None
        last = self.last_dose_of(vaccine.name)
        return last.date_given + timedelta(days=vaccine.dose_intervals[count - 1])

    def is_overdue(self, vaccine, today=None):
        """True if a next dose is due and that date has already passed."""
        due = self.next_dose_due(vaccine)
        return due is not None and due < (today or date.today())

    def is_fully_vaccinated(self, vaccine):
        return len(self.doses_of(vaccine.name)) >= vaccine.doses_required

    def completion_percent(self, vaccines):
        """Percentage of ALL required doses (every vaccine) this person has received."""
        required = 0
        received = 0
        for vaccine in vaccines.values():
            required += vaccine.doses_required
            received += min(len(self.doses_of(vaccine.name)), vaccine.doses_required)
        return round(received / required * 100) if required else 0

    def status_for(self, vaccine):
        """Plain-language status for one vaccine."""
        not_started, in_progress, complete = STATUS_LABELS   # tuple unpacking
        count = len(self.doses_of(vaccine.name))
        if count == 0:
            return not_started
        if self.is_fully_vaccinated(vaccine):
            return complete
        due = self.next_dose_due(vaccine).isoformat()
        late = "  ** OVERDUE **" if self.is_overdue(vaccine) else ""
        return (f"{in_progress} ({count} of {vaccine.doses_required} doses, "
                f"next due from {due}){late}")

    def display_info(self):
        print(f"  Recipient ID : {self.recipient_id}")
        print(f"  Age group    : {self.age_group}")
        print(f"  Doses given  : {len(self.doses)}")
        for record in self.doses.values():
            print(f"    - {record}")


# ===============================================================
# SECTION 3 - REGISTRY FUNCTIONS (THE DICTIONARY)
# The DICTIONARY is the one data structure used to store multiple
# objects, with the unique ID as the key:
#     registry = {"R-001": <Recipient>, ...}
#     workers  = {"HW-01": <HealthWorker>, ...}
#     vaccines = {"Polio": <Vaccine>, ...}
# Each Recipient also keeps its doses in a dictionary {record_id: record}.
# ===============================================================

def add_record(records, key, item):
    """Add an object to a dictionary (rejects duplicate IDs)."""
    if key in records:
        raise ValueError(f"ID {key} already exists.")
    records[key] = item
    return item


def find_recipient(registry, recipient_id):
    """Look up a Recipient by ID, with a friendly error if missing."""
    key = recipient_id.strip().upper()
    if key not in registry:
        raise ValueError(f"No recipient found with ID {recipient_id.strip()}.")
    return registry[key]


def delete_recipient(registry, recipient_id):
    """Remove a recipient AND all of their dose records. Returns the removed object."""
    recipient = find_recipient(registry, recipient_id)
    del registry[recipient.recipient_id]
    VaccinationRecord.record_removal(len(recipient.doses))
    Recipient.record_removal()
    return recipient


def display_all(registry, vaccines):
    """Print a simple table of every recipient in the registry."""
    if not registry:
        print("  The registry is empty.")
        return
    print(f"  {'ID':<8}{'Age group':<12}{'Doses':<8}{'Complete':<10}")
    print("  " + "-" * 38)
    for recipient_id, recipient in registry.items():
        print(f"  {recipient_id:<8}{recipient.age_group:<12}{len(recipient.doses):<8}"
              f"{recipient.completion_percent(vaccines):>5}%")


def search_by_age_group(registry, age_group):
    """Return how many recipients are in one age group, printing each one."""
    found = 0
    for recipient in registry.values():
        if recipient.age_group == age_group:
            print(f"  {recipient.recipient_id:<8}{len(recipient.doses)} dose(s)")
            found += 1
    return found


# ===============================================================
# SECTION 4 - SAMPLE DATA (fictional - no real people)
# ===============================================================

def load_sample_data():
    """Create sample vaccines, workers, recipients and doses."""
    vaccines = {}
    for text in VACCINE_DEFINITIONS:
        vaccine = Vaccine.from_text(text)          # class method
        add_record(vaccines, vaccine.name, vaccine)

    workers = {}
    for code, clinic in (("HW-01", "Community Health Post"), ("HW-02", "District Hospital")):
        add_record(workers, code, HealthWorker(code, clinic))

    registry = {}
    for age_group in ("5-17", "18-49", "0-4", "0-4"):
        recipient = Recipient.create_with_next_id(age_group)   # class method
        add_record(registry, recipient.recipient_id, recipient)

    # (worker code, recipient ID, vaccine name, date) - a tuple of tuples
    sample_doses = (
        ("HW-01", "R-001", "Hepatitis B", "2026-08-03"),
        ("HW-01", "R-001", "Hepatitis B", "2026-09-01"),
        ("HW-02", "R-002", "Measles-Rubella", "2026-09-02"),
        ("HW-02", "R-003", "Yellow Fever", "2026-09-05"),
        ("HW-01", "R-004", "Polio", "2026-07-01"),
        ("HW-01", "R-004", "Polio", "2026-08-03"),
        ("HW-01", "R-004", "Polio", "2026-09-04"),
        ("HW-02", "R-004", "Measles-Rubella", "2026-07-01"),
        ("HW-02", "R-004", "Measles-Rubella", "2026-08-05"),
        ("HW-01", "R-004", "Yellow Fever", "2026-07-01"),
    )
    for worker_code, recipient_id, vaccine_name, text in sample_doses:
        workers[worker_code].administer_dose(registry[recipient_id], vaccines[vaccine_name],
                                             VaccinationRecord.parse_date(text))
    return vaccines, workers, registry


# ===============================================================
# SECTION 5 - INPUT HELPERS
# ===============================================================

def ask(prompt):
    """Ask a question and return the answer without extra spaces."""
    return input(prompt).strip()


def choose_from(title, records):
    """Show a numbered list of a dictionary's items and return the chosen object."""
    print(f"  {title}:")
    number = 0
    for item in records.values():
        number += 1
        print(f"    {number}. {item}")
    choice = ask("  Choose a number: ")
    if not choice.isdigit() or not 1 <= int(choice) <= len(records):
        raise ValueError("Please enter one of the numbers shown.")
    number = 0
    for item in records.values():
        number += 1
        if number == int(choice):
            return item


# ===============================================================
# SECTION 6 - MENU ACTIONS
# ===============================================================

def register_recipient(registry):
    print("  Age groups: " + ", ".join(VALID_AGE_GROUPS))
    recipient = Recipient.create_with_next_id(ask("  Enter the age group: "))
    add_record(registry, recipient.recipient_id, recipient)
    print(f"  [OK] Registered. The anonymous ID is {recipient.recipient_id}.")


def record_dose(registry, vaccines, workers):
    recipient = find_recipient(registry, ask("  Recipient ID (e.g. R-001): "))
    vaccine = choose_from("Vaccines", vaccines)
    worker = choose_from("Health workers", workers)
    date_given = VaccinationRecord.parse_date(ask("  Date given (YYYY-MM-DD): "))
    record = worker.administer_dose(recipient, vaccine, date_given)
    print(f"  [OK] Saved: {record}")


def view_recipient(registry, vaccines):
    recipient = find_recipient(registry, ask("  Recipient ID (e.g. R-001): "))
    print()
    recipient.display_info()
    print(f"  Completion   : {recipient.completion_percent(vaccines)}% of all doses")
    for vaccine in vaccines.values():
        print(f"    {vaccine.name:<16}: {recipient.status_for(vaccine)}")


def show_coverage(registry, vaccines):
    print("\n  VACCINATION COVERAGE REPORT")
    print("  " + "-" * 52)
    for vaccine in vaccines.values():
        fully, total, percent = vaccine.coverage(registry)   # tuple unpacking
        bar = "#" * (percent // 10) + "." * (10 - percent // 10)
        print(f"  {vaccine.name:<17}{fully} of {total} fully vaccinated  [{bar}] {percent:>3}%")


def remove_recipient(registry):
    recipient = find_recipient(registry, ask("  Recipient ID to delete: "))
    recipient.display_info()
    if ask("  Type YES to delete this recipient and all their records: ").upper() != "YES":
        print("  Cancelled - nothing was deleted.")
        return
    count = len(recipient.doses)
    delete_recipient(registry, recipient.recipient_id)
    print(f"  [OK] Deleted {recipient.recipient_id} and {count} dose record(s).")


def search_age_group(registry):
    print("  Age groups: " + ", ".join(VALID_AGE_GROUPS))
    age_group = ask("  Enter the age group to search: ")
    if not Recipient.is_valid_age_group(age_group):
        raise ValueError("Age group must be one of: " + ", ".join(VALID_AGE_GROUPS))
    print(f"\n  RECIPIENTS IN AGE GROUP {age_group}")
    print("  " + "-" * 30)
    if search_by_age_group(registry, age_group) == 0:
        print("  Nobody in this age group yet.")


def show_most_protected(registry, vaccines):
    top = Recipient.find_most_protected(registry, vaccines)
    print("\n  MOST PROTECTED RECIPIENT (highest completion)")
    print("  " + "-" * 46)
    if top is None:
        print("  The registry is empty.")
        return
    print(f"  {top.recipient_id} (age group {top.age_group}) - "
          f"{top.completion_percent(vaccines)}% of all doses, {len(top.doses)} dose(s) given")
    for vaccine in vaccines.values():
        print(f"    {vaccine.name:<16}: {top.status_for(vaccine)}")


def show_top_worker(workers):
    top = HealthWorker.find_top_worker(workers)
    print("\n  HEALTH WORKER ACTIVITY")
    print("  " + "-" * 46)
    for worker in workers.values():
        worker.display_info()
    if top is not None:
        print(f"  Top health worker: {top.worker_code} ({top.doses_administered} doses)")


def show_overdue(registry, vaccines):
    print(f"\n  FOLLOW-UP LIST - OVERDUE DOSES (as of {date.today().isoformat()})")
    print("  " + "-" * 52)
    found = 0
    for recipient in registry.values():
        for vaccine in vaccines.values():
            if recipient.is_overdue(vaccine):
                found += 1
                due = recipient.next_dose_due(vaccine)
                days_late = (date.today() - due).days
                print(f"  {recipient.recipient_id}  {vaccine.name:<16} dose "
                      f"{len(recipient.doses_of(vaccine.name)) + 1} was due {due} "
                      f"({days_late} days ago)")
    if found == 0:
        print("  No overdue doses. Well done!")


def show_summary(registry, vaccines, workers):
    fully_all = 0
    for recipient in registry.values():
        if recipient.completion_percent(vaccines) == 100:
            fully_all += 1
    print("\n  SYSTEM SUMMARY")
    print("  " + "-" * 40)
    print(f"  Recipients registered : {Recipient.get_total_recipients()}")
    print(f"  Vaccines on schedule  : {len(vaccines)}")
    print(f"  Health workers        : {HealthWorker.total_workers}")
    print(f"  Dose records          : {VaccinationRecord.get_total_records()}")
    print(f"  Fully vaccinated (all): {fully_all}")
    print("\n  VACCINE SCHEDULES (fixed tuple)")
    for vaccine in vaccines.values():
        gaps = ", ".join(str(days) for days in vaccine.dose_intervals) or "single dose"
        print(f"    {vaccine.name:<17}{vaccine.doses_required} dose(s)   gaps in days: {gaps}")


# ===============================================================
# SECTION 7 - MENU AND DEMO
# ===============================================================

MENU = (
    "Register a new recipient",
    "Record a vaccine dose",
    "View one recipient",
    "View all recipients",
    "Vaccination coverage report",
    "Delete a recipient",
    "Search recipients by age group",
    "Show the most protected recipient",
    "Show the top health worker",
    "Show overdue doses (follow-up list)",
    "System summary",
)


def main():
    vaccines, workers, registry = load_sample_data()
    actions = {
        "1": lambda: register_recipient(registry),
        "2": lambda: record_dose(registry, vaccines, workers),
        "3": lambda: view_recipient(registry, vaccines),
        "4": lambda: display_all(registry, vaccines),
        "5": lambda: show_coverage(registry, vaccines),
        "6": lambda: remove_recipient(registry),
        "7": lambda: search_age_group(registry),
        "8": lambda: show_most_protected(registry, vaccines),
        "9": lambda: show_top_worker(workers),
        "10": lambda: show_overdue(registry, vaccines),
        "11": lambda: show_summary(registry, vaccines, workers),
    }
    print("=== Community Vaccination Tracker (no personal data stored) ===")
    while True:
        print("\n  MENU")
        number = 0
        for label in MENU:
            number += 1
            print(f"  {number:>2}. {label}")
        print("   0. Exit")
        choice = ask("  Choose an option: ")
        if choice == "0":
            print(f"  Recipients in the registry: {Recipient.get_total_recipients()}. Goodbye!")
            break
        if choice not in actions:
            print("  Problem: please enter one of the numbers shown.")
            continue
        try:
            actions[choice]()
        except ValueError as error:
            print(f"  Problem: {error}")


def heading(text):
    print(f"\n=== {text} ===")


def run_demo():
    """Scripted walk-through that shows every assignment requirement."""
    heading("1. Creating objects (Task 1)")
    vaccines, workers, registry = load_sample_data()
    for vaccine in vaccines.values():
        print(f"  {vaccine}")
    for worker in workers.values():
        worker.display_info()

    heading("2. The registry dictionary (Task 2)")
    display_all(registry, vaccines)

    heading("3. Objects interacting: a worker gives a dose (Task 3, instance method)")
    record = workers["HW-02"].administer_dose(registry["R-003"], vaccines["Polio"],
                                              VaccinationRecord.parse_date("2026-09-20"))
    print(f"  {record}")

    heading("4. Schedule rules protect patients (error handling)")
    for worker_code, rid, name, text in (("HW-02", "R-003", "Polio", "2026-09-25"),
                                         ("HW-02", "R-003", "Yellow Fever", "2026-09-26"),
                                         ("HW-01", "R-001", "Polio", "2099-01-01")):
        try:
            workers[worker_code].administer_dose(registry[rid], vaccines[name],
                                                 VaccinationRecord.parse_date(text))
        except ValueError as error:
            print(f"  Problem: {error}")

    heading("5. One recipient's history and status")
    registry["R-001"].display_info()
    for vaccine in vaccines.values():
        print(f"    {vaccine.name:<16}: {registry['R-001'].status_for(vaccine)}")

    heading("6. Class methods and static methods")
    print(f"  Recipient.get_total_recipients()     -> {Recipient.get_total_recipients()}")
    print(f"  Vaccine.from_text('Rotavirus:28')    -> {Vaccine.from_text('Rotavirus:28')}")
    print(f"  Recipient.is_valid_age_group('18-49') -> {Recipient.is_valid_age_group('18-49')}")
    print(f"  Recipient.is_valid_age_group('30')    -> {Recipient.is_valid_age_group('30')}")

    heading("7. Coverage, most protected recipient and top worker")
    show_coverage(registry, vaccines)
    show_most_protected(registry, vaccines)
    show_top_worker(workers)

    heading("8. Overdue doses")
    show_overdue(registry, vaccines)

    heading("9. Deleting a recipient")
    removed = delete_recipient(registry, "R-002")
    print(f"  [OK] Deleted {removed.recipient_id}.")
    display_all(registry, vaccines)
    show_summary(registry, vaccines, workers)


# ===============================================================
# SECTION 8 - UNIT TESTS  (python vaccination_tracker.py --test)
# ===============================================================

class TestVaccine(unittest.TestCase):
    def test_from_text_multi_dose(self):
        vaccine = Vaccine.from_text("Hepatitis B:28,150")
        self.assertEqual(vaccine.dose_intervals, (28, 150))
        self.assertEqual(vaccine.doses_required, 3)

    def test_from_text_single_dose(self):
        self.assertEqual(Vaccine.from_text("Yellow Fever:").doses_required, 1)

    def test_bad_text_rejected(self):
        with self.assertRaises(ValueError):
            Vaccine.from_text("Polio:abc")

    def test_coverage_returns_tuple(self):
        vaccine = Vaccine("Yellow Fever")
        registry = {}
        done = Recipient("B-001", "18-49")
        done.receive_dose(vaccine, "HW-01", date(2026, 9, 1))
        add_record(registry, done.recipient_id, done)
        add_record(registry, "B-002", Recipient("B-002", "18-49"))
        self.assertEqual(vaccine.coverage(registry), (1, 2, 50))


class TestRecipient(unittest.TestCase):
    def setUp(self):
        self.vaccine = Vaccine("Measles-Rubella", (28,))
        self.worker = HealthWorker("HW-01", "Test Clinic")
        self.person = Recipient("T-001", "18-49")

    def test_valid_and_invalid_age_group(self):
        self.assertTrue(Recipient.is_valid_age_group("65+"))
        self.assertFalse(Recipient.is_valid_age_group("200"))
        with self.assertRaises(ValueError):
            Recipient("T-002", "999")

    def test_two_doses_complete_schedule(self):
        self.worker.administer_dose(self.person, self.vaccine, date(2026, 9, 1))
        self.assertFalse(self.person.is_fully_vaccinated(self.vaccine))
        self.worker.administer_dose(self.person, self.vaccine, date(2026, 9, 29))
        self.assertTrue(self.person.is_fully_vaccinated(self.vaccine))
        self.assertEqual(self.worker.doses_administered, 2)

    def test_dose_too_early_rejected(self):
        self.worker.administer_dose(self.person, self.vaccine, date(2026, 9, 1))
        with self.assertRaises(ValueError):
            self.worker.administer_dose(self.person, self.vaccine, date(2026, 9, 10))
        self.assertEqual(self.worker.doses_administered, 1)

    def test_extra_dose_rejected(self):
        self.person.receive_dose(self.vaccine, "HW-01", date(2026, 9, 1))
        self.person.receive_dose(self.vaccine, "HW-01", date(2026, 10, 1))
        with self.assertRaises(ValueError):
            self.person.receive_dose(self.vaccine, "HW-01", date(2026, 12, 1))

    def test_next_dose_due_and_overdue(self):
        self.person.receive_dose(self.vaccine, "HW-01", date(2026, 9, 1))
        self.assertEqual(self.person.next_dose_due(self.vaccine), date(2026, 9, 29))
        self.assertTrue(self.person.is_overdue(self.vaccine, today=date(2026, 10, 5)))
        self.assertFalse(self.person.is_overdue(self.vaccine, today=date(2026, 9, 20)))

    def test_class_method_counts_and_ids_not_reused(self):
        before = Recipient.get_total_recipients()
        first = Recipient.create_with_next_id("0-4")
        registry = {first.recipient_id: first}
        self.assertEqual(Recipient.get_total_recipients(), before + 1)
        delete_recipient(registry, first.recipient_id)
        second = Recipient.create_with_next_id("0-4")
        self.assertNotEqual(first.recipient_id, second.recipient_id)

    def test_completion_and_most_protected(self):
        vaccines = {"MR": self.vaccine}
        other = Recipient("T-009", "0-4")
        self.person.receive_dose(self.vaccine, "HW-01", date(2026, 9, 1))
        registry = {"T-001": self.person, "T-009": other}
        self.assertEqual(self.person.completion_percent(vaccines), 50)
        self.assertIs(Recipient.find_most_protected(registry, vaccines), self.person)


class TestRegistryAndWorkers(unittest.TestCase):
    def test_add_find_and_duplicate(self):
        registry = {}
        add_record(registry, "A-001", Recipient("A-001", "5-17"))
        self.assertEqual(find_recipient(registry, "a-001").recipient_id, "A-001")
        with self.assertRaises(ValueError):
            add_record(registry, "A-001", Recipient("A-001", "5-17"))
        with self.assertRaises(ValueError):
            find_recipient(registry, "Z-999")

    def test_delete_recipient(self):
        registry = {"D-001": Recipient("D-001", "65+")}
        delete_recipient(registry, "D-001")
        self.assertNotIn("D-001", registry)

    def test_top_worker(self):
        busy = HealthWorker("HW-08", "Clinic A")
        quiet = HealthWorker("HW-09", "Clinic B")
        busy.administer_dose(Recipient("W-001", "5-17"), Vaccine("Yellow Fever"), date(2026, 9, 1))
        self.assertIs(HealthWorker.find_top_worker({"HW-08": busy, "HW-09": quiet}), busy)


class TestDateParsing(unittest.TestCase):
    def test_parse_date(self):
        self.assertEqual(VaccinationRecord.parse_date("2026-09-30"), date(2026, 9, 30))
        with self.assertRaises(ValueError):
            VaccinationRecord.parse_date("30/09/2026")
        with self.assertRaises(ValueError):
            VaccinationRecord.parse_date("2099-01-01")


if __name__ == "__main__":
    if "--test" in sys.argv:
        unittest.main(argv=[sys.argv[0], "-v"])
    elif "--demo" in sys.argv:
        run_demo()
    else:
        main()
