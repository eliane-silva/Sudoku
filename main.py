# main.py
import tkinter as tk
from process_manager import ProcessManager
from sudoku_ui import SudokuUI

def main():
    # Tela de carregamento
    loading_root = tk.Tk()
    loading_root.title("Carregando")
    tk.Label(
        loading_root,
        text="O programa está carregando, por favor aguarde...",
        bg="lightblue"
    ).pack(padx=20, pady=10)
    loading_root.configure(bg="lightblue")
    loading_root.update()

    # Inicializa o gerenciador do processo (substitua "./program" pelo caminho do seu executável)
    pm = ProcessManager(["./program"])
    pm.start_process()

    loading_root.destroy()

    # Inicia a interface gráfica do Sudoku
    app = SudokuUI(pm)
    app.run()

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Ocorreu um erro: {e}")
    finally:
        print("Finalizando o processo...")
        # Se necessário, o encerramento do processo será tratado na função fechar_janela da interface.
