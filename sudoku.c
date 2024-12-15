#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

#define LINE_LENGTH 200       // comprimento máximo da linha lida no arquivo csv
#define PUZZLE_SIZE 81        // tamanho do puzzle
#define MAX_RECORDS 9000005   // quantidade máxima de registros (9 milhões + 5, por segurança)

// Variável global para contar operações na busca
int qOperacoes = 0;

// Estrutura para armazenar a tabela de índices
typedef struct {
    long *ids;           // Array com as chaves (9 primeiros dígitos)
    char *solucoes;      // Array com todas as soluções concatenadas. Cada solução tem 81 chars.
    int nElementos;
} tTabelaIdx;

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

    // Alocar array de ids
    tab->ids = (long*) malloc(maxRegistros * sizeof(long));
    if (!tab->ids) {
        perror("Erro ao alocar memória para os ids");
        free(tab);
        return NULL;
    }

    // Alocar array de soluções (81 chars por registro)
    tab->solucoes = (char*) malloc(maxRegistros * PUZZLE_SIZE * sizeof(char));
    if (!tab->solucoes) {
        perror("Erro ao alocar memória para as soluções");
        free(tab->ids);
        free(tab);
        return NULL;
    }

    tab->nElementos = 0;
    return tab;
}

// Função para liberar a tabela
void LiberarTabela(tTabelaIdx *tab) {
    if (tab) {
        if (tab->ids) {
            free(tab->ids);
        }
        if (tab->solucoes) {
            free(tab->solucoes);
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

        char *ptr = line;
        // Remover quebra de linha no final, se houver
        char *nl = strchr(ptr, '\n');
        if (nl) *nl = '\0';

        // Verificar se a linha é grande o suficiente
        int len = (int)strlen(ptr);
        if (len < PUZZLE_SIZE + 1) { 
            continue;
        }

        // Encontrar a vírgula que separa o puzzle da solução
        char *virgula = strchr(ptr, ',');
        if (!virgula) {
            fprintf(stderr, "Erro: linha inválida, sem vírgula: %s\n", line);
            continue;
        }

        // Puzzle original até a vírgula
        int puzzleLen = (int)(virgula - ptr);
        if (puzzleLen < PUZZLE_SIZE) {
            fprintf(stderr, "Erro: linha de puzzle invalida (menos de 81 chars): %s\n", line);
            continue;
        }

        // Agora extrair os 9 primeiros dígitos para formar a chave
        long chave = 0;
        for (int i = 0; i < 9; i++) {
            if (ptr[i] < '0' || ptr[i] > '9') {
                fprintf(stderr, "Erro: caractere não-numérico nos 9 primeiros dígitos: %s\n", line);
                chave = -1;
                break;
            }
            chave = chave * 10 + (ptr[i] - '0');
        }
        if (chave < 0) continue;

        // Agora pegar a solução completa após a vírgula
        char *solucao = virgula + 1;
        int solLen = (int)strlen(solucao);
        if (solLen < PUZZLE_SIZE) {
            fprintf(stderr, "Erro: linha de solucao invalida (<81 chars): %s\n", line);
            continue;
        }

        // Armazenar no struct
        tab->ids[count] = chave;
        memcpy(&tab->solucoes[count * PUZZLE_SIZE], solucao, PUZZLE_SIZE);

        count++;
    }

    fclose(file);
    tab->nElementos = count;
    printf("Total de registros carregados: %d\n", count);
    return count;
}

// Para ordenar, vamos usar um array de índices. Ordenamos os índices de acordo com ids.
typedef struct {
    int idx;
    long chave;
} tIdxAux;

int compareIds(const void *a, const void *b) {
    const tIdxAux *A = (const tIdxAux *)a;
    const tIdxAux *B = (const tIdxAux *)b;
    if (A->chave < B->chave) return -1;
    if (A->chave > B->chave) return 1;
    return 0;
}

// Função para ordenar os dados em paralelo
void OrdenarDados(tTabelaIdx *tab) {
    tIdxAux *aux = (tIdxAux*) malloc(tab->nElementos * sizeof(tIdxAux));
    if (!aux) {
        perror("Erro ao alocar memoria para ordenacao");
        return;
    }

    for (int i = 0; i < tab->nElementos; i++) {
        aux[i].idx = i;
        aux[i].chave = tab->ids[i];
    }

    qsort(aux, tab->nElementos, sizeof(tIdxAux), compareIds);

    // Criar arrays temporários para rearranjar
    long *idsTemp = (long*) malloc(tab->nElementos * sizeof(long));
    char *solTemp = (char*) malloc(tab->nElementos * PUZZLE_SIZE * sizeof(char));

    if (!idsTemp || !solTemp) {
        perror("Erro ao alocar memoria temporaria para ordenacao");
        free(aux);
        if (idsTemp) free(idsTemp);
        if (solTemp) free(solTemp);
        return;
    }

    for (int i = 0; i < tab->nElementos; i++) {
        int oldIdx = aux[i].idx;
        idsTemp[i] = tab->ids[oldIdx];
        memcpy(&solTemp[i * PUZZLE_SIZE], &tab->solucoes[oldIdx * PUZZLE_SIZE], PUZZLE_SIZE);
    }

    // Copiar de volta
    memcpy(tab->ids, idsTemp, tab->nElementos * sizeof(long));
    memcpy(tab->solucoes, solTemp, tab->nElementos * PUZZLE_SIZE * sizeof(char));

    free(idsTemp);
    free(solTemp);
    free(aux);
}

// Função de busca por interpolação
int BuscaInterpolacao(tTabelaIdx *tab, long chave) {
    int inf = 0, sup = tab->nElementos - 1, meio;

    qOperacoes = 0;
    while (inf <= sup && tab->ids[inf] <= chave && tab->ids[sup] >= chave) {
        qOperacoes++;
        
        if (tab->ids[sup] == tab->ids[inf]) {
            meio = inf;
        } else {
            meio = inf + (int)((double)(sup - inf) * (double)(chave - tab->ids[inf]) / (double)(tab->ids[sup] - tab->ids[inf]));
        }

        printf("meio inter = %d [%ld]\n", meio, tab->ids[meio]);

        if (tab->ids[meio] == chave) {
            return meio;
        } else {
            if (chave > tab->ids[meio]) {
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
    OrdenarDados(tab);
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
        exibirTabuleiro(&tab->solucoes[index * PUZZLE_SIZE]);
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
