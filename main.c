#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <sys/time.h>
#include "estrutura.h"
#include "leitor.h"

void criarJogoBuscado(char *entrada, int *jogo)
{
    char buffer[10];
    buffer[9] = '\0';
    for (int i = 0; i < 9; i++)
    {
        strncpy(buffer, entrada + i * 9, 9);
        jogo[i] = atoi(buffer);
    }
}

int main(int argc, char **argv)
{
    printf("Carregando os dados da lista...\n");

    tListaIndexada lista = criarLista();
    clock_t inicio = clock();
    carregarDados("sudoku.csv", &lista);
    clock_t fim = clock();
    double tempo_carregamento = (double)(fim - inicio) / CLOCKS_PER_SEC;

    printf("Tempo de carregamento: %.3f segundos.\n\n", tempo_carregamento);
    printf("Ordenando a lista...\n");

    inicio = clock();
    ordenarLista(lista);
    fim = clock();
    double tempo_ordenacao = (double)(fim - inicio) / CLOCKS_PER_SEC;

    printf("Tempo de ordenacao: %.3f segundos.\n\n", tempo_ordenacao);

    int qOperacoes = 0;
    int jogoBuscado[9];
    while (1)
    {
        printf("Insira um jogo de entrada (Ou nao insira nada para sair): ");

        char buffer[83];
        fgets(buffer, sizeof(buffer), stdin);

        if (strlen(buffer) != 82)
        {
            if (buffer[0] == '\n')
            {
                printf("\nNenhuma entrada foi fornecida. Saindo...\n\n");
                break;
            }
            else
            {
                printf("\nEntrada invalida. Por favor, insira exatamente 81 caracteres.\n\n");
                continue;
            }
        }

        criarJogoBuscado(buffer, jogoBuscado);

        printf("\nBuscando jogo...\n");

        struct timeval inicioBusca, fimBusca;
        gettimeofday(&inicioBusca, NULL);
        int indice = buscaBinaria(lista, jogoBuscado, &qOperacoes);
        gettimeofday(&fimBusca, NULL);
        int tempo_busca = (int)(fimBusca.tv_sec - inicioBusca.tv_sec) * 1e6 + (fimBusca.tv_usec - inicioBusca.tv_usec);

        printf("Tempo de busca: %d microssegundos.\n", tempo_busca);
        printf("Total de operacoes realizadas: %d\n\n", qOperacoes);
        if (indice != -1)
        {
            printf("Jogo Completo:\n%s\n\n", lista.jogos[indice].jogoPreenchido);
        }
        else
        {
            printf("Jogo nao encontrado\n\n");
        }
    }

    apagarLista(lista);
    return 0;
}