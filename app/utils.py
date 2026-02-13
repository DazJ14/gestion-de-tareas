import string
import random

def generate_invite_code(length=6):
    """Genera un código alfanumérico único de 6 caracteres (Mayúsculas y Números)"""
    characters = string.ascii_uppercase + string.digits
    return ''.join(random.choice(characters) for _ in range(length))