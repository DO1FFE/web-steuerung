# web-steuerung

Dieses Projekt stellt eine einfache Flask-Webanwendung bereit, 
 mit der Befehle innerhalb von Verzeichnissen unter `/home/do1ffe`
 ausgeführt werden können. Die Anwendung lauscht auf `0.0.0.0`
 Port `8014` und ermittelt die verfügbaren Verzeichnisse aus den
 Systemd-Service-Dateien unter `/etc/systemd/system`. Es werden alle
 `*.service`-Dateien durchsucht, deren Zeile mit
 `WorkingDirectory=/home/do1ffe` beginnt. Das dahinter angegebene
 Verzeichnis erscheint dann in der Auswahlliste. Die darin ausführbaren
 Befehle sind fest vorgegeben und lassen sich über Buttons anklicken.

Voreingestellte Befehle:

- **Start Service** – `sudo systemctl start xxx.service`
- **Stop Service** – `sudo systemctl stop xxx.service`
- **Erneuern** – `erneuern`

**Wichtig:** Das Ausführen beliebiger Befehle über eine Weboberfläche 
ist potentiell sehr unsicher und sollte nur in vertrauenswürdigen Umgebungen 
verwendet werden.

## Starten
```bash
pip install flask
python app.py
```

Danach ist die Oberfläche unter `http://<server-ip>:8014/` erreichbar.
