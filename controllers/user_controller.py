# controllers/user_controller.py
from models.user_model import get_user_by_username, get_user_by_email, add_user

def login_user(username, password):
    user = get_user_by_username(username)
    if user and user["password"] == password:
        return True
    return False

def register_user(data):
    """Registers a new user, returns (success, message) tuple."""
    # Check if username already exists
    existing_username = get_user_by_username(data["username"])
    if existing_username:
        return False, "Bu kullanıcı adı zaten kullanılıyor!"
    
    # Check if email already exists
    existing_email = get_user_by_email(data["email"])
    if existing_email:
        return False, "Bu email adresi zaten kayıtlı!"
    
    try:
        add_user(data)
        return True, "Kayıt başarıyla oluşturuldu!"
    except Exception as e:
        return False, f"Kayıt sırasında hata oluştu: {str(e)}"