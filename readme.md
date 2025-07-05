
# Docker Build & Compose Tool

Ένα γραφικό εργαλείο για Windows που απλοποιεί τη δημιουργία Docker images και docker-compose files από Python scripts.

📋 Περιεχόμενα  
Χαρακτηριστικά  
Προαπαιτούμενα  
Εγκατάσταση  
Χρήση  
Παραδείγματα  
Troubleshooting  
Συμβουλές  

## 🚀 Χαρακτηριστικά

- Φιλικό GUI: Εύκολη χρήση μέσω γραφικού περιβάλλοντος  
- Αυτόματη δημιουργία Dockerfile: Δημιουργεί βελτιστοποιημένο Dockerfile  
- Υποστήριξη requirements.txt: Αυτόματη εγκατάσταση dependencies  
- Port mapping: Προαιρετική ρύθμιση ports για web applications  
- Docker Compose: Δημιουργία έτοιμου docker-compose.yml  
- Real-time logging: Παρακολούθηση της διαδικασίας build σε πραγματικό χρόνο  
- Έλεγχος Docker: Αυτόματος έλεγχος εγκατάστασης Docker  

## 📦 Προαπαιτούμενα

### Windows

- Python 3.8 ή νεότερη έκδοση  
- Docker Desktop για Windows  
- tkinter (συνήθως προεγκατεστημένο με Python)  

### Linux/CasaOS

- Python 3.8+  
- Docker Engine  
- tkinter: `sudo apt-get install python3-tk`  

## 🛠️ Εγκατάσταση

### 1. Εγκατάσταση Docker

#### Windows:

```bash
# Κατεβάστε και εγκαταστήστε Docker Desktop
# https://www.docker.com/products/docker-desktop/
```

#### Linux/CasaOS:

```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
```

### 2. Εγκατάσταση εργαλείου

```bash
git clone <repository_url>
cd docker-tool

python docker_tool.py
```

## 🎯 Χρήση

### Βήμα 1: Επιλογή Python Script

- Κάντε κλικ στο "Επιλογή..."  
- Επιλέξτε το Python αρχείο που θέλετε να containerize  
- Το όνομα του image θα οριστεί αυτόματα  

### Βήμα 2: Δημιουργία Docker Image

- Επεξεργαστείτε το όνομα του image αν χρειάζεται  
- Κάντε κλικ στο "🚀 Build Docker Image"  
- Παρακολουθήστε τη διαδικασία στο log  

### Βήμα 2.5: Ρύθμιση Ports (Προαιρετικό)

- Ενεργοποιήστε το "Port Mapping" αν έχετε web app  
- Ορίστε Host Port (π.χ. 8080)  
- Ορίστε Container Port (π.χ. 8080)  

### Βήμα 3: Δημιουργία Docker Compose

- Κάντε κλικ στο "📄 Δημιουργία docker-compose.yml"  
- Επιλέξτε τη θέση αποθήκευσης  
- Το αρχείο θα δημιουργηθεί αυτόματα  

## 📁 Παραδείγματα

### Παράδειγμα 1: Απλό Console App

**test_app.py:**

```python
import time
import datetime

def main():
    print("🚀 Python App Started!")
    print(f"📅 Current time: {datetime.datetime.now()}")

    for i in range(5):
        print(f"⏰ Working... {i+1}/5")
        time.sleep(2)

    print("✅ App finished successfully!")

if __name__ == "__main__":
    main()
```

**Εκτέλεση:**

```bash
docker-compose up
```

### Παράδειγμα 2: Web Application

**web_app.py:**

```python
from http.server import HTTPServer, BaseHTTPRequestHandler
import datetime

class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

        html = f"""<html>
<body>
<h1>🐳 Docker Test App</h1>
<p>Current time: {datetime.datetime.now()}</p>
<p>Container is running!</p>
</body>
</html>"""
        self.wfile.write(html.encode())

def main():
    server = HTTPServer(('0.0.0.0', 8080), SimpleHandler)
    print("🌐 Starting web server on port 8080")
    server.serve_forever()

if __name__ == "__main__":
    main()
```

**Ρύθμιση Ports:**

- Host Port: 8080  
- Container Port: 8080  
- Πρόσβαση: http://localhost:8080  

## 🔧 Troubleshooting

### Πρόβλημα: "Docker δεν βρέθηκε"

```bash
docker --version
sudo systemctl start docker
# Windows: Ανοίξτε το Docker Desktop από το Start Menu
```

### Πρόβλημα: "pull access denied"

```bash
cd /path/to/your/project
docker build -t your-image-name .
docker-compose up
```

### Πρόβλημα: "Port already in use"

```bash
netstat -tulpn | grep :8080
docker-compose down
# Αλλάξτε το port στο docker-compose.yml
```

### Πρόβλημα: Build αποτυγχάνει

```bash
docker system prune
docker logs <container_name>
docker build -t test-app . --no-cache
```

## 💡 Συμβουλές

### Βελτίωση Performance

Χρησιμοποιήστε `.dockerignore`:

```dockerignore
__pycache__/
*.pyc
*.pyo
*.pyd
.git/
.gitignore
README.md
```

Βελτιστοποίηση Dockerfile:

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "app.py"]
```

### Χρήσιμες Docker Commands

```bash
docker images
docker ps
docker stop <container_name>
docker rm <container_name>
docker system prune -a
docker logs <container_name>
```

### Δημιουργία requirements.txt

```bash
pip freeze > requirements.txt
```

## 🌐 Παραδείγματα Web Apps

### Flask App

```python
from flask import Flask
app = Flask(__name__)

@app.route('/')
def hello():
    return '<h1>Hello from Docker!</h1>'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
```

### FastAPI App

```python
from fastapi import FastAPI
import uvicorn

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hello from Docker!"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
```

## 📝 Σημειώσεις

- Το εργαλείο δημιουργεί αυτόματα βελτιστοποιημένα Dockerfiles  
- Υποστηρίζει αυτόματη εγκατάσταση dependencies από requirements.txt  
- Το port mapping είναι προαιρετικό - χρησιμοποιήστε το μόνο για web apps  
- Μπορείτε να επεξεργαστείτε το docker-compose.yml μετά τη δημιουργία  

## 🐞 Αναφορά Σφαλμάτων

Αν αντιμετωπίσετε προβλήματα:

- Ελέγξτε τα logs στο εργαλείο  
- Βεβαιωθείτε ότι το Docker τρέχει  
- Ελέγξτε τα permissions (Linux)  
- Δοκιμάστε να τρέξετε τις εντολές manually  

**Δημιουργήθηκε για απλή και γρήγορη containerization Python εφαρμογών! 🐳**
