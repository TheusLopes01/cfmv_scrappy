from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager
from vet_list_sp import formatList
import sqlite3
import time

# =========================
# Configurações Selenium
# =========================
chrome_options = Options()
chrome_options.add_experimental_option("detach", True)

servico = Service(ChromeDriverManager().install())
navegador = webdriver.Chrome(service=servico, options=chrome_options)
navegador.get('https://app.cfmv.gov.br/paginas/busca')

# =========================
# Conexão com SQLite
# =========================
conn = sqlite3.connect("vets_sp.db")
cursor = conn.cursor()

# Tabelas
cursor.execute("""
CREATE TABLE IF NOT EXISTS vets_found (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    vet TEXT UNIQUE,
    result TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS vets_error (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    vet TEXT UNIQUE
)
""")
conn.commit()

# Recuperar já processados
cursor.execute("SELECT vet FROM vets_found")
found_existing = {row[0] for row in cursor.fetchall()}

cursor.execute("SELECT vet FROM vets_error")
error_existing = {row[0] for row in cursor.fetchall()}

processed = found_existing | error_existing
print(f"🔄 Já processados: {len(processed)}")

# =========================
# Loop principal
# =========================
batch_size = 50
counter = 0

for vet in formatList:
    if vet in processed:
        print(f"⏩ Pulando (já processado): {vet}")
        continue

    # Seleciona UF
    formUf = navegador.find_element(By.NAME, 'filtro_uf')
    Select(formUf).select_by_value("SP")

    # Seleciona tipo de busca
    navegador.find_element(By.CSS_SELECTOR, "input[name='filtro_tp_texto'][value='2']").click()
    navegador.find_element(By.CSS_SELECTOR, "input[name='filtro_procurar'][value='2']").click()

    # Preenche input
    inputForm = navegador.find_element(By.NAME, 'filtro_texto')
    inputForm.clear()
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
        print(f"❌ Erro ao buscar {vet}, registrado no banco de erros")
        cursor.execute("INSERT OR IGNORE INTO vets_error (vet) VALUES (?)", (vet,))
        conn.commit()
        continue  # pula para o próximo vet
    except TimeoutException:
        pass

    # Pega resultados
    time.sleep(0.5)
    result = navegador.find_element(By.ID, "relatorio").text
    print(f"✅ Resultado para {vet}:\n{result}\n")

    # Salva no banco
    cursor.execute("INSERT OR IGNORE INTO vets_found (vet, result) VALUES (?, ?)", (vet, result))

    counter += 1

    # Salvar a cada batch_size
    if counter % batch_size == 0:
        conn.commit()
        print(f"💾 {counter} registros salvos no banco até agora")

    # Prepara novo search
    navegador.find_element(By.CSS_SELECTOR, "h2.texto-verde.text-center.mb-2.mt-2.border-bottom.filtrosDatatable.col-12.border").click()
    time.sleep(0.5)

# Commit final e fechar conexão
conn.commit()
conn.close()
print("\n🎉 Processo finalizado! Todos os dados foram salvos.")
