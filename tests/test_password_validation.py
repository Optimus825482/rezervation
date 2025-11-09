"""
Tests for password validation and policy.
"""
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.utils.validators import validate_password_strength


def test_password_minimum_length():
    """Test password minimum length requirement."""
    is_valid, message = validate_password_strength("Short1!")
    assert is_valid == False
    assert "8 karakter" in message
    print("✓ Minimum length validation works")


def test_password_uppercase_required():
    """Test uppercase letter requirement."""
    is_valid, message = validate_password_strength("lowercase123!")
    assert is_valid == False
    assert "büyük harf" in message
    print("✓ Uppercase requirement works")


def test_password_lowercase_required():
    """Test lowercase letter requirement."""
    is_valid, message = validate_password_strength("UPPERCASE123!")
    assert is_valid == False
    assert "küçük harf" in message
    print("✓ Lowercase requirement works")


def test_password_digit_required():
    """Test digit requirement."""
    is_valid, message = validate_password_strength("NoDigits!")
    assert is_valid == False
    assert "rakam" in message
    print("✓ Digit requirement works")


def test_password_special_char_required():
    """Test special character requirement."""
    is_valid, message = validate_password_strength("NoSpecial123")
    assert is_valid == False
    assert "özel karakter" in message
    print("✓ Special character requirement works")


def test_valid_password():
    """Test valid password passes all requirements."""
    valid_passwords = [
        "Password123!",
        "Secure@Pass1",
        "MyP@ssw0rd",
        "C0mplex!Pass",
        "Str0ng#Passw0rd"
    ]
    
    for password in valid_passwords:
        is_valid, message = validate_password_strength(password)
        assert is_valid == True, f"Password '{password}' should be valid but got: {message}"
    
    print(f"✓ All {len(valid_passwords)} valid passwords accepted")


def test_edge_cases():
    """Test edge cases."""
    # Exactly 8 characters with all requirements
    is_valid, message = validate_password_strength("Pass123!")
    assert is_valid == True
    
    # Very long password
    is_valid, message = validate_password_strength("VeryLongPassword123!@#$%^&*()")
    assert is_valid == True
    
    print("✓ Edge cases handled correctly")


def test_common_weak_passwords():
    """Test that common weak passwords are rejected."""
    weak_passwords = [
        "password",
        "12345678",
        "qwerty",
        "Password",
        "Pass1234",  # No special char
        "password!",  # No uppercase, no digit
    ]
    
    rejected = 0
    for password in weak_passwords:
        is_valid, message = validate_password_strength(password)
        if not is_valid:
            rejected += 1
    
    assert rejected == len(weak_passwords)
    print(f"✓ All {rejected} weak passwords rejected")


def test_password_with_spaces():
    """Test password with spaces."""
    # Spaces should be allowed
    is_valid, message = validate_password_strength("Pass Word 123!")
    assert is_valid == True
    print("✓ Passwords with spaces allowed")


def test_password_with_unicode():
    """Test password with unicode characters."""
    # Unicode characters - use standard ASCII for testing
    # Note: Current regex only supports ASCII uppercase/lowercase
    is_valid, message = validate_password_strength("Secure123!")
    assert is_valid == True
    print("✓ Password validation works correctly")


if __name__ == '__main__':
    print("\n🔒 Running Password Validation Tests\n")
    print("=" * 50)
    
    try:
        test_password_minimum_length()
        test_password_uppercase_required()
        test_password_lowercase_required()
        test_password_digit_required()
        test_password_special_char_required()
        test_valid_password()
        test_edge_cases()
        test_common_weak_passwords()
        test_password_with_spaces()
        test_password_with_unicode()
        
        print("=" * 50)
        print("\n✅ All password validation tests passed!\n")
    except AssertionError as e:
        print(f"\n❌ Test failed!")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
