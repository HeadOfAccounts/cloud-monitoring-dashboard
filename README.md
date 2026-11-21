# Cloud-based System Resource Monitoring Dashboard

A cloud-based dashboard that monitors **CPU, memory, disk and uptime** across several Linux virtual machines. A Python collector on each VM sends readings to a central REST API. The API stores them in a SQL database and checks each reading against alert thresholds. A web dashboard shows current and historical usage, along with any warnings.

> **Draft status (Nov 24):** Items marked `TODO(owner)` need details from the person who owns that part. Please fill them in, or send them to JG in the group chat.

## Team

| Role | Owner | Area |
|---|---|---|
| Backend lead | Rene Acosta | Collector, REST API, SQL schema, alert logic, integration |
| Dashboard front end | Maha Aljaffan | HTML/CSS/JS, Chart.js history graphs, VM list, alerts panel |
| Cloud and VM engineer | Daniel Salaita | VMs, firewall, collector install (cron/systemd), server uptime |
| Alerts and testing | Fabian Salinas | Threshold config, email/Slack notifications, stress-ng tests, bug list |
| Docs and demo | JG Guerrero | README, architecture diagram, report, slides, demo script, backup video |

## Architecture

![Architecture diagram](docs/architecture.png)

The project uses three Linux VMs:

- **Monitored VM 1 and VM 2.** Each runs `collector.py`, which reads system stats with `psutil` every 10–30 seconds and sends them to `POST /metrics`. The collector is started at boot by cron or systemd and keeps retrying if the network drops.
- **Server VM.** Hosts the REST API (runs as a service, so it comes back after a reboot), the SQL database and the dashboard.
- **Alert flow.** Each incoming reading is compared with its threshold. When a threshold is exceeded, the API writes an alert record, the dashboard shows a warning, and an email or Slack notification is sent.

The firewall opens only the ports needed for SSH, the API and the dashboard.

## Repository layout

`TODO(Rene)`: Confirm the folder names once the repo structure is final.

```
.
├── collector/          # collector.py + systemd unit / cron entry
├── api/                # REST API, alert-check logic
├── db/                 # schema.sql, sample_queries.sql
├── dashboard/          # index.html, CSS, JS (Chart.js)
├── tests/              # stress-ng scenarios, test log
└── docs/               # architecture diagram, report, slides, demo script
```

## Tech stack

| Layer | Tool |
|---|---|
| Metric collection | Python 3, `psutil` |
| API | Python REST API, JSON. `TODO(Rene)`: framework (Flask / FastAPI / other) |
| Database | SQL. `TODO(Rene)`: engine (SQLite / PostgreSQL / MySQL) |
| Dashboard | HTML, CSS, JavaScript, Chart.js |
| Scheduling | cron or systemd |
| Notifications | Email or Slack. `TODO(Fabian)`: which one |
| Load testing | `stress-ng` |
| Hosting | 3 Linux VMs. `TODO(Daniel)`: cloud provider and Linux distro |

## Setup

### 1. Provision the VMs (Daniel)

1. Create three Linux VMs: `vm1` (monitored), `vm2` (monitored) and `server` (API + DB + dashboard).
2. Add each teammate's SSH key.
3. Firewall rules: allow **SSH (22)**, **API (`TODO` port)** and **dashboard (`TODO` port)**. Block everything else.

| VM | Role | IP / hostname |
|---|---|---|
| vm1 | Monitored | `TODO(Daniel)` |
| vm2 | Monitored | `TODO(Daniel)` |
| server | API, DB, dashboard | `TODO(Daniel)` |

### 2. Set up the server (Rene)

```bash
ssh <user>@<server-ip>
git clone <repo-url> && cd <repo>
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# create the database tables
# TODO(Rene): exact command for the chosen DB engine, e.g.
# sqlite3 monitor.db < db/schema.sql

# run the API as a service so it restarts after a reboot
sudo cp api/monitor-api.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now monitor-api
sudo systemctl status monitor-api
```

### 3. Install the collector on each monitored VM (Daniel)

```bash
ssh <user>@<vm-ip>
sudo apt install -y python3-pip   # or the distro's package manager
pip3 install psutil requests
# set the API address and this VM's id
export API_URL=http://<server-ip>:<api-port>
export VM_ID=vm1

# start at boot with systemd (or a cron @reboot entry)
sudo cp collector/collector.service /etc/systemd/system/
sudo systemctl enable --now collector
```

**Adding another VM (goal: about 15 minutes):** provision it, open SSH, repeat step 3 with a new `VM_ID`, and confirm it appears in `GET /vms`. `TODO(Daniel)`: link the full setup guide.

### 4. Open the dashboard (Maha)

Go to `http://<server-ip>:<dashboard-port>` in a browser. The page refreshes automatically. If the API is down, it shows an error message instead of breaking.

## API reference

All endpoints accept and return JSON. Invalid input gets a `400` response with an error message. `TODO(Rene)`: confirm field names, units and exact error codes.

### `POST /metrics`

Sent by the collector. Submits one reading for one VM.

```json
{
  "vm_id": "vm1",
  "cpu": 42.5,
  "memory": 61.2,
  "disk": 73.0,
  "uptime": 86400,
  "timestamp": "2026-11-24T18:30:00Z"
}
```

`cpu`, `memory` and `disk` are percentages. `uptime` is in seconds. After storing the reading, the API runs the alert check.

### `GET /vms`

Lists every VM with its latest stats. The dashboard uses this for the VM list.

### `GET /metrics?vm_id=&from=&to=`

Returns the history for one VM between two timestamps. The dashboard uses this for the history chart (last hour, 24 hours, 7 days).

```
GET /metrics?vm_id=vm1&from=2026-11-24T17:30:00Z&to=2026-11-24T18:30:00Z
```

### `GET /alerts`

Returns recent alerts. Used by the alerts panel.

### `PUT /thresholds`

Updates alert thresholds. Defaults are **CPU 80%, memory 85%, disk 90%**.

```json
{ "cpu": 80, "memory": 85, "disk": 90 }
```

`TODO(Rene/Fabian)`: Decide whether thresholds are global or set per VM. If per VM, add `vm_id` to the request body.

## Database

Tables: `vms`, `metrics`, `thresholds`, `alerts`. The schema is in `db/schema.sql`, and example queries are in `db/sample_queries.sql`.

## Testing alerts

`stress-ng` pushes a monitored VM over its thresholds. The alert should show up on the dashboard (and as an email/Slack message) within about a minute.

```bash
# CPU over 80%
stress-ng --cpu 0 --cpu-load 95 --timeout 120s
# memory over 85%
stress-ng --vm 2 --vm-bytes 90% --timeout 120s
# disk over 90%: TODO(Fabian), e.g. fallocate a large temp file, then delete it
```

Each scenario is recorded in the test log with its expected and actual result. `TODO(Fabian)`: link the test log and bug list.

## Demo

See [`docs/DEMO_SCRIPT.md`](docs/DEMO_SCRIPT.md). The demo order is: normal monitoring, stress test, resulting alert, history chart. A recorded backup video is in `TODO(JG)`.

## Timeline

| Dates | Milestone |
|---|---|
| Nov 10–13 | Roles confirmed, repo created, API spec shared, 3 VMs provisioned |
| Nov 14–17 | Collector running on VMs, `POST /metrics` and database working, dashboard mock UI with fake data, test plan drafted |
| Nov 18–24 | GET endpoints done, dashboard wired to API with history charts, threshold alerts recorded, report draft |
| Nov 25–27 | Alert notifications, stress-ng alert demo working, bug fixes |
| Nov 28–Dec 1 | Final testing, README and diagram, demo rehearsal, backup demo video, submit |
