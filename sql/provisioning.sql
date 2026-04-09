CREATE TABLE IF NOT EXISTS students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    firstName TEXT NOT NULL CHECK (LENGTH(TRIM(firstName)) >= 2),
    lastName TEXT NOT NULL CHECK (LENGTH(TRIM(lastName)) >= 2),
    email TEXT NOT NULL UNIQUE CHECK (
        INSTR(email, '@') > 1
        AND INSTR(SUBSTR(email, INSTR(email, '@') + 1), '.') > 1
    ),
    grade REAL NOT NULL CHECK (grade >= 0 AND grade <= 20),
    field TEXT NOT NULL CHECK (field IN ('informatique', 'mathématiques', 'physique', 'chimie'))
);
