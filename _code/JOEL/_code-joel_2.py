# Clasicos
import pandas as pd
import numpy as np

# Paths
import re
import os
from pathlib import Path

# For simulate human behavior.
import time
from time import sleep
import random

# Clear data
import unidecode

# DIVERSOS
from IPython.core.display import display, HTML
display(HTML("<style>.container { width:80% !important; }</style>"))
from datetime import date
from parsel import Selector
import pytest
import json

# Options driver
from webdriver_manager.chrome import ChromeDriverManager
from win32com.client import Dispatch

# SELENIUM
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

# DEFINIR EL PATH PRINCIPAL
os.chdir(r"C:\Users\JOEL\Desktop\geobosques_scrapping")

# GUARDAD EL PATH COMO OBJETO Y ABREVIR PARA RUTAS FUTURAS
inicio = os.getcwd()
new_dir = 'LAP_CEM' + str(date.today())

# CREAR UNA CARPETA Y DEFINIR SU PATH
Path(new_dir).mkdir(exist_ok=True)
descargas = os.path.join(inicio, new_dir); descargas


####ABRIR PAGINA DE INTERÉS
options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")
driver = webdriver.Chrome(r"C:\Users\JOEL\AppData\Local\Programs\Python\Python38\Lib\site-packages\selenium\chromedriver.exe", chrome_options=options)
driver.get("http://geobosques.minam.gob.pe/geobosque/view/perdida.php")


####CAMBIAR NOMBRES RAROS
nombres = pd.read_excel('dpto_prov_dist.xlsx') 
nombres.at[115 , 'dist'] = 'CORONEL CASTA'  # AYACUCHO	PARINACOCHAS CORONEL CASTAÑEDA 115
nombres.at[133 , 'dist'] = 'HUACA'          # AYACUCHO SUCRE HUACAÑA  133
nombres.at[233 , 'dist'] = 'CHANCAYBA'      # CAJAMARCAR SANTA  CRUZ 233
nombres.at[563 , 'dist'] = 'BA'             # HUANUCO LAURICOCHA BAÑOS 563
nombres.at[854 , 'dist'] = 'FERRE'          # LAMBAYEQUE FERREÑAFE FERREÑAFE 854
nombres.at[1005, 'dist'] = 'PARI'           # PIURA TALARA PARIÑAS 1005
nombres.at[1105, 'dist'] = 'NU'             # PUNO MELGAR NUÑOA 1105

#### OBTENER DATOS
tabla_final  = pd.DataFrame()
for i in range(0,len(nombres)):
    try: 
        driver.find_element(By.CSS_SELECTOR, "#dr_departamento_chosen span").click()
        driver.find_element(By.CSS_SELECTOR, "#dr_departamento_chosen .chosen-search-input").click()
        driver.find_element(By.CSS_SELECTOR, "#dr_departamento_chosen .chosen-search-input").send_keys(str(nombres['dpto'][i]))
        driver.find_element(By.CSS_SELECTOR, ".active-result").click()
        time.sleep( 0.5 )
        driver.find_element(By.CSS_SELECTOR, "#dr_provincia_chosen span").click()
        driver.find_element(By.CSS_SELECTOR, "#dr_provincia_chosen .chosen-search-input").click()
        driver.find_element(By.CSS_SELECTOR, "#dr_provincia_chosen .chosen-search-input").send_keys(str(nombres['prov'][i]))
        driver.find_element(By.CSS_SELECTOR, "#dr_provincia_chosen .active-result").click()
        time.sleep( 0.5 )
        driver.find_element(By.CSS_SELECTOR, "#dr_distrito_chosen span").click()
        driver.find_element(By.CSS_SELECTOR, "#dr_distrito_chosen .chosen-search-input").click()
        driver.find_element(By.CSS_SELECTOR, "#dr_distrito_chosen .chosen-search-input").send_keys(str(nombres['dist'][i]))
        driver.find_element(By.CSS_SELECTOR, "#dr_distrito_chosen em").click()
        time.sleep( 0.5 )
        
        print("----------")
        print(str(nombres['dpto'][i])+" "+str(nombres['prov'][i])+" "+str(nombres['dist'][i]))
        print("----------")
              
        tabla_html = driver.find_element_by_id("pannel-perdida-t-ha")
        tabla_intermedia = pd.read_html( tabla_html.get_attribute('outerHTML') )[0]
        tabla_intermedia = tabla_intermedia.assign(dpto=nombres['dpto'][i], prov=nombres['prov'][i], dist = nombres['dist'][i])
        tabla_final = pd.concat([tabla_final, tabla_intermedia], axis=0).reset_index(drop=True)
    except:
        pass
    
#### PREPARANDO DATOS PARA EXPORTAR

# ELIMINAR FILA ESPECÍFICAS
tabla_final.drop(tabla_final[tabla_final['Rango']=="Total"].index, inplace=True)

# ORDENAR COLUMNAS PARA UN NUEVO DF
cols = list(tabla_final.columns)
cols = cols[22:26] + cols[0:22]
pre_final = tabla_final[cols]

# ORDENAR LA VARIABLE "RANGO"
pre_final["orden"] = ""
pre_final.loc[pre_final["Rango"] == "<1", "orden"] = '5'
pre_final.loc[pre_final["Rango"] == "1 - 5", "orden"] = '4'
pre_final.loc[pre_final["Rango"] == "5 - 50", "orden"] = '3'
pre_final.loc[pre_final["Rango"] == "50 - 500", "orden"] = '2'
pre_final.loc[pre_final["Rango"] == "> 500", "orden"] = '1'

#  SORTEAR DF
pre_final = pre_final.sort_values(by=['dpto', 'prov', 'dist', 'orden'])
final = pre_final.drop('orden', axis=1)

#### EXPORTAR DATOS
final.to_excel('GeoBosques.xlsx', index=False)
