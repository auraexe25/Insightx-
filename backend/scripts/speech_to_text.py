"""
Speech to Text using Local OpenAI Whisper
Real-time microphone recording and transcription (FREE - runs locally)
"""

# Check for required packages
try:
    import sounddevice as sd
    import numpy as np
    import whisper  # type: ignore  # Package: openai-whisper
except ImportError as e:
    print("Missing required packages. Install them with:")
    print("pip install sounddevice numpy openai-whisper")
    raise e


class SpeechToText:
    def __init__(self, model_name: str = "base"):
        """
        Initialize the Speech to Text client with local Whisper model.
        
        Args:
            model_name: Whisper model size. Options: 'tiny', 'base', 'small', 'medium', 'large'
                       - tiny: ~1GB RAM, fastest, least accurate
                       - base: ~1GB RAM, good balance (default)
                       - small: ~2GB RAM, better accuracy
                       - medium: ~5GB RAM, high accuracy
                       - large: ~10GB RAM, best accuracy
        """
        print(f"Loading Whisper '{model_name}' model... (first time may download)")
        self.model = whisper.load_model(model_name)
        print("Model loaded!")
        self.sample_rate = 16000  # Whisper works best with 16kHz
        self.channels = 1  # Mono audio

    def record_audio(self, duration: int = 5) -> np.ndarray:
        """
        Record audio from the microphone.
        
        Args:
            duration: Recording duration in seconds.
            
        Returns:
            Numpy array containing the audio data.
        """
        print(f"Recording for {duration} seconds... Speak now!")
        audio_data = sd.rec(
            int(duration * self.sample_rate),
            samplerate=self.sample_rate,
            channels=self.channels,
            dtype=np.int16
        )
        sd.wait()  # Wait until recording is finished
        print("Recording complete!")
        return audio_data

    def record_until_silence(self, silence_threshold: float = 0.01, 
                              silence_duration: float = 2.0,
                              max_duration: float = 60.0) -> np.ndarray:
        """
        Record audio until silence is detected.
        
        Args:
            silence_threshold: RMS threshold below which is considered silence.
            silence_duration: Duration of silence (in seconds) to stop recording.
            max_duration: Maximum recording duration in seconds.
            
        Returns:
            Numpy array containing the audio data.
        """
        print("Recording... (will stop after silence or max duration)")
        print("Press Ctrl+C to stop manually.")
        
        chunk_duration = 0.1  # Process audio in 100ms chunks
        chunk_samples = int(self.sample_rate * chunk_duration)
        silence_chunks = int(silence_duration / chunk_duration)
        max_chunks = int(max_duration / chunk_duration)
        
        audio_chunks = []
        silent_count = 0
        
        try:
            with sd.InputStream(samplerate=self.sample_rate, 
                               channels=self.channels, 
                               dtype=np.int16) as stream:
                for _ in range(max_chunks):
                    chunk, _ = stream.read(chunk_samples)
                    audio_chunks.append(chunk.copy())
                    
                    # Calculate RMS to detect silence
                    rms = np.sqrt(np.mean(chunk.astype(np.float32) ** 2)) / 32768
                    
                    if rms < silence_threshold:
                        silent_count += 1
                        if silent_count >= silence_chunks:
                            print("Silence detected, stopping...")
                            break
                    else:
                        silent_count = 0
                        
        except KeyboardInterrupt:
            print("\nRecording stopped manually.")
        
        print("Recording complete!")
        return np.concatenate(audio_chunks, axis=0)

    def transcribe(self, audio_data: np.ndarray, language: str = None) -> str:
        """
        Transcribe audio data using local Whisper model.
        
        Args:
            audio_data: Numpy array containing audio data.
            language: Optional language code (e.g., 'en', 'es', 'fr'). Auto-detected if None.
            
        Returns:
            Transcribed text.
        """
        # Convert to float32 and normalize for Whisper
        audio_float = audio_data.flatten().astype(np.float32) / 32768.0
        
        # Transcribe using local model
        options = {}
        if language:
            options["language"] = language
            
        result = self.model.transcribe(audio_float, **options)
        return result["text"].strip()

    def record_and_transcribe(self, duration: int = 5, language: str = None) -> str:
        """
        Record audio and transcribe it.
        
        Args:
            duration: Recording duration in seconds.
            language: Optional language code.
            
        Returns:
            Transcribed text.
        """
        audio_data = self.record_audio(duration)
        return self.transcribe(audio_data, language)

    def listen_and_transcribe(self, language: str = None) -> str:
        """
        Listen until silence and transcribe.
        
        Args:
            language: Optional language code.
            
        Returns:
            Transcribed text.
        """
        audio_data = self.record_until_silence()
        return self.transcribe(audio_data, language)


def main():
    """Demo the speech to text functionality."""
    print("=" * 50)
    print("Speech to Text Demo (Local Whisper - FREE)")
    print("=" * 50)
    
    # Initialize with base model
    stt = SpeechToText(model_name="base")
    
    print("\nOptions:")
    print("1. Record for fixed duration")
    print("2. Record until silence")
    
    choice = input("\nSelect option (1 or 2): ").strip()
    
    if choice == "1":
        duration = input("Enter recording duration in seconds (default: 5): ").strip()
        duration = int(duration) if duration else 5
        text = stt.record_and_transcribe(duration=duration)
    else:
        text = stt.listen_and_transcribe()
    
    print("\n" + "=" * 50)
    print("Transcription:")
    print("=" * 50)
    print(text)


if __name__ == "__main__":
    main()
