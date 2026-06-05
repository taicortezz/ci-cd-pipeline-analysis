# Controle das Execucoes do Experimento

Este arquivo registra manualmente as principais informacoes de cada execucao
real do GitHub Actions. Ele sera usado como apoio para o relatorio final da
atividade, reunindo evidencias como IDs das runs, commits, status, duracoes,
artefatos gerados e variacoes aplicadas.

## Execucoes

| Execucao | Workflow | Run | Commit SHA | Mensagem do commit | Branch | Evento | Status | Duracao total | Duracao do job principal | Quantidade de testes | Falhas nos testes | Artefato gerado | Tamanho do artefato | Variacao aplicada | Observacoes |
|---|---|---|---|---|---|---|---|---|---|---:|---:|---|---|---|---|
| 1 | CI | #1 | 1a38570 | Add GitHub Actions CI workflow | main | push | Success | 15s | 11s | 30 | 0 | test-results | 929 Bytes | Baseline inicial com pipeline simples, sem cache, sem paralelismo e sem testes lentos. | Primeira execucao real do workflow no GitHub Actions. O pipeline executou lint, testes automatizados, geracao de resumo dos testes e upload do artefato test-results. |
| 2 | CI | #2 | c9b3307 | Add experiment execution log | main | push | Success | 14s | 11s | 30 | 0 | test-results | nao registrado | Segunda execucao baseline sem alteracoes na API, testes ou workflow. | Execucao utilizada para verificar a variacao natural do pipeline. O comportamento foi praticamente identico ao da Execucao 1. |
| 3 | CI | #3 | 11ddfc1 | Aumenta quantidade de testes automatizados | main | push | Success | 15s | 12s | 47 | 0 | test-results | nao registrado | Aumento da quantidade de testes automatizados, de 30 para 47 testes, sem introducao de testes lentos. | O aumento da quantidade de testes nao gerou aumento significativo na duracao total do pipeline, sugerindo que os testes adicionados possuem baixo custo de execucao e que parte relevante do tempo total ainda esta associada ao overhead do workflow. |
| 4 | CI | #4 | 5c6fd5f | Adiciona teste de carga para experimento de metricas CI | main | push | Success | 18s | ci = 13s | 48 | 0 | test-results | 1.14 KB | Introducao de teste de carga/custoso, simulando fluxo intensivo de criacao, conclusao, consulta, estatisticas e remocao de tarefas. | A duracao total aumentou em relacao as execucoes anteriores, indicando impacto perceptivel da etapa de testes mais custosa. |
| 5 | CI | #5 | 7a8938f | Adiciona cache de dependencias no CI | main | push | Success | 17s | ci = 15s | 48 | 0 | test-results | 1.14 KB | Adicao de cache de dependencias pip no workflow usando actions/setup-python. | Primeira execucao apos adicionar cache. A reducao foi pequena em relacao a execucao anterior, possivelmente porque o cache ainda estava sendo criado ou porque a instalacao de dependencias nao era o principal gargalo. |
| 6 | CI | #6 | a346354 | Executa pipeline com cache aquecido | main | push | Success | 19s | ci = 15s | 48 | 0 | test-results | 1.13 KB | Execucao com cache aquecido, sem alteracao de codigo. | O cache hit foi confirmado no log do GitHub Actions, mas o tempo total nao reduziu. Isso indica que o cache funcionou, porem nao representou ganho significativo neste projeto pequeno. |
| 7 | CI | #7 | 4fb5737 | Separa pipeline em jobs paralelos | main | push | Success | 21s | lint = 11s; tests = 16s | 48 | 0 | test-results | nao registrado | Separacao do pipeline em dois jobs independentes e paralelos: lint e tests. | O paralelismo nao reduziu o tempo total do workflow. Como os jobs executam em runners separados, houve overhead adicional de checkout, setup Python, cache e instalacao de dependencias em cada job. |

## Observacoes Gerais

- As execucoes devem ser registradas apos a conclusao real do workflow no GitHub Actions.
- Os dados deste arquivo devem ser comparados posteriormente com os artefatos e metricas coletadas automaticamente.
