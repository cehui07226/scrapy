using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.IO;
using System.Diagnostics;

namespace bin2rnx {
    class Program {
        static void Main(string[] args) {
            if (args.Length != 2) {
                return;
            } else {
                string bin_path = args[0];
                string dat_path = args[1];
                try {
                    bin2dat(bin_path, dat_path);
                    dat2rnx(dat_path);
                } catch (Exception e) {
                    Console.WriteLine(e.Message);
                }
            }
        }
        static void dat2rnx(string dat_path) {
            
            if (!File.Exists(dat_path)) {
                return;
            }
            using (Process process = new Process()) {
                string dat2rnx_path = Path.Combine(Environment.CurrentDirectory, "dat2rnx.exe");
                process.StartInfo.FileName = dat2rnx_path;
                process.StartInfo.UseShellExecute = false;
                process.StartInfo.RedirectStandardInput = true;
                process.StartInfo.RedirectStandardOutput = true;
                process.StartInfo.RedirectStandardError = true;
                process.StartInfo.CreateNoWindow = true;
                process.StartInfo.Arguments = "-rCORS -oCORS -ACORS -aGZ " + dat_path;
                process.OutputDataReceived += Process_OutputDataReceived;
                process.ErrorDataReceived += Process_ErrorDataReceived;
                process.Start();
                process.BeginOutputReadLine();
                process.BeginErrorReadLine();
                process.WaitForExit(15 * 1000);
                try {
                    process.Kill();
                } catch (Exception) {
                    Console.WriteLine("Force to exit");
                }
            }
        }

        static void bin2dat(string bin_path, string dat_path) {
            if (!File.Exists(bin_path)) {
                return;
            }
            using (Process process = new Process()) {
                string runpk_path = Path.Combine(Environment.CurrentDirectory, "runpkr.exe");
                process.StartInfo.FileName = runpk_path;
                process.StartInfo.UseShellExecute = false;
                process.StartInfo.RedirectStandardInput = true;
                process.StartInfo.RedirectStandardOutput = true;
                process.StartInfo.RedirectStandardError = true;
                process.StartInfo.CreateNoWindow = true;
                process.StartInfo.Arguments = "-dv " + bin_path + " " + dat_path;
                process.OutputDataReceived += Process_OutputDataReceived;
                process.ErrorDataReceived += Process_ErrorDataReceived;
                process.Start();
                process.BeginOutputReadLine();
                process.BeginErrorReadLine();
                process.WaitForExit(15 * 1000);
                try {
                    process.Kill();
                } catch (Exception) {
                    Console.WriteLine("Force to exit");
                }
            }
        }

        private static void Process_ErrorDataReceived(object sender, DataReceivedEventArgs e) {
            Console.WriteLine(e.Data);
        }

        private static void Process_OutputDataReceived(object sender, DataReceivedEventArgs e) {
            Console.WriteLine(e.Data);
        }
    }
}
