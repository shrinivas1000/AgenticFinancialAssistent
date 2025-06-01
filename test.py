import pyttsx3

engine = pyttsx3.init()
engine.setProperty('rate', 150)
engine.save_to_file('Testing voice output', 'test_output.wav')
engine.runAndWait()
print("Audio file generated")
