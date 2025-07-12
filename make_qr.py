import qrcode

URL = "https://table-finder-9xkv.onrender.com"          # change after you deploy to the cloud
qrcode.make(URL).save("table_qr.png")
print("✓ QR code saved to table_qr.png")