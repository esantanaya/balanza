import os
import re
import traceback

import xlrd

from cElectronica import CatalogoCuenta, CuentaCatalogo, CatalogoError


def genera_catalogo(nombre_archivo):
    ex = r'^\d{3}[A-Z\-]*\d*$'
    libro = xlrd.open_workbook(nombre_archivo)
    if nombre_archivo.startswith('CAT'):
        rfc = nombre_archivo.split('.')[0][3:]
    else:
        raise CatalogoError(f'Archivo invalido {nombre_archivo}')
    pestanas = libro.sheets()
    for pestana in pestanas:
        cuentas = []
        try:
            anio = pestana.name.split(' ')[1]
        except ValueError:
            raise CatalogoError('Recuerda nombrar correctamente las pestañas'
                                f'{nombre_archivo} {pestana.name}')
        catalogo = CatalogoCuenta(rfc, '13', anio)
        for fila in pestana.get_rows():
            if fila[1].ctype == 2:
                valor_fila = str(fila[1].value)
                valor_fila = valor_fila.split('.')[0]
                fila[1].value = valor_fila
            if re.match(ex, fila[1].value):
                cuenta = CuentaCatalogo(
                    fila[0].value,
                    fila[1].value,
                    fila[2].value,
                    fila[3].value,
                )
                cuentas.append(cuenta)
        catalogo.cuentas = cuentas
        for nombre, mes in catalogo.MESES_NOMBRE.items():
            catalogo.mes = f'{mes:02d}'
            catalogo.crea_xml()


def obtener_archivos():
    archivos = os.listdir()
    regex = [
        re.match(
            r'^CAT[A-ZÑ&]{3,4}\d{6}(?:[A-Z\d]{3})?\.xlsx?', x
        ) for x in archivos
    ]
    archivos_validos = [x.string for x in regex if x is not None]
    return archivos_validos


def main():
    archivos = obtener_archivos()
    for archivo in archivos:
        genera_catalogo(archivo)


if __name__ == '__main__':
    try:
        main()
    except Exception:
        traceback.print_exc()
    finally:
        input('Terminamos, presiona Enter')
