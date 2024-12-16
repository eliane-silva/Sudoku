#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "leitor.h"

int carregarDados(char *nomeDoArquivo, tListaIndexada *lista)
{
    FILE *arquivo = fopen(nomeDoArquivo, "r");
    if (!arquivo)
    {
        perror("Erro ao abrir o arquivo");
        return -1;
    }

    char linha[165];
    if (!fgets(linha, sizeof(linha), arquivo))
    {
        perror("Erro: arquivo vazio ou inválido.\n");
        fclose(arquivo);
        return -1;
    }

    lista->nElementos = 0;

    while (fgets(linha, sizeof(linha), arquivo))
    {
        tJogo jogo = criarJogo();

        char buffer[10];
        buffer[9] = '\0';
        for (int i = 0; i < 9; i++)
        {
            strncpy(buffer, linha + i * 9, 9);
            jogo.jogoInicial[i] = atoi(buffer);

            strncpy(jogo.jogoPreenchido + i * 10, 82 + linha + i * 9, 9);
            jogo.jogoPreenchido[i * 10 + 9] = '\n';
        }
    
        lista->jogos[lista->nElementos++] = jogo;
    }
    fclose(arquivo);
    printf("Total de registros carregados: %d\n", lista->nElementos);

    return lista->nElementos;
}
