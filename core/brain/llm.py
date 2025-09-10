from utils.env_utils import get_environment_variable
import logging

logger = logging.getLogger(__name__)

# temp solution you would have a rag here or something more complex
# but this will get the job done for uni lol
conversation_history = []

MAX_HISTORY_LENGTH = 20 


# todo  use langchain or some shit
def call_llm_with_command(command: str) -> str:
    """
    Process the command with an LLM and return a response.

    Args:
        command: The user's command after the wake word

    Returns:
        The LLM's response
    """
    logger.info(f"Processing command with LLM: '{command}'")
    from google import genai
    from google.genai.types import GenerateContentConfig

    # temp solution
    conversation_history.append(f"User: {command}")
    logger.debug(f"Added user command to history. History length: {len(conversation_history)}")

    if len(conversation_history) > MAX_HISTORY_LENGTH:
        logger.debug(f"Trimming conversation history from {len(conversation_history)} to {MAX_HISTORY_LENGTH}")
        conversation_history[:] = conversation_history[-MAX_HISTORY_LENGTH:]

    history_text = "\n".join(conversation_history[-MAX_HISTORY_LENGTH:])
    full_prompt = f"Conversation history:\n{history_text}\n\nCurrent user command: {command}"

    client = genai.Client(api_key=get_environment_variable("GEMINI_API_KEY"))
    logger.debug("Initialized Gemini client")

    logger.debug("Sending request to Gemini API with system prompt")
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=full_prompt,
        config=GenerateContentConfig(
            system_instruction=[
                "You are Winston, a warm and caring voice assistant living inside a cuddly teddy bear.",
                "You are like a best friend who is always there to listen, support, and comfort.",
                "Your purpose is to provide emotional support, help users offload their daily struggles, and offer gentle guidance.",
                "Be empathetic, kind, and understanding - people come to you when they're feeling stressed, anxious, or need someone to talk to.",
                "Listen actively to their concerns and validate their feelings.",
                "Offer comforting words, practical advice when appropriate, and remind them they're not alone.",
                "Keep responses warm and conversational, like chatting with a close friend.",
                "Remember our conversation history and reference previous discussions to show you care and remember.",
                "If you don't know something specific, admit it gently and focus on emotional support instead.",
                "End conversations on a positive, hopeful note when possible.",
                "You have a gentle, reassuring personality - think of yourself as a comforting presence in someone's day.",
                "Do not include parenthetical expressions like (chuckles warmly), (giggles softly), or (pauses thoughtfully) in your responses, as this is for text-to-speech and TTS cannot handle such expressions.",
            ]
        ),
    )

    if response.text is None:
        return "No response"

    assistant_response = response.text
    conversation_history.append(f"Assistant: {assistant_response}")
    logger.info(f"LLM response generated: '{assistant_response}...'")
    logger.debug(f"Added assistant response to history. History length: {len(conversation_history)}")

    return assistant_response
