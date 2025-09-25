from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import TimeoutException
from vet_list_sp import formatList
import time


# =========================
# Configurações Selenium
# =========================
chrome_options = Options()
chrome_options.add_experimental_option("detach", True)  # mantém o navegador aberto

servico = Service(ChromeDriverManager().install())
navegador = webdriver.Chrome(service=servico, options=chrome_options)
navegador.get('https://app.cfmv.gov.br/paginas/busca')

allRecords = []

for vet in formatList:
    # Seleciona UF
    formUf = navegador.find_element(By.NAME, 'filtro_uf')
    Select(formUf).select_by_value("SP")

    # Seleciona tipo de busca
    navegador.find_element(By.CSS_SELECTOR, "input[name='filtro_tp_texto'][value='2']").click()
    navegador.find_element(By.CSS_SELECTOR, "input[name='filtro_procurar'][value='2']").click()

    # Preenche input
    inputForm = navegador.find_element(By.NAME, 'filtro_texto')
    #inputForm.clear()
    inputForm.send_keys(vet)

    # Clica em filtrar
    SearchButton = navegador.find_element(By.CSS_SELECTOR, "input.btn-info.btn-padrao.col-5[value='Filtrar']")
    SearchButton.click()

    # Checa se apareceu mensagem de erro
    try:
        errorButton = WebDriverWait(navegador, 3).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "input.ui-button.ui-corner-all.ui-widget"))
        )
        errorButton.click()
        print(f"Erro ao buscar {vet}, cliquei no botão de erro.")
        continue  # pula para o próximo vet
    except TimeoutException:
        pass

    # Pega resultados
    time.sleep(0.5)
    result = navegador.find_element(By.ID, "relatorio")
    print(result.text)

    # Prepara novo search
    navegador.find_element(By.CSS_SELECTOR, "h2.texto-verde.text-center.mb-2.mt-2.border-bottom.filtrosDatatable.col-12.border").click()
    time.sleep(0.5)

