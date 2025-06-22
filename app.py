from flask import (
    Flask,
    request,
    render_template,
    redirect,
    url_for,
    session,
    jsonify,
)
import os
import subprocess
import re
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", os.urandom(24))

users_env = os.getenv("USERS", "")
USERS = {
    u.split(":", 1)[0]: u.split(":", 1)[1] for u in users_env.split(",") if ":" in u
}

BASE_DIR = "/home/do1ffe"

# Vordefinierte Befehle, die per Button ausgeführt werden können
COMMANDS = {
    "Start Service": "sudo systemctl start {service}",
    "Stop Service": "sudo systemctl stop {service}",
    "Erneuern": "erneuern",
}


def get_service_status(service: str) -> str:
    """Prüft mit systemctl, ob der Service aktiv ist."""
    try:
        result = subprocess.run(
            ["sudo", "systemctl", "is-active", service],
            capture_output=True,
            text=True,
            check=False,
        )
        state = result.stdout.strip()
        if state == "active":
            return "gestartet"
        else:
            return "gestoppt"
    except Exception as e:
        return f"Fehler beim Prüfen: {e}"


def find_service_dirs():
    """Liest Systemd-Service-Dateien und ordnet Directories den Service-Namen zu."""
    service_dir = "/etc/systemd/system"
    dirs = {}
    if not os.path.isdir(service_dir):
        return dirs
    for name in os.listdir(service_dir):
        if not name.endswith(".service"):
            continue
        path = os.path.join(service_dir, name)
        try:
            result = subprocess.run(
                ["sudo", "grep", "-m", "1", "^WorkingDirectory=/home/", path],
                capture_output=True,
                text=True,
                check=False,
            )
            if result.returncode == 0 and result.stdout:
                line = result.stdout.splitlines()[0].strip()
                m = re.match(r"^WorkingDirectory=(/home/.*)", line)
                if m:
                    full_path = m.group(1)
                    if os.path.basename(os.path.normpath(full_path)) == "web-steuerung":
                        continue
                    base_abs = os.path.abspath(BASE_DIR)
                    if (
                        os.path.commonpath([os.path.abspath(full_path), base_abs])
                        != base_abs
                    ):
                        continue
                    rel = os.path.relpath(full_path, BASE_DIR)
                    if os.path.isdir(os.path.join(BASE_DIR, rel)):
                        dirs[rel] = name
        except Exception:
            continue
    return dict(sorted(dirs.items()))


@app.route("/login", methods=["GET", "POST"])
def login():
    error = ""
    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")
        if USERS.get(username) == password:
            session["username"] = username
            return redirect(url_for("index"))
        else:
            error = "Ung\u00fcltige Anmeldedaten"
    return render_template("login.html", error=error)


@app.route("/logout")
def logout():
    session.pop("username", None)
    return redirect(url_for("login"))


@app.route("/statuses")
def statuses():
    """Liefert den Status aller Dienste als JSON."""
    if "username" not in session:
        return jsonify({"error": "unauthorized"}), 401

    service_dirs = find_service_dirs()
    dirs = list(service_dirs.keys())
    data = {d: get_service_status(service_dirs[d]) for d in dirs}
    return jsonify({"statuses": data})


@app.route("/", methods=["GET", "POST"])
def index():
    if "username" not in session:
        return redirect(url_for("login"))

    service_dirs = find_service_dirs()
    dirs = list(service_dirs.keys())
    # Ermittele den Status für jeden gefundenen Service
    statuses = {d: get_service_status(service_dirs[d]) for d in dirs}

    path = request.form.get("path", dirs[0] if dirs else "")
    command_key = request.form.get("command")
    output = ""
    status = statuses.get(path, "")
    if command_key in COMMANDS and path:
        abs_path = os.path.abspath(os.path.join(BASE_DIR, path))
        if abs_path.startswith(os.path.abspath(BASE_DIR)):
            try:
                service = service_dirs.get(path, "")
                cmd_template = COMMANDS[command_key]
                cmd = cmd_template.format(service=service)
                result = subprocess.run(
                    cmd, cwd=abs_path, shell=True, capture_output=True, text=True
                )
                output = result.stdout + result.stderr
            except Exception as e:
                output = str(e)
        else:
            output = "Ungültiger Pfad"
    return render_template(
        "index.html",
        base=BASE_DIR,
        dirs=dirs,
        statuses=statuses,
        path=path,
        commands=COMMANDS,
        output=output,
        status=status,
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8014)
