# process_manager.py
import subprocess
import time

class ProcessManager:
    def __init__(self, command, timeout=30):
        self.command = command
        self.timeout = timeout
        self.process = None
        self.total_de_registros = 0
        self.tempo_de_carregamento = 0
        self.tempo_de_ordenacao = 0

    def start_process(self):
        self.process = subprocess.Popen(
            self.command,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        ready = False
        start_time = time.time()

        while True:
            line = self.process.stdout.readline().strip()
            if "ok" in line:
                ready = True
                break

            if line:
                if "registros" in line:
                    self.total_de_registros = int(line.replace("registros ", ""))
                    print(f"Total de Registros Carregados: {self.total_de_registros}")
                elif "carregamento" in line:
                    self.tempo_de_carregamento = float(line.replace("carregamento ", ""))
                    print(f"Tempo de Carregamento: {self.tempo_de_carregamento}")
                elif "ordenacao" in line:
                    self.tempo_de_ordenacao = float(line.replace("ordenacao ", ""))
                    print(f"Tempo de Ordenação: {self.tempo_de_ordenacao}")
                else:
                    print(f"C: {line}")

            if time.time() - start_time > self.timeout:
                print("Tempo limite atingido.")
                break

        if not ready:
            print("Falha ao iniciar o programa C.")
            self.terminate_process()

    def send_input(self, data):
        if self.process:
            self.process.stdin.write(data + "\n")
            self.process.stdin.flush()

    def read_line(self):
        if self.process:
            return self.process.stdout.readline().strip()
        return None

    def terminate_process(self):
        if self.process and self.process.poll() is None:
            self.process.terminate()
