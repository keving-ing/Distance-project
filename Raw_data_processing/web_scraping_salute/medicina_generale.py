from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import time

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
wait = WebDriverWait(driver, 20)

# 1️⃣ Apri la pagina
driver.get('https://salutelazio.it/ricerca-medici')

# 2️⃣ Seleziona ASL Rieti
select_asl = Select(wait.until(EC.presence_of_element_located((By.ID, '_it_smc_laziocrea_sysmed_web_internal_portlet_SearchFormPortlet_asl'))))
select_asl.select_by_value('120110')
print("✅ Selezionata ASL Rieti")

time.sleep(10)

# 3️⃣ Clicca su "Avvia la ricerca"
avvia_btn = driver.find_element(By.ID, '_it_smc_laziocrea_sysmed_web_internal_portlet_SearchFormPortlet_submit')
driver.execute_script("arguments[0].click();", avvia_btn)
print("✅ Cliccato su Avvia la ricerca")

# 4️⃣ Aspetta che compaia la tabella
wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.table-data tr')))
time.sleep(2)

data = []

# 5️⃣ Processo su 20 pagine esatte
pagina_corrente = 1
while pagina_corrente <= 5:
    print(f"➡️ Lettura pagina {pagina_corrente}")

    righe = driver.find_elements(By.CSS_SELECTOR, '.table-data tr')

    for riga in righe:
        celle = riga.find_elements(By.TAG_NAME, 'td')
        if len(celle) >= 6:
            cognome = celle[0].text.strip()
            nome = celle[1].text.strip()

            dettagli_btns = celle[-1].find_elements(By.CLASS_NAME, 'page-link')
            if dettagli_btns:
                driver.execute_script("arguments[0].click();", dettagli_btns[0])
                time.sleep(3)

                indirizzi = driver.find_elements(By.CSS_SELECTOR, 'p.text-uppercase')
                for indirizzo in indirizzi:
                    testo = indirizzo.text.strip()
                    if testo and 'ORARI PRESSO QUESTO STUDIO' not in testo:
                        data.append({
                            'Cognome': cognome,
                            'Nome': nome,
                            'Indirizzo': testo
                        })

                print(f"✅ Presi ambulatori di: {cognome} {nome}")
            else:
                print(f"⚠️ Nessun bottone Dettagli per {cognome} {nome}, passo oltre.")

    # 6️⃣ Clicca "Successivo" se non siamo all'ultima pagina
    if pagina_corrente < 5:
        next_buttons = driver.find_elements(By.LINK_TEXT, "Successivo")
        if next_buttons:
            driver.execute_script("arguments[0].click();", next_buttons[0])
            print(f"➡️ Passo alla pagina {pagina_corrente + 1}")
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, '.table-data tr')))
            time.sleep(10)
    pagina_corrente += 1

# 7️⃣ Chiudi driver
driver.quit()

# 8️⃣ Salvataggio finale
df = pd.DataFrame(data)
df = df.drop_duplicates()
df.to_csv('medici_asl_rieti.csv', index=False)

print(f"🎉 Scraping completato! Totale ambulatori unici trovati: {len(df)}")
