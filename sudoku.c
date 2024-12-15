#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

#define LINE_LENGTH 200 // comprimento máximo da linha lida no arquivo csv 
#define PUZZLE_SIZE 81  // tamanho do puzzle
#define MAX_RECORDS 1000 // quantidade máxima de registros lidos do arquivo csv

// Estrutura para armazenar um elemento (um Sudoku)
typedef struct {
    long id; // chave de busca (9 primeiros dígitos do puzzle)
    char jogo_respondido[PUZZLE_SIZE + 1]; // Solução completa do Sudoku
} tElemento;

// Estrutura para armazenar a tabela de índices
typedef struct {
    tElemento *elementos;
    int nElementos;
} tTabelaIdx;

// Variável global para contar operações na busca
int qOperacoes = 0;

// Função para comparar dois elementos (para ordenação)
int compareElementos(const void *a, const void *b) {
    const tElemento *elemA = (const tElemento *)a;
    const tElemento *elemB = (const tElemento *)b;

    if (elemA->id < elemB->id) return -1;
    if (elemA->id > elemB->id) return 1;
    return 0;
}

// Função para exibir o tabuleiro formatado
static void exibirTabuleiro(const char *solution) {
    for (int i = 0; i < PUZZLE_SIZE; i++) {
        printf("%c ", solution[i]);
        if ((i + 1) % 9 == 0) printf("\n");
    }
}

// Função para alocar a tabela
tTabelaIdx *AlocarTabela(int maxRegistros) {
    tTabelaIdx *tab = (tTabelaIdx*) malloc(sizeof(tTabelaIdx));
    if (!tab) {
        perror("Erro ao alocar memória para a tabela");
        return NULL;
    }
    tab->elementos = (tElemento*) malloc(maxRegistros * sizeof(tElemento));
    if (!tab->elementos) {
        perror("Erro ao alocar memória para os elementos");
        free(tab);
        return NULL;
    }
    tab->nElementos = 0;
    return tab;
}

// Função para liberar a tabela
void LiberarTabela(tTabelaIdx *tab) {
    if (tab) {
        if (tab->elementos) {
            free(tab->elementos);
        }
        free(tab);
    }
}

// Função para carregar os dados do CSV
static int carregarDados(const char *filename, tTabelaIdx *tab) {
    FILE *file = fopen(filename, "r");
    if (!file) {
        perror("Erro ao abrir o arquivo");
        return -1;
    }

    char line[LINE_LENGTH];
    int count = 0;

    // Ignorar o cabeçalho
    if (!fgets(line, sizeof(line), file)) {
        fprintf(stderr, "Erro: arquivo vazio ou inválido.\n");
        fclose(file);
        return -1;
    }

    // Ler linhas do arquivo
    while (fgets(line, sizeof(line), file) && count < MAX_RECORDS) {
        char *token = strtok(line, ",");
        if (!token || strlen(token) < PUZZLE_SIZE) {
            fprintf(stderr, "Erro: linha de puzzle invalida: %s\n", line);
            continue;
        }

        // Converter os 9 primeiros dígitos do puzzle em uma chave única
        long chave = 0;
        for (int i = 0; i < 9; i++) {
            chave = chave * 10 + (token[i] - '0');
        }

        // Obter a solução
        char *token_solucao = strtok(NULL, ",");
        if (!token_solucao || strlen(token_solucao) < PUZZLE_SIZE) {
            fprintf(stderr, "Erro: linha de solucao invalida: %s\n", line);
            continue;
        }

        tab->elementos[count].id = chave;
        strncpy(tab->elementos[count].jogo_respondido, token_solucao, PUZZLE_SIZE);
        tab->elementos[count].jogo_respondido[PUZZLE_SIZE] = '\0';

        count++;
    }

    fclose(file);
    tab->nElementos = count;
    printf("Total de registros carregados: %d\n", count);
    return count;
}

// Função de busca por interpolação fornecida, adaptada para o nosso código
int BuscaInterpolacao(tTabelaIdx *tab, long chave) {
    int inf = 0, sup = tab->nElementos - 1, meio;

    qOperacoes = 0;
    while (inf <= sup && tab->elementos[inf].id <= chave && tab->elementos[sup].id >= chave) {
        qOperacoes++;
        
        // Cálculo da posição (meio) usando interpolação
        if (tab->elementos[sup].id == tab->elementos[inf].id) {
            // Evitar divisão por zero caso todos sejam iguais
            meio = inf;
        } else {
            meio = inf + (int)((double)(sup - inf) * (double)(chave - tab->elementos[inf].id) / (double)(tab->elementos[sup].id - tab->elementos[inf].id));
        }

        printf("meio inter = %d [%ld]\n", meio, tab->elementos[meio].id);

        if (tab->elementos[meio].id == chave) {
            return meio;
        } else {
            if (chave > tab->elementos[meio].id) {
                inf = meio + 1;
            } else {
                sup = meio - 1;
            }
        }
    }

    return -1;
}

int main() {
    tTabelaIdx *tab = AlocarTabela(MAX_RECORDS);
    if (!tab) return EXIT_FAILURE;

    printf("\n========== SISTEMA DE BUSCA DE SUDOKU ==========\n\nCarregando dados...\n");
    clock_t inicio_carregamento = clock();
    int count = carregarDados("sudoku.csv", tab);
    clock_t fim_carregamento = clock();

    if (count < 0) {
        LiberarTabela(tab);
        return EXIT_FAILURE;
    }

    printf("Ordenando dados...\n");
    clock_t inicio_ordenacao = clock();
    qsort(tab->elementos, tab->nElementos, sizeof(tElemento), compareElementos);
    clock_t fim_ordenacao = clock();

    printf("\nPronto para busca.\nDigite os *9 primeiros numeros* do Puzzle do Sudoku (exemplo: 380500091):\n");
    long chave_busca;
    if (scanf("%ld", &chave_busca) != 1) {
        fprintf(stderr, "Erro. Entrada invalida.\n");
        LiberarTabela(tab);
        return EXIT_FAILURE;
    }

    printf("\nBuscando solucao...\n");
    clock_t inicio_busca = clock();
    int index = BuscaInterpolacao(tab, chave_busca);
    clock_t fim_busca = clock();

    if (index >= 0) {
        printf("\n========== SOLUCAO ENCONTRADA ==========\n\n");
        exibirTabuleiro(tab->elementos[index].jogo_respondido);
    } else {
        printf("\n========== SOLUCAO NÃO ENCONTRADA ==========\n");
    }

    double tempo_carregamento = (double)(fim_carregamento - inicio_carregamento) / CLOCKS_PER_SEC;
    double tempo_ordenacao = (double)(fim_ordenacao - inicio_ordenacao) / CLOCKS_PER_SEC;
    double tempo_busca = (double)(fim_busca - inicio_busca) / CLOCKS_PER_SEC;

    printf("\n--- Estatisticas de Tempo ---\n\n");
    printf("Tempo de carregamento: %.6f segundos\n", tempo_carregamento);
    printf("Tempo de ordenacao: %.6f segundos\n", tempo_ordenacao);
    printf("Tempo de busca: %.6f segundos\n", tempo_busca);
    printf("Numero de operacoes realizadas na busca: %d\n", qOperacoes);

    LiberarTabela(tab);
    return EXIT_SUCCESS;
}
