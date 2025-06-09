from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
import time
import re

def get_travel_time(from_address, to_address):
    # Avvia Chrome
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    driver.get("https://moovitapp.com/index/it/mezzi_pubblici-Roma_e_Lazio-61")
    time.sleep(5)

    # Trova input origine e destinazione
    from_input = driver.find_element(By.ID, "from-input")
    to_input = driver.find_element(By.ID, "to-input")

    # Inserisci indirizzi
    from_input.clear()
    from_input.send_keys(from_address)
    time.sleep(2)
    from_input.send_keys(Keys.ARROW_DOWN, Keys.ENTER)
    time.sleep(2)

    to_input.clear()
    to_input.send_keys(to_address)
    time.sleep(2)
    to_input.send_keys(Keys.ARROW_DOWN, Keys.ENTER)
    time.sleep(2)

    # Clicca su Cerca
    search_btn = driver.find_element(By.CSS_SELECTOR, ".search-button")
    search_btn.click()
    time.sleep(10)  # Attendi il caricamento risultati

    # Estrai durata
    try:
        duration_element = driver.find_element(By.CSS_SELECTOR, ".duration")
        duration_text = duration_element.text.strip()  # es. "4 h 2 min" oppure "27 min"
    except:
        print("⚠️ Nessun risultato trovato.")
        driver.quit()
        return None

    driver.quit()

    # Converte testo in minuti
    match = re.match(r"(?:(\d+)\s*h\s*)?(?:(\d+)\s*min)?", duration_text)
    if match:
        hours = int(match.group(1)) if match.group(1) else 0
        minutes = int(match.group(2)) if match.group(2) else 0
        total_minutes = hours * 60 + minutes
        return total_minutes
    else:
        return None

# Esempio di utilizzo
if __name__ == "__main__":
    from_place = "Viale Trastevere, Roma"
    to_place = "Via Nazionale, Roma"
    time_minutes = get_travel_time(from_place, to_place)
    if time_minutes is not None:
        print(f"🕒 Tempo di viaggio: {time_minutes} minuti")
    else:
        print("❌ Tempo non disponibile.")
