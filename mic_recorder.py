import pyaudiowpatch as pyaudio
import wave
import threading
import time
import tempfile

class MicRecorder:
    def __init__(self):
        self.p = pyaudio.PyAudio()
        self.frames = []
        self.recording = False
        self.stream = None

    def start_recording(self):
        print("Empezando a grabar micrófono...")
        self.frames = []
        self.recording = True
        
        # Usar el micrófono por defecto (canales=1, rate=16000 ideal para STT)
        try:
            self.stream = self.p.open(format=pyaudio.paInt16,
                                      channels=1,
                                      rate=16000,
                                      input=True,
                                      frames_per_buffer=1024)
        except Exception as e:
            print("Error al abrir micrófono:", e)
            self.recording = False
            return
            
        def record_loop():
            while self.recording:
                try:
                    data = self.stream.read(1024, exception_on_overflow=False)
                    self.frames.append(data)
                except:
                    break
                    
        threading.Thread(target=record_loop, daemon=True).start()

    def stop_recording(self):
        if not self.recording:
            return None
            
        print("Grabación detenida.")
        self.recording = False
        time.sleep(0.1)
        
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
            self.stream = None
            
        if not self.frames:
            return None
            
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
        temp_file.close() # Lo cerramos para que wave.open pueda escribirlo
        
        wf = wave.open(temp_file.name, 'wb')
        wf.setnchannels(1)
        wf.setsampwidth(self.p.get_sample_size(pyaudio.paInt16))
        wf.setframerate(16000)
        wf.writeframes(b''.join(self.frames))
        wf.close()
        
        return temp_file.name
