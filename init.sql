CREATE TABLE IF NOT EXISTS borrowers (
    id        INTEGER PRIMARY KEY,
    name      VARCHAR(100) NOT NULL,
    province  VARCHAR(100) NOT NULL,
    monthly_income_usd  DOUBLE PRECISION NOT NULL DEFAULT 400,
    late_payments       INTEGER NOT NULL DEFAULT 0
);

-- for databases created before these model inputs existed
ALTER TABLE borrowers ADD COLUMN IF NOT EXISTS monthly_income_usd DOUBLE PRECISION NOT NULL DEFAULT 400;
ALTER TABLE borrowers ADD COLUMN IF NOT EXISTS late_payments INTEGER NOT NULL DEFAULT 0;

CREATE TABLE IF NOT EXISTS applications (
    id            SERIAL PRIMARY KEY,
    borrower_id   INTEGER NOT NULL REFERENCES borrowers (id),
    amount_usd    INTEGER NOT NULL CHECK (amount_usd BETWEEN 100 AND 5000),
    term_months   INTEGER NOT NULL CHECK (term_months IN (3, 6, 12, 18, 24)),
    status        VARCHAR(20) NOT NULL DEFAULT 'pending'
                  CHECK (status IN ('pending', 'approved', 'rejected')),
    submitted_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_applications_borrower ON applications (borrower_id);
CREATE INDEX IF NOT EXISTS idx_applications_status ON applications (status);

CREATE TABLE IF NOT EXISTS predictions (
    id                   SERIAL PRIMARY KEY,
    application_id       INTEGER NOT NULL REFERENCES applications (id),
    default_probability  DOUBLE PRECISION NOT NULL CHECK (default_probability BETWEEN 0 AND 1),
    model_version        VARCHAR(20) NOT NULL,
    created_at           TIMESTAMPTZ NOT NULL DEFAULT now()
);

INSERT INTO borrowers (id, name, province) VALUES
    (1042, 'Sokha Chan', 'Kampong Cham'),
    (1043, 'Dara Phan',  'Phnom Penh'),
    (1044, 'Srey Mom',   'Siem Reap')
ON CONFLICT (id) DO NOTHING;
