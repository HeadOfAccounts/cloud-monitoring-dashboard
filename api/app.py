import os, sqlite3
from datetime import datetime, timezone
from flask import Flask, request, jsonify, g

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "monitor.db")
app = Flask(__name__)

def db():
    if "db" not in g:
        g.db = sqlite3.connect(DB)
        g.db.row_factory = sqlite3.Row
    return g.db

@app.teardown_appcontext
def close(_):
    d = g.pop("db", None)
    if d:
        d.close()

@app.after_request
def cors(r):  # lets the dashboard call the API from another origin
    r.headers["Access-Control-Allow-Origin"] = "*"
    r.headers["Access-Control-Allow-Headers"] = "Content-Type"
    r.headers["Access-Control-Allow-Methods"] = "GET,POST,PUT,OPTIONS"
    return r

def init_db():
    with sqlite3.connect(DB) as c:
        c.executescript(open(os.path.join(HERE, "schema.sql")).read())

@app.post("/metrics")
def post_metrics():
    d = request.get_json(silent=True) or {}
    try:
        vm = str(d["vm_id"])
        vals = {"cpu": float(d["cpu"]), "memory": float(d["memory"]), "disk": float(d["disk"])}
        uptime = int(d["uptime"])
    except (KeyError, TypeError, ValueError):
        return jsonify(error="invalid payload"), 400
    ts = d.get("timestamp") or datetime.now(timezone.utc).isoformat()
    c = db()
    c.execute("INSERT INTO vms(id,last_seen) VALUES(?,?) "
              "ON CONFLICT(id) DO UPDATE SET last_seen=excluded.last_seen", (vm, ts))
    c.execute("INSERT INTO metrics(vm_id,cpu,memory,disk,uptime,ts) VALUES(?,?,?,?,?,?)",
              (vm, vals["cpu"], vals["memory"], vals["disk"], uptime, ts))
    fired = []
    for t in c.execute("SELECT metric,value FROM thresholds").fetchall():
        v = vals.get(t["metric"])
        if v is not None and v > t["value"]:
            c.execute("INSERT INTO alerts(vm_id,metric,value,threshold,ts) VALUES(?,?,?,?,?)",
                      (vm, t["metric"], v, t["value"], ts))
            fired.append(t["metric"])
    c.commit()
    return jsonify(status="ok", alerts=fired), 201

@app.get("/vms")
def vms():
    rows = db().execute(
        "SELECT m.* FROM metrics m JOIN "
        "(SELECT vm_id, MAX(id) mid FROM metrics GROUP BY vm_id) x ON m.id = x.mid").fetchall()
    return jsonify([dict(r) for r in rows])

@app.get("/metrics")
def history():
    vm = request.args.get("vm_id")
    if not vm:
        return jsonify(error="vm_id required"), 400
    q = "SELECT * FROM metrics WHERE vm_id=?"
    args = [vm]
    if request.args.get("from"):
        q += " AND ts>=?"; args.append(request.args["from"])
    if request.args.get("to"):
        q += " AND ts<=?"; args.append(request.args["to"])
    q += " ORDER BY ts DESC LIMIT 1000"
    return jsonify([dict(r) for r in db().execute(q, args).fetchall()])

@app.get("/alerts")
def alerts():
    rows = db().execute("SELECT * FROM alerts ORDER BY id DESC LIMIT 100").fetchall()
    return jsonify([dict(r) for r in rows])

@app.get("/thresholds")
def get_thresholds():
    return jsonify({r["metric"]: r["value"] for r in db().execute("SELECT * FROM thresholds")})

@app.put("/thresholds")
def put_thresholds():
    d = request.get_json(silent=True) or {}
    c = db()
    for k, v in d.items():
        if k in ("cpu", "memory", "disk"):
            c.execute("UPDATE thresholds SET value=? WHERE metric=?", (float(v), k))
    c.commit()
    return get_thresholds()

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000)