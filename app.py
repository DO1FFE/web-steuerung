from flask import Flask, request, render_template_string
import os
import subprocess

app = Flask(__name__)

BASE_DIR = '/home/do1ffe'

# Vordefinierte Befehle, die per Button ausgeführt werden können
COMMANDS = {
    'Start Service': 'sudo systemctl start xxx.service',
    'Stop Service': 'sudo systemctl stop xxx.service',
    'Erneuern': 'erneuern',
}

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
    dirs = []
    if os.path.isdir(BASE_DIR):
        dirs = [d for d in os.listdir(BASE_DIR) if os.path.isdir(os.path.join(BASE_DIR, d))]
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
