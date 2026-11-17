CREATE TABLE IF NOT EXISTS vms (id TEXT PRIMARY KEY, last_seen TEXT);
CREATE TABLE IF NOT EXISTS metrics (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  vm_id TEXT NOT NULL, cpu REAL, memory REAL, disk REAL, uptime INTEGER, ts TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_metrics_vm_ts ON metrics(vm_id, ts);
CREATE TABLE IF NOT EXISTS thresholds (metric TEXT PRIMARY KEY, value REAL NOT NULL);
INSERT OR IGNORE INTO thresholds VALUES ('cpu',80),('memory',85),('disk',90);
CREATE TABLE IF NOT EXISTS alerts (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  vm_id TEXT, metric TEXT, value REAL, threshold REAL, ts TEXT
);