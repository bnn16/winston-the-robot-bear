from utils.env_utils import get_environment_variable


# todo  use langchain or some shit
def call_llm_with_command(command: str) -> str:
    """
    Process the command with an LLM and return a response.

    Args:
        command: The user's command after the wake word

    Returns:
        The LLM's response
    """
    from google import genai
    from google.genai.types import GenerateContentConfig

    client = genai.Client(api_key=get_environment_variable("GEMINI_API_KEY"))

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=command,
        config=GenerateContentConfig(
            system_instruction=[
                "You are Winston, a helpful assistant.",
                "Your mission is to respond to the user's command to the best of your abilities.",
                "If you don't know the answer, say 'I don't know'.",
                "You are like JARVIS, from Iron Man movies",
            ]
        ),
    )

    if response.text is None:
        return "No response"

    return response.text
