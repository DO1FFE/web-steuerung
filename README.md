# web-steuerung

Dieses Projekt stellt eine einfache Flask-Webanwendung bereit, 
 mit der Befehle innerhalb von Verzeichnissen unter `/home/do1ffe`
 ausgeführt werden können. Die Anwendung lauscht auf `0.0.0.0`
 Port `8014` und ermittelt die verfügbaren Verzeichnisse aus den
 Systemd-Service-Dateien unter `/etc/systemd/system`. Es werden alle
 `*.service`-Dateien durchsucht, deren Zeile mit
 `WorkingDirectory=/home/` beginnt. Angezeigt werden nur die Verzeichnisse
 unterhalb von `/home/do1ffe`, wobei das Projektverzeichnis `web-steuerung`
 ignoriert wird. Die darin ausführbaren
Befehle sind fest vorgegeben und lassen sich über Buttons anklicken.
Die Weboberfläche verwendet jetzt Bootstrap für ein moderneres Layout.

Voreingestellte Befehle:

- **Start Service** – `sudo systemctl start <service>.service`
- **Stop Service** – `sudo systemctl stop <service>.service`
- **Erneuern** – `erneuern`
Dabei entspricht `<service>` dem Dateinamen der gefundenen `.service`-Datei.

**Wichtig:** Das Ausführen beliebiger Befehle über eine Weboberfläche 
ist potentiell sehr unsicher und sollte nur in vertrauenswürdigen Umgebungen 
verwendet werden.

## Starten
```bash
pip install flask
python app.py
```

Danach ist die Oberfläche unter `http://<server-ip>:8014/` erreichbar.
