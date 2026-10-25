# Códigos de Ejemplo Modbus TCP - MOD-0007-TCP

Esta carpeta contiene ejemplos de prueba completos y funcionales en **Python** y **C# (.NET)** para validar cada una de las funciones del protocolo **Modbus TCP** implementadas en el módulo industrial **MOD-0007-TCP** (8 Entradas Digitales / 8 Salidas Digitales).

---

## 1. Parámetros de Red por Defecto

| Parámetro | Valor de Fábrica | Notas |
| :--- | :--- | :--- |
| **Dirección IP** | `192.168.100.10` | Configurable vía servidor Web interno |
| **Puerto TCP** | `502` | Puerto estándar Modbus TCP |
| **Unit ID / Slave ID** | `1` | Dirección de esclavo Modbus |
| **Mascara de Subred** | `255.255.255.0` | — |

> [!IMPORTANT]
> Para probar la unidad desde tu computadora, configura la tarjeta de red Ethernet de tu PC con una IP estática en el mismo segmento, por ejemplo:
> - **IP PC:** `192.168.100.50`
> - **Máscara:** `255.255.255.0`
> - **Puerta de enlace:** `192.168.100.1` (o en blanco)

---

## 2. Funciones Modbus Evaluadas en Ambos Archivos

Cada archivo incluye pruebas para los 8 códigos de función soportados:

1. **FC01 (0x01) - Read Coils**:
   - Lee el estado lógico de las 8 Salidas Digitales (Coils `0` a `7` corresponden a DO 1 a DO 8).
2. **FC02 (0x02) - Read Discrete Inputs**:
   - Lee el estado optoacoplado de las 8 Entradas Digitales (Inputs `0` a `7` corresponden a DI 1 a DI 8).
3. **FC03 (0x03) - Read Holding Registers**:
   - Lee registros de retención de 16 bits:
     - Registros `160` a `167`: Estado individual de las entradas DI 1 a DI 8.
     - Registro `178`: Byte consolidado de Salidas Digitales (bits 0-7 = DO 1-8).
     - Registro `179`: Byte consolidado de Entradas Digitales (bits 0-7 = DI 1-8).
     - Registros `192` a `199`: Estado individual de las salidas DO 1 a DO 8.
4. **FC04 (0x04) - Read Input Registers**:
   - Lectura de registros de telemetría / entrada.
5. **FC05 (0x05) - Write Single Coil**:
   - Activa (ON) y desactiva (OFF) una salida digital individual (ej. Coil `0` para DO 1).
6. **FC06 (0x06) - Write Single Register**:
   - Escribe un registro individual de retención (ej. Registro `193` para controlar DO 2).
7. **FC15 (0x0F) - Write Multiple Coils**:
   - Escribe un patrón simultáneo en las 8 salidas digitales mediante bobinas múltiples.
8. **FC16 (0x10) - Write Multiple Registers**:
   - Escribe un bloque continuo de registros de retención (ej. Registros `194` y `195` para DO 3 y DO 4).

---

## 3. Ejecución en Python

### Requisitos Previos
Tener Python 3.8+ instalado. Instalar la librería `pymodbus`:

```bash
pip install -r requirements.txt
```
*(O directamente: `pip install pymodbus`)*

### Ejecución
```bash
python prueba_modbus_tcp.py
```

---

## 4. Ejecución en C# (.NET)

### Opción A: Desde Terminal con .NET SDK
Si tienes el SDK de .NET instalado (.NET 8.0 o superior):

```bash
dotnet restore
dotnet run
```

### Opción B: Con Visual Studio
1. Abre Visual Studio o VS Code.
2. Abre la carpeta o crea una solución apuntando a `PruebaModbusTCP.csproj`.
3. El gestor NuGet restaurará automáticamente el paquete `NModbus`.
4. Presiona **F5** o haz clic en **Iniciar depuración / Run**.

---

## 5. Estructura de Archivos

- [prueba_modbus_tcp.py](file:///d:/Projects/Remote%20IO/MOD-0007-TCP/Manual/codigo%20ejemplo/prueba_modbus_tcp.py): Script de prueba en Python con todas las funciones.
- [requirements.txt](file:///d:/Projects/Remote%20IO/MOD-0007-TCP/Manual/codigo%20ejemplo/requirements.txt): Dependencias de Python (`pymodbus`).
- [PruebaModbusTCP.cs](file:///d:/Projects/Remote%20IO/MOD-0007-TCP/Manual/codigo%20ejemplo/PruebaModbusTCP.cs): Código de prueba en C# con `NModbus`.
- [PruebaModbusTCP.csproj](file:///d:/Projects/Remote%20IO/MOD-0007-TCP/Manual/codigo%20ejemplo/PruebaModbusTCP.csproj): Proyecto de consola para .NET.
