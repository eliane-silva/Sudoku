import subprocess
import time
import tkinter as tk
from tkinter import messagebox

process = None

try:
    # Janela de aviso inicial
    loading_root = tk.Tk()
    loading_root.title("Carregando")
    tk.Label(
        loading_root, text="O programa está carregando, por favor aguarde..."
    ).pack(padx=20, pady=10)
    loading_root.update()

    process = subprocess.Popen(
        ["./program"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    ready = False
    timeout = 30
    start_time = time.time()

    total_de_registros = 0
    tempo_de_carregamento = 0
    tempo_de_ordenacao = 0
    tempo_de_busca_nanossegundos = 0
    total_de_operacoes = 0
    jogo_respondido = ""

    while True:
        linha = process.stdout.readline().strip()
        if "ok" in linha:
            ready = True
            break

        if linha:
            if "registros" in linha:
                total_de_registros = int(linha.replace("registros ", ""))
                print(f"Total de Registros Carregados: {total_de_registros}")
            elif "carregamento" in linha:
                tempo_de_carregamento = float(linha.replace("carregamento ", ""))
                print(f"Tempo de Carregamento: {tempo_de_carregamento}")
            elif "ordenacao" in linha:
                tempo_de_ordenacao = float(linha.replace("ordenacao ", ""))
                print(f"Tempo de Ordenação: {tempo_de_ordenacao}")
            else:
                print(f"C: {linha}")

        if time.time() - start_time > timeout:
            print("Tempo limite atingido.")
            break

    if not ready:
        print("Falha ao iniciar o programa C.")
        process.terminate()

    def formatar_sudoku(jogo):
        """Formata os 81 dígitos em uma grade 9x9"""
        grid = [[int(jogo[i * 9 + j]) for j in range(9)] for i in range(9)]
        return grid

    def limpar_sudoku():
        for widget in sudoku_frame.winfo_children():
            widget.destroy()

    def mostrar_sudoku(grid):
        limpar_sudoku()
        for i in range(9):
            for j in range(9):
                # Configura bordas extras entre blocos 3x3
                border_top = 6 if i in [0, 3, 6] else 1
                border_left = 6 if j in [0, 3, 6] else 1
                border_bottom = 6 if i == 8 else 1
                border_right = 6 if j == 8 else 1

                cell = tk.Label(
                    sudoku_frame,
                    text=str(grid[i][j]),
                    borderwidth=1,
                    relief="solid",
                    width=3,
                    height=1,
                )
                cell.grid(
                    row=i,
                    column=j,
                    padx=(border_left, border_right),
                    pady=(border_top, border_bottom),
                )

    loading_root.destroy()

    root = tk.Tk()
    root.title("Sudoku")
    root.geometry("800x600")
    root.minsize(800, 600)

    def fechar_janela():
        # Janela de aviso ao fechar
        closing_root = tk.Toplevel(root)
        closing_root.title("Fechando")
        tk.Label(closing_root, text="O programa está encerrando, por favor aguarde...").pack(padx=20, pady=10)
        closing_root.update()

        if process is not None and process.poll() is None:
            process.stdin.write("\n")
            process.stdin.flush()

            linha = process.stdout.readline().strip()
            if "Programa em C finalizado" in linha:
                print("Programa C fechando corretamente.")
            else:
                print("Falha ao fechar corretamente.")

            process.terminate()

        # Fecha a janela de aviso de encerramento e a principal
        closing_root.destroy()
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", fechar_janela)

    instrucao_label = tk.Label(root, text="Digite um jogo (81 dígitos):")
    instrucao_label.pack(pady=10)

    entry = tk.Entry(root, width=81)
    entry.pack(pady=10)

    def mostrar_resultado():
        entrada = entry.get()
        if len(entrada) == 81:
            process.stdin.write(entrada + "\n")
            process.stdin.flush()
        else:
            messagebox.showerror("Erro", "Entrada inválida, deve ter 81 caracteres.")
            entry.delete(0, tk.END)
            return

        entry.delete(0, tk.END)
        linha = process.stdout.readline().strip()
        if "jogo nao encontrado" in linha:
            resultado_label.config(text=linha)
            limpar_sudoku()
        else:
            global tempo_de_busca_nanossegundos, total_de_operacoes, jogo_respondido
            tempo_de_busca_nanossegundos = int(linha)
            total_de_operacoes = int(process.stdout.readline().strip())
            jogo_respondido = "".join(
                [process.stdout.readline().strip() for _ in range(9)]
            )

            grid = formatar_sudoku(jogo_respondido)
            resultado_label.config(
                text=f"Tempo da Busca: {tempo_de_busca_nanossegundos} nanossegundos.\nTotal de Operações: {total_de_operacoes}."
            )
            mostrar_sudoku(grid)

    # Botão para calcular o resultado
    achar_button = tk.Button(root, text="Achar Resultado", command=mostrar_resultado)
    achar_button.pack(pady=10)

    # Label onde o resultado será mostrado
    texto = f"Total de Registros: {total_de_registros}\n"
    texto += f"Tempo de Carregamento: {tempo_de_carregamento}\n"
    texto += f"Tempo de Ordenação: {tempo_de_ordenacao}\n"

    resultado_label = tk.Label(root, text=texto)
    resultado_label.pack(pady=10)

    resultado_label = tk.Label(root, text="")
    resultado_label.pack(pady=10)

    sudoku_frame = tk.Frame(root)
    sudoku_frame.pack(pady=10)

    root.mainloop()

except Exception as e:
    print(f"Ocorreu um erro: {e}")
