from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import pandas as pd
import time


driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

url = 'https://www.asl.fr.it/pediatri-libera-scelta/'
driver.get(url)
time.sleep(3)

data = []

while True:
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    cards = soup.find_all('div', class_='card card--alert rounded-sm p-4 mb-4')

    print(f"Trovate {len(cards)} card in questa pagina.")

    for card in cards:
        nome = card.find('h3', class_='card-title').text.strip()

        indirizzo = ''
        comune = ''

        p_tags = card.find_all('p', class_='card-text mb-1')
        for p in p_tags:
            if 'Indirizzo' in p.text:
                indirizzo = p.text.replace('Indirizzo', '').strip()
            if 'Comune' in p.text:
                comune = p.text.replace('Comune', '').strip()

        data.append({
            'Nome': nome,
            'Indirizzo': indirizzo,
            'Comune': comune
        })

    # Controllo presenza bottone "Successivo"
    next_buttons = driver.find_elements(By.CLASS_NAME, 'next')
    if next_buttons:
        current_url = driver.current_url
        driver.execute_script("arguments[0].click();", next_buttons[0])
        print("➡️ Passo alla pagina successiva...")
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'card'))
        )
        time.sleep(2)
        if driver.current_url == current_url:
            print("🚨 Rilevata ultima pagina! Stop.")
            break
    else:
        print("✅ Fine pagine!")
        break



driver.quit()

# 3️⃣ Salvataggio CSV
df = pd.DataFrame(data)
df.to_csv('pediatri_asl_frosinone.csv', index=False)

print(f"🎉 Scraping completato! Trovati {len(df)} medici.")
