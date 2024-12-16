#ifndef _estrutura_H_
#define _estrutura_H_

typedef struct
{
    int *jogoInicial;    // Array com 9 ints, cada um representando uma linha do jogo
    char *jogoPreenchido; // Array com 90 chars, representando os 81 números, as quebras de linha e o \0
} tJogo;

typedef struct
{
    tJogo *jogos;   // Array com ponteiros para cada jogo
    int nElementos; // Tamanho máximo do array de jogos
} tListaIndexada;

extern tJogo criarJogo();
extern void apagarJogo(tJogo jogo);

extern tListaIndexada criarLista();
extern void apagarLista(tListaIndexada lista);

extern int compararJogo(const void *a, const void *b);
extern void ordenarLista(tListaIndexada lista);

extern char *buscaInterpolacao(tListaIndexada lista, int *jogo, int *qOperacoes);

#endif
