import os
import asyncio
import edge_tts
import pygame
import tempfile
import time

def init_virtual_audio():
    # Inicializar pygame mixer específico para el cable virtual
    pygame.mixer.init(devicename='CABLE Input (VB-Audio Virtual Cable)')

def speak_translated(text, lang="Inglés"):
    if not text.strip():
        return
        
    print(f"[Virtual Speaker] Hablando en {lang}: {text}")
    
    # Archivo temporal para el MP3
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
    temp_file.close()
    
    # Elegir voz según el idioma
    voices = {
        "Inglés": "en-US-AriaNeural",
        "Francés": "fr-FR-DeniseNeural",
        "Alemán": "de-DE-KatjaNeural"
    }
    voice_name = voices.get(lang, "en-US-AriaNeural")
    
    communicate = edge_tts.Communicate(text, voice_name)
    asyncio.run(communicate.save(temp_file.name))
    
    # Reproducir usando pygame
    pygame.mixer.music.load(temp_file.name)
    pygame.mixer.music.play()
    
    # Esperar a que termine
    while pygame.mixer.music.get_busy():
        time.sleep(0.1)
        
    # Limpiar
    pygame.mixer.music.unload()
    try:
        os.remove(temp_file.name)
    except:
        pass
