def formatar_sudoku(jogo):
    """
    Converte uma string de 81 dígitos em uma matriz 9x9.
    """
    return [[int(jogo[i * 9 + j]) for j in range(9)] for i in range(9)]
