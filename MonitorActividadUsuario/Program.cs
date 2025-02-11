using System;
using System.Diagnostics;
using System.Runtime.InteropServices;
using System.Text;
using System.IO;
using System.Threading.Tasks;
using NodaTime;
using System.Security.Cryptography;
using System.Windows.Forms;
using System.Linq.Expressions;

class Program
{
    private const int MAX_INTENTOS_ERROR = 10;
    private const int INTERVALO_CONSULTA_MS = 1000;
    private const string NOMBRE_APLICACION = "RegistroActividadIntegral";

    private const string CLAVE_BASE64 = "TkA1YTIwMjUq";
    private const string IV_BASE64 = "MzcxNTA4OTg1MDIyMTA0NA==";

    private static readonly byte[] clave = ObtenerClaveDesdeBase64(CLAVE_BASE64);
    private static readonly byte[] iv = ObtenerIVDesdeBase64(IV_BASE64);

    private static readonly DateTimeZone zonaBogota = DateTimeZoneProviders.Tzdb["America/Bogota"];
    private static readonly string usuario = Environment.GetEnvironmentVariable("USERNAME")?.ToUpper() ?? "DESCONOCIDO";
    private static readonly string nombreComputador = Environment.GetEnvironmentVariable("COMPUTERNAME")?.ToUpper() ?? "DESCONOCIDO";
    private static readonly string rutaBase = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.CommonApplicationData), NOMBRE_APLICACION);
    private static readonly string rutaArchivoDatos = Path.Combine(rutaBase, $"{GenerarHash(usuario)}.dll");
    private static readonly string rutaCarpetaLogs = Path.Combine(rutaBase, "logs");
    private static readonly string rutaArchivoLogs = Path.Combine(rutaCarpetaLogs, $"{GenerarHash(usuario)}.log");

    private static DateTime ultimaHoraGuardada = DateTime.MinValue;

    [DllImport("user32.dll")]
    private static extern IntPtr GetForegroundWindow();

    [DllImport("user32.dll")]
    private static extern int GetWindowText(IntPtr hWnd, StringBuilder lpString, int nMaxCount);

    [DllImport("user32.dll")]
    private static extern int GetWindowTextLength(IntPtr hWnd);

    [DllImport("user32.dll")]
    private static extern IntPtr GetWindowThreadProcessId(IntPtr hWnd, out uint lpdwProcessId);

    static async Task Main()
    {
        try
        {
            InicializarArchivo(rutaArchivoDatos);

            int intentosError = 0;
            string ultimaVentanaActiva = string.Empty;
            DateTime ultimoTiempo = DateTime.Now;

            while (intentosError <= MAX_INTENTOS_ERROR)
            {
                try
                {
                    DateTime ahora = DateTime.Now;
                    bool cambioHoraForzado = false;

                    if (EsCambioHoraInminente(ahora, 5))
                    {
                        if (!string.IsNullOrEmpty(ultimaVentanaActiva) &&
                           (ahora - ultimaHoraGuardada).TotalMinutes >= 1)
                        {
                            TimeSpan tiempoUso = ahora - ultimoTiempo;
                            GuardarRegistroCifrado(rutaArchivoDatos, ultimaVentanaActiva, tiempoUso);

                            ultimaHoraGuardada = ahora;
                            ultimoTiempo = ahora;
                            cambioHoraForzado = true;
                        }
                    }

                    if (!cambioHoraForzado)
                    {
                        string ventanaActual = ObtenerVentanaActiva();
                        if (!string.IsNullOrEmpty(ventanaActual) && ventanaActual != ultimaVentanaActiva && !ventanaActual.Contains("Dexon Agent|WerFault"))
                        {
                            if (!string.IsNullOrEmpty(ultimaVentanaActiva))
                            {
                                TimeSpan tiempoUso = ahora - ultimoTiempo;
                                GuardarRegistroCifrado(rutaArchivoDatos, ultimaVentanaActiva, tiempoUso);
                            }
                            ultimaVentanaActiva = ventanaActual;
                            ultimoTiempo = ahora;
                        }
                    }

                    await Task.Delay(INTERVALO_CONSULTA_MS);
                    intentosError = 0;
                }
                catch (Exception e)
                {
                    RegistrarLog("ERROR", $"Excepción en bucle principal: {e.Message}");
                    intentosError++;
                }
            }
        }
        catch (Exception e)
        {
            RegistrarLog("CRÍTICO", $"Error en inicialización: {e.Message}");
        }
    }

    private static void InicializarArchivo(string ruta)
    {
        if (!File.Exists(ruta)) File.WriteAllText(ruta, string.Empty);
    }

    private static bool EsCambioHoraInminente(DateTime ahora, int segundosAnticipacion)
    {
        return ahora.TimeOfDay >= new TimeSpan(ahora.Hour, 59, 60 - segundosAnticipacion)
               && ahora.TimeOfDay < new TimeSpan(ahora.Hour + 1, 0, 0);
    }

    private static void GuardarRegistroCifrado(string rutaArchivo, string ventana, TimeSpan tiempo)
    {
        try
        {
            string[] partesVentana = ventana.Replace(",", "").Replace("\n", "").Replace("\r", "").Split('|');
            ZonedDateTime tiempoActual = SystemClock.Instance.GetCurrentInstant().InZone(zonaBogota);

            string registro = $"{tiempoActual:yyyy-MM-dd HH:mm:ss.ffffff}{tiempoActual.Offset}:00," +
                              $"{nombreComputador},{usuario},{partesVentana[0]},{partesVentana[1]}," +
                              $"{partesVentana[2].Replace("\\", "").Replace(".", "")}," +
                              $"{tiempo.TotalSeconds.ToString("F2", System.Globalization.CultureInfo.InvariantCulture)}";

            string rutaTemporal = rutaArchivo + "_E.tmp";
            DescifrarArchivo(rutaArchivo, rutaTemporal);
            File.AppendAllText(rutaTemporal, registro + Environment.NewLine);

            CifrarArchivo(rutaTemporal, rutaArchivo);
            File.Delete(rutaTemporal);
        }
        catch (Exception e)
        {
            throw new Exception($"Error al guardar registro: {e.Message}");
        }
    }

    private static void CifrarArchivo(string rutaEntrada, string rutaSalida)
    {
        using (Aes aes = Aes.Create())
        using (FileStream fsEntrada = File.OpenRead(rutaEntrada))
        using (FileStream fsSalida = File.Create(rutaSalida))
        using (ICryptoTransform encryptor = aes.CreateEncryptor(clave, iv))
        using (CryptoStream cs = new CryptoStream(fsSalida, encryptor, CryptoStreamMode.Write))
        {
            fsEntrada.CopyTo(cs);
        }
    }

    private static void DescifrarArchivo(string rutaEntrada, string rutaSalida)
    {
        if (!File.Exists(rutaEntrada)) return;

        using (Aes aes = Aes.Create())
        using (FileStream fsEntrada = File.OpenRead(rutaEntrada))
        using (FileStream fsSalida = File.Create(rutaSalida))
        using (ICryptoTransform decryptor = aes.CreateDecryptor(clave, iv))
        using (CryptoStream cs = new CryptoStream(fsEntrada, decryptor, CryptoStreamMode.Read))
        {
            cs.CopyTo(fsSalida);
        }
    }

    private static string ObtenerVentanaActiva()
    {
        IntPtr ventanaActiva = GetForegroundWindow();
        GetWindowThreadProcessId(ventanaActiva, out uint idProceso);

        int longitud = GetWindowTextLength(ventanaActiva);
        StringBuilder titulo = new StringBuilder(longitud + 1);
        GetWindowText(ventanaActiva, titulo, titulo.Capacity);

        Process proceso = Process.GetProcessById((int)idProceso);

        var pantalla = Screen.FromHandle(ventanaActiva);

        return $"{titulo.Replace("|", "")}|{proceso.ProcessName.Replace("|", "")}|{pantalla.DeviceName}";
    }

    private static void RegistrarLog(string estado, string mensaje)
    {
        try
        {
            Directory.CreateDirectory(rutaCarpetaLogs);
            string marcaTiempo = SystemClock.Instance.GetCurrentInstant().InZone(zonaBogota).ToString("yyyy-MM-dd HH:mm:ss.fff", null);
            File.AppendAllText(rutaArchivoLogs, $"{marcaTiempo} | {estado.PadRight(8)} | {mensaje}{Environment.NewLine}");
        }
        catch { }
    }


    private static byte[] ObtenerClaveDesdeBase64(string base64Password)
    {
        byte[] passwordBytes = Convert.FromBase64String(base64Password);
        if (passwordBytes.Length < 32) Array.Resize(ref passwordBytes, 32);
        return passwordBytes;
    }

    private static byte[] ObtenerIVDesdeBase64(string base64IV)
    {
        return Convert.FromBase64String(base64IV);
    }

    private static string GenerarHash(string texto, int longitud = 10)
    {
        using (SHA256 sha256 = SHA256.Create())
        {
            byte[] hash = sha256.ComputeHash(Encoding.UTF8.GetBytes(texto));
            return BitConverter.ToString(hash).Replace("-", "").Substring(0, Math.Min(longitud, 32));
        }
    }
}