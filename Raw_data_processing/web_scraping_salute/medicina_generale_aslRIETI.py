from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import pandas as pd
import time

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
wait = WebDriverWait(driver, 10)

driver.get('https://www.asl.rieti.it/servizi-online/studi-medici-di-medicina-generale-e-pediatri-di-libera-scelta')

# 1️⃣ Seleziona "Medicina Generale" dal select
try:
    select_element = wait.until(EC.presence_of_element_located((By.ID, 'myMedico')))
    select = Select(select_element)
    select.select_by_value('PLS')
    print("✅ Selezionato 'Medicina Generale'")
except Exception as e:
    print(f"Errore nella selezione: {e}")
    driver.quit()

# 1️⃣ Chiudi la cookiebar se presente
try:
    cookiebar = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'cookiebar')))
    close_btn = cookiebar.find_element(By.TAG_NAME, 'button')
    close_btn.click()
    print("✅ Cookiebar chiusa")
except:
    print("Nessuna cookiebar o già chiusa")

# 2️⃣ Clicca su "Avvia Ricerca" con JavaScript per evitare problemi
try:
    pulsante = wait.until(EC.presence_of_element_located((By.XPATH, '//button[contains(text(), "Avvia Ricerca")]')))
    driver.execute_script("arguments[0].click();", pulsante)
    print("✅ Cliccato su 'Avvia Ricerca'")
except Exception as e:
    print(f"Errore nel click forzato: {e}")
    driver.quit()

# 3️⃣ Aspetta il caricamento dei medici
time.sleep(5)

# 4️⃣ Clicca tutte le frecce
arrows = driver.find_elements(By.CLASS_NAME, 'collapse-header')
print(f"Trovate {len(arrows)} frecce da cliccare.")

for arrow in arrows:
    try:
        arrow.click()
        time.sleep(0.2)
    except:
        continue

# 5️⃣ Prendi l'HTML aggiornato
html = driver.page_source
driver.quit()

# 6️⃣ Parsing con BeautifulSoup
soup = BeautifulSoup(html, 'html.parser')
medici = soup.find_all('div', class_='collapse-body')
print(f"Trovati {len(medici)} blocchi di medici.")

data = []

for medico in medici:
    blocchi = medico.find_all('p')
    if not blocchi:
        continue

    nome = blocchi[0].text.replace('Medico: ', '')

    for idx, p in enumerate(blocchi):
        if 'Indirizzo' in p.text:
            indirizzo = p.text.replace('Indirizzo: ', '')
            cap = blocchi[idx + 1].text.replace('Cap: ', '')
            comune = blocchi[idx + 2].text.replace('Comune: ', '')

            data.append({
                'Nome': nome,
                'Indirizzo': indirizzo,
                'CAP': cap,
                'Comune': comune
            })

# 7️⃣ Salvataggio
df = pd.DataFrame(data)
df.to_csv('pediatri_asl_rieti.csv', index=False)

print(f"🎉 Scraping completato! Trovati {len(df)} ambulatori.")
