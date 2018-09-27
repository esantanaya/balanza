import os
import re

import xlrd
from lxml import etree as et
from lxml import objectify as obj

from cElectronica import Balanza, Cuenta, BalanzaError

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
NAMESPACES = {
    'BCE':
    'http://www.sat.gob.mx/esquemas/ContabilidadE/1_3/BalanzaComprobacion',
    'xsi': 'http://www.w3.org/2001/XMLSchema-instance',
}
NS_SCHEMALOCATION = 'http://www.sat.gob.mx/esquemas/ContabilidadE/1_3/BalanzaComprobacion http://www.sat.gob.mx/esquemas/ContabilidadE/1_3/BalanzaComprobacion/BalanzaComprobacion_1_3.xsd'


def crea_xml(balanza):
    nombre_xml = (
        f'{balanza.rfc}{balanza.anio}{balanza.mes}B{balanza.tipo_envio}.xml'
    )
    attr_schema = et.QName(NAMESPACES['xsi'], 'schemaLocation')
    with et.xmlfile(nombre_xml, encoding='UTF-8') as xml:
        xml.write_declaration(standalone=True)
        with xml.element(
            '{' + NAMESPACES['BCE'] + '}' + 'Balanza',
            nsmap=NAMESPACES,
            attrib={
                attr_schema: NS_SCHEMALOCATION,
                'Version': balanza.version,
                'RFC': balanza.rfc,
                'TipoEnvio': balanza.tipo_envio,
                'Mes': balanza.mes,
                'Anio': balanza.anio
            }
        ) as elemento_padre:
            for cuenta in balanza.cuentas:
                xml.write(et.Element(
                    '{' + NAMESPACES['BCE'] + '}' + 'Ctas',
                    nsmap=NAMESPACES,
                    attrib={
                        'NumCta': cuenta.num_cta,
                        'SaldoIni': cuenta.saldo_ini,
                        'Debe': cuenta.debe,
                        'Haber': cuenta.haber,
                        'SaldoFin': cuenta.saldo_fin,
                    },
                )
                )


def genera_contabilidad(nombre_archivo):
    ex = r'^\d{3}[A-Z\-]*\d*$'
    libro = xlrd.open_workbook(nombre_archivo)
    rfc_actual = nombre_archivo.split('.')[0]
    pestanas = libro.sheets()
    for pestana in pestanas:
        cuentas = []
        try:
            mes_nombre, anio = pestana.name.split(' ')
        except ValueError as ve:
            raise BalanzaError(
                'Recuerda nombrar correctamente las pestañas '
                + f'{nombre_archivo} {pestana.name}'
            )
        mes_numero = MESES_NOMBRE[mes_nombre]
        mes = f'0{str(mes_numero)}'[-2:]
        balanza = Balanza(rfc_actual, 'N', mes, anio)
        for fila in pestana.get_rows():
            if fila[1].ctype == 2:
                valor_fila = str(fila[1].value)
                valor_fila = valor_fila.split('.')[0]
                fila[1].value = valor_fila
            if re.match(ex, fila[1].value):
                cuenta = Cuenta(
                    fila[1].value,
                    fila[3].value,
                    fila[4].value,
                    fila[5].value,
                    fila[6].value
                )
                cuentas.append(cuenta)
        balanza.cuentas = cuentas
        crea_xml(balanza)


def obtener_archivos():
    archivos = os.listdir()
    regex = [
        re.match(
            r'^[A-ZÑ&]{3,4}\d{6}(?:[A-Z\d]{3})?\.xlsx?', x
        ) for x in archivos
    ]
    archivos_validos = [x.string for x in regex if x != None]
    return archivos_validos


def main():
    archivos = obtener_archivos()
    for archivo in archivos:
        genera_contabilidad(archivo)


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(e)
    finally:
        input('Terminamos, presiona Enter')
