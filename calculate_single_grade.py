import re
import numpy as np
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException

# Insira o nome do filme aqui
film = "big-time-movie"
url = f"https://letterboxd.com/film/{film}/"
wait_timeout = 30

options = webdriver.ChromeOptions()
# options.add_argument("-headless")
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option("useAutomationExtension", False)

driver = webdriver.Chrome(options=options)
wait = WebDriverWait(driver, wait_timeout)

try:
    driver.get(url)

    # Cloudflare: página "Just a moment..." até o challenge passar
    wait.until(lambda d: "just a moment" not in d.title.lower())

    # Histograma vem via CSI assíncrono (/csi/film/.../rating-histogram/)
    histogram = wait.until(
        EC.presence_of_element_located((By.CLASS_NAME, "rating-histogram"))
    )
    secoes = histogram.find_elements(By.CLASS_NAME, "cell")

    notas = []
    for secao in secoes:
        try:
            if len(notas) >= 10:
                break
            nome = secao.find_element(By.TAG_NAME, "a")
            original_title = nome.get_attribute("data-original-title") or nome.get_attribute("title") or ""
            match = re.search(r"\((\d+)%\)", original_title)
            if not match:
                notas.append(0)
                continue
            notas.append(int(match.group(1)))
        except NoSuchElementException:
            notas.append(0)

    print("Filme coletado com sucesso!")
except TimeoutException:
    print(
        f"Timeout após {wait_timeout}s. Possíveis causas:\n"
        "- Cloudflare pedindo verificação (resolva no navegador e rode de novo)\n"
        f"- Histograma ainda não carregou em {url}"
    )
    raise SystemExit(1)
finally:
    driver.quit()


def calcular_nota_final(distribuicao):
    pesos = np.array([0.5, 1, 1.5, 2, 2.5, 3, 3.5, 4, 4.5, 5])
    votos = np.array(distribuicao)
    total_votos = np.sum(votos)

    if total_votos == 0:
        return 0.0

    media_ponderada = np.dot(pesos, votos) / total_votos

    moda_ponderada = pesos[np.argmax(votos / total_votos)]

    desvio_ponderado = np.std(votos * pesos / total_votos)

    ajuste_extremo = media_ponderada + (moda_ponderada - media_ponderada) * desvio_ponderado

    nota_final = min(pesos, key=lambda x: abs(x - ajuste_extremo))
    return nota_final


nota_final = calcular_nota_final(notas)

print(f"A nota do filme {film} é {nota_final}")
