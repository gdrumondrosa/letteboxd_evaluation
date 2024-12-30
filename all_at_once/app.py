from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
import re
import time
import pandas as pd

options = Options()
options = webdriver.FirefoxOptions()
options.add_argument('-headless')
driver = webdriver.Firefox(options=options)

driver.get("https://letterboxd.com/guidrumz/films/")

page = 1
stop = False

df = pd.DataFrame({"Filme":[], "Slug": []})

while stop == False:
    time.sleep(3)

    secoes = driver.find_elements(By.CLASS_NAME,"poster-container")

    if page == 5:
        stop = True

    for secao in secoes:
        try: 
            nome = secao.find_element(By.CLASS_NAME,"film-poster")
            nome = nome.get_attribute('data-film-name')
        except NoSuchElementException: 
            nome = "-"
        try:
            slug = secao.find_element(By.CLASS_NAME,"film-poster")
            slug = slug.get_attribute('data-film-slug')
        except NoSuchElementException: 
            slug = "-"

        row = {"Filme": nome, "Slug": slug}
        df = pd.concat([df,pd.DataFrame([row])], ignore_index = True)
    
    print(f'Page {page} completed!')
    page = page + 1
    driver.get("https://letterboxd.com/guidrumz/films/page/"+ str(page) +"/")

print(df)

df['Notas'] = None

for index, film in df['Slug'].items():
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
    
    df.at[index, 'Notas'] = notas

    print(f'Filme {index} coletado com sucesso!')
    
df.to_csv('movie_grades.csv')

driver.quit()