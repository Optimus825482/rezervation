# -*- coding: utf-8 -*-
from app.utils.validators import validate_turkish_phone, validate_password_strength

def test_turkish_phone_validation():
    """Test Turkish phone validation"""
    assert validate_turkish_phone('05321234567') == True
    assert validate_turkish_phone('+905321234567') == True
    assert validate_turkish_phone('123') == False
    assert validate_turkish_phone('invalid') == False

def test_password_strength():
    """Test password strength validation"""
    is_valid, msg = validate_password_strength('Weak')
    assert is_valid == False
    
    is_valid, msg = validate_password_strength('StrongPass123!')
    assert is_valid == True
    assert 'güçlü' in msg.lower() or 'strong' in msg.lower()
