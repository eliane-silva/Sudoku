#include <stdio.h>
#include "estrutura.h"
#include "leitor.h"
#include "constantes.h"

int carregarDados(char *nomeDoArquivo, tListaIndexada lista)
{
}

// int main() {
//     FILE *file = fopen("numeros.txt", "r");
//     if (!file) {
//         perror("Erro ao abrir o arquivo");
//         return 1;
//     }

//     char str[82];  // 81 números + caractere nulo
//     if (!fgets(str, sizeof(str), file)) {
//         perror("Erro ao ler o arquivo");
//         fclose(file);
//         return 1;
//     }
//     fclose(file);

//     int secao[9];
//     char buffer[10];  // 9 dígitos + '\0'

//     buffer[9] = '\0';  // Define uma vez

//     for (int i = 0; i < 9; i++) {
//         strncpy(buffer, str + i * 9, 9);  // Copia 9 dígitos
//         secao[i] = atoi(buffer);         // Converte para int
//         printf("Seção %d: %d\n", i + 1, secao[i]);
//     }

//     return 0;
// }
