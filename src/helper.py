# Room for imports if needed.

def get_id_conversation(userid, conversation_name) -> str:
    """
    Returns a string of the format: 
    "{userid}_{conversation_name}"
    """
    return str(f"{userid}_{conversation_name}")
