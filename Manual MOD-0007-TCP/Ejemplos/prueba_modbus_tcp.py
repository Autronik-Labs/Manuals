"""
================================================================================
GUIA DE PRUEBAS MODBUS TCP - MOD-0007-TCP (PYTHON)
================================================================================
Dispositivo: MOD-0007-TCP (8 Entradas Digitales, 8 Salidas Digitales)
Protocolo:   Modbus TCP / IP
Puerto:      502
IP Defecto:  192.168.100.10
Unit ID:     1

Este script demuestra y prueba de forma individual cada uno de los 8 codigos
de funcion Modbus admitidos por el hardware:
  - 0x01 (FC01): Read Coils
  - 0x02 (FC02): Read Discrete Inputs
  - 0x03 (FC03): Read Holding Registers
  - 0x04 (FC04): Read Input Registers
  - 0x05 (FC05): Write Single Coil
  - 0x06 (FC06): Write Single Register
  - 0x0F (FC15): Write Multiple Coils
  - 0x10 (FC16): Write Multiple Registers

Requisitos:
  pip install pymodbus
================================================================================
"""

import sys
import time

try:
    from pymodbus.client import ModbusTcpClient
except ImportError:
    print("[ERROR] La libreria 'pymodbus' no esta instalada.")
    print("        Instalala ejecutando: pip install pymodbus")
    sys.exit(1)


# ==============================================================================
# CONFIGURACION DE CONEXION
# ==============================================================================
MODBUS_IP = "192.168.100.10"  # IP por defecto de fabrica del MOD-0007-TCP
MODBUS_PORT = 502             # Puerto estandar Modbus TCP
SLAVE_ID = 1                  # Unit ID / Node ID del MOD-0007-TCP


def obtener_cliente():
    """Crea y conecta el cliente Modbus TCP."""
    cliente = ModbusTcpClient(host=MODBUS_IP, port=MODBUS_PORT, timeout=3.0)
    if not cliente.connect():
        print(f"[ERROR] No se pudo conectar a {MODBUS_IP}:{MODBUS_PORT}")
        print("        Verifica el cable Ethernet, la IP y que tu PC este en la misma subred (ej: 192.168.100.50).")
        return None
    print(f"[OK] Conectado exitosamente a {MODBUS_IP}:{MODBUS_PORT} (Unit ID: {SLAVE_ID})")
    return cliente


def llamar_modbus(metodo, *args, **kwargs):
    """
    Funcion auxiliar para compatibilidad entre versiones de pymodbus (v2 vs v3).
    Intenta primero con 'slave' y si falla intenta con 'unit'.
    """
    try:
        return metodo(*args, slave=SLAVE_ID, **kwargs)
    except TypeError:
        return metodo(*args, unit=SLAVE_ID, **kwargs)


# ==============================================================================
# PRUEBAS INDIVIDUALES POR CADA CODIGO DE FUNCION
# ==============================================================================

def probar_fc01_read_coils(cliente):
    """
    FC01 (0x01) - READ COILS:
    Lee el estado actual de las 8 Salidas Digitales (DO 1 a DO 8).
    Direcciones: 0x0000 a 0x0007 (Coils 0 a 7).
    """
    print("\n" + "="*70)
    print("1. PROBANDO FC01 (0x01) - Read Coils (Salidas Digitales 1-8)")
    print("="*70)
    
    rr = llamar_modbus(cliente.read_coils, address=0, count=8)
    if rr.isError():
        print(f"   [FALLO] Error en FC01: {rr}")
    else:
        bits = rr.bits[:8]
        print(f"   [EXITO] Lectura de Coils 0-7: {bits}")
        for i, estado in enumerate(bits):
            txt = "ENCENDIDA (ON / 24V)" if estado else "APAGADA (OFF / 0V)"
            print(f"     -> DO {i + 1} (Coil {i}): {txt}")


def probar_fc02_read_discrete_inputs(cliente):
    """
    FC02 (0x02) - READ DISCRETE INPUTS:
    Lee el estado optoacoplado de las 8 Entradas Digitales (DI 1 a DI 8).
    Direcciones: 0x0000 a 0x0007 (Inputs 0 a 7).
    """
    print("\n" + "="*70)
    print("2. PROBANDO FC02 (0x02) - Read Discrete Inputs (Entradas Digitales 1-8)")
    print("="*70)

    rr = llamar_modbus(cliente.read_discrete_inputs, address=0, count=8)
    if rr.isError():
        print(f"   [FALLO] Error en FC02: {rr}")
    else:
        bits = rr.bits[:8]
        print(f"   [EXITO] Lectura de Inputs 0-7: {bits}")
        for i, estado in enumerate(bits):
            txt = "ACTIVA (24V detectados)" if estado else "INACTIVA (0V / Abierta)"
            print(f"     -> DI {i + 1} (Input {i}): {txt}")


def probar_fc03_read_holding_registers(cliente):
    """
    FC03 (0x03) - READ HOLDING REGISTERS:
    Lee registros de configuracion, estado consolidado y E/S.
      - Reg 160-167 (0x00A0..0x00A7): Estado individual DI 1..8
      - Reg 176 (0x00B0): Node ID
      - Reg 178 (0x00B2): Byte consolidado de Salidas Digitales (0-255)
      - Reg 179 (0x00B3): Byte consolidado de Entradas Digitales (0-255)
      - Reg 192-199 (0x00C0..0x00C7): Control/Estado individual DO 1..8
    """
    print("\n" + "="*70)
    print("3. PROBANDO FC03 (0x03) - Read Holding Registers")
    print("="*70)

    # 3.1. Leer Byte consolidado de E/S (Reg 178 y 179)
    rr_bytes = llamar_modbus(cliente.read_holding_registers, address=178, count=2)
    if not rr_bytes.isError():
        do_mask = rr_bytes.registers[0]
        di_mask = rr_bytes.registers[1]
        print(f"   [EXITO] Byte Salidas (Reg 178):  {do_mask} (Hex: 0x{do_mask:02X}, Bin: {bin(do_mask):>10})")
        print(f"   [EXITO] Byte Entradas (Reg 179): {di_mask} (Hex: 0x{di_mask:02X}, Bin: {bin(di_mask):>10})")
    else:
        print(f"   [AVISO] No se pudo leer Reg 178-179: {rr_bytes}")

    # 3.2. Leer Estado individual de las 8 Entradas (Reg 160 a 167)
    rr_di = llamar_modbus(cliente.read_holding_registers, address=160, count=8)
    if not rr_di.isError():
        print(f"   [EXITO] Registros 160-167 (DI 1..8): {rr_di.registers}")
    else:
        print(f"   [AVISO] Fallo al leer Reg 160-167: {rr_di}")


def probar_fc04_read_input_registers(cliente):
    """
    FC04 (0x04) - READ INPUT REGISTERS:
    Lee los registros de entrada analogica / telemetria o estado mapeado.
    """
    print("\n" + "="*70)
    print("4. PROBANDO FC04 (0x04) - Read Input Registers")
    print("="*70)

    rr = llamar_modbus(cliente.read_input_registers, address=0, count=8)
    if rr.isError():
        print(f"   [INFO] Retorno FC04: {rr} (Comun si el equipo mapea todas sus E/S a Holding Registers)")
    else:
        print(f"   [EXITO] Registros de entrada 0-7: {rr.registers}")


def probar_fc05_write_single_coil(cliente):
    """
    FC05 (0x05) - WRITE SINGLE COIL:
    Enciende y apaga una salida individual (por ejemplo, Salida Digital 1 en Coil 0).
    """
    print("\n" + "="*70)
    print("5. PROBANDO FC05 (0x05) - Write Single Coil (Conmutar DO 1)")
    print("="*70)

    coil_dir = 0  # Coil 0 = DO 1

    print(f"   -> Encendiendo DO 1 (Coil {coil_dir}) = TRUE...")
    rr1 = llamar_modbus(cliente.write_coil, address=coil_dir, value=True)
    if rr1.isError():
        print(f"   [FALLO] Error al encender: {rr1}")
    else:
        print("   [EXITO] DO 1 Encendida (LED DO1 del MOD-0007-TCP debe estar activo).")

    time.sleep(1.0)

    print(f"   -> Apagando DO 1 (Coil {coil_dir}) = FALSE...")
    rr2 = llamar_modbus(cliente.write_coil, address=coil_dir, value=False)
    if rr2.isError():
        print(f"   [FALLO] Error al apagar: {rr2}")
    else:
        print("   [EXITO] DO 1 Apagada.")


def probar_fc06_write_single_register(cliente):
    """
    FC06 (0x06) - WRITE SINGLE REGISTER:
    Escribe un valor de 16 bits en un registro de retencion.
    Ejemplo: Encender la Salida 2 escribiendo 1 en el Registro 193 (0x00C1).
    """
    print("\n" + "="*70)
    print("6. PROBANDO FC06 (0x06) - Write Single Register (DO 2 via Reg 193)")
    print("="*70)

    reg_dir = 193  # Registro 193 = DO 2

    print(f"   -> Escribiendo 1 en Reg {reg_dir} (Activar DO 2)...")
    rr1 = llamar_modbus(cliente.write_register, address=reg_dir, value=1)
    if rr1.isError():
        print(f"   [FALLO] Error al escribir registro: {rr1}")
    else:
        print("   [EXITO] Registro 193 actualizado a 1 (DO 2 activada).")

    time.sleep(1.0)

    print(f"   -> Escribiendo 0 en Reg {reg_dir} (Desactivar DO 2)...")
    rr2 = llamar_modbus(cliente.write_register, address=reg_dir, value=0)
    if rr2.isError():
        print(f"   [FALLO] Error al escribir registro: {rr2}")
    else:
        print("   [EXITO] Registro 193 actualizado a 0 (DO 2 desactivada).")


def probar_fc15_write_multiple_coils(cliente):
    """
    FC15 (0x0F) - WRITE MULTIPLE COILS:
    Escribe el estado de multiples bobinas simultaneamente.
    Ejemplo: Generar un patron alternado (1,0,1,0,1,0,1,0) en las 8 salidas.
    """
    print("\n" + "="*70)
    print("7. PROBANDO FC15 (0x0F) - Write Multiple Coils (Patron en DO 1..8)")
    print("="*70)

    patron_on = [True, False, True, False, True, False, True, False]
    print(f"   -> Aplicando patron alternado: {patron_on}")
    rr1 = llamar_modbus(cliente.write_coils, address=0, values=patron_on)
    if rr1.isError():
        print(f"   [FALLO] Error en FC15: {rr1}")
    else:
        print("   [EXITO] Salidas impares encendidas (1, 3, 5, 7).")

    time.sleep(1.5)

    todos_off = [False] * 8
    print(f"   -> Apagando todas las salidas: {todos_off}")
    rr2 = llamar_modbus(cliente.write_coils, address=0, values=todos_off)
    if rr2.isError():
        print(f"   [FALLO] Error al apagar salidas en FC15: {rr2}")
    else:
        print("   [EXITO] Todas las 8 salidas apagadas.")


def probar_fc16_write_multiple_registers(cliente):
    """
    FC16 (0x10) - WRITE MULTIPLE REGISTERS:
    Escribe un bloque de registros de retencion consecutivos.
    Ejemplo: Encender las salidas 3 y 4 escribiendo [1, 1] en Reg 194-195.
    """
    print("\n" + "="*70)
    print("8. PROBANDO FC16 (0x10) - Write Multiple Registers (Reg 194-195: DO 3 y 4)")
    print("="*70)

    # Reg 194 = DO 3, Reg 195 = DO 4
    print("   -> Escribiendo [1, 1] en Reg 194-195 (Activar DO 3 y DO 4)...")
    rr1 = llamar_modbus(cliente.write_registers, address=194, values=[1, 1])
    if rr1.isError():
        print(f"   [FALLO] Error en FC16: {rr1}")
    else:
        print("   [EXITO] Registros 194-195 actualizados a 1.")

    time.sleep(1.5)

    print("   -> Restaurando [0, 0] en Reg 194-195 (Apagar DO 3 y DO 4)...")
    rr2 = llamar_modbus(cliente.write_registers, address=194, values=[0, 0])
    if rr2.isError():
        print(f"   [FALLO] Error al restaurar registros en FC16: {rr2}")
    else:
        print("   [EXITO] Salidas 3 y 4 apagadas correctamente.")


# ==============================================================================
# MENU PRINCIPAL / EJECUCION DE BATERIA DE PRUEBAS
# ==============================================================================

def main():
    print("="*70)
    print("   SUITE DE PRUEBAS MODBUS TCP - MOD-0007-TCP")
    print(f"   Destino: {MODBUS_IP}:{MODBUS_PORT} | Unit ID: {SLAVE_ID}")
    print("="*70)

    cliente = obtener_cliente()
    if not cliente:
        return

    try:
        # Ejecutar secuencialmente cada funcion Modbus soportada
        probar_fc01_read_coils(cliente)
        time.sleep(0.5)

        probar_fc02_read_discrete_inputs(cliente)
        time.sleep(0.5)

        probar_fc03_read_holding_registers(cliente)
        time.sleep(0.5)

        probar_fc04_read_input_registers(cliente)
        time.sleep(0.5)

        probar_fc05_write_single_coil(cliente)
        time.sleep(0.5)

        probar_fc06_write_single_register(cliente)
        time.sleep(0.5)

        probar_fc15_write_multiple_coils(cliente)
        time.sleep(0.5)

        probar_fc16_write_multiple_registers(cliente)

        print("\n" + "="*70)
        print("   TODAS LAS PRUEBAS MODBUS HAN FINALIZADO")
        print("="*70)

    except KeyboardInterrupt:
        print("\n[INFO] Prueba interrumpida por el usuario.")
    except Exception as e:
        print(f"\n[ERROR INESPERADO] {e}")
    finally:
        cliente.close()
        print("[INFO] Conexion Modbus TCP cerrada.")


if __name__ == "__main__":
    main()
