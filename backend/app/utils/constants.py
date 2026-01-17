"""Application constants - Banks, Categories, Tenors, Titles, etc."""

# List of Nigerian banks for the bank selection dropdown
BANKS: list[str] = [
    "Access Bank",
    "Citibank",
    "Ecobank",
    "Fidelity Bank",
    "First Bank",
    "First City Monument Bank",
    "Guaranty Trust Bank",
    "Heritage Bank",
    "Keystone Bank",
    "Polaris Bank",
    "Providus Bank",
    "Stanbic IBTC Bank",
    "Standard Chartered Bank",
    "Sterling Bank",
    "SunTrust Bank",
    "Union Bank",
    "United Bank for Africa",
    "Unity Bank",
    "Wema Bank",
    "Zenith Bank",
    "Jaiz Bank",
    "Other",
]

# Investor categories for classification
INVESTOR_CATEGORIES: list[str] = [
    "Individual",
    "Insurance",
    "Corporate",
    "Others",
    "Foreign Investor",
    "Non-Bank Financial Institution",
    "Co-operative Society",
    "Government Agencies",
    "Staff Scheme",
    "Micro Finance Bank",
]

# Months of the year for offer selection
MONTHS: list[str] = [
    "January",
    "February",
    "March",
    "April",
    "May",
    "June",
    "July",
    "August",
    "September",
    "October",
    "November",
    "December",
]

# Bond tenor options
TENORS: list[str] = ["2-Year", "3-Year"]

# Title options for applicants
TITLES: list[str] = [
    "Mr.",
    "Mrs.",
    "Miss",
    "Dr.",
    "Chief",
    "Prof.",
    "Alhaji",
    "Alhaja",
]

# Applicant types
APPLICANT_TYPES: list[str] = ["Individual", "Joint", "Corporate"]

# Residency options
RESIDENCY_OPTIONS: list[str] = ["Resident", "Non-Resident"]

# Bond value constraints
BOND_VALUE_MIN: float = 5_000.0
BOND_VALUE_MAX: float = 50_000_000.0
BOND_VALUE_STEP: float = 1_000.0

# Bond value ranges for analytics
BOND_VALUE_RANGES: list[tuple[float, float, str]] = [
    (0, 10_000, "₦0 - ₦10,000"),
    (10_000, 50_000, "₦10,000 - ₦50,000"),
    (50_000, 100_000, "₦50,000 - ₦100,000"),
    (100_000, 500_000, "₦100,000 - ₦500,000"),
    (500_000, 1_000_000, "₦500,000 - ₦1,000,000"),
    (1_000_000, float("inf"), "₦1,000,000+"),
]
