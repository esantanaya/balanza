import os
import re

import xlrd
from lxml import etree as et

from src.cElectronica import Balanza, Cuenta

MESES_NOMBRE = {
    'Abril': 4,
    'Agosto': 8,
    'Diciembre': 12,
    'Enero': 1,
    'Febrero': 2,
    'Julio': 7,
    'Junio': 6,
    'Marzo': 3,
    'Mayo': 5,
    'Noviembre': 11,
    'Octubre': 10,
    'Septiembre': 9,
}
# TODO: Deshacer esto, ya está definido en la clase, mi sindrome de down, sorry
NS_BCE = 'http://www.sat.gob.mx/esquemas/ContabilidadE/1_3/BalanzaComprobacion'
NS_XSI = 'http://www.w3.org/2001/XMLSchema-instance'
NS_SCHEMALOCATION = 'http://www.w3.org/2001/XMLSchema-instance'

def crea_xml(balanza):
    nombre_xml = (f'{balanza.rfc}-{balanza.mes}-{balanza.anio}'
        +f'-{balanza.tipo_envio}.xml')
    with et.xmlfile(nombre_xml, encoding='UTF-8') as xml:
        with xml.element(
            # TODO: No se refleja bien el namespace
            f'{{NS_BCE}}Balanza',
            nsmap={'BCE': NS_BCE, 'xsi': NS_XSI},
            attrib={
                'xsi': NS_SCHEMALOCATION,
                'Version': balanza.version,
                'RFC': balanza.rfc,
                'TipoEnvio': balanza.tipo_envio,
                'Mes': balanza.mes,
                'Anio': balanza.anio
            }
        ):
            for cuenta in balanza.cuentas:
                # TODO: Terminar las cuentas
                xml.write(et.Element(f'{{NS_BCE}}Ctas'))


def genera_contabilidad(nombre_archivo):
    libro = xlrd.open_workbook(nombre_archivo)
    rfc_actual = nombre_archivo.split('.')[0]
    pestanas = libro.sheets()
    for pestana in pestanas:
        cuentas = []
        mes_nombre, anio = pestana.name.split(' ')
        mes_numero = MESES_NOMBRE[mes_nombre]
        mes = f'0{str(mes_numero)}'[-2:]
        balanza = Balanza(rfc_actual, 'N', mes, anio)
        for fila in pestana.get_rows():
            if fila[1].value.isdigit():
                cuenta = Cuenta(
                    fila[1].value,
                    fila[3].value,
                    fila[4].value,
                    fila[5].value,
                    fila[6].value
                )
                cuentas.append(cuenta)
        balanza.cuentas = cuentas
    return balanza


def obtener_archivos():
    archivos = os.listdir()
    regex = [re.match(r'^\w[\w\s\(\)]+\.xlsx?', x) for x in archivos]
    archivos_validos = [x.string for x in archivos_validos if x != None]
    return archivos_validos

def main():
    archivos = obtener_archivos()
    for archivo in archivos:
        genera_contabilidad(archivo)


if __name__ == '__main__':
    main()
