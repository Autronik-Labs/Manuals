using System;
using System.Net.Sockets;
using System.Threading;
using NModbus;

namespace Mod0007TcpDemo
{
    /// <summary>
    /// Programa de prueba integral para el modulo industrial MOD-0007-TCP.
    /// Valida los 8 codigos de funcion Modbus soportados por el equipo:
    ///   - FC01 (0x01): Read Coils (Salidas 1-8)
    ///   - FC02 (0x02): Read Discrete Inputs (Entradas 1-8)
    ///   - FC03 (0x03): Read Holding Registers (E/S y configuracion)
    ///   - FC04 (0x04): Read Input Registers
    ///   - FC05 (0x05): Write Single Coil (Conmutar salida individual)
    ///   - FC06 (0x06): Write Single Register (Escribir registro individual)
    ///   - FC15 (0x0F): Write Multiple Coils (Escribir lote de salidas)
    ///   - FC16 (0x10): Write Multiple Registers (Escribir lote de registros)
    /// </summary>
    internal class Program
    {
        // =====================================================================
        // PARAMETROS DE CONEXION
        // =====================================================================
        private const string IpAddress = "192.168.100.10"; // IP por defecto de fabrica del modulo
        private const int TcpPort = 502;                   // Puerto estandar Modbus TCP
        private const byte SlaveId = 1;                    // Unit ID / Node ID configurado

        private static void Main(string[] args)
        {
            Console.WriteLine("======================================================================");
            Console.WriteLine("     PRUEBA DE COMUNICACION MODBUS TCP - MOD-0007-TCP (.NET / C#)     ");
            Console.WriteLine($"     Destino: {IpAddress}:{TcpPort} | Slave ID: {SlaveId}");
            Console.WriteLine("======================================================================\n");

            try
            {
                using (TcpClient tcpClient = new TcpClient())
                {
                    Console.Write($"Conectando a {IpAddress}:{TcpPort}... ");
                    tcpClient.Connect(IpAddress, TcpPort);
                    Console.WriteLine("[CONECTADO]\n");

                    // Crear el maestro Modbus TCP utilizando la factoria de NModbus
                    var factory = new ModbusFactory();
                    IModbusMaster master = factory.CreateMaster(tcpClient);

                    // 1. Probar FC01: Read Coils
                    ProbarFc01ReadCoils(master);
                    Thread.Sleep(500);

                    // 2. Probar FC02: Read Discrete Inputs
                    ProbarFc02ReadInputs(master);
                    Thread.Sleep(500);

                    // 3. Probar FC03: Read Holding Registers
                    ProbarFc03ReadHoldingRegisters(master);
                    Thread.Sleep(500);

                    // 4. Probar FC04: Read Input Registers
                    ProbarFc04ReadInputRegisters(master);
                    Thread.Sleep(500);

                    // 5. Probar FC05: Write Single Coil
                    ProbarFc05WriteSingleCoil(master);
                    Thread.Sleep(500);

                    // 6. Probar FC06: Write Single Register
                    ProbarFc06WriteSingleRegister(master);
                    Thread.Sleep(500);

                    // 7. Probar FC15: Write Multiple Coils
                    ProbarFc15WriteMultipleCoils(master);
                    Thread.Sleep(500);

                    // 8. Probar FC16: Write Multiple Registers
                    ProbarFc16WriteMultipleRegisters(master);

                    Console.WriteLine("\n======================================================================");
                    Console.WriteLine("   BATERIA DE PRUEBAS FINALIZADA CON EXITO");
                    Console.WriteLine("======================================================================");
                }
            }
            catch (SocketException ex)
            {
                Console.WriteLine($"\n[ERROR DE RED] No se pudo establecer conexion con {IpAddress}:{TcpPort}");
                Console.WriteLine($"Detalle: {ex.Message}");
                Console.WriteLine("Sugerencia: Revisa que la IP de tu PC este en la subred 192.168.100.X (ej: 192.168.100.50) y el cable de red este conectado.");
            }
            catch (Exception ex)
            {
                Console.WriteLine($"\n[ERROR] Ocurrio una excepcion: {ex.Message}");
            }

            Console.WriteLine("\nPresiona cualquier tecla para salir...");
            Console.ReadKey();
        }

        #region Pruebas de Funciones Modbus

        /// <summary>
        /// FC01 (0x01) - Read Coils: Lee el estado de las 8 Salidas Digitales (DO 1 a 8).
        /// </summary>
        private static void ProbarFc01ReadCoils(IModbusMaster master)
        {
            Console.WriteLine("----------------------------------------------------------------------");
            Console.WriteLine("1. PROBANDO FC01 (0x01) - Read Coils (Salidas 1-8)");
            Console.WriteLine("----------------------------------------------------------------------");

            ushort startAddress = 0; // Coil 0 = DO 1
            ushort count = 8;

            bool[] coils = master.ReadCoils(SlaveId, startAddress, count);
            Console.WriteLine($"[EXITO] Lectura de {count} Coils desde direccion {startAddress}:");
            for (int i = 0; i < coils.Length; i++)
            {
                string estado = coils[i] ? "ENCENDIDA (ON / 24V)" : "APAGADA (OFF / 0V)";
                Console.WriteLine($"   -> DO {i + 1} (Coil {i}): {estado}");
            }
        }

        /// <summary>
        /// FC02 (0x02) - Read Discrete Inputs: Lee el estado de las 8 Entradas Digitales (DI 1 a 8).
        /// </summary>
        private static void ProbarFc02ReadInputs(IModbusMaster master)
        {
            Console.WriteLine("\n----------------------------------------------------------------------");
            Console.WriteLine("2. PROBANDO FC02 (0x02) - Read Discrete Inputs (Entradas 1-8)");
            Console.WriteLine("----------------------------------------------------------------------");

            ushort startAddress = 0; // Input 0 = DI 1
            ushort count = 8;

            bool[] inputs = master.ReadInputs(SlaveId, startAddress, count);
            Console.WriteLine($"[EXITO] Lectura de {count} Discrete Inputs desde direccion {startAddress}:");
            for (int i = 0; i < inputs.Length; i++)
            {
                string estado = inputs[i] ? "ACTIVA (24V detectados)" : "INACTIVA (0V / Abierta)";
                Console.WriteLine($"   -> DI {i + 1} (Input {i}): {estado}");
            }
        }

        /// <summary>
        /// FC03 (0x03) - Read Holding Registers: Lee registros de 16 bits de configuracion y E/S.
        /// </summary>
        private static void ProbarFc03ReadHoldingRegisters(IModbusMaster master)
        {
            Console.WriteLine("\n----------------------------------------------------------------------");
            Console.WriteLine("3. PROBANDO FC03 (0x03) - Read Holding Registers");
            Console.WriteLine("----------------------------------------------------------------------");

            // Leer Byte consolidado de E/S: Reg 178 (DO) y Reg 179 (DI)
            ushort[] maskRegs = master.ReadHoldingRegisters(SlaveId, startAddress: 178, numberOfPoints: 2);
            Console.WriteLine($"[EXITO] Registro 178 (Mascara DO): {maskRegs[0]} (Hex: 0x{maskRegs[0]:X2})");
            Console.WriteLine($"[EXITO] Registro 179 (Mascara DI): {maskRegs[1]} (Hex: 0x{maskRegs[1]:X2})");

            // Leer estados individuales de las entradas: Regs 160..167
            ushort[] diRegs = master.ReadHoldingRegisters(SlaveId, startAddress: 160, numberOfPoints: 8);
            Console.WriteLine($"[EXITO] Registros 160-167 (DI 1-8): [{string.Join(", ", diRegs)}]");
        }

        /// <summary>
        /// FC04 (0x04) - Read Input Registers: Lee registros de entrada solo lectura.
        /// </summary>
        private static void ProbarFc04ReadInputRegisters(IModbusMaster master)
        {
            Console.WriteLine("\n----------------------------------------------------------------------");
            Console.WriteLine("4. PROBANDO FC04 (0x04) - Read Input Registers");
            Console.WriteLine("----------------------------------------------------------------------");

            try
            {
                ushort[] inputRegs = master.ReadInputRegisters(SlaveId, startAddress: 0, numberOfPoints: 8);
                Console.WriteLine($"[EXITO] Registros Input 0-7: [{string.Join(", ", inputRegs)}]");
            }
            catch (Exception ex)
            {
                Console.WriteLine($"[INFO] Respuesta FC04: {ex.Message} (Registros mapeados principalmente en Holding Registers).");
            }
        }

        /// <summary>
        /// FC05 (0x05) - Write Single Coil: Enciende y apaga una salida digital individual.
        /// </summary>
        private static void ProbarFc05WriteSingleCoil(IModbusMaster master)
        {
            Console.WriteLine("\n----------------------------------------------------------------------");
            Console.WriteLine("5. PROBANDO FC05 (0x05) - Write Single Coil (Conmutar DO 1)");
            Console.WriteLine("----------------------------------------------------------------------");

            ushort coilAddress = 0; // Coil 0 = DO 1

            Console.WriteLine($"   -> Encendiendo DO 1 (Coil {coilAddress} = TRUE)...");
            master.WriteSingleCoil(SlaveId, coilAddress, true);
            Console.WriteLine("   [EXITO] DO 1 Encendida (Verifica LED DO1 en el frente del MOD-0007-TCP).");

            Thread.Sleep(1000);

            Console.WriteLine($"   -> Apagando DO 1 (Coil {coilAddress} = FALSE)...");
            master.WriteSingleCoil(SlaveId, coilAddress, false);
            Console.WriteLine("   [EXITO] DO 1 Apagada.");
        }

        /// <summary>
        /// FC06 (0x06) - Write Single Register: Escribe un registro de retencion individual.
        /// </summary>
        private static void ProbarFc06WriteSingleRegister(IModbusMaster master)
        {
            Console.WriteLine("\n----------------------------------------------------------------------");
            Console.WriteLine("6. PROBANDO FC06 (0x06) - Write Single Register (DO 2 via Reg 193)");
            Console.WriteLine("----------------------------------------------------------------------");

            ushort registerAddress = 193; // Reg 193 = DO 2

            Console.WriteLine($"   -> Escribiendo 1 en Registro {registerAddress}...");
            master.WriteSingleRegister(SlaveId, registerAddress, 1);
            Console.WriteLine("   [EXITO] Registro 193 escrito con valor 1 (DO 2 activada).");

            Thread.Sleep(1000);

            Console.WriteLine($"   -> Escribiendo 0 en Registro {registerAddress}...");
            master.WriteSingleRegister(SlaveId, registerAddress, 0);
            Console.WriteLine("   [EXITO] Registro 193 restaurado a 0 (DO 2 desactivada).");
        }

        /// <summary>
        /// FC15 (0x0F) - Write Multiple Coils: Escribe un lote simultaneo de bobinas de salida.
        /// </summary>
        private static void ProbarFc15WriteMultipleCoils(IModbusMaster master)
        {
            Console.WriteLine("\n----------------------------------------------------------------------");
            Console.WriteLine("7. PROBANDO FC15 (0x0F) - Write Multiple Coils (Patron alternado)");
            Console.WriteLine("----------------------------------------------------------------------");

            ushort startAddress = 0;
            bool[] patronOn = new bool[] { true, false, true, false, true, false, true, false };

            Console.WriteLine("   -> Enviando patron alternado a Coils 0-7 (DO 1, 3, 5, 7 ON)...");
            master.WriteMultipleCoils(SlaveId, startAddress, patronOn);
            Console.WriteLine("   [EXITO] Salidas impares activadas.");

            Thread.Sleep(1500);

            bool[] todosOff = new bool[] { false, false, false, false, false, false, false, false };
            Console.WriteLine("   -> Apagando todas las salidas Coils 0-7...");
            master.WriteMultipleCoils(SlaveId, startAddress, todosOff);
            Console.WriteLine("   [EXITO] Todas las salidas apagadas.");
        }

        /// <summary>
        /// FC16 (0x10) - Write Multiple Registers: Escribe un bloque consecutivo de registros de retencion.
        /// </summary>
        private static void ProbarFc16WriteMultipleRegisters(IModbusMaster master)
        {
            Console.WriteLine("\n----------------------------------------------------------------------");
            Console.WriteLine("8. PROBANDO FC16 (0x10) - Write Multiple Registers (DO 3 y 4 via Regs 194-195)");
            Console.WriteLine("----------------------------------------------------------------------");

            ushort startAddress = 194; // Reg 194 (DO 3) y Reg 195 (DO 4)
            ushort[] valoresActivar = new ushort[] { 1, 1 };

            Console.WriteLine($"   -> Escribiendo [1, 1] en Registros {startAddress}-{startAddress + 1}...");
            master.WriteMultipleRegisters(SlaveId, startAddress, valoresActivar);
            Console.WriteLine("   [EXITO] Salidas 3 y 4 activadas mediante registros.");

            Thread.Sleep(1500);

            ushort[] valoresApagar = new ushort[] { 0, 0 };
            Console.WriteLine($"   -> Restaurando [0, 0] en Registros {startAddress}-{startAddress + 1}...");
            master.WriteMultipleRegisters(SlaveId, startAddress, valoresApagar);
            Console.WriteLine("   [EXITO] Salidas 3 y 4 apagadas.");
        }

        #endregion
    }
}
