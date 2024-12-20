# ELIANE SANTOS SILVA
# KLAYVERT DE ANDRADE ARAUJO
# LUCAS RONDINELI LUCENA

import subprocess
import time
import tkinter as tk
from tkinter import messagebox

process = None

try:
    loading_root = tk.Tk()
    loading_root.title("Carregando")
    tk.Label(
        loading_root, text="O programa está carregando, por favor aguarde...",
        bg="lightblue"
    ).pack(padx=20, pady=10)
    loading_root.configure(bg="lightblue")
    loading_root.update()

    process = subprocess.Popen(
        ["./program.exe"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
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
        return [[int(jogo[i * 9 + j]) for j in range(9)] for i in range(9)]

    def limpar_sudoku():
        for widget in sudoku_frame.winfo_children():
            widget.destroy()

    def mostrar_sudoku(grid, interativo=False):
        limpar_sudoku() 
        global cell_widgets
        cell_widgets = [[None for _ in range(9)] for _ in range(9)]  # Cria uma matriz para armazenar os widgets de célula

        for i in range(9):
            for j in range(9):
                valor = grid[i][j]
                
                border_top = 6 if i in [0, 3, 6] else 1
                border_left = 6 if j in [0, 3, 6] else 1
                border_bottom = 6 if i == 8 else 1
                border_right = 6 if j == 8 else 1

                if interativo and valor == 0:
                    # Cria uma célula editável para valores 0
                    cell = tk.Entry(
                        sudoku_frame,
                        width=3,
                        justify='center',
                        font=("Arial", 14),
                        relief="solid",
                        borderwidth=1
                    )
                    cell.grid(
                        row=i,
                        column=j,
                        padx=(border_left, border_right),
                        pady=(border_top, border_bottom)
                    )
                    cell.bind("<FocusOut>", lambda e, x=i, y=j: validar_campo(e, x, y))  # Validação ao sair do campo
                    cell_widgets[i][j] = cell
                else:
                    # Cria uma célula fixa (Label) para valores diferentes de 0
                    cell = tk.Label(
                        sudoku_frame,
                        text=str(valor) if valor != 0 else "",
                        borderwidth=1,
                        relief="solid",
                        width=3,
                        height=1,
                        bg="lightgray",
                        font=("Arial", 14)
                    )
                    cell.grid(
                        row=i,
                        column=j,
                        padx=(border_left, border_right),
                        pady=(border_top, border_bottom)
                    )
                    cell_widgets[i][j] = cell

    def validar_campo(event, x, y):
        cell = cell_widgets[x][y]
        valor = cell.get().strip()
        
        if valor == "":
            cell.config(bg="white")
            return
        
        if not valor.isdigit() or not (1 <= int(valor) <= 9):
            cell.config(bg="red")
        elif int(valor) == solution[x][y]:
            cell.config(bg="green")
        else:
            cell.config(bg="red")

    def mostrar_resultado():
        entrada = entry.get()
        remover_botao_dica()
        if len(entrada) == 81:
            process.stdin.write(entrada + "\n")
            process.stdin.flush()
        elif len(entrada) == 0:
            print("Saindo...")
            return
        else:
            print("Entrada inválida, deve ter 81 caracteres.")
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
            jogo_respondido = "".join([process.stdout.readline().strip() for _ in range(9)])
            
            grid = formatar_sudoku(jogo_respondido)
            resultado_label.config(
                text=f"Tempo da Busca: {tempo_de_busca_nanossegundos} nanossegundos.\nTotal de Operações: {total_de_operacoes}.")
            mostrar_sudoku(grid)
        
        if process.poll() is not None:
            return 

    def buscar_jogo():
        entrada = entry.get()
        if len(entrada) != 81 or not entrada.isdigit():
            messagebox.showerror("Erro", "Entrada inválida. Digite 81 dígitos (0 a 9).")
            return

        try:
            process = subprocess.Popen(
                ['./buscar_puzzle'],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            output, error = process.communicate(input=entrada)

            if error:
                raise RuntimeError(error.strip())

            linhas = output.strip().split("\n")
            if "jogo nao encontrado" in linhas[0]:
                messagebox.showerror("Erro", "Jogo não encontrado no arquivo.")
                limpar_sudoku()
            else:
                global solution
                # Atualiza a solução e o grid
                puzzle, solution_str = linhas  # Recebe o puzzle e a solução
                solution = [[int(solution_str[i * 9 + j]) for j in range(9)] for i in range(9)]
                mostrar_sudoku(
                    [[int(puzzle[i * 9 + j]) for j in range(9)] for i in range(9)], 
                    interativo=True
                )
                resultado_label.config(text="Puzzle carregado com sucesso.")
                adicionar_botao_dica()

        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao executar o subprocesso: {e}")

    def adicionar_botao_dica():
        global dica_button
        if 'dica_button' not in globals() or not dica_button.winfo_exists():
            dica_button = tk.Button(root, text="Dica", command=dar_dica)
            dica_button.pack(pady=10)

    def remover_botao_dica():
        global dica_button
        if 'dica_button' in globals() and dica_button.winfo_exists():
            dica_button.destroy()
            del dica_button

    def dar_dica():
        # Percorrer o grid e procurar uma célula vazia (valor 0 ou "")
        for i in range(9):
            for j in range(9):
                cell = cell_widgets[i][j]
                if isinstance(cell, tk.Entry) and cell.get() == "":
                    # Preencher o campo vazio com a solução
                    valor_solução = solution[i][j]
                    cell.insert(0, str(valor_solução))  
                    cell.config(bg="yellow")  
                    return
                elif isinstance(cell, tk.Label) and cell.cget("text") == "":  # Verifica se é uma célula de Label vazia
                    # Preencher a Label com a solução
                    valor_solução = solution[i][j]
                    cell.config(text=str(valor_solução))  
                    cell.config(bg="yellow")  # Cor para indicar que foi dado uma dica
                    return

        messagebox.showinfo("Dica", "Não há mais campos vazios para preencher.")

    loading_root.destroy()
    
    root = tk.Tk()
    root.title("Sudoku")
    root.geometry("800x600")
    root.minsize(800, 600)
    root.configure(bg="lightblue")

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

    cell_widgets = [[None for _ in range(9)] for _ in range(9)]
    solution = None

    instrucao_label = tk.Label(root, text="Digite um jogo (81 dígitos):", font=("Arial", 12), bg="lightblue")
    instrucao_label.pack(pady=10)

    entry = tk.Entry(root, width=81, font=("Arial", 12))
    entry.pack(pady=10)

    achar_button = tk.Button(root, text="Buscar Solução", command=mostrar_resultado, bg="#4CAF50", fg="white", font=("Arial", 12))
    achar_button.pack(pady=10)

    buscar_button = tk.Button(root, text="Buscar Puzzle", command=buscar_jogo, bg="#4CAF50", fg="white", font=("Arial", 12))
    buscar_button.pack(pady=10)

    # Label onde o resultado será mostrado
    texto = f"Total de Registros: {total_de_registros}\n"
    texto += f"Tempo de Carregamento: {tempo_de_carregamento}\n"
    texto += f"Tempo de Ordenação: {tempo_de_ordenacao}\n"

    resultado_label = tk.Label(root, text=texto, font=("Arial", 12), bg="lightblue")
    resultado_label.pack(pady=10)

    sudoku_frame = tk.Frame(root, bg="lightblue")
    sudoku_frame.pack(pady=10)

    root.mainloop()

except Exception as e:
    print(f"Ocorreu um erro: {e}")

finally:
    print("Finalizando o processo...")
    if process is not None and process.poll() is None:
        process.terminate()
