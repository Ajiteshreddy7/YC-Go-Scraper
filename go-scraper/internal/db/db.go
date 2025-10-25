package db

import (
	"database/sql"
	"os"

	_ "github.com/lib/pq"
)

type DB struct {
	Conn *sql.DB
}

// Connect opens a Postgres connection using POSTGRES_URL env var or default
func Connect() (*DB, error) {
	dsn := os.Getenv("POSTGRES_URL")
	if dsn == "" {
		dsn = "postgres://postgres:postgres@localhost:5432/postgres?sslmode=disable"
	}
	conn, err := sql.Open("postgres", dsn)
	if err != nil {
		return nil, err
	}
	if err := conn.Ping(); err != nil {
		return nil, err
	}
	return &DB{Conn: conn}, nil
}

func (d *DB) Close() error {
	return d.Conn.Close()
}

// CreateSchema creates the job_applications table if not exists
func (d *DB) CreateSchema() error {
	q := `
    CREATE TABLE IF NOT EXISTS job_applications (
        id SERIAL PRIMARY KEY,
        title TEXT,
        company TEXT,
        location TEXT,
        salary TEXT,
        type TEXT,
        url TEXT UNIQUE,
        date_added TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        status TEXT DEFAULT 'Not Applied'
    );
    `
	_, err := d.Conn.Exec(q)
	return err
}

// InsertJob inserts a job record, ignores duplicate URL errors
func (d *DB) InsertJob(job map[string]interface{}) error {
	// job expected keys: Title, Company, Location, URL, Type
	q := `INSERT INTO job_applications(title, company, location, type, url) VALUES($1,$2,$3,$4,$5) ON CONFLICT (url) DO NOTHING;`
	_, err := d.Conn.Exec(q, job["Title"], job["Company"], job["Location"], job["Type"], job["URL"])
	return err
}

// InsertJob using typed Job from scraper
func (d *DB) InsertJobTyped(title, company, location, typ, url string) error {
	q := `INSERT INTO job_applications(title, company, location, type, url) VALUES($1,$2,$3,$4,$5) ON CONFLICT (url) DO NOTHING;`
	_, err := d.Conn.Exec(q, title, company, location, typ, url)
	return err
}
