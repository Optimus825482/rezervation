"""HTML self-closing div'leri düzelten script"""
import re

def fix_self_closing_divs(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Self-closing div pattern: <div ...></div> (aynı satırda)
    # Bunları <div ...> olarak değiştir
    pattern = r'(<div[^>]*)(></div>)'
    
    def replacer(match):
        opening = match.group(1)
        # Eğer self-closing bir div ise (içerik yok), sadece açılış tag'i bırak
        return opening + '>'
    
    fixed_content = re.sub(pattern, replacer, content)
    
    # Dosyayı yaz
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(fixed_content)
    
    print("✅ Self-closing div'ler düzeltildi!")

if __name__ == '__main__':
    fix_self_closing_divs('app/templates/event/edit.html')
