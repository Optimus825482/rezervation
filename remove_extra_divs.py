"""Fazla kapanış div'lerini silen script"""

def remove_extra_closing_divs(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Silinecek satırlar (script'ten gelen)
    lines_to_remove = [593, 594, 747, 776, 777, 802, 854, 951]
    
    # Yeni içerik
    new_lines = []
    for i, line in enumerate(lines, 1):
        if i not in lines_to_remove:
            new_lines.append(line)
        else:
            print(f"🗑️  Satır {i} silindi: {line.strip()}")
    
    # Dosyayı yaz
    with open(file_path, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
    
    print(f"\n✅ {len(lines_to_remove)} fazla div silindi!")

if __name__ == '__main__':
    remove_extra_closing_divs('app/templates/event/edit.html')
