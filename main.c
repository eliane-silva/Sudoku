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
    printf("Programa em C iniciado\n");
    fflush(stdout);

    tListaIndexada lista = criarLista();
    clock_t inicio = clock();
    carregarDados("sudoku.csv", &lista);
    clock_t fim = clock();
    double tempo_carregamento = (double)(fim - inicio) / CLOCKS_PER_SEC;

    printf("registros %d\n", lista.nElementos);
    printf("carregamento %.3f\n", tempo_carregamento);
    fflush(stdout);

    inicio = clock();
    ordenarLista(lista);
    fim = clock();
    double tempo_ordenacao = (double)(fim - inicio) / CLOCKS_PER_SEC;

    printf("ordenacao %.3f\n", tempo_ordenacao);
    fflush(stdout);

    printf("ok\n");
    fflush(stdout);

    int qOperacoes = 0;
    int jogoBuscado[9];
    while (1)
    {
        fflush(stdout);
        char buffer[83];
        fgets(buffer, sizeof(buffer), stdin);

        if (strlen(buffer) != 82)
        {
            if (buffer[0] == '\n')
            {
                break;
            }
            else
            {
                printf("entrada invalida\n");
                continue;
            }
        }

        criarJogoBuscado(buffer, jogoBuscado);

        struct timeval inicioBusca, fimBusca;
        gettimeofday(&inicioBusca, NULL);
        int indice = buscaBinaria(lista, jogoBuscado, &qOperacoes);
        gettimeofday(&fimBusca, NULL);
        int tempo_busca = (int)(fimBusca.tv_sec - inicioBusca.tv_sec) * 1e6 + (fimBusca.tv_usec - inicioBusca.tv_usec);

        if (indice != -1)
        {
            printf("%d\n", tempo_busca);
            printf("%d\n", qOperacoes);
            printf("%s\n", lista.jogos[indice].jogoPreenchido);
        }
        else
        {
            printf("jogo nao encontrado\n");
        }
       fflush(stdout);
    }

    apagarLista(lista);

    printf("Programa em C finalizado\n");
    fflush(stdout);
    return 0;
}
