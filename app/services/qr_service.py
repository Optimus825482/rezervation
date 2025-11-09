import qrcode
import os
from uuid import uuid4

def generate_qr_code(reservation_id, reservation_code):
    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(f"RES-{reservation_code}")
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    upload_dir = 'app/static/uploads/qr'
    os.makedirs(upload_dir, exist_ok=True)
    
    filename = f"{reservation_id}.png"
    filepath = os.path.join(upload_dir, filename)
    img.save(filepath)
    
    return f"uploads/qr/{filename}"
