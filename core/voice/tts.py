from elevenlabs import ElevenLabs, VoiceSettings, play

from utils.env_utils import get_environment_variable


def speak_response(text: str):
    """Convert text to speech using ElevenLabs."""
    elevenlabs = ElevenLabs(api_key=get_environment_variable("ELEVENLABS_API_KEY"))
    # TODO: add options for multiple voices, based on the name detected? :thonk: or what user selected later
    response = elevenlabs.text_to_speech.convert(
        voice_id="Fahco4VZzobUeiPqni1S",
        output_format="mp3_44100_128",
        text=text,
        model_id="eleven_turbo_v2_5",
        voice_settings=VoiceSettings(
            stability=0.5,
            similarity_boost=1.0,
            use_speaker_boost=False,
            speed=1.0,
        ),
    )

    play(response)
