using System;
using System.Text;
using System.IO;
using System.Net.Http;
using System.Threading.Tasks;
using System.Linq;
using Newtonsoft.Json;
using System.Net.NetworkInformation;
using System.Security.Cryptography;
using System.Collections.Generic;
using System.Globalization;

class Program
{
    private const int MAX_INTENTOS_ERROR = 10;
    private const int INTERVALO_SINCRONIZACION_MS = 300000;
    private const string HOST_PRUEBA_VPN = "192.168.1.33";
    private const string ENDPOINT_URL = "http://192.168.1.33:8000/registro_actividades";
    private const string NOMBRE_APLICACION = "RegistroActividadIntegral";

    private const string CLAVE_BASE64 = "TkA1YTIwMjUq";
    private const string IV_BASE64 = "MzcxNTA4OTg1MDIyMTA0NA==";

    private static readonly byte[] clave = ObtenerClaveDesdeBase64(CLAVE_BASE64);
    private static readonly byte[] iv = ObtenerIVDesdeBase64(IV_BASE64);

    private static readonly HttpClient clienteHttp = new HttpClient();

    private static readonly string usuario = Environment.GetEnvironmentVariable("USERNAME")?.ToUpper() ?? "DESCONOCIDO";
    private static readonly string rutaBase = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.CommonApplicationData), NOMBRE_APLICACION);
    private static readonly string rutaArchivoDatos = Path.Combine(rutaBase, $"{GenerarHash(usuario)}.dll");
    private static readonly string rutaCarpetaLogs = Path.Combine(rutaBase, "logs");
    private static readonly string rutaArchivoLogs = Path.Combine(rutaCarpetaLogs, $"{GenerarHash(usuario)}.log");
    
    static async Task Main()
    {
        InicializarArchivo(rutaArchivoDatos);
        int intentosError = 0;

        while (intentosError <= MAX_INTENTOS_ERROR)
        {
            try
            {
                if (EstaConectadoVPN()) await EnviarDatosNoSincronizados();
                intentosError = 0;
                await Task.Delay(INTERVALO_SINCRONIZACION_MS);
            }
            catch (Exception e)
            {
                RegistrarLog("ERROR", e.Message);
                intentosError++;
            }
        }
    }
    private static void InicializarArchivo(string ruta)
    {
        if (!File.Exists(ruta)) File.WriteAllText(ruta, string.Empty);
    }

    private static bool EstaConectadoVPN()
    {
        try
        {
            using (var ping = new Ping())
            {
                PingReply respuesta = ping.Send(HOST_PRUEBA_VPN, 1000);
                return respuesta.Status == IPStatus.Success;
            }
        }
        catch (Exception e)
        {
            RegistrarLog("ERROR", $"Error inesperado al hacer ping: {e.Message}");
            return false;
        }
    }

    private static List<string> LeerRegistrosCifrados()
    {
        try
        {
            string rutaTemporal = rutaArchivoDatos + "_L.tmp";
            DescifrarArchivo(rutaArchivoDatos, rutaTemporal);
            var registros = File.ReadAllLines(rutaTemporal).ToList();
            File.Delete(rutaTemporal);
            return registros;
        }
        catch (Exception e)
        {
            throw new Exception($"Leer registros cifrados: {e.Message}");
        }
    }

    private static async Task EnviarDatosNoSincronizados()
    {
        List<string> registros = LeerRegistrosCifrados();
        if (registros.Count == 0) return;
        var datosParaEnviar = registros.Select(l => l.Split(',')).Select(partes => new
        {
            timestamp = partes[0],
            nombre_computador = partes[1],
            usuario = partes[2],
            titulo_ventana = partes[3],
            nombre_proceso = partes[4],
            pantalla = partes[5],
            segundos_empleados = double.Parse(partes[6], CultureInfo.InvariantCulture)
        }).ToList();

        string json = JsonConvert.SerializeObject(datosParaEnviar);
        HttpResponseMessage respuesta = await clienteHttp.PostAsync(ENDPOINT_URL, new StringContent(json, Encoding.UTF8, "application/json"));
        if (respuesta.IsSuccessStatusCode) File.WriteAllText(rutaArchivoDatos, string.Empty);
        else
        {
            RegistrarLog("ERROR", $"Fallo en sincronización. Estado: {respuesta.StatusCode}, Respuesta: {await respuesta.Content.ReadAsStringAsync()}");
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

    private static void RegistrarLog(string estado, string mensaje)
    {
        try
        {
            string marcaTiempo = DateTime.Now.ToString("yyyy-MM-dd HH:mm:ss");
            File.AppendAllText(rutaArchivoLogs, $"{marcaTiempo} - {estado}: {mensaje}{Environment.NewLine}");
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