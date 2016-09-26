using System;
using System.Collections.Generic;
using System.Linq;
using System.Net;
using System.Text;

namespace netrs {
    class Program {
        static void Main(string[] args) {
            if (args.Length != 2) {
                return;
            }
            try {
                string url = args[0];
                string save_path = args[1];
                using (var client = new WebClient()) {
                    client.DownloadFile(url, save_path);
                }
            } catch (Exception e) {
                Console.WriteLine(DateTime.Now.ToString() + " >>> " + e.Message);
            }
        }
    }
}
