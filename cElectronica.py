from datetime import datetime as dt


class Balanza:
    def __init__(self, rfc=None, tipo_envio=None, mes=None, anio=None):
        self._name_space_bce = 'http://www.sat.gob.mx/esquemas/ContabilidadE/1_3/BalanzaComprobacion'
        self._name_space_xsi = 'http://www.w3.org/2001/XMLSchema-instance'
        self._schemaLocation = 'http://www.sat.gob.mx/esquemas/ContabilidadE/1_3/BalanzaComprobacion http://www.sat.gob.mx/esquemas/ContabilidadE/1_3/BalanzaComprobacion/BalanzaComprobacion_1_3.xsd'
        self._version = '1.3'
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
        MESES = (('0'+f'{x}')[-2:] for x in range(1, 13))
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

    def __str__(self):
        return f'Balanza {self._anio}-{self._mes}'


class Cuenta:
    def __init__(
        self,
        num_cta=None,
        saldo_ini=None,
        debe=None,
        haber=None,
        saldo_fin=None,
    ):
        self._num_cta = num_cta
        self._saldo_ini = saldo_ini
        self._debe = debe
        self._haber = haber
        self._saldo_fin = saldo_fin

    def _valida_decimales(numero):
        val_dec = str(numero).split('.')
        if len(val_dec[1]) > 2:
            raise BalanzaError(
                'Sólo puede haber dos o menos decimales'
                + f'{self._balanza} {self._num_cta}'
            )
        else:
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


class BalanzaError(Exception):
    def __init__(self, error):
        super().__init__(self, error)