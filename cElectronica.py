from datetime import datetime as dt

from lxml import etree as et


class Contabilidad:
    MESES_NOMBRE = {
        'Enero': 1,
        'Febrero': 2,
        'Marzo': 3,
        'Abril': 4,
        'Mayo': 5,
        'Junio': 6,
        'Julio': 7,
        'Agosto': 8,
        'Septiembre': 9,
        'Octubre': 10,
        'Noviembre': 11,
        'Diciembre': 12,
        'Cierre': 13,
    }

    def __init__(self):
        self._namespace_xsi = 'http://www.w3.org/2001/XMLSchema-instance'
        self._version = '1.3'


class Balanza(Contabilidad):
    def __init__(self, rfc=None, tipo_envio=None, mes=None, anio=None):
        super().__init__()
        self._namespace_bce = ('http://www.sat.gob.mx/esquemas/ContabilidadE'
                               '/1_3/BalanzaComprobacion')
        self._namespaces = {
            'BCE': self._namespace_bce,
            'xsi': self._namespace_xsi,
        }
        self._schemaLocation = ('http://www.sat.gob.mx/esquemas/ContabilidadE'
                                '/1_3/BalanzaComprobacion http://www.sat.gob'
                                '.mx/esquemas/ContabilidadE/1_3/BalanzaCompro'
                                'bacion/BalanzaComprobacion_1_3.xsd')
        self._rfc = rfc
        self._tipo_envio = tipo_envio
        self._mes = mes
        self._anio = anio
        self._cuentas = None

    @property
    def version(self):
        return self._version

    @version.setter
    def version(self, version):
        self._version = version

    @property
    def rfc(self):
        return self._rfc

    @rfc.setter
    def rfc(self, rfc):
        if 12 < len(rfc) > 13:
            self._rfc = 'Longitud de RFC incorrecta'
        else:
            self._rfc = rfc

    @property
    def tipo_envio(self):
        return self._tipo_envio

    @tipo_envio.setter
    def tipo_envio(self, tipo_envio):
        TIPOS = ('N', 'C')
        if tipo_envio not in TIPOS:
            self._tipo_envio = TIPOS[0]
        else:
            self._tipo_envio = tipo_envio

    @property
    def mes(self):
        return self._mes

    @mes.setter
    def mes(self, mes):
        MESES = (('0'+f'{x}')[-2:] for x in range(1, 14))
        if mes not in MESES:
            raise BalanzaError('Error! mes {mes} fuera del rango 1-13')
        else:
            self._mes = str(mes)

    @property
    def anio(self):
        return self._anio

    @anio.setter
    def anio(self, anio):
        if 2015 < int(anio) > 2099:
            self._anio = dt.now().year
        else:
            self._anio = str(anio)

    @property
    def cuentas(self):
        return self._cuentas

    @cuentas.setter
    def cuentas(self, cuentas):
        self._cuentas = cuentas

    def _convierte_xml(self):
        nombre_xml = f'{self.rfc}{self.anio}{self.mes}B{self.tipo_envio}.xml'
        attr_schema = et.QName(NA)

    def __str__(self):
        return f'Balanza {self._anio}-{self._mes}'

    def crea_xml(self):
        nombre_xml = (
            f'{self.rfc}{self.anio}{self.mes}B{self.tipo_envio}.xml'
        )
        attr_schema = et.QName(self._namespace_xsi, 'schemaLocation')
        elemento = et.Element(
            f'{{{self._namespace_bce}}}Balanza',
            nsmap=self._namespaces,
            attrib={
                attr_schema: self._schemaLocation,
                'Version': self.version,
                'RFC': self.rfc,
                'TipoEnvio': self.tipo_envio,
                'Mes': self.mes,
                'Anio': self.anio,
            }
        )
        for cuenta in self.cuentas:
            et.SubElement(
                elemento,
                f'{{{self._namespace_bce}}}Ctas',
                nsmap=self._namespaces,
                attrib={
                    'NumCta': cuenta.num_cta,
                    'SaldoIni': cuenta.saldo_ini,
                    'Debe': cuenta.debe,
                    'Haber': cuenta.haber,
                    'SaldoFin': cuenta.saldo_fin,
                }
            )
        arbol = et.ElementTree(elemento)
        arbol.write(nombre_xml, encoding='utf-8', pretty_print=True,
                    standalone=True)


class Cuenta:
    def __init__(self, num_cta=None, saldo_ini=None, debe=None, haber=None,
                 saldo_fin=None):
        self.num_cta = num_cta
        self.saldo_ini = saldo_ini
        self.debe = debe
        self.haber = haber
        self.saldo_fin = saldo_fin

    def _valida_decimales(self, numero):
        if isinstance(numero, float) or isinstance(numero, int):
            return str(round(numero, 2))
        numero = str(numero)
        if len(numero) == 0 or numero == 'None':
            return '0'
        if '.' in numero:
            val_dec = numero.split('.')
            if len(val_dec[1]) > 2:
                raise BalanzaError(
                    'Sólo puede haber dos o menos decimales'
                    + f'{self._num_cta}'
                )
        elif not numero.isdigit():
            raise BalanzaError(f'Tenías que ingresar un número ({numero})')

        return numero

    @property
    def num_cta(self):
        return self._num_cta

    @num_cta.setter
    def num_cta(self, num_cta):
        if len(num_cta) < 1:
            raise BalanzaError(
               'Error! ingresó un número de cuenta vacío para la balanza '
               + f'{self.balanza}'
            )
        self._num_cta = num_cta

    @property
    def saldo_ini(self):
        return self._saldo_ini

    @saldo_ini.setter
    def saldo_ini(self, saldo_ini):
        self._saldo_ini = self._valida_decimales(saldo_ini)

    @property
    def debe(self):
        return self._debe

    @debe.setter
    def debe(self, debe):
        self._debe = self._valida_decimales(debe)

    @property
    def haber(self):
        return self._haber

    @haber.setter
    def haber(self, haber):
        self._haber = self._valida_decimales(haber)

    @property
    def saldo_fin(self):
        return self._saldo_fin

    @saldo_fin.setter
    def saldo_fin(self, saldo_fin):
        self._saldo_fin = self._valida_decimales(saldo_fin)


class CatalogoCuenta(Contabilidad):
    def __init__(self, rfc, mes, anio):
        super().__init__()
        self._namespace_catalogo = ('http://www.sat.gob.mx/esquemas/'
                                    'ContabilidadE/1_3/CatalogoCuentas')
        self._namespaces = {
            'catalogocuentas': self._namespace_catalogo,
            'xsi': self._namespace_xsi,
        }
        self._schemaLocation = ('http://www.sat.gob.mx/esquemas/ContabilidadE'
                                '/1_3/CatalogoCuentas http://www.sat.gob.mx/'
                                'esquemas/ContabilidadE/1_3/CatalogoCuentas/'
                                'CatalogoCuentas_1_3.xsd')
        self._rfc = rfc
        self._mes = mes
        self._anio = anio
        self.cuentas = None

    @property
    def rfc(self):
        return self._rfc

    @rfc.setter
    def rfc(self, rfc):
        self._rfc = rfc

    @property
    def mes(self):
        return self._mes

    @mes.setter
    def mes(self, mes):
        self._mes = mes

    @property
    def anio(self):
        return self._anio

    @anio.setter
    def anio(self, anio):
        self._anio = anio

    def crea_xml(self):
        nombre_xml = f'{self.rfc}{self.anio}{self.mes}CT.xml'
        attr_schema = et.QName(self._namespace_xsi, 'schemaLocation')
        elemento = et.Element(
            f'{{{self._namespace_catalogo}}}Catalogo',
            nsmap=self._namespaces,
            attrib={
                attr_schema: self._schemaLocation,
                'Version': self._version,
                'RFC': self.rfc,
                'Mes': self.mes,
                'Anio': self.anio,
            }
        )
        for cuenta in self.cuentas:
            et.SubElement(
                elemento,
                f'{{{self._namespace_catalogo}}}Ctas',
                nsmap=self._namespaces,
                attrib={
                    'CodAgrup': cuenta.cod_agrupador,
                    'NumCta': cuenta.cuenta,
                    'Desc': cuenta.descripcion,
                    'Nivel': cuenta.nivel,
                    'Natur': cuenta.naturaleza,
                }
            )
        arbol = et.ElementTree(elemento)
        arbol.write(nombre_xml, encoding='utf-8', pretty_print=True,
                    standalone=True)


class CuentaCatalogo:

    NATURALEZAS = ('A', 'D')

    def __init__(self, cod_agrupador, cuenta, descripcion, naturaleza):
        self.cod_agrupador = cod_agrupador
        self.cuenta = cuenta
        self.descripcion = descripcion
        self.naturaleza = naturaleza
        self.nivel = str(len(cuenta.split('-')))

    def _valida_decimales(self, numero):
        num = str(numero)
        separa = num.split('.')
        if len(separa) == 2:
            entero, decimal = separa
            if decimal == '' or decimal == '0':
                return entero
            elif len(decimal) == 1:
                num = f'{entero}.{int(decimal):02d}'
        return num

    @property
    def cod_agrupador(self):
        return self._cod_agrupador

    @cod_agrupador.setter
    def cod_agrupador(self, cod_agrupador):
        self._cod_agrupador = self._valida_decimales(cod_agrupador)

    @property
    def cuenta(self):
        return self._cuenta

    @cuenta.setter
    def cuenta(self, cuenta):
        self._cuenta = cuenta

    @property
    def descripcion(self):
        return self._descripcion

    @descripcion.setter
    def descripcion(self, descripcion):
        self._descripcion = descripcion

    @property
    def naturaleza(self):
        return self._naturaleza

    @naturaleza.setter
    def naturaleza(self, naturaleza):
        if naturaleza in self.NATURALEZAS:
            self._naturaleza = naturaleza
        else:
            raise BalanzaError(
                f'La naturaleza solo puede ser {self.NATURALEZAS} '
                f'Tu pusiste {naturaleza} en la cuenta {self.cuenta}'
            )

    @property
    def nivel(self):
        return self._nivel

    @nivel.setter
    def nivel(self, nivel):
        self._nivel = nivel


class BalanzaError(Exception):

    BALANZA = ('Cuenta', 'Saldo Inicial',
                       'Debe', 'Haber', 'Saldo Final')
    CATALOGO = ('Código Agrupador', 'Cuenta',
                        'Descripción', 'Naturaleza')

    def __init__(self, error):
        super().__init__(self, error)


class CatalogoError(Exception):
    pass
