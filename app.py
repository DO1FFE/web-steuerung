from flask import Flask, request, render_template_string
import os
import subprocess
import re

app = Flask(__name__)

BASE_DIR = '/home/do1ffe'

# Vordefinierte Befehle, die per Button ausgeführt werden können
COMMANDS = {
    'Start Service': 'sudo systemctl start xxx.service',
    'Stop Service': 'sudo systemctl stop xxx.service',
    'Erneuern': 'erneuern',
}


def find_service_dirs():
    """Liest Systemd-Service-Dateien und extrahiert Directory-Pfade."""
    service_dir = '/etc/systemd/system'
    dirs = []
    if not os.path.isdir(service_dir):
        return dirs
    for name in os.listdir(service_dir):
        if not name.endswith('.service'):
            continue
        path = os.path.join(service_dir, name)
        try:
            result = subprocess.run(
                ['sudo', 'grep', '-m', '1', '^WorkingDirectory=/home/do1ffe', path],
                capture_output=True,
                text=True,
                check=False,
            )
            if result.returncode == 0 and result.stdout:
                line = result.stdout.splitlines()[0].strip()
                m = re.match(r'^WorkingDirectory=(/home/do1ffe.*)', line)
                if m:
                    full_path = m.group(1)
                    rel = os.path.relpath(full_path, BASE_DIR)
                    if os.path.isdir(os.path.join(BASE_DIR, rel)):
                        dirs.append(rel)
        except Exception:
            continue
    return sorted(set(dirs))

TEMPLATE = '''
<!doctype html>
<title>Web Steuerung</title>
<h1>Befehle ausführen</h1>
<form method=post>
    <label>Verzeichnis:</label>
    <select name=path>
    {% for d in dirs %}
        <option value="{{ d }}" {% if d == path %}selected{% endif %}>{{ d }}</option>
    {% endfor %}
    </select>
    <br>
    {% for key in commands.keys() %}
        <button type="submit" name="command" value="{{ key }}">{{ key }}</button>
    {% endfor %}
</form>
<pre>{{ output }}</pre>
'''

@app.route('/', methods=['GET', 'POST'])
def index():
    dirs = find_service_dirs()
    path = request.form.get('path', dirs[0] if dirs else '')
    command_key = request.form.get('command')
    output = ''
    if command_key in COMMANDS and path:
        abs_path = os.path.abspath(os.path.join(BASE_DIR, path))
        if abs_path.startswith(os.path.abspath(BASE_DIR)):
            try:
                cmd = COMMANDS[command_key]
                result = subprocess.run(cmd, cwd=abs_path, shell=True, capture_output=True, text=True)
                output = result.stdout + result.stderr
            except Exception as e:
                output = str(e)
        else:
            output = 'Ungültiger Pfad'
    return render_template_string(
        TEMPLATE,
        base=BASE_DIR,
        dirs=dirs,
        path=path,
        commands=COMMANDS,
        output=output,
    )

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8014)
