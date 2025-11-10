"""Fazla kapanış div'lerini bulan script"""
import re

def find_unmatched_divs(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    stack = []  # (line_num, indent_level)
    unmatched_closing = []
    
    for i, line in enumerate(lines, 1):
        # Indent seviyesini hesapla
        indent = len(line) - len(line.lstrip())
        
        # Açılış div'leri bul (self-closing değil)
        opening_matches = list(re.finditer(r'<div[^/>]*(?<!/)>', line))
        for match in opening_matches:
            stack.append((i, indent, line.strip()[:80]))
        
        # Kapanış div'leri bul
        closing_matches = list(re.finditer(r'</div>', line))
        for match in closing_matches:
            if stack:
                stack.pop()
            else:
                unmatched_closing.append((i, line.strip()))
    
    print(f"📊 Sonuçlar:")
    print(f"   Açılmamış kapanış div'ler: {len(unmatched_closing)}")
    print(f"   Kapanmamış açılış div'ler: {len(stack)}")
    
    if unmatched_closing:
        print(f"\n❌ Fazla kapanış div'ler:")
        for line_num, line_content in unmatched_closing:
            print(f"   Satır {line_num}: {line_content}")
    
    if stack:
        print(f"\n⚠️  Kapanmamış açılış div'ler:")
        for line_num, indent, line_content in stack[-10:]:  # Son 10'u göster
            print(f"   Satır {line_num}: {line_content}")

if __name__ == '__main__':
    find_unmatched_divs('app/templates/event/edit.html')
