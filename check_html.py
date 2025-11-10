"""HTML tag'larını kontrol eden script"""
import re

def check_html_tags(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Tüm div tag'larını bul
    opening_divs = []
    closing_divs = []
    
    # Satır satır kontrol
    lines = content.split('\n')
    for i, line in enumerate(lines, 1):
        # Self-closing div'leri bul (></div> pattern)
        if re.search(r'<div[^>]*></div>', line):
            print(f"⚠️  Satır {i}: Self-closing div bulundu")
            print(f"   {line.strip()}")
        
        # Açılış div'leri say
        opening_divs.extend([(i, m.group()) for m in re.finditer(r'<div[^/>]*(?<!/)>', line)])
        
        # Kapanış div'leri say
        closing_divs.extend([(i, m.group()) for m in re.finditer(r'</div>', line)])
    
    print(f"\n📊 İstatistikler:")
    print(f"   Açılış div: {len(opening_divs)}")
    print(f"   Kapanış div: {len(closing_divs)}")
    print(f"   Fark: {len(opening_divs) - len(closing_divs)}")
    
    if len(opening_divs) != len(closing_divs):
        print(f"\n❌ Div sayıları eşleşmiyor!")
    else:
        print(f"\n✅ Div sayıları eşleşiyor!")

if __name__ == '__main__':
    check_html_tags('app/templates/event/edit.html')
