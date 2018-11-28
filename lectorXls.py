import os
import re

import xlrd

from cElectronica import Balanza, Cuenta, BalanzaError


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
        mes_numero = Balanza.MESES_NOMBRE[mes_nombre]
        mes = f'{mes_numero:02d}'
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
        balanza.crea_xml()


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
