import qrcode

URL = "http://127.0.0.1:5000"          # change after you deploy to the cloud
qrcode.make(URL).save("table_qr.png")
print("✓ QR code saved to table_qr.png")