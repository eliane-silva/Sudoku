#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include "estrutura.h"

int main() {
    char entrada[82];
    fgets(entrada, 82, stdin);
    entrada[strcspn(entrada, "\n")] = 0;

    FILE *file = fopen("sudoku.csv", "r");
    if (!file) {
        fprintf(stderr, "Erro ao abrir o arquivo\n");
        return 1;
    }

    char linha[200];
    while (fgets(linha, sizeof(linha), file)) {
        char *puzzle = strtok(linha, ",");
        char *solution = strtok(NULL, ",");

        if (solution) {
            solution[strcspn(solution, "\n")] = 0; 
        }

        if (strcmp(puzzle, entrada) == 0) {
            printf("%s\n%s\n", puzzle, solution);
            fclose(file);
            return 0;
        }
    }

    fclose(file);
    printf("jogo nao encontrado\n");
    return 0;
}
