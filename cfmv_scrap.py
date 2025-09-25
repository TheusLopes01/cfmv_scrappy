from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import Select
import time


# =========================
# Configurações Selenium
# =========================
chrome_options = Options()
chrome_options.add_experimental_option("detach", True)  # mantém o navegador aberto

servico = Service(ChromeDriverManager().install())
navegador = webdriver.Chrome(service=servico, options=chrome_options)
navegador.get('https://app.cfmv.gov.br/paginas/busca')

formUf = navegador.find_element(By.NAME, 'filtro_uf')

dropdownSelect = Select(formUf)
dropdownSelect.select_by_value("SP")

inputTpText = navegador.find_element(By.CSS_SELECTOR, "input[name= 'filtro_tp_texto'][value= '2']")
inputTpText.click()

inputSearch = navegador.find_element(By.CSS_SELECTOR, "input[name= 'filtro_procurar'][value= '2']")
inputSearch.click()

inputForm = navegador.find_element(By.NAME, 'filtro_texto').send_keys("SP0039953")

SearchButton = navegador.find_element(By.CSS_SELECTOR, "input[class= 'btn-info btn-padrao col-5'][value= 'Filtrar']")
SearchButton.click()

time.sleep(2)
result = navegador.find_element(By.ID, "relatorio")

print(result.text)
