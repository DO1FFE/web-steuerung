from flask import Flask, request, render_template
import os
import subprocess
import re

app = Flask(__name__)

BASE_DIR = '/home/do1ffe'

# Vordefinierte Befehle, die per Button ausgeführt werden können
COMMANDS = {
    'Start Service': 'sudo systemctl start {service}',
    'Stop Service': 'sudo systemctl stop {service}',
    'Erneuern': 'erneuern',
}


def find_service_dirs():
    """Liest Systemd-Service-Dateien und ordnet Directories den Service-Namen zu."""
    service_dir = '/etc/systemd/system'
    dirs = {}
    if not os.path.isdir(service_dir):
        return dirs
    for name in os.listdir(service_dir):
        if not name.endswith('.service'):
            continue
        path = os.path.join(service_dir, name)
        try:
            result = subprocess.run(
                ['sudo', 'grep', '-m', '1', '^WorkingDirectory=/home/', path],
                capture_output=True,
                text=True,
                check=False,
            )
            if result.returncode == 0 and result.stdout:
                line = result.stdout.splitlines()[0].strip()
                m = re.match(r'^WorkingDirectory=(/home/.*)', line)
                if m:
                    full_path = m.group(1)
                    if os.path.basename(os.path.normpath(full_path)) == 'web-steuerung':
                        continue
                    base_abs = os.path.abspath(BASE_DIR)
                    if os.path.commonpath([os.path.abspath(full_path), base_abs]) != base_abs:
                        continue
                    rel = os.path.relpath(full_path, BASE_DIR)
                    if os.path.isdir(os.path.join(BASE_DIR, rel)):
                        dirs[rel] = name
        except Exception:
            continue
    return dict(sorted(dirs.items()))


@app.route('/', methods=['GET', 'POST'])
def index():
    service_dirs = find_service_dirs()
    dirs = list(service_dirs.keys())
    path = request.form.get('path', dirs[0] if dirs else '')
    command_key = request.form.get('command')
    output = ''
    if command_key in COMMANDS and path:
        abs_path = os.path.abspath(os.path.join(BASE_DIR, path))
        if abs_path.startswith(os.path.abspath(BASE_DIR)):
            try:
                service = service_dirs.get(path, '')
                cmd_template = COMMANDS[command_key]
                cmd = cmd_template.format(service=service)
                result = subprocess.run(cmd, cwd=abs_path, shell=True, capture_output=True, text=True)
                output = result.stdout + result.stderr
            except Exception as e:
                output = str(e)
        else:
            output = 'Ungültiger Pfad'
    return render_template(
        'index.html',
        base=BASE_DIR,
        dirs=dirs,
        path=path,
        commands=COMMANDS,
        output=output,
    )

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8014)
