# Actividad 2 - Sistema bancario

Programa en Python para practicar excepciones personalizadas.

## Cómo ejecutar

1. Instalar Python 3.10 o posterior.
2. Abrir esta carpeta en Visual Studio Code.
3. Ejecutar `python banco.py` desde la terminal (en Windows también puede funcionar `py banco.py`).
4. Elegir una opción del 1 al 8.

## Funciones

Crear cuentas, depositar, retirar, transferir, consultar saldo, bloquear o desbloquear y ver el historial. Se usa `Decimal` para representar cantidades monetarias. El límite de retiros y transferencias salientes es de $5,000 por cuenta y día. Los errores se registran en `errores_banco.log`.

## Errores personalizados

`BancoError`, `SaldoInsuficienteError`, `CuentaNoEncontradaError`, `CuentaBloqueadaError`, `MontoInvalidoError` y `LimiteDiarioExcedidoError`.

## Pruebas

Ejecutar `python pruebas.py` para comprobar las excepciones y las operaciones principales.

## Repositorio

Pegar aquí la URL del repositorio público de GitHub una vez que se haya publicado.
