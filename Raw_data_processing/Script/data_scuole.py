# Ricarica il file CSV dopo il reset dello stato
import pandas as pd

csv_file_path = "SCUANAGRAFESTAT20242520240901.csv"

# Carica il file CSV
df = pd.read_csv(csv_file_path)

# Filtra le scuole della regione Lazio
df_lazio = df[df['REGIONE'] == 'LAZIO']

# Filtra solo le scuole di interesse
scuole_interesse = ['SCUOLA PRIMARIA', 'SCUOLA INFANZIA', 'SCUOLA PRIMO GRADO', 'ISTITUTO COMPRENSIVO']
df_lazio_filtrato = df_lazio[df_lazio['DESCRIZIONETIPOLOGIAGRADOISTRUZIONESCUOLA'].isin(scuole_interesse)]

# Salva il nuovo dataset filtrato
csv_file_filtrato = "scuole_lazio_filtrate.xlsx"
#df_lazio_filtrato.to_csv(csv_file_filtrato, index=False)

df_lazio_filtrato.to_excel(csv_file_filtrato, index=False)