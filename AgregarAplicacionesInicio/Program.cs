using Microsoft.Win32;
using System;
using System.IO;

namespace AgregarAplicacionesInicio
{
    internal class Program
    {

        private static string nombreAplicacionMonitor = "MonitorActividadUsuario";
        private static string nombreAplicacionSincronizador = "SincronizadorDatos";
        private static string nombreAplicacion = "RegistroActividadIntegral";
        private static string claveInicio = @"Software\Microsoft\Windows\CurrentVersion\Run";
        private static string rutaBase = Environment.GetEnvironmentVariable("ProgramData").Replace('\\', '/') + "/" + nombreAplicacion + "/";
        private static string rutaCarpetaLogs = rutaBase + "logs/";
        private static string rutaArchivoLogs = rutaCarpetaLogs + nombreAplicacion + ".log";
        private static string rutaEjecutableMonitor = AppDomain.CurrentDomain.BaseDirectory + nombreAplicacionMonitor + ".exe";
        private static string rutaEjecutableCopiaMonitor = rutaBase + nombreAplicacionMonitor + ".exe";
        private static string rutaEjecutableSincronizador = AppDomain.CurrentDomain.BaseDirectory + nombreAplicacionSincronizador + ".exe";
        private static string rutaEjecutableCopiaSincronizador = rutaBase + nombreAplicacionSincronizador + ".exe";
        static void Main(string[] args)
        {
            try
            {
                AsegurarDirectorioExiste(rutaBase);
                AsegurarDirectorioExiste(rutaCarpetaLogs);
                File.Copy(rutaEjecutableMonitor, rutaEjecutableCopiaMonitor, true);
                File.Copy(rutaEjecutableSincronizador, rutaEjecutableCopiaSincronizador, true);
                using (RegistryKey clave = Registry.LocalMachine.OpenSubKey(claveInicio, true))
                {
                    if (clave != null)
                    {
                        string valorActualMonitor = clave.GetValue(nombreAplicacionMonitor) as string;
                        if (valorActualMonitor != rutaEjecutableCopiaMonitor) clave.SetValue(nombreAplicacionMonitor, $"\"{rutaEjecutableCopiaMonitor.Replace('/', '\\')}\"");
                        string valorActual = clave.GetValue(nombreAplicacionSincronizador) as string;
                        if (valorActual != rutaEjecutableCopiaSincronizador) clave.SetValue(nombreAplicacionSincronizador, $"\"{rutaEjecutableCopiaSincronizador.Replace('/', '\\')}\"");
                    }
                    else throw new Exception("No se pudo acceder a la clave del registro.");
                }
            }
            catch (Exception e)
            {
                RegistrarLog("Error", "No se pudo agrergar las aplicaciones de inicio:" + e.Message);
            }
        }

        private static void RegistrarLog(string estado, string mensaje)
        {
            string marcaTiempo = DateTime.Now.ToString("yyyy-MM-dd HH:mm:ss");
            File.AppendAllText(rutaArchivoLogs, $"{marcaTiempo} - {estado}: {mensaje}{Environment.NewLine}");
        }

        private static void AsegurarDirectorioExiste(string ruta)
        {
            if (!Directory.Exists(ruta)) Directory.CreateDirectory(ruta);
        }
    }
}
