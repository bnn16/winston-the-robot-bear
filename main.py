from utils.env_utils import load_environment_variables


def main():
    print("Project JarvisKit/AssistantKit")
    env = load_environment_variables()

    if env is None:
        print("❌ Exiting due to missing environment variables")
        return

    try:
        from core.voice import STT

        stt = STT()
        print("Voice module ready")
    except ImportError:
        print("Voice module not found")


if __name__ == "__main__":
    main()
