package main

import (
	"encoding/json"
	"flag"
	"html/template"
	"os"
	"path/filepath"
	"regexp"
	"sort"
	"strings"
	"time"

	"github.com/ajiteshreddy7/yc-go-scraper/internal/db"
	"github.com/ajiteshreddy7/yc-go-scraper/internal/logger"
)

type Job struct {
	ID        int
	Title     string
	Company   string
	Location  string
	Type      string
	URL       string
	DateAdded time.Time
	Status    string
}

// deriveLevels returns canonical level labels found in a job title
func deriveLevels(title string) []string {
	t := strings.ToLower(title)
	var out []string
	add := func(s string) { out = append(out, s) }
	if matched, _ := regexp.MatchString(`\bintern(ship)?\b`, t); matched {
		add("Intern")
	}
	if strings.Contains(t, "new grad") || strings.Contains(t, "new graduate") {
		add("New Grad")
	}
	if strings.Contains(t, "entry level") || strings.Contains(t, "entry-level") {
		add("Entry Level")
	}
	if strings.Contains(t, "junior") {
		add("Junior")
	}
	if strings.Contains(t, "associate") {
		add("Associate")
	}
	if strings.Contains(t, "apprentice") {
		add("Apprentice")
	}
	if strings.Contains(t, "fellow") {
		add("Fellow")
	}
	if strings.Contains(t, "co-op") || strings.Contains(t, "co op") || strings.Contains(t, "coop") {
		add("Co-op")
	}
	if len(out) == 0 {
		if matched, _ := regexp.MatchString(`\b(engineer|developer|analyst|specialist|coordinator)\b`, t); matched {
			if ok, _ := regexp.MatchString(`\b(senior|staff|principal|lead|manager|director|architect|head|chief|vp)\b`, t); !ok {
				add("Entry Level")
			}
		}
	}
	if len(out) > 1 {
		seen := map[string]bool{}
		uniq := []string{}
		for _, v := range out {
			if !seen[v] {
				seen[v] = true
				uniq = append(uniq, v)
			}
		}
		out = uniq
	}
	return out
}

const indexHTML = `<!DOCTYPE html>
<html>
<head>
    <title>Job Opportunities Tracker</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: #f8f9fa; padding: 20px; }
        .container { max-width: 1200px; margin: 0 auto; }
        h1 { color: #343a40; text-align: center; margin-bottom: 30px; }
        .stats { display: flex; justify-content: space-around; margin-bottom: 30px; flex-wrap: wrap; gap: 15px; }
        .stat-card { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); text-align: center; min-width: 150px; }
        .stat-number { font-size: 2em; font-weight: bold; color: #007bff; }
        .stat-label { color: #6c757d; margin-top: 5px; }
        .filters { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); margin-bottom: 20px; }
        .filter-row { display: flex; gap: 10px; flex-wrap: wrap; align-items: center; margin-bottom: 15px; }
        .filter-row label { font-weight: 600; color: #495057; min-width: 100px; }
        input[type="text"], select { padding: 8px 12px; border: 1px solid #ced4da; border-radius: 6px; flex: 1; min-width: 200px; }
        .level-checkboxes { display: flex; flex-wrap: wrap; gap: 15px; }
        .level-checkboxes label { display: flex; align-items: center; gap: 5px; }
        button { background: #007bff; color: white; border: none; padding: 10px 20px; border-radius: 6px; cursor: pointer; font-weight: 500; }
        button:hover { background: #0069d9; }
        .jobs-table { background: white; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); overflow: hidden; }
        table { width: 100%; border-collapse: collapse; }
        th, td { padding: 12px; text-align: left; border-bottom: 1px solid #dee2e6; }
        th { background: #007bff; color: white; position: sticky; top: 0; }
        tr:hover { background: #f8f9fa; }
        a { color: #007bff; text-decoration: none; }
        a:hover { text-decoration: underline; }
        .status-not-applied { color: #dc3545; font-weight: bold; }
        .status-applied { color: #28a745; font-weight: bold; }
        .export-btn { background: #28a745; margin-left: 10px; }
        .export-btn:hover { background: #218838; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 Job Opportunities Tracker</h1>
        
        <div class="stats">
            <div class="stat-card">
                <div class="stat-number" id="total-jobs">{{.TotalJobs}}</div>
                <div class="stat-label">Total Jobs</div>
            </div>
            <div class="stat-card">
                <div class="stat-number" id="not-applied">{{.NotApplied}}</div>
                <div class="stat-label">Not Applied</div>
            </div>
            <div class="stat-card">
                <div class="stat-number" id="applied">{{.Applied}}</div>
                <div class="stat-label">Applied</div>
            </div>
        </div>
        
        <div class="filters">
            <div class="filter-row">
                <label>Search:</label>
                <input type="text" id="search" placeholder="Search by title, company, location..." />
            </div>
            <div class="filter-row">
                <label>Job Levels:</label>
                <div class="level-checkboxes" id="levels">
                    {{range .Levels}}
                    <label><input type="checkbox" value="{{.}}" checked> {{.}}</label>
                    {{end}}
                </div>
            </div>
            <div class="filter-row">
                <label>Company:</label>
                <select id="company">
                    <option value="">All Companies</option>
                    {{range .Companies}}
                    <option value="{{.}}">{{.}}</option>
                    {{end}}
                </select>
                <label>Location:</label>
                <select id="location">
                    <option value="">All Locations</option>
                    {{range .Locations}}
                    <option value="{{.}}">{{.}}</option>
                    {{end}}
                </select>
                <label>Status:</label>
                <select id="status">
                    <option value="">All Statuses</option>
                    <option value="Not Applied">Not Applied</option>
                    <option value="Applied">Applied</option>
                </select>
                <button onclick="filterJobs()">Apply Filters</button>
                <button class="export-btn" onclick="exportCSV()">Download CSV</button>
            </div>
        </div>
        
        <div class="jobs-table">
            <table>
                <thead>
                    <tr>
                        <th>Date</th>
                        <th>Company</th>
                        <th>Title</th>
                        <th>Location</th>
                        <th>Level</th>
                        <th>Status</th>
                        <th>Link</th>
                    </tr>
                </thead>
                <tbody id="jobs-body">
                    {{range .Jobs}}
                    <tr data-title="{{.Title}}" data-company="{{.Company}}" data-location="{{.Location}}" data-levels="{{.Levels}}" data-status="{{.Status}}">
                        <td>{{.DateAdded}}</td>
                        <td>{{.Company}}</td>
                        <td>{{.Title}}</td>
                        <td>{{.Location}}</td>
                        <td>{{.Levels}}</td>
                        <td><span class="status-{{.StatusClass}}">{{.Status}}</span></td>
                        <td><a href="{{.URL}}" target="_blank">Apply</a></td>
                    </tr>
                    {{end}}
                </tbody>
            </table>
        </div>
    </div>
    
    <script>
        const allJobs = Array.from(document.querySelectorAll('#jobs-body tr'));
        
        function filterJobs() {
            const search = document.getElementById('search').value.toLowerCase();
            const selectedLevels = Array.from(document.querySelectorAll('#levels input:checked')).map(cb => cb.value.toLowerCase());
            const company = document.getElementById('company').value;
            const location = document.getElementById('location').value;
            const status = document.getElementById('status').value;
            
            let visibleCount = 0;
            let notAppliedCount = 0;
            let appliedCount = 0;
            
            allJobs.forEach(row => {
                const title = row.dataset.title.toLowerCase();
                const rowCompany = row.dataset.company;
                const rowLocation = row.dataset.location;
                const rowLevels = row.dataset.levels.toLowerCase();
                const rowStatus = row.dataset.status;
                
                let show = true;
                
                // Search filter
                if (search && !title.includes(search) && !rowCompany.toLowerCase().includes(search) && !rowLocation.toLowerCase().includes(search)) {
                    show = false;
                }
                
                // Level filter
                if (selectedLevels.length > 0) {
                    const matchesLevel = selectedLevels.some(level => rowLevels.includes(level));
                    if (!matchesLevel) show = false;
                }
                
                // Company filter
                if (company && rowCompany !== company) show = false;
                
                // Location filter
                if (location && rowLocation !== location) show = false;
                
                // Status filter
                if (status && rowStatus !== status) show = false;
                
                row.style.display = show ? '' : 'none';
                
                if (show) {
                    visibleCount++;
                    if (rowStatus === 'Not Applied') notAppliedCount++;
                    else appliedCount++;
                }
            });
            
            document.getElementById('total-jobs').textContent = visibleCount;
            document.getElementById('not-applied').textContent = notAppliedCount;
            document.getElementById('applied').textContent = appliedCount;
        }
        
        function exportCSV() {
            const visibleRows = allJobs.filter(row => row.style.display !== 'none');
            let csv = 'Date,Company,Title,Location,Level,Status,URL\n';
            
            visibleRows.forEach(row => {
                const cells = row.querySelectorAll('td');
                const url = row.querySelector('a').href;
                const rowData = [
                    cells[0].textContent,
                    cells[1].textContent,
                    cells[2].textContent,
                    cells[3].textContent,
                    cells[4].textContent,
                    cells[5].textContent,
                    url
                ].map(field => '"' + field.replace(/"/g, '""') + '"');
                csv += rowData.join(',') + '\n';
            });
            
            const blob = new Blob([csv], { type: 'text/csv' });
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'job_applications.csv';
            a.click();
            window.URL.revokeObjectURL(url);
        }
        
        // Initialize
        filterJobs();
    </script>
</body>
</html>`

func main() {
	outDir := flag.String("out", "public", "Output directory for static site")
	flag.Parse()

	logger.InitFromEnv()
	logger.Info("Generating static site")

	d, err := db.Connect()
	if err != nil {
		logger.Fatal("db connect: %v", err)
	}
	defer d.Close()

	// Fetch all jobs
	rows, err := d.Conn.Query(`SELECT id, title, company, location, type, url, date_added, status FROM job_applications ORDER BY date_added DESC`)
	if err != nil {
		logger.Fatal("query jobs: %v", err)
	}
	defer rows.Close()

	type JobWithLevels struct {
		Job
		Levels      string
		StatusClass string
	}

	var jobs []JobWithLevels
	levelSet := map[string]bool{}
	companySet := map[string]bool{}
	locationSet := map[string]bool{}
	notApplied := 0
	applied := 0

	for rows.Next() {
		var job Job
		var typ string
		if err := rows.Scan(&job.ID, &job.Title, &job.Company, &job.Location, &typ, &job.URL, &job.DateAdded, &job.Status); err != nil {
			logger.Error("scan row: %v", err)
			continue
		}
		job.Type = typ

		// Derive levels
		levels := deriveLevels(job.Title)
		for _, lv := range levels {
			levelSet[lv] = true
		}
		levelsStr := strings.Join(levels, ", ")
		if levelsStr == "" {
			levelsStr = "General"
		}

		statusClass := "not-applied"
		if job.Status == "Applied" {
			statusClass = "applied"
			applied++
		} else {
			notApplied++
		}

		jobs = append(jobs, JobWithLevels{
			Job:         job,
			Levels:      levelsStr,
			StatusClass: statusClass,
		})

		companySet[job.Company] = true
		locationSet[job.Location] = true
	}

	// Convert sets to sorted slices
	var levels []string
	for k := range levelSet {
		levels = append(levels, k)
	}
	sort.Strings(levels)

	var companies []string
	for k := range companySet {
		companies = append(companies, k)
	}
	sort.Strings(companies)

	var locations []string
	for k := range locationSet {
		locations = append(locations, k)
	}
	sort.Strings(locations)

	// Generate index.html
	tmpl := template.Must(template.New("index").Parse(indexHTML))

	data := struct {
		Jobs       []JobWithLevels
		Levels     []string
		Companies  []string
		Locations  []string
		TotalJobs  int
		NotApplied int
		Applied    int
	}{
		Jobs:       jobs,
		Levels:     levels,
		Companies:  companies,
		Locations:  locations,
		TotalJobs:  len(jobs),
		NotApplied: notApplied,
		Applied:    applied,
	}

	if err := os.MkdirAll(*outDir, 0755); err != nil {
		logger.Fatal("create output dir: %v", err)
	}

	indexPath := filepath.Join(*outDir, "index.html")
	f, err := os.Create(indexPath)
	if err != nil {
		logger.Fatal("create index.html: %v", err)
	}
	defer f.Close()

	if err := tmpl.Execute(f, data); err != nil {
		logger.Fatal("execute template: %v", err)
	}

	logger.Info("Generated static site in %s", *outDir)

	// Also export jobs.json for API access
	jobsJSON := filepath.Join(*outDir, "jobs.json")
	jf, err := os.Create(jobsJSON)
	if err != nil {
		logger.Fatal("create jobs.json: %v", err)
	}
	defer jf.Close()

	enc := json.NewEncoder(jf)
	enc.SetIndent("", "  ")
	if err := enc.Encode(data); err != nil {
		logger.Fatal("encode json: %v", err)
	}

	logger.Info("Generated jobs.json")
	logger.Info("Site ready with %d jobs", len(jobs))
}
