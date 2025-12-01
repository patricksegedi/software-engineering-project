from ..main_ai import start_ai_session_with_components

def speaker_activate(user: str, audio_processor, voice_recorder):
    """Activate AI session for authenticated user"""
    print(f"[DEBUG] Starting AI session for user: {user}")
    try:
        start_ai_session_with_components(user, audio_processor, voice_recorder)
    except Exception as e:
        print(f"[ERROR] Failed to start AI session: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # This should not be called directly anymore
    print("Please run through main app.py")