import os
import sys
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext

class DockerBuilderApp(tk.Tk):
    def __init__(self):
        super().__init__()

        # Ορισμός εικονιδίου παραθύρου (taskbar + titlebar)
        try:
            icon_path = os.path.join(
                getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__))),
                'icon.ico'
            )
            self.iconbitmap(icon_path)
        except Exception as e:
            print("⚠️ Icon load failed:", e)

        self.title("Docker Build & Compose Tool")
        self.geometry("700x500")
        self.resizable(False, False)

        self.python_file_path = tk.StringVar()
        self.image_name = tk.StringVar(value="my-python-app")
        self.host_port = tk.StringVar()
        self.container_port = tk.StringVar()
        self.enable_ports = tk.BooleanVar()

        self.create_widgets()

        self.log("✓ Το Docker βρέθηκε στο σύστημα.")

    def create_widgets(self):
        pady = 5

        # Βήμα 1
        tk.Label(self, text="Βήμα 1: Επιλογή Python Script", font=('Segoe UI', 10, 'bold')).pack(anchor='w', padx=10, pady=(10, 0))
        frame1 = tk.Frame(self)
        frame1.pack(fill='x', padx=10)
        tk.Entry(frame1, textvariable=self.python_file_path, width=60).pack(side='left', fill='x', expand=True)
        tk.Button(frame1, text="Επιλογή...", command=self.select_python_file).pack(side='right')

        # Βήμα 2
        tk.Label(self, text="Βήμα 2: Δημιουργία Docker Image", font=('Segoe UI', 10, 'bold')).pack(anchor='w', padx=10, pady=(15, 0))
        tk.Entry(self, textvariable=self.image_name).pack(fill='x', padx=10)

        tk.Button(self, text="🔵 Build Docker Image", command=self.build_docker_image, bg="#007bff", fg="white").pack(fill='x', padx=10, pady=pady)

        # Βήμα 2.5 (Ports)
        ports_frame = tk.LabelFrame(self, text="Βήμα 2.5: Ρύθμιση Ports (Προαιρετικό)")
        ports_frame.pack(fill='x', padx=10, pady=pady)
        tk.Checkbutton(ports_frame, text="Ενεργοποίηση Port Mapping", variable=self.enable_ports).pack(anchor='w', padx=10)

        ports_inner = tk.Frame(ports_frame)
        ports_inner.pack(fill='x', padx=10, pady=5)
        tk.Label(ports_inner, text="Host Port:").grid(row=0, column=0)
        tk.Entry(ports_inner, textvariable=self.host_port, width=10).grid(row=0, column=1, padx=5)
        tk.Label(ports_inner, text="Container Port:").grid(row=0, column=2)
        tk.Entry(ports_inner, textvariable=self.container_port, width=10).grid(row=0, column=3, padx=5)
        tk.Label(ports_frame, text="π.χ. Host: 8080, Container: 80 → http://localhost:8080", font=("Segoe UI", 8, "italic")).pack(anchor='w', padx=10)

        # Βήμα 3
        tk.Label(self, text="Βήμα 3: Λήψη Docker Compose", font=('Segoe UI', 10, 'bold')).pack(anchor='w', padx=10, pady=(10, 0))
        tk.Button(self, text="📝 Δημιουργία docker-compose.yml", command=self.generate_docker_compose).pack(fill='x', padx=10, pady=pady)

        # Log
        tk.Label(self, text="Αρχείο καταγραφής (Log)", font=('Segoe UI', 10, 'bold')).pack(anchor='w', padx=10, pady=(10, 0))
        self.log_text = scrolledtext.ScrolledText(self, height=8, font=('Consolas', 10), bg='black', fg='lime', state='disabled')
        self.log_text.pack(fill='both', padx=10, pady=(0, 10), expand=True)

    def select_python_file(self):
        filepath = filedialog.askopenfilename(filetypes=[("Python files", "*.py")])
        if filepath:
            self.python_file_path.set(filepath)

    def log(self, message):
        self.log_text.configure(state='normal')
        self.log_text.insert('end', f"✓ {message}\n")
        self.log_text.see('end')
        self.log_text.configure(state='disabled')

    def build_docker_image(self):
        py_path = self.python_file_path.get()
        image = self.image_name.get()

        if not py_path or not os.path.isfile(py_path):
            messagebox.showerror("Σφάλμα", "Επιλέξτε ένα έγκυρο Python αρχείο.")
            return

        dockerfile_content = f"FROM python:3.10-slim\nCOPY {os.path.basename(py_path)} /app/\nWORKDIR /app\nCMD [\"python\", \"{os.path.basename(py_path)}\"]\n"

        with open("Dockerfile", "w") as f:
            f.write(dockerfile_content)

        os.system(f"copy \"{py_path}\" . > nul")
        os.system(f"docker build -t {image} .")
        self.log(f"Η εικόνα Docker '{image}' δημιουργήθηκε.")

    def generate_docker_compose(self):
        image = self.image_name.get()
        ports = ""
        if self.enable_ports.get():
            host = self.host_port.get()
            container = self.container_port.get()
            if host and container:
                ports = f"      - \"{host}:{container}\"\n"

        compose = (
            "version: '3'\n"
            "services:\n"
            "  app:\n"
            f"    image: {image}\n"
            f"{'    ports:\n' + ports if ports else ''}"
        )

        with open("docker-compose.yml", "w") as f:
            f.write(compose)

        self.log("Το αρχείο docker-compose.yml δημιουργήθηκε.")

if __name__ == "__main__":
    app = DockerBuilderApp()
    app.mainloop()
