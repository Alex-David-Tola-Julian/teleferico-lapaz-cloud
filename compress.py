import gzip, shutil
import os

print("Comprimiendo CSV...")
with open("data/teleferico_lapaz.csv", "rb") as f_in:
    with gzip.open("data/teleferico_lapaz.csv.gz", "wb") as f_out:
        shutil.copyfileobj(f_in, f_out)
        
size = os.path.getsize("data/teleferico_lapaz.csv.gz") / (1024*1024)
print(f"Comprimido exitosamente. Tamaño: {size:.2f} MB")
