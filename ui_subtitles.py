import tkinter as tk
from tkinter import scrolledtext, filedialog, ttk
from threading import Lock
from datetime import datetime

import os
import sys

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class SubtitlesUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Hermes: The Real-Time Voice Proxy")
        
        # Configurar ventana siempre arriba y ligeramente transparente
        self.root.attributes('-topmost', True)
        self.root.attributes('-alpha', 0.95)
        self.root.configure(bg='#1e1e1e')
        
        # Iniciar maximizado en pantalla
        self.root.state('zoomed')
        
        # --- BARRA SUPERIOR (Controles) ---
        self.top_frame = tk.Frame(self.root, bg='#333333')
        self.top_frame.pack(side=tk.TOP, fill=tk.X)

        # Logo
        try:
            self.logo_img = tk.PhotoImage(file=resource_path("logo.png"))
            self.lbl_logo = tk.Label(self.top_frame, image=self.logo_img, bg='#333333')
            self.lbl_logo.pack(side=tk.LEFT, padx=(10, 0), pady=5)
        except Exception as e:
            print("No se pudo cargar el logo:", e)

        # Botón Encendido/Apagado
        self.is_active = False
        self.btn_toggle = tk.Button(self.top_frame, text="🔴 PAUSADO", bg='#7f8c8d', fg='white', font=('Segoe UI', 9, 'bold'), relief=tk.FLAT, command=self.toggle_active, width=12)
        self.btn_toggle.pack(side=tk.LEFT, padx=10, pady=5)
        
        # Selector de Idioma
        tk.Label(self.top_frame, text="Idioma de Reunión:", bg='#333333', fg='white', font=('Segoe UI', 9)).pack(side=tk.LEFT, padx=(10, 2))
        self.lang_var = tk.StringVar()
        self.combo_lang = ttk.Combobox(self.top_frame, textvariable=self.lang_var, values=["Inglés", "Francés", "Alemán"], state="readonly", width=10)
        self.combo_lang.current(0)
        self.combo_lang.pack(side=tk.LEFT, padx=5, pady=5)
        
        # Info Dispositivos
        self.lbl_devices = tk.Label(self.top_frame, text="🔈 Altavoces: --- | 🎙️ Micro: ---", bg='#333333', fg='#cccccc', font=('Segoe UI', 9))
        self.lbl_devices.pack(side=tk.RIGHT, padx=10, pady=5)
        
        # Línea de neón dorada
        self.neon_line = tk.Frame(self.root, bg='#f1c40f', height=2)
        self.neon_line.pack(side=tk.TOP, fill=tk.X)
        
        # --- LAYOUT PRINCIPAL ---
        self.left_frame = tk.Frame(self.root, bg='#1e1e1e')
        # Left frame gets 2/3 of space -> expand=True, right frame gets fixed width
        self.left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.right_frame = tk.Frame(self.root, bg='#2d2d2d', width=650)
        self.right_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=10, pady=10)
        self.right_frame.pack_propagate(False)

        # --- PANEL IZQUIERDO (Subtítulos en vivo) ---
        self.english_var = tk.StringVar()
        self.english_var.set("Hermes está pausado.")
        self.spanish_var = tk.StringVar()
        self.spanish_var.set("")

        self.lbl_en = tk.Label(self.left_frame, textvariable=self.english_var, fg='#aaaaaa', bg='#1e1e1e', font=('Segoe UI', 12, 'italic'), wraplength=700, justify='center')
        self.lbl_en.pack(pady=(15, 0), fill=tk.X)

        self.lbl_es = tk.Label(self.left_frame, textvariable=self.spanish_var, fg='#f1c40f', bg='#1e1e1e', font=('Segoe UI', 18, 'bold'), wraplength=700, justify='center')
        self.lbl_es.pack(pady=(10, 15), fill=tk.X)
        
        # Botón de hablar
        self.btn_talk = tk.Button(self.left_frame, text="🗣 Mantén pulsado para hablar", bg='#e74c3c', fg='white', font=('Segoe UI', 12, 'bold'), relief=tk.FLAT)
        self.btn_talk.pack(pady=5)
        
        # Powered By text
        self.lbl_powered = tk.Label(self.left_frame, text="⚡ Powered by AssemblyAI & Google Gemini", bg='#1e1e1e', fg='#555555', font=('Segoe UI', 9, 'bold'))
        self.lbl_powered.pack(side=tk.BOTTOM, pady=5)
        
        # --- PANEL DERECHO (Historial / Log) ---
        lbl_log_title = tk.Label(self.right_frame, text="📄 Historial de Conversación", fg='white', bg='#2d2d2d', font=('Segoe UI', 10, 'bold'))
        lbl_log_title.pack(anchor=tk.W, pady=(0,5))

        self.log_area = scrolledtext.ScrolledText(self.right_frame, bg='#1e1e1e', fg='#ffffff', font=('Consolas', 10), wrap=tk.WORD, height=8)
        self.log_area.pack(fill=tk.BOTH, expand=True)
        self.log_area.config(state=tk.DISABLED)
        
        # Definir tags para colores
        self.log_area.tag_config('sys_header', foreground='#3498db', font=('Consolas', 10, 'bold'))
        self.log_area.tag_config('user_header', foreground='#2ecc71', font=('Consolas', 10, 'bold'))
        self.log_area.tag_config('texto', foreground='#ffffff')

        self.btn_export = tk.Button(self.right_frame, text="💾 Exportar Log", bg='#3498db', fg='white', font=('Segoe UI', 9), relief=tk.FLAT, command=self.export_log)
        self.btn_export.pack(fill=tk.X, pady=(5,0))

        # --- LÓGICA Y EVENTOS ---
        self.lock = Lock()
        self.on_press_cb = None
        self.on_release_cb = None
        
        self.btn_talk.bind('<ButtonPress-1>', self._on_press)
        self.btn_talk.bind('<ButtonRelease-1>', self._on_release)

    def toggle_active(self):
        self.is_active = not self.is_active
        if self.is_active:
            self.btn_toggle.config(bg='#27ae60', text="🟢 ACTIVO")
            self.english_var.set("Esperando audio...")
        else:
            self.btn_toggle.config(bg='#7f8c8d', text="🔴 PAUSADO")
            self.english_var.set("Hermes está pausado.")
            self.spanish_var.set("")

    def set_callbacks(self, on_press, on_release):
        self.on_press_cb = on_press
        self.on_release_cb = on_release
        
    def set_devices_info(self, speaker_name, mic_name):
        self.lbl_devices.config(text=f"🔈 Altavoces: {speaker_name} | 🎙️ Micro: {mic_name}")

    def set_processing_state(self, is_processing):
        if not self.is_active: return
        if is_processing:
            self.btn_talk.config(bg='#8e44ad', text="⚡ Procesando IA...")
            self.btn_talk.update()
        else:
            self.btn_talk.config(bg='#e74c3c', text="🗣 Mantén pulsado para hablar")
            self.btn_talk.update()

    def _on_press(self, event):
        if not self.is_active: return
        self.btn_talk.config(bg='#c0392b', text="🎙 GRABANDO (Suelta para enviar)")
        if self.on_press_cb:
            self.on_press_cb()

    def _on_release(self, event):
        if not self.is_active: return
        self.set_processing_state(True)
        if self.on_release_cb:
            self.on_release_cb()

    def update_english(self, text, is_final=False):
        if not self.is_active: return
        with self.lock:
            if is_final:
                self.english_var.set(text)
            else:
                self.english_var.set(f"{text} ...")

    def update_spanish(self, text):
        if not self.is_active: return
        with self.lock:
            self.spanish_var.set(text)

    def append_log(self, speaker, original_text, translated_text):
        if not self.is_active: return
        timestamp = datetime.now().strftime("%H:%M:%S")
        lang = self.combo_lang.get()[:2].upper()
        
        with self.lock:
            self.log_area.config(state=tk.NORMAL)
            
            if speaker == "ZOOM":
                header = f"[{timestamp}] SISTEMA ({lang} ➔ ES):\n"
                self.log_area.insert(tk.END, header, 'sys_header')
            else:
                header = f"[{timestamp}] TÚ (ES ➔ {lang}):\n"
                self.log_area.insert(tk.END, header, 'user_header')
                
            self.log_area.insert(tk.END, f"  Orig: {original_text}\n", 'texto')
            self.log_area.insert(tk.END, f"  Trad: {translated_text}\n\n", 'texto')
            
            self.log_area.see(tk.END)
            self.log_area.config(state=tk.DISABLED)

    def export_log(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".txt", 
                                                 filetypes=[("Text files", "*.txt")],
                                                 title="Guardar historial de conversación",
                                                 initialfile=f"Hermes_Log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
        if file_path:
            with open(file_path, 'w', encoding='utf-8') as f:
                with self.lock:
                    f.write(self.log_area.get(1.0, tk.END))

    def start(self):
        self.root.mainloop()

    def quit(self):
        self.root.quit()
