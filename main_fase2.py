import os
import queue
import threading
from dotenv import load_dotenv

import assemblyai as aai
from google import genai
from google.genai import types

from ui_subtitles import SubtitlesUI
from mic_recorder import MicRecorder
from virtual_speaker import init_virtual_audio, speak_translated
from audio_capture import start_audio_capture
from translator_core import translate_incoming

load_dotenv()
client = genai.Client()

ui = None
translation_queue = queue.Queue()

# ----- ORQUESTADOR FASE 1 (Escuchar Zoom) -----
def translation_worker():
    while True:
        english_text = translation_queue.get()
        if english_text is None: break
        
        # Saltarse si está apagado
        if not ui or not ui.is_active: 
            translation_queue.task_done()
            continue
            
        lang = ui.combo_lang.get()
        spanish_text = translate_incoming(english_text, source_lang=lang)
        if ui and ui.is_active: 
            ui.update_spanish(spanish_text)
            ui.append_log("ZOOM", english_text, spanish_text)
        translation_queue.task_done()

def on_data(transcriber, event):
    if not ui or not ui.is_active: return
    if not getattr(event, "transcript", ""): return
    if event.end_of_turn:
        ui.update_english(event.transcript, is_final=True)
        translation_queue.put(event.transcript)
    else:
        ui.update_english(event.transcript, is_final=False)

def on_error(transcriber, error): print("Error AssemblyAI:", error)

def on_open(device_name): 
    print(f"Conectado a AssemblyAI (Escuchando: {device_name})...")
    if ui:
        ui.set_devices_info(device_name or "Sistema", "CABLE Output")

def on_close(): pass

# ----- ORQUESTADOR FASE 2 (Hablar al Zoom) -----
recorder = MicRecorder()

def translate_es_to_en(spanish_text: str, target_lang: str) -> str:
    """Traduce tu español al idioma destino"""
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=spanish_text,
            config=types.GenerateContentConfig(
                system_instruction=f"Eres un experto en soporte IT. Traduce este texto del Español al {target_lang} de forma natural. Devuelve SOLO la traducción.",
                temperature=0.3,
            )
        )
        return response.text.strip()
    except Exception as e:
        print("Error al traducir tu voz:", e)
        return ""

def process_my_speech(wav_file_path):
    if not ui or not ui.is_active: return
    
    try:
        print("Transcribiendo lo que has dicho...")
        config = aai.TranscriptionConfig(language_code="es")
        transcriber = aai.Transcriber()
        transcript = transcriber.transcribe(wav_file_path, config=config)
        
        if transcript.error:
            print("Error transcribiendo tu voz:", transcript.error)
            return
            
        mi_texto_es = transcript.text
        print(f"Yo (Español): {mi_texto_es}")
        
        target_lang = ui.combo_lang.get()
        mi_texto_en = translate_es_to_en(mi_texto_es, target_lang)
        print(f"Yo ({target_lang}): {mi_texto_en}")
        
        if ui and ui.is_active: 
            ui.update_spanish(f"TÚ: {mi_texto_es}")
            ui.update_english(f"YOU: {mi_texto_en}", is_final=True)
            ui.append_log("TÚ", mi_texto_es, mi_texto_en)
        
        speak_translated(mi_texto_en, lang=target_lang)
        
        try: os.remove(wav_file_path)
        except: pass
    finally:
        if ui:
            ui.set_processing_state(False)

def on_press_mic():
    if ui and ui.is_active:
        recorder.start_recording()

def on_release_mic():
    if ui and ui.is_active:
        wav_path = recorder.stop_recording()
        if wav_path:
            threading.Thread(target=process_my_speech, args=(wav_path,), daemon=True).start()

# ----- MAIN -----
def main():
    global ui
    print("Arrancando el Agente Completo (Fase 1 y Fase 2)...")
    init_virtual_audio() # Inicializar pygame y enlazarlo al VB-Cable
    
    # UI (Instanciar primero para que los callbacks la encuentren)
    ui = SubtitlesUI()
    ui.set_callbacks(on_press_mic, on_release_mic)
    
    # Hilos
    threading.Thread(target=translation_worker, daemon=True).start()
    threading.Thread(target=start_audio_capture, args=(on_data, on_error, on_open, on_close), daemon=True).start()
    
    try:
        ui.start()
    except KeyboardInterrupt:
        pass

if __name__ == '__main__':
    main()
