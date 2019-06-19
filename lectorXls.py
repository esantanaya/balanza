import os
import re
import traceback
from string import capwords

import xlrd

from cElectronica import (CatalogoCuenta, CuentaCatalogo,
                          Balanza, Cuenta, BalanzaError)


def detecta_titulos(fila):
    TITULOS = ('Código Agrupador', 'Cuenta', 'Descripción', 'Saldo Inicial',
               'Debe', 'Haber', 'Saldo Final', 'Naturaleza')
    TITULOS_BALANZA = ('Cuenta', 'Saldo Inicial',
                       'Debe', 'Haber', 'Saldo Final')
    TITULOS_CATALOGO = ('Código Agrupador', 'Cuenta',
                        'Descripción', 'Naturaleza')
    valores = [capwords(x.value) for x in fila]
    if all([x in valores for x in TITULOS]):
        return 2
    if all([x in valores for x in TITULOS_BALANZA]):
        return 0
    if all([x in valores for x in TITULOS_CATALOGO]):
        return 1
    return -1


def asigna_columna(fila):
    return {capwords(celda.value): num for num, celda in enumerate(fila)}


def id_fila(fila, asig_col):
    for nombre, col in asig_col.items():
        if nombre == 'Código Agrupador':
            ex = r'^\d{3}\.?(\.\d{1,2})?$'
            fila[col].ctype


def numero_fila_titulos(pestana):
    for num, fila in enumerate(pestana.get_rows()):
        if all(map(lambda x: x.ctype == 1, fila)):
            return num


def genera_contabilidad(nombre_archivo):
    ex = r'^\d{3}[A-Z\-]*\d*$'
    libro = xlrd.open_workbook(nombre_archivo)
    rfc_actual = nombre_archivo.split('.')[0]
    pestanas = libro.sheets()
    for pestana in pestanas:
        try:
            mes_nombre, anio = pestana.name.split(' ')
        except ValueError:
            raise BalanzaError(
                'Recuerda nombrar correctamente las pestañas '
                + f'{nombre_archivo} {pestana.name}'
            )
        mes_numero = Balanza.MESES_NOMBRE[mes_nombre]
        mes = f'{mes_numero:02d}'
        fila_titulos = pestana.row(numero_fila_titulos(pestana))
        dic_titulos = asigna_columna(fila_titulos)
        opciones = detecta_titulos(fila_titulos)
        if opciones == -1:
            raise BalanzaError('Para que funcione el programa los titulos de '
                               f'las columnas deben ser {BalanzaError.BALANZA}'
                               f', para la balanza y {BalanzaError.CATALOGO}'
                               ' para el catálogo, pueden estar en otro orden'
                               ' o que haya otros titulos pero si aparecen '
                               'deben tener ese nombre.'
                               f' Los titulos que usaste son: {fila_titulos}'
                               f' en la pestaña {pestana.name} del archivo '
                               f'{nombre_archivo}')
        if opciones == 2 or opciones == 0:
            cuentas = []
            balanza = Balanza(rfc_actual, 'N', mes, anio)
            for fila in pestana.get_rows():
                if fila[1].ctype == 2:
                    valor_fila = str(fila[1].value)
                    valor_fila = valor_fila.split('.')[0]
                    fila[1].value = valor_fila
                if re.match(ex, fila[1].value):
                    cuenta = Cuenta(
                        fila[dic_titulos['Cuenta']].value,
                        fila[dic_titulos['Saldo Inicial']].value,
                        fila[dic_titulos['Debe']].value,
                        fila[dic_titulos['Haber']].value,
                        fila[dic_titulos['Saldo Final']].value,
                    )
                    cuentas.append(cuenta)
            balanza.cuentas = cuentas
            balanza.crea_xml()
        if opciones == 2 or opciones == 1:
            cuentas = []
            catalogo = CatalogoCuenta(rfc_actual, mes, anio)
            for fila in pestana.get_rows():
                if fila[1].ctype == 2:
                    valor_fila = str(fila[1].value)
                    valor_fila = valor_fila.split('.')[0]
                    fila[1].value = valor_fila
                if re.match(ex, fila[1].value):
                    try:
                        cuenta = CuentaCatalogo(
                            fila[dic_titulos['Código Agrupador']].value,
                            fila[dic_titulos['Cuenta']].value,
                            fila[dic_titulos['Descripción']].value,
                            fila[dic_titulos['Naturaleza']].value,
                        )
                    except BalanzaError as err:
                        le = input(f'Vaya ocurrió un error: {err}, '
                                   'lo quieres corregir?(S/N)')
                        if le.lower() == 's':
                            res = input('Ingresa la naturaleza correcta: ')
                            cuenta = CuentaCatalogo(
                                fila[dic_titulos['Código Agrupador']].value,
                                fila[dic_titulos['Cuenta']].value,
                                fila[dic_titulos['Descripción']].value,
                                res,
                            )
                    cuentas.append(cuenta)
            catalogo.cuentas = cuentas
            catalogo.crea_xml()


def obtener_archivos():
    archivos = os.listdir()
    regex = [
        re.match(
            r'^[A-ZÑ&]{3,4}\d{6}(?:[A-Z\d]{3})?\.xlsx?', x
        ) for x in archivos
    ]
    archivos_validos = [x.string for x in regex if x is not None]
    if len(archivos_validos) < 1:
        raise BalanzaError('No encontré ningún archivo válido, recuerda'
                           ' que el nombre del archivo debe ser un RFC')
    return archivos_validos


def main():
    archivos = obtener_archivos()
    for archivo in archivos:
        genera_contabilidad(archivo)


if __name__ == '__main__':
    try:
        main()
    except Exception:
        traceback.print_exc()
    finally:
        input('Terminamos, presiona Enter')
