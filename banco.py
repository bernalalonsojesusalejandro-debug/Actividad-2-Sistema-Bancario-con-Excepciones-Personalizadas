"""Actividad 2. Sistema bancario con excepciones personalizadas."""
import logging
from datetime import date, datetime
from decimal import Decimal, InvalidOperation

logging.basicConfig(filename='errores_banco.log', level=logging.WARNING,
                    format='%(asctime)s | %(levelname)s | %(message)s',
                    encoding='utf-8')


class BancoError(Exception):
    """Error base del banco; guarda un código para identificar el problema."""
    def __init__(self, mensaje, codigo='BANCO_ERROR'):
        super().__init__(mensaje)
        self.codigo = codigo


class SaldoInsuficienteError(BancoError):
    """Indica que una cuenta no tiene dinero suficiente para una operación."""
    def __init__(self, saldo_actual, monto_solicitado):
        self.saldo_actual = saldo_actual
        self.monto_solicitado = monto_solicitado
        self.deficit = monto_solicitado - saldo_actual
        super().__init__(f'Saldo insuficiente: tienes ${saldo_actual:.2f}, '
                         f'necesitas ${monto_solicitado:.2f} (faltan ${self.deficit:.2f})',
                         'SALDO_INSUFICIENTE')


class CuentaNoEncontradaError(BancoError):
    """Se produce cuando se busca una cuenta que no está registrada."""
    def __init__(self, numero_cuenta):
        self.numero_cuenta = numero_cuenta
        super().__init__(f'La cuenta {numero_cuenta} no existe', 'CUENTA_NO_ENCONTRADA')


class CuentaBloqueadaError(BancoError):
    """Impide movimientos en una cuenta que está bloqueada."""
    def __init__(self, numero_cuenta):
        self.numero_cuenta = numero_cuenta
        super().__init__(f'La cuenta {numero_cuenta} está bloqueada', 'CUENTA_BLOQUEADA')


class MontoInvalidoError(BancoError):
    """Se usa si un monto no es numérico, no es finito o no es positivo."""
    def __init__(self, monto):
        self.monto = monto
        super().__init__(f'Monto inválido: {monto}. Debe ser positivo', 'MONTO_INVALIDO')


class LimiteDiarioExcedidoError(BancoError):
    """Indica que el retiro o transferencia supera el límite diario."""
    def __init__(self, limite, retirado_hoy, monto_solicitado):
        self.limite = limite
        self.retirado_hoy = retirado_hoy
        self.monto_solicitado = monto_solicitado
        super().__init__(f'Límite diario excedido: límite ${limite:.2f}, '
                         f'retirado hoy ${retirado_hoy:.2f}, solicitado ${monto_solicitado:.2f}',
                         'LIMITE_EXCEDIDO')


def validar_monto(monto):
    """Convierte a Decimal y lanza MontoInvalidoError si el valor no sirve."""
    try:
        valor = Decimal(str(monto))
    except (InvalidOperation, ValueError, TypeError) as error:
        raise MontoInvalidoError(monto) from error
    if not valor.is_finite() or valor <= 0:
        raise MontoInvalidoError(monto)
    if valor.as_tuple().exponent < -2:
        raise MontoInvalidoError(monto)
    return valor


class CuentaBancaria:
    """Guarda los datos, saldo y movimientos de una cuenta."""
    LIMITE_DIARIO = Decimal('5000.00')

    def __init__(self, numero, titular, saldo_inicial=0):
        """Inicializa una cuenta y registra su saldo de apertura."""
        self.numero = str(numero)
        self.titular = titular
        self._saldo = Decimal('0.00')
        self._bloqueada = False
        self._retirado_hoy = Decimal('0.00')
        self._fecha_retiros = date.today()
        self._historial = []
        inicial = Decimal('0.00') if str(saldo_inicial) == '0' else validar_monto(saldo_inicial)
        if inicial:
            self._saldo = inicial
        self._registrar('Apertura', inicial)

    @property
    def saldo(self):
        """Devuelve el saldo sin permitir modificarlo directamente."""
        return self._saldo

    def _registrar(self, tipo, monto):
        """Agrega un movimiento con fecha y saldo final."""
        self._historial.append((datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                                tipo, monto, self._saldo))

    def _verificar_activa(self):
        """Comprueba que la cuenta no esté bloqueada."""
        if self._bloqueada:
            raise CuentaBloqueadaError(self.numero)

    def _verificar_retiro(self, monto):
        """Revisa el saldo y el límite antes de descontar dinero."""
        self._verificar_activa()
        if date.today() != self._fecha_retiros:
            self._retirado_hoy = Decimal('0.00')
            self._fecha_retiros = date.today()
        if monto > self._saldo:
            raise SaldoInsuficienteError(self._saldo, monto)
        if self._retirado_hoy + monto > self.LIMITE_DIARIO:
            raise LimiteDiarioExcedidoError(self.LIMITE_DIARIO, self._retirado_hoy, monto)

    def depositar(self, monto):
        """Suma un monto positivo a una cuenta activa."""
        cantidad = validar_monto(monto)
        self._verificar_activa()
        self._saldo += cantidad
        self._registrar('Depósito', cantidad)

    def retirar(self, monto):
        """Descuenta dinero si hay saldo y no se rebasa el límite."""
        cantidad = validar_monto(monto)
        self._verificar_retiro(cantidad)
        self._saldo -= cantidad
        self._retirado_hoy += cantidad
        self._registrar('Retiro', cantidad)

    def consultar_saldo(self):
        """Consulta el saldo de una cuenta activa."""
        self._verificar_activa()
        return self.saldo

    def bloquear(self):
        """Bloquea la cuenta para impedir movimientos."""
        self._bloqueada = True

    def desbloquear(self):
        """Permite nuevamente operar con la cuenta."""
        self._bloqueada = False

    def mostrar_historial(self):
        """Devuelve una copia del historial para mostrarlo en el menú."""
        return list(self._historial)


class Banco:
    """Administra las cuentas registradas y las transferencias."""
    _total = 0

    def __init__(self):
        """Prepara el diccionario de cuentas del banco."""
        self._cuentas = {}

    def crear_cuenta(self, numero, titular, saldo_inicial=0):
        """Crea una cuenta con número único y titular válido."""
        numero = str(numero).strip()
        if not numero or not str(titular).strip():
            raise BancoError('El número y el titular son obligatorios', 'DATOS_INVALIDOS')
        if numero in self._cuentas:
            raise BancoError(f'La cuenta {numero} ya existe', 'CUENTA_DUPLICADA')
        cuenta = CuentaBancaria(numero, str(titular).strip(), saldo_inicial)
        self._cuentas[numero] = cuenta
        Banco._total += 1
        return cuenta

    def obtener_cuenta(self, numero):
        """Busca una cuenta o lanza CuentaNoEncontradaError."""
        try:
            return self._cuentas[str(numero).strip()]
        except KeyError as error:
            raise CuentaNoEncontradaError(numero) from error

    def transferir(self, origen, destino, monto):
        """Transfiere dinero solo si ambas cuentas permiten la operación."""
        cantidad = validar_monto(monto)
        cuenta_origen = self.obtener_cuenta(origen)
        cuenta_destino = self.obtener_cuenta(destino)
        if cuenta_origen.numero == cuenta_destino.numero:
            raise BancoError('No puedes transferir a la misma cuenta', 'MISMA_CUENTA')
        cuenta_destino._verificar_activa()
        cuenta_origen._verificar_retiro(cantidad)
        cuenta_origen._saldo -= cantidad
        cuenta_origen._retirado_hoy += cantidad
        cuenta_destino._saldo += cantidad
        cuenta_origen._registrar(f'Transferencia a {destino}', cantidad)
        cuenta_destino._registrar(f'Transferencia de {origen}', cantidad)

    @classmethod
    def total_cuentas(cls):
        """Informa cuántas cuentas se crearon en el programa."""
        return cls._total


def reportar_error(error):
    """Registra un error y lo relanza para que el menú lo muestre."""
    try:
        raise error
    except BancoError:
        logging.warning('%s | %s', error.codigo, error)
        raise


def menu():
    """Presenta las opciones y captura los errores bancarios por tipo."""
    banco = Banco()
    while True:
        print('\n--- BANCO DIGITAL ---')
        print('1. Crear cuenta\n2. Depositar\n3. Retirar\n4. Transferir')
        print('5. Consultar saldo\n6. Bloquear/desbloquear')
        print('7. Ver historial\n8. Salir')
        opcion = input('Elige una opción: ').strip()
        if opcion == '8':
            print('Gracias por usar el banco.')
            break
        try:
            if opcion == '1':
                numero = input('Número de cuenta: ')
                titular = input('Titular: ')
                monto = input('Saldo inicial (0 si no depositas): ')
                banco.crear_cuenta(numero, titular, monto)
                print('Cuenta creada. Total:', Banco.total_cuentas())
            elif opcion == '2':
                banco.obtener_cuenta(input('Cuenta: ')).depositar(input('Monto: '))
                print('Depósito realizado.')
            elif opcion == '3':
                banco.obtener_cuenta(input('Cuenta: ')).retirar(input('Monto: '))
                print('Retiro realizado.')
            elif opcion == '4':
                origen = input('Cuenta origen: ')
                destino = input('Cuenta destino: ')
                banco.transferir(origen, destino, input('Monto: '))
                print('Transferencia realizada.')
            elif opcion == '5':
                cuenta = banco.obtener_cuenta(input('Cuenta: '))
                print(f'Saldo disponible: ${cuenta.consultar_saldo():.2f}')
            elif opcion == '6':
                cuenta = banco.obtener_cuenta(input('Cuenta: '))
                if cuenta._bloqueada:
                    cuenta.desbloquear()
                    print('Cuenta desbloqueada.')
                else:
                    cuenta.bloquear()
                    print('Cuenta bloqueada.')
            elif opcion == '7':
                cuenta = banco.obtener_cuenta(input('Cuenta: '))
                for fecha, tipo, monto, saldo in cuenta.mostrar_historial():
                    print(f'{fecha} | {tipo} | ${monto:.2f} | saldo ${saldo:.2f}')
            else:
                print('Opción no válida. Intenta de nuevo.')
        except SaldoInsuficienteError as error:
            print('No se pudo realizar el movimiento:', error)
            try:
                reportar_error(error)
            except SaldoInsuficienteError:
                pass  # Ya se informó al usuario y quedó registrado.
        except CuentaNoEncontradaError as error:
            print('Revisa el número de cuenta:', error)
            logging.warning('%s | %s', error.codigo, error)
        except CuentaBloqueadaError as error:
            print('Operación no permitida:', error)
            logging.warning('%s | %s', error.codigo, error)
        except MontoInvalidoError as error:
            print('Revisa la cantidad:', error)
            logging.warning('%s | %s', error.codigo, error)
        except LimiteDiarioExcedidoError as error:
            print('No puedes retirar esa cantidad:', error)
            logging.warning('%s | %s', error.codigo, error)
        except BancoError as error:
            print('Aviso:', error)
            logging.warning('%s | %s', error.codigo, error)
        else:
            logging.info('Opción %s completada', opcion)
        finally:
            logging.info('Terminó el intento de operación %s', opcion)


if __name__ == '__main__':
    menu()
