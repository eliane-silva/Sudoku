# sudoku_ui.py
import tkinter as tk
from tkinter import messagebox
from sudoku_logic import formatar_sudoku
from constants import (
    BG_COLOR,
    BUTTON_COLOR,
    BUTTON_HOVER_COLOR,
    TEXT_COLOR,
    FONT_PRIMARY,
    FONT_SECONDARY,
    BORDER_COLOR,
    GRID_SIZE
)

class SudokuUI:
    def __init__(self, process_manager):
        self.process_manager = process_manager

        # Cria a janela principal
        self.root = tk.Tk()
        self.root.title("Sudoku Master")
        self.root.geometry("900x700")
        self.root.minsize(800, 600)
        self.root.configure(bg=BG_COLOR)

        # Cria a interface principal (header, controles, grade)
        self.ui_elements = self.setup_main_ui(self.root)
        self.entry = self.ui_elements["entry"]
        self.sudoku_frame = self.ui_elements["sudoku_frame"]
        self.dica_frame = self.ui_elements["dica_frame"]  
        self.resultado_label = self.ui_elements["resultado_label"]
        self.btn_buscar = self.ui_elements["btn_buscar"]
        self.btn_resolver = self.ui_elements["btn_resolver"]

        # Liga os comandos dos botões aos métodos
        self.btn_resolver.config(command=self.mostrar_resultado)
        self.btn_buscar.config(command=self.buscar_jogo)
        # O botão "Dica" será adicionado dinamicamente

        # Variáveis de estado
        self.cell_widgets = [[None for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        self.solution = None
        self.dica_button = None  # Botão de dica não aparece inicialmente

        self.root.protocol("WM_DELETE_WINDOW", self.fechar_janela)

    def setup_main_ui(self, root):
        main_frame = tk.Frame(root, bg=BG_COLOR)
        main_frame.pack(expand=True, fill="both", padx=20, pady=20)

        # Header
        header_frame = tk.Frame(main_frame, bg=BG_COLOR)
        header_frame.pack(fill="x", pady=10)
        tk.Label(header_frame, text="SUDOKU MASTER", bg=BG_COLOR, fg=TEXT_COLOR,
                font=("Arial", 20, "bold")).pack(side="left")

        # Controles
        controls_frame = tk.Frame(main_frame, bg=BG_COLOR)
        controls_frame.pack(fill="x", pady=15)

        entry = tk.Entry(controls_frame, width=30, font=FONT_PRIMARY, bg="white",
                        relief="flat", borderwidth=2, highlightbackground=BORDER_COLOR,
                        highlightthickness=1)
        entry.pack(side="left", padx=5, ipady=3)

        buttons_frame = tk.Frame(controls_frame, bg=BG_COLOR)
        buttons_frame.pack(side="left", padx=10)
        btn_buscar = create_button(buttons_frame, "Buscar Puzzle")
        btn_resolver = create_button(buttons_frame, "Buscar Solução")
        btn_buscar.pack(side="left", padx=5)
        btn_resolver.pack(side="left", padx=5)

        # Grade do Sudoku
        sudoku_frame = tk.Frame(main_frame, bg=BG_COLOR)
        sudoku_frame.pack(pady=15)

        # Frame para o botão Dica (localizado logo abaixo do sudoku)
        dica_frame = tk.Frame(main_frame, bg=BG_COLOR)
        dica_frame.pack(pady=(0, 15))  # Ajuste o padding conforme desejado

        # Métricas
        metrics_frame = tk.Frame(main_frame, bg=BG_COLOR)
        metrics_frame.pack(fill="x", pady=10)
        texto = (
            f"Total de Registros: {self.process_manager.total_de_registros}\n"
            f"Tempo de Carregamento: {self.process_manager.tempo_de_carregamento}\n"
            f"Tempo de Ordenação: {self.process_manager.tempo_de_ordenacao}\n"
        )
        resultado_label = tk.Label(metrics_frame, text=texto, bg=BG_COLOR, fg=TEXT_COLOR,
                                    font=FONT_SECONDARY, justify="left")
        resultado_label.pack(side="left")

        # Retorna também o frame de dica para podermos usá-lo depois
        return {
            "entry": entry,
            "sudoku_frame": sudoku_frame,
            "dica_frame": dica_frame,
            "resultado_label": resultado_label,
            "btn_buscar": btn_buscar,
            "btn_resolver": btn_resolver
        }
 
    def limpar_sudoku(self):
        for widget in self.sudoku_frame.winfo_children():
            widget.destroy()

    def mostrar_sudoku(self, grid, interativo=False):
        self.limpar_sudoku()
        self.cell_widgets = [[None for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        for i in range(GRID_SIZE):
            for j in range(GRID_SIZE):
                valor = grid[i][j]
                # Define espaçamentos maiores para delimitar as regiões 3x3
                border_top = 6 if i in [0, 3, 6] else 1
                border_left = 6 if j in [0, 3, 6] else 1
                border_bottom = 6 if i == GRID_SIZE - 1 else 1
                border_right = 6 if j == GRID_SIZE - 1 else 1

                if interativo and valor == 0:
                    cell = tk.Entry(self.sudoku_frame, width=3, justify="center",
                                    font=("Arial", 14), relief="solid", borderwidth=1)
                    cell.grid(row=i, column=j, padx=(border_left, border_right),
                              pady=(border_top, border_bottom))
                    # Usa lambda para capturar corretamente os índices atuais
                    cell.bind("<FocusOut>", lambda e, x=i, y=j: self.validar_campo(e, x, y))
                else:
                    cell = tk.Label(self.sudoku_frame,
                                    text=str(valor) if valor != 0 else "",
                                    borderwidth=1, relief="solid",
                                    width=3, height=1, bg="lightgray",
                                    font=("Arial", 14))
                    cell.grid(row=i, column=j, padx=(border_left, border_right),
                              pady=(border_top, border_bottom))
                self.cell_widgets[i][j] = cell

    def validar_campo(self, event, x, y):
        """
        Valida o valor inserido na célula:
         - Se vazio, restaura cor branca.
         - Se não for dígito ou fora do intervalo, pinta de vermelho.
         - Se estiver correto (de acordo com a solução), pinta de verde; caso contrário, vermelho.
        """
        cell = self.cell_widgets[x][y]
        valor = cell.get().strip()
        if valor == "":
            cell.config(bg="white")
            return
        if not valor.isdigit() or not (1 <= int(valor) <= GRID_SIZE):
            cell.config(bg="red")
        elif self.solution and int(valor) == self.solution[x][y]:
            cell.config(bg="green")
        else:
            cell.config(bg="red")

    def mostrar_resultado(self):
        entrada = self.entry.get().strip()

        if len(entrada) != GRID_SIZE * GRID_SIZE:
            messagebox.showerror("Erro", "Entrada inválida, deve ter 81 caracteres.")
            self.entry.delete(0, tk.END)
            return

        self.entry.delete(0, tk.END)
        self.process_manager.send_input(entrada)
        linha = self.process_manager.read_line()

        if "jogo nao encontrado" in linha:
            self.resultado_label.config(text=linha)
            self.limpar_sudoku()
        else:
            try:
                tempo = int(linha)
                operacoes = int(self.process_manager.read_line())
                jogo_respondido = self.ler_jogo_respondido()
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao ler resposta: {e}")
                return

            grid = formatar_sudoku(jogo_respondido)
            self.resultado_label.config(text=f"Tempo da Busca: {tempo} nanossegundos.\n"
                                             f"Total de Operações: {operacoes}.")
            self.mostrar_sudoku(grid)

    def buscar_jogo(self):
        entrada = self.entry.get().strip()
        if len(entrada) != GRID_SIZE * GRID_SIZE or not entrada.isdigit():
            messagebox.showerror("Erro", "Entrada inválida. Digite 81 dígitos (0 a 9).")
            self.entry.delete(0, tk.END)
            return

        self.entry.delete(0, tk.END)
        self.process_manager.send_input(entrada)
        linha = self.process_manager.read_line()

        if "jogo nao encontrado" in linha:
            messagebox.showerror("Erro", "Jogo não encontrado no arquivo.")
            self.limpar_sudoku()
        else:
            try:
                tempo = int(linha)
                operacoes = int(self.process_manager.read_line())
                jogo_respondido = self.ler_jogo_respondido()
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao ler resposta: {e}")
                return

            # Atualiza a solução e exibe o puzzle para edição
            puzzle = [[int(entrada[i * GRID_SIZE + j]) for j in range(GRID_SIZE)] 
                      for i in range(GRID_SIZE)]
            self.solution = [
                [int(jogo_respondido[i * GRID_SIZE + j]) for j in range(GRID_SIZE)]
                for i in range(GRID_SIZE)
            ]
            self.mostrar_sudoku(puzzle, interativo=True)
            self.resultado_label.config(text="Puzzle carregado com sucesso.")
            self.adicionar_botao_dica()

    def ler_jogo_respondido(self):
        """Lê GRID_SIZE linhas da resposta e retorna uma string com os 81 dígitos."""
        return "".join([self.process_manager.read_line().strip() for _ in range(GRID_SIZE)])

    def adicionar_botao_dica(self):
        if not self.dica_button or not self.dica_button.winfo_exists():
            self.dica_button = create_button(self.dica_frame, "Dica", self.dar_dica)
            self.dica_button.pack() 

    def remover_botao_dica(self):
        """Remove o botão de dica, se existir."""
        if self.dica_button and self.dica_button.winfo_exists():
            self.dica_button.destroy()
            self.dica_button = None

    def dar_dica(self):
        """
        Percorre a grade e na primeira célula vazia, insere o valor correto (da solução)
        e pinta a célula de amarelo.
        """
        for i in range(GRID_SIZE):
            for j in range(GRID_SIZE):
                cell = self.cell_widgets[i][j]
                if isinstance(cell, tk.Entry) and cell.get().strip() == "":
                    cell.insert(0, str(self.solution[i][j]))
                    cell.config(bg="yellow")
                    return
                elif isinstance(cell, tk.Label) and cell.cget("text") == "":
                    cell.config(text=str(self.solution[i][j]), bg="yellow")
                    return
        messagebox.showinfo("Dica", "Não há mais campos vazios para preencher.")

    def fechar_janela(self):
        """Exibe uma janela de aviso enquanto encerra o processo e fecha a aplicação."""
        closing_root = tk.Toplevel(self.root)
        closing_root.title("Fechando")
        tk.Label(closing_root, text="O programa está encerrando, por favor aguarde...",
                 bg="lightblue").pack(padx=20, pady=10)
        closing_root.configure(bg="lightblue")
        closing_root.update()

        if self.process_manager.process and self.process_manager.process.poll() is None:
            self.process_manager.send_input("")
            linha = self.process_manager.read_line()
            if "Programa em C finalizado" in linha:
                print("Programa C fechando corretamente.")
            else:
                print("Falha ao fechar corretamente.")
            self.process_manager.terminate_process()

        closing_root.destroy()
        self.root.destroy()

    def run(self):
        self.root.mainloop()

# Função auxiliar para criar botões com efeito hover, mantendo o padrão de cores
def create_button(parent, text, command=None):
    btn = tk.Button(
        parent,
        text=text,
        command=command,
        bg=BUTTON_COLOR,
        fg="white",
        activebackground=BUTTON_HOVER_COLOR,
        font=FONT_SECONDARY,
        borderwidth=0,
        relief="flat",
        padx=15,
        pady=5
    )
    btn.bind("<Enter>", lambda e: btn.config(bg=BUTTON_HOVER_COLOR))
    btn.bind("<Leave>", lambda e: btn.config(bg=BUTTON_COLOR))
    return btn
