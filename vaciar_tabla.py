import os, requests, time
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_ANON_KEY")
TABLE = os.getenv("SUPABASE_TABLE", "teleferico")

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=minimal",
}
REST = f"{SUPABASE_URL.rstrip('/')}/rest/v1/{TABLE}"

print("Iniciando borrado por meses...")
for year in range(2019, 2025):
    for month in range(1, 13):
        start_date = f"{year}-{month:02d}-01"
        if month == 12:
            end_date = f"{year+1}-01-01"
        else:
            end_date = f"{year}-{month+1:02d}-01"
            
        print(f"Borrando datos desde {start_date} hasta {end_date}...")
        res = requests.delete(f"{REST}?fecha=gte.{start_date}&fecha=lt.{end_date}", headers=HEADERS)
        if res.status_code not in (200, 204):
            print(f"Error borrando {start_date}: {res.status_code} - {res.text}")
        time.sleep(0.5)

print("Verificando si quedaron registros...")
r_count = requests.get(
    REST + "?select=id",
    headers={**HEADERS, "Prefer": "count=exact", "Range": "0-0"}
)
print("Content-Range final:", r_count.headers.get("Content-Range", "0/0"))
