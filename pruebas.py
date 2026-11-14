"""Pruebas sencillas del sistema bancario."""
from banco import (Banco, BancoError, SaldoInsuficienteError,
                   CuentaNoEncontradaError, CuentaBloqueadaError,
                   MontoInvalidoError, LimiteDiarioExcedidoError)


def comprobar(nombre, accion, tipo):
    """Comprueba que una operación provoque el error esperado."""
    try:
        accion()
    except tipo as error:
        print(f'OK - {nombre}: [{error.codigo}] {error}')
    else:
        raise AssertionError(f'No se produjo el error: {nombre}')


banco = Banco()
banco.crear_cuenta('101', 'Ana', 6000)
banco.crear_cuenta('102', 'Luis', 100)
comprobar('Cuenta no encontrada', lambda: banco.obtener_cuenta('999'), CuentaNoEncontradaError)
comprobar('Monto inválido', lambda: banco.obtener_cuenta('101').depositar(-20), MontoInvalidoError)
comprobar('Saldo insuficiente', lambda: banco.obtener_cuenta('102').retirar(200), SaldoInsuficienteError)
comprobar('Límite diario', lambda: banco.obtener_cuenta('101').retirar(5500), LimiteDiarioExcedidoError)
banco.obtener_cuenta('102').bloquear()
comprobar('Cuenta bloqueada', lambda: banco.obtener_cuenta('102').depositar(10), CuentaBloqueadaError)
banco.obtener_cuenta('102').desbloquear()
comprobar('Cuenta duplicada', lambda: banco.crear_cuenta('101', 'Otro', 0), BancoError)
banco.transferir('101', '102', 250)
assert banco.obtener_cuenta('101').saldo == 5750
assert banco.obtener_cuenta('102').saldo == 350
assert Banco.total_cuentas() == 2
print('OK - Transferencia, saldos y total de cuentas.')
print('Todas las pruebas terminaron correctamente.')
