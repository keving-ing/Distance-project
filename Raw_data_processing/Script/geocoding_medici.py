import pandas as pd
import re
import os

# Lista dei file da pulire
csv_files = [
    "medici_asl_rieti.csv"
]

# Funzione di normalizzazione avanzata dell'indirizzo
def normalize_address(address):
    if pd.isna(address):
        return ""
    address = address.lower()
    address = re.sub(r'\bn\.', 'numero', address)
    address = re.sub(r'[^a-z0-9\s]', '', address)
    address = re.sub(r'\s+', ' ', address).strip()
    return address

# Processa ogni file
for file in csv_files:
    if not os.path.isfile(file):
        print(f"❌ File non trovato: {file}")
        continue

    print(f"\n📂 Pulizia file: {file}")
    df = pd.read_csv(file)

    # Normalizza gli indirizzi
    df['Indirizzo_normalizzato'] = df['Indirizzo'].apply(normalize_address)

    # Rimuove duplicati
    df_clean = df.drop_duplicates(subset='Indirizzo_normalizzato', keep='first')

    # Salva file pulito
    output_file = file.replace(".csv", "_noDuplicati.csv")
    df_clean.drop(columns=['Indirizzo_normalizzato'], inplace=True)
    df_clean.to_csv(output_file, index=False)

    # Stampa ultime righe
    print(f"✅ Salvato {output_file} con {len(df_clean)} righe (originali: {len(df)})")
    print(df_clean.tail())
