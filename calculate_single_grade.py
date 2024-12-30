from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
import re
import time
import numpy as np

options = Options()
options = webdriver.FirefoxOptions()
options.add_argument('-headless')
driver = webdriver.Firefox(options=options)

# Insira o nome do filme aqui
film = ""

driver.get("https://letterboxd.com/film/"+ film +"/")
time.sleep(3)

secoes = driver.find_elements(By.CLASS_NAME,"rating-histogram-bar")

notas = []

for secao in secoes:
    try: 
        nome = secao.find_element(By.CLASS_NAME,"ir")
        original_title = nome.get_attribute('data-original-title')
        match = re.search(r"\((\d+)%\)", original_title)
        percentage = int(match.group(1))
        notas.append(percentage)
    except NoSuchElementException: 
        notas.append(0)

print(f'Filme coletado com sucesso!')

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

print(f'A nota do filme {film} é {nota_final}')