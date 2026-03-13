import asyncio
import pyttsx3
import speech_recognition as sr
from agent.dispatcher import dispatch_command

WAKE_WORDS = ["jarvis", "javis", "jarviss"]


def speak_text(text):
    engine = pyttsx3.init()
    engine.setProperty('rate', 180)
    engine.say(text)
    engine.runAndWait()
    engine.stop()


async def handle_command(recognizer, source):
    speak_text("How can I help you?")  # Professional response
    print("🎤 Listening for command...")

    try:
        audio = recognizer.listen(source, timeout=5, phrase_time_limit=8)
        user_input = recognizer.recognize_google(audio)
        print(f"You said: {user_input}")

        if any(word in user_input.lower() for word in ["exit", "quit", "stop"]):
            speak_text("Goodbye.")
            return True

            # This calls your dispatcher which uses the tools in os_tools.py
        result = await dispatch_command(user_input)
        print(f"Agent: {result}")
        speak_text(result)

    except sr.UnknownValueError:
        print("Wait: No speech detected.")
    except Exception as e:
        print(f"Error: {e}")
    return False


async def main():
    recognizer = sr.Recognizer()
    recognizer.dynamic_energy_threshold = True

    print(f"😴 Jarvis is in sleep mode. Say 'Jarvis' to wake me up...")

    while True:
        with sr.Microphone() as source:
            recognizer.adjust_for_ambient_noise(source, duration=0.8)
            try:
                audio = recognizer.listen(source, timeout=None, phrase_time_limit=2)
                text = recognizer.recognize_google(audio).lower()

                if any(wake in text for wake in WAKE_WORDS):
                    print(f"⚡ Wake word detected!")
                    should_exit = await handle_command(recognizer, source)
                    if should_exit:
                        break
                    print(f"😴 Going back to sleep...")

            except sr.UnknownValueError:
                continue
            except Exception as e:
                print(f"System Status: {e}")


if __name__ == "__main__":
    asyncio.run(main())