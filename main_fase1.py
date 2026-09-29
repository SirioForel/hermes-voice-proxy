import threading
import queue
import assemblyai as aai
from audio_capture import start_audio_capture
from translator_core import translate_to_spanish
from ui_subtitles import SubtitlesUI
import time

# Cola para manejar traducciones sin bloquear el audio
translation_queue = queue.Queue()
ui = None

def translation_worker():
    """Hilo que procesa los textos finales y pide la traducción a Gemini"""
    while True:
        english_text = translation_queue.get()
        if english_text is None:
            break
            
        spanish_text = translate_to_spanish(english_text)
        
        if ui:
            ui.update_spanish(spanish_text)
            
        translation_queue.task_done()

# --- Callbacks de AssemblyAI ---
def on_data(transcriber, event):
    if not getattr(event, "transcript", ""):
        return
        
    if event.end_of_turn:
        if ui:
            ui.update_english(event.transcript, is_final=True)
        # Enviar a Gemini para traducir
        translation_queue.put(event.transcript)
    else:
        # Texto parcial, solo actualizamos UI
        if ui:
            ui.update_english(event.transcript, is_final=False)

def on_error(transcriber, error):
    print("Error en AssemblyAI:", error)

def on_open(session_opened):
    print("Conectado a AssemblyAI y escuchando sistema...")

def on_close():
    print("Desconectado de AssemblyAI.")

def capture_thread():
    """Hilo para ejecutar la captura de audio WASAPI"""
    start_audio_capture(on_data, on_error, on_open, on_close)

def main():
    global ui
    print("Arrancando Intérprete IA para Zoom...")
    
    # 1. Iniciar hilo de traducción (Gemini)
    t_worker = threading.Thread(target=translation_worker, daemon=True)
    t_worker.start()

    # 2. Arrancar la Interfaz Gráfica
    ui = SubtitlesUI()
    
    # 3. Arrancar el hilo de captura de audio (AssemblyAI)
    t_capture = threading.Thread(target=capture_thread, daemon=True)
    t_capture.start()
    
    # El hilo principal se queda dibujando la UI (Tkinter)
    try:
        ui.start()
    except KeyboardInterrupt:
        pass
    finally:
        print("Cerrando...")

if __name__ == '__main__':
    main()
