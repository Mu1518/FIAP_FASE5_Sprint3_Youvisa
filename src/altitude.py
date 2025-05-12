from pykml import parser
import pandas as pd


def extrair_altitude_kml(caminho_kml):
    """Extrai altitudes diretamente de arquivos KML que já contenham dados de elevação"""
    with open(caminho_kml, 'r', encoding='utf-8') as f:  # Abrir o arquivo com codificação UTF-8
        doc = parser.parse(f).getroot()

    dados = []
    for placemark in doc.findall('.//{http://www.opengis.net/kml/2.2}Placemark'):
        coords = placemark.find(
            './/{http://www.opengis.net/kml/2.2}coordinates')
        if coords is not None:
            for ponto in coords.text.strip().split(' '):
                valores = ponto.split(',')
                if len(valores) == 3:  # verificando se há latitude, longitude e altitude
                    lon, lat, alt = map(float, valores)
                    dados.append(
                        {'Latitude': lat, 'Longitude': lon, 'Altitude': alt})

    return pd.DataFrame(dados)


def extrair_dados_altitude(caminho_kml):
    with open(caminho_kml, 'r', encoding='utf-8') as f:
        doc = parser.parse(f).getroot()
    dados = []
    for placemark in doc.findall('.//{http://www.opengis.net/kml/2.2}Placemark'):
        coords = placemark.find(
            './/{http://www.opengis.net/kml/2.2}coordinates')
        if coords is not None:
            for ponto in coords.text.strip().split(' '):
                valores = ponto.split(',')
                if len(valores) == 3:
                    lon, lat, alt = map(float, valores)
                    dados.append({'lat': lat, 'lon': lon, 'altitude': alt})
    return dados

# Caminho do arquivo KML
caminho_kml = r'C:\Users\techg\Desktop\TESTESP3\BR_Localidades_2010_v1.kml'

# Extrair dados do KML
df_kml = extrair_altitude_kml(caminho_kml)

# Exibir os dados extraídos
print("Dados extraídos do KML:")
print(df_kml.head())
