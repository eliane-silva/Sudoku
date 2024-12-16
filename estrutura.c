#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "estrutura.h"
#include "constantes.h"

tJogo criarJogo()
{
    tJogo jogo;

    jogo.jogoInicial = malloc(sizeof(int) * 9);
    if (!jogo.jogoInicial)
    {
        puts("Erro ao alocar o jogo inicial.");
        exit(1);
    }

    jogo.jogoPreenchido = malloc(sizeof(char) * 90);
    if (!jogo.jogoPreenchido)
    {
        free(jogo.jogoInicial);
        puts("Erro ao alocar o jogo preenchido.");
        exit(1);
    }

    jogo.jogoPreenchido[89] = '\0';

    return jogo;
}

void apagarJogo(tJogo jogo)
{
    free(jogo.jogoInicial);
    free(jogo.jogoPreenchido);
}

tListaIndexada criarLista()
{
    tListaIndexada lista;

    lista.jogos = malloc(sizeof(tJogo) * TOTAL_JOGOS);
    if (!lista.jogos)
    {
        puts("Erro ao alocar o array dos jogos.");
        exit(1);
    }

    lista.nElementos = 0;

    return lista;
}

void apagarLista(tListaIndexada lista)
{
    for (int i = 0; i < lista.nElementos; i++)
    {
        apagarJogo(lista.jogos[i]);
    }
    free(lista.jogos);
}

int compararJogo(const void *a, const void *b)
{
    const tJogo *jogo1 = (const tJogo *)a;
    const tJogo *jogo2 = (const tJogo *)b;

    // Comparar cada parte na ordem de prioridade
    for (int i = 0; i < 9; i++)
    {
        if (jogo1->jogoInicial[i] < jogo2->jogoInicial[i])
        {
            return -1; // O primeiro jogo vem primeiro
        }
        else if (jogo1->jogoInicial[i] > jogo2->jogoInicial[i])
        {
            return 1; // O segundo jogo vem primeiro
        }
    }
    return 0; // São iguais
}

void ordenarLista(tListaIndexada lista)
{
    qsort(lista.jogos, lista.nElementos, sizeof(tJogo), compararJogo);
}

int buscaBinaria(tListaIndexada lista, int *jogo, int *qOperacoes)
{
    tJogo jogoBuscado = criarJogo();
    memcpy(jogoBuscado.jogoInicial, jogo, 9 * sizeof(int));
    int inf = 0, sup = lista.nElementos - 1, meio;

    (*qOperacoes) = 0;
    int linha = 0;

    while (inf <= sup)
    {
        (*qOperacoes)++;

        int *jogoInf = lista.jogos[inf].jogoInicial;
        int *jogoSup = lista.jogos[sup].jogoInicial;

        double taxa;

        // if (linha < 8 && jogo[linha] == jogoInf[linha] || jogo[linha] == jogoSup[linha])
        // {
        //     double valorInf = jogoInf[linha] * 1e9 + jogoInf[linha + 1];
        //     double valorSup = jogoSup[linha] * 1e9 + jogoSup[linha + 1];
        //     double valorJogo = jogo[linha] * 1e9 + jogo[linha + 1];
            
        //     taxa = (double)(valorJogo - valorInf) / (valorSup - valorInf);
        // }
        // else
        // {
        //     taxa = (double)(jogo[linha] - jogoInf[linha]) / (jogoSup[linha] - jogoInf[linha]);
        // }

        meio = inf + (int)((sup - inf) / 2);
        // meio = inf + (int)((sup - inf) * taxa);

        int comparacao = compararJogo(&jogoBuscado, &lista.jogos[meio]);
        if (comparacao == 0)
        {
            apagarJogo(jogoBuscado);
            return meio;
        }

        if (comparacao == 1)
        {
            inf = meio + 1;
        }
        else
        {
            sup = meio - 1;
        }

        // if (jogo[linha] == lista.jogos[inf].jogoInicial[linha] && jogo[linha] == lista.jogos[sup].jogoInicial[linha])
        // {
        //     linha++;
        // }
    }

    apagarJogo(jogoBuscado);
    return -1;
}
