import os
import audioop
import pyaudiowpatch as pyaudio
import assemblyai as aai
from dotenv import load_dotenv

load_dotenv()
aai.settings.api_key = os.getenv("ASSEMBLYAI_API_KEY")

def start_audio_capture(on_data_cb, on_error_cb, on_open_cb, on_close_cb):
    """Captura WASAPI Loopback y lo manda a AssemblyAI usando el nuevo SDK v3."""
    CHUNK = 4096
    with pyaudio.PyAudio() as p:
        try:
            wasapi_info = p.get_host_api_info_by_type(pyaudio.paWASAPI)
        except OSError:
            print("Error: WASAPI no está disponible en este sistema.")
            return

        default_speakers = p.get_device_info_by_index(wasapi_info["defaultOutputDevice"])
        
        if not default_speakers["isLoopbackDevice"]:
            for loopback in p.get_loopback_device_info_generator():
                if default_speakers["name"] in loopback["name"]:
                    default_speakers = loopback
                    break
            else:
                print("No se encontró un dispositivo Loopback compatible.")
                return

        sample_rate = int(default_speakers["defaultSampleRate"])
        channels = default_speakers["maxInputChannels"]
        
        transcriber = aai.streaming.v3.RealTimeTranscriber(
            api_key=os.getenv("ASSEMBLYAI_API_KEY")
        )
        transcriber.on(aai.streaming.v3.RealTimeEvents.Turn, on_data_cb)
        transcriber.on(aai.streaming.v3.RealTimeEvents.Error, on_error_cb)

        stream = p.open(format=pyaudio.paInt16,
                        channels=channels,
                        rate=sample_rate,
                        input=True,
                        frames_per_buffer=CHUNK,
                        input_device_index=default_speakers["index"])
        
        print(f"Capturando desde: {default_speakers['name']}")
        
        # Conectar el Transcriber v3
        params = aai.streaming.v3.RealTimeParameters(
            sample_rate=sample_rate, 
            language_codes=["en", "es", "fr", "de", "it", "pt"]
        )
        on_open_cb(default_speakers['name'])
        transcriber.connect(params)
        
        try:
            while True:
                data = stream.read(CHUNK, exception_on_overflow=False)
                if channels == 2:
                    data = audioop.tomono(data, 2, 0.5, 0.5)
                transcriber.stream(data)
        except KeyboardInterrupt:
            pass
        finally:
            stream.stop_stream()
            stream.close()
            transcriber.disconnect()
            on_close_cb()
