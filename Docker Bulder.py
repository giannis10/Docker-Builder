import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import os
import subprocess
import threading
import queue
import time

def check_docker_installed():
    """Checks if Docker is installed and accessible."""
    try:
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        
        subprocess.run(
            ["docker", "--version"], 
            check=True, 
            capture_output=True,
            startupinfo=startupinfo
        )
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

class DockerToolApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Docker Build & Compose Tool")
        self.root.geometry("800x650")

        self.script_path = tk.StringVar()
        self.image_name = tk.StringVar(value="my-python-app")
        self.host_port = tk.StringVar()
        self.container_port = tk.StringVar()
        self.enable_port = tk.BooleanVar(value=False)  # Fixed: added value parameter
        
        self.log_queue = queue.Queue()
        self.docker_available = False
        self.build_thread = None
        self.build_process = None

        self.create_widgets()
        self.perform_initial_checks()
        
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.periodic_call()

    def create_widgets(self):
        main_frame = tk.Frame(self.root, padx=15, pady=15)
        main_frame.pack(fill=tk.BOTH, expand=True)
        main_frame.grid_columnconfigure(0, weight=1)

        # Step 1: Select Script
        script_frame = tk.LabelFrame(main_frame, text="Βήμα 1: Επιλογή Python Script")
        script_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        script_frame.grid_columnconfigure(0, weight=1)
        sf_inner = tk.Frame(script_frame, padx=5, pady=5)
        sf_inner.pack(fill=tk.X)
        sf_inner.grid_columnconfigure(0, weight=1)
        tk.Entry(sf_inner, textvariable=self.script_path).grid(row=0, column=0, sticky="ew")
        tk.Button(sf_inner, text="Επιλογή...", command=self.browse_file).grid(row=0, column=1, padx=(5, 0))

        # Step 2: Set Image Name & Build
        build_frame = tk.LabelFrame(main_frame, text="Βήμα 2: Δημιουργία Docker Image")
        build_frame.grid(row=1, column=0, sticky="ew", pady=5)
        build_frame.grid_columnconfigure(1, weight=1)
        tk.Label(build_frame, text="Όνομα Image:", padx=5, pady=10).grid(row=0, column=0)
        tk.Entry(build_frame, textvariable=self.image_name).grid(row=0, column=1, sticky="ew", padx=5)
        self.build_button = tk.Button(build_frame, text="🚀 Build Docker Image", command=self.start_build_thread, height=2, bg="#007bff", fg="white", state="disabled")
        self.build_button.grid(row=1, column=0, columnspan=2, sticky="ew", pady=5, padx=5)

        # Step 2.5: Port Configuration (Optional)
        port_frame = tk.LabelFrame(main_frame, text="Βήμα 2.5: Ρύθμιση Ports (Προαιρετικό)")
        port_frame.grid(row=2, column=0, sticky="ew", pady=5)
        port_frame.grid_columnconfigure(1, weight=1)
        
        # Checkbox to enable port configuration
        self.port_checkbox = tk.Checkbutton(port_frame, text="Ενεργοποίηση Port Mapping", 
                                           variable=self.enable_port, command=self.toggle_port_fields)
        self.port_checkbox.grid(row=0, column=0, columnspan=3, sticky="w", padx=5, pady=5)
        
        # Port fields (initially disabled)
        tk.Label(port_frame, text="Host Port:", padx=5).grid(row=1, column=0, sticky="w")
        self.host_port_entry = tk.Entry(port_frame, textvariable=self.host_port, width=10, state="disabled")
        self.host_port_entry.grid(row=1, column=1, sticky="w", padx=5)
        
        tk.Label(port_frame, text="Container Port:", padx=5).grid(row=1, column=2, sticky="w", padx=(20,5))
        self.container_port_entry = tk.Entry(port_frame, textvariable=self.container_port, width=10, state="disabled")
        self.container_port_entry.grid(row=1, column=3, sticky="w", padx=5)
        
        # Help text
        help_label = tk.Label(port_frame, text="π.χ. Host: 8080, Container: 80 → http://localhost:8080", 
                             font=('Arial', 8), fg="gray")
        help_label.grid(row=2, column=0, columnspan=4, sticky="w", padx=5, pady=2)

        # Step 3: Get Compose File
        compose_frame = tk.LabelFrame(main_frame, text="Βήμα 3: Λήψη Docker Compose")
        compose_frame.grid(row=3, column=0, sticky="ew", pady=(10,0))
        compose_frame.grid_columnconfigure(0, weight=1)
        self.compose_button = tk.Button(compose_frame, text="📄 Δημιουργία docker-compose.yml", command=self.create_compose_file, state="disabled")
        self.compose_button.pack(fill=tk.X, pady=5, padx=5)
        
        # Output Log
        log_frame = tk.LabelFrame(main_frame, text="Αρχείο καταγραφής (Log)")
        log_frame.grid(row=4, column=0, sticky="nsew", pady=(10, 0))
        log_frame.grid_rowconfigure(0, weight=1)
        log_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_rowconfigure(4, weight=1)
        self.output_text = scrolledtext.ScrolledText(log_frame, wrap=tk.WORD, state="disabled", bg="black", fg="white")
        self.output_text.grid(row=0, column=0, sticky="nsew")

    def perform_initial_checks(self):
        self.docker_available = check_docker_installed()
        if self.docker_available:
            self.build_button.config(state="normal")
            self.log_message("✅ Το Docker βρέθηκε στο σύστημα.\n")
        else:
            self.build_button.config(state="disabled")
            error_msg = "❌ Το Docker δεν βρέθηκε! \nΠαρακαλώ εγκαταστήστε το Docker και κάντε επανεκκίνηση της εφαρμογής."
            self.log_message(error_msg)
            messagebox.showerror("Docker Not Found", error_msg)
        
    def browse_file(self):
        filename = filedialog.askopenfilename(title="Επιλέξτε Python script", filetypes=(("Python files", "*.py"), ("All files", "*.*")))
        if filename:
            self.script_path.set(filename)
            base_name = os.path.splitext(os.path.basename(filename))[0].lower().replace("_", "-")
            self.image_name.set(f"{base_name}-app")

    def toggle_port_fields(self):
        """Enable/disable port configuration fields"""
        if self.enable_port.get():
            self.host_port_entry.config(state="normal")
            self.container_port_entry.config(state="normal")
            # Set default values if empty
            if not self.host_port.get():
                self.host_port.set("8080")
            if not self.container_port.get():
                self.container_port.set("8080")
        else:
            self.host_port_entry.config(state="disabled")
            self.container_port_entry.config(state="disabled")

    def log_message(self, message):
        self.output_text.config(state="normal")
        self.output_text.insert(tk.END, message)
        self.output_text.see(tk.END)
        self.output_text.config(state="disabled")
        
    def start_build_thread(self):
        script = self.script_path.get()
        if not script or not os.path.exists(script):
            messagebox.showerror("Σφάλμα", "Παρακαλώ επιλέξτε ένα έγκυρο αρχείο Python.")
            return
        
        # Clear previous output
        self.output_text.config(state="normal")
        self.output_text.delete(1.0, tk.END)
        self.output_text.config(state="disabled")
        
        # Update UI
        self.build_button.config(state="disabled", text="Building...")
        self.compose_button.config(state="disabled")
        
        # Start build thread
        self.build_thread = threading.Thread(target=self.build_worker, daemon=True)
        self.build_thread.start()

    def create_enhanced_dockerfile(self, script_file, script_name):
        """Create a more robust Dockerfile with error handling and requirements"""
        script_dir = os.path.dirname(script_file)
        dockerfile_path = os.path.join(script_dir, "Dockerfile")
        
        # Check if requirements.txt exists
        requirements_path = os.path.join(script_dir, "requirements.txt")
        has_requirements = os.path.exists(requirements_path)
        
        dockerfile_content = f"""FROM python:3.9-slim

WORKDIR /app

# Copy requirements first for better caching
{f"COPY requirements.txt ." if has_requirements else "# No requirements.txt found"}
{f"RUN pip install --no-cache-dir -r requirements.txt" if has_requirements else ""}

# Copy the Python script
COPY {script_name} .

# Make sure the script is executable
RUN chmod +x {script_name}

CMD ["python", "./{script_name}"]
"""
        
        try:
            with open(dockerfile_path, 'w', encoding='utf-8') as f:
                f.write(dockerfile_content)
            self.log_queue.put(f"✅ Dockerfile δημιουργήθηκε: {dockerfile_path}\n")
            if has_requirements:
                self.log_queue.put(f"✅ Βρέθηκε requirements.txt - θα εγκατασταθούν οι dependencies\n")
            else:
                self.log_queue.put(f"ℹ️ Δεν βρέθηκε requirements.txt - χρήση βασικής Python εικόνας\n")
            self.log_queue.put("\n")
            return True
        except Exception as e:
            self.log_queue.put(f"❌ Αποτυχία δημιουργίας Dockerfile: {e}\n")
            return False

    def build_worker(self):
        try:
            script_file = self.script_path.get()
            image_name = self.image_name.get()
            script_dir = os.path.dirname(script_file)
            script_name = os.path.basename(script_file)

            # Create enhanced Dockerfile
            if not self.create_enhanced_dockerfile(script_file, script_name):
                self.log_queue.put("build_failed")
                return

            self.log_queue.put(f"--- Εκκίνηση Docker Build για την εικόνα '{image_name}' ---\n")
            
            # Create subprocess with proper configuration
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            
            self.build_process = subprocess.Popen(
                ["docker", "build", "-t", image_name, "."], 
                cwd=script_dir, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.STDOUT, 
                text=True, 
                encoding='utf-8', 
                errors='replace',
                startupinfo=startupinfo,
                universal_newlines=True,
                bufsize=1  # Line buffered
            )
            
            # Better output reading with timeout
            while self.build_process.poll() is None:
                try:
                    line = self.build_process.stdout.readline()
                    if line:
                        self.log_queue.put(line)
                    else:
                        time.sleep(0.1)  # Small delay if no output
                except Exception as e:
                    self.log_queue.put(f"Error reading output: {e}\n")
                    break
            
            # Read any remaining output
            remaining_output = self.build_process.stdout.read()
            if remaining_output:
                self.log_queue.put(remaining_output)
            
            # Check return code
            rc = self.build_process.returncode
            
            if rc == 0:
                self.log_queue.put(f"\n--- ✅ Build Ολοκληρώθηκε Επιτυχώς! ---\n")
                self.log_queue.put(f"✅ Η εικόνα '{image_name}' δημιουργήθηκε με επιτυχία\n")
                self.log_queue.put("build_success")
            else:
                self.log_queue.put(f"\n--- ❌ Build Απέτυχε με κωδικό σφάλματος: {rc} ---\n")
                self.log_queue.put("build_failed")
                
        except Exception as e:
            self.log_queue.put(f"\n--- ❌ Παρουσιάστηκε ένα σφάλμα: {e} ---\n")
            self.log_queue.put("build_failed")
        finally:
            if self.build_process:
                try:
                    self.build_process.stdout.close()
                except:
                    pass
                self.build_process = None

    def create_compose_file(self):
        script_dir = os.path.dirname(self.script_path.get())
        image_name = self.image_name.get()
        container_name = image_name.replace('-app', '-container')
        
        # Base compose content
        compose_content = f"""version: '3.8'

services:
  {container_name}:
    image: {image_name}:latest
    container_name: {container_name}
    restart: unless-stopped"""
        
        # Add port mapping if enabled
        if self.enable_port.get():
            host_port = self.host_port.get().strip()
            container_port = self.container_port.get().strip()
            
            if host_port and container_port:
                try:
                    # Validate ports are numbers
                    int(host_port)
                    int(container_port)
                    compose_content += f"""
    ports:
      - "{host_port}:{container_port}" """
                except ValueError:
                    messagebox.showerror("Σφάλμα", "Τα ports πρέπει να είναι αριθμοί!")
                    return
        
        # Add additional configuration section
        compose_content += """
    # Add any additional configuration here
    # volumes:
    #   - ./data:/app/data
    # environment:
    #   - ENV_VAR=value
    # networks:
    #   - mynetwork
"""
        
        save_path = filedialog.asksaveasfilename(
            initialdir=script_dir, 
            initialfile="docker-compose.yml", 
            defaultextension=".yml", 
            filetypes=[("YAML files", "*.yml"), ("All files", "*.*")]
        )
        
        if save_path:
            try:
                with open(save_path, 'w', encoding='utf-8') as f:
                    f.write(compose_content)
                
                # Show success message with port info
                success_msg = f"Το αρχείο docker-compose.yml αποθηκεύτηκε στο:\n{save_path}"
                if self.enable_port.get() and self.host_port.get() and self.container_port.get():
                    success_msg += f"\n\n🌐 Η εφαρμογή θα είναι διαθέσιμη στο: http://localhost:{self.host_port.get()}"
                
                messagebox.showinfo("Επιτυχία", success_msg)
            except Exception as e:
                messagebox.showerror("Σφάλμα", f"Δεν ήταν δυνατή η αποθήκευση του αρχείου:\n{e}")

    def periodic_call(self):
        """Process messages from the queue"""
        message_count = 0
        while not self.log_queue.empty() and message_count < 10:  # Limit messages per call
            try:
                message = self.log_queue.get_nowait()
                if message == "build_success":
                    self.compose_button.config(state="normal")
                    self.build_button.config(state="normal", text="🚀 Build Docker Image")
                elif message == "build_failed":
                    self.build_button.config(state="normal", text="🚀 Build Docker Image")
                else:
                    self.log_message(message)
                message_count += 1
            except queue.Empty:
                break
        
        # Continue periodic calls
        self.root.after(100, self.periodic_call)

    def on_closing(self):
        if self.build_thread and self.build_thread.is_alive():
            if messagebox.askokcancel("Έξοδος", "Μια διαδικασία build είναι σε εξέλιξη. Είστε σίγουροι ότι θέλετε να κλείσετε την εφαρμογή;"):
                # Try to terminate the build process
                if self.build_process:
                    try:
                        self.build_process.terminate()
                    except:
                        pass
                self.root.destroy()
        else:
            self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = DockerToolApp(root)
    root.mainloop()