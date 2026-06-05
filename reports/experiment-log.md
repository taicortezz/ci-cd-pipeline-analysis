# Controle das Execucoes do Experimento

Este arquivo registra manualmente as principais informacoes de cada execucao
real do GitHub Actions. Ele sera usado como apoio para o relatorio final da
atividade, reunindo evidencias como IDs das runs, commits, status, duracoes,
artefatos gerados e variacoes aplicadas.

## Execucoes

| Execucao | Workflow | Run | Commit SHA | Mensagem do commit | Branch | Evento | Status | Duracao total | Duracao do job principal | Quantidade de testes | Falhas nos testes | Artefato gerado | Tamanho do artefato | Variacao aplicada | Observacoes |
|---|---|---|---|---|---|---|---|---|---|---:|---:|---|---|---|---|
| 1 | CI | #1 | 1a38570 | Add GitHub Actions CI workflow | main | push | Success | 15s | 11s | 30 | 0 | test-results | 929 Bytes | Baseline inicial com pipeline simples, sem cache, sem paralelismo e sem testes lentos. | Primeira execucao real do workflow no GitHub Actions. O pipeline executou lint, testes automatizados, geracao de resumo dos testes e upload do artefato test-results. |

## Observacoes Gerais

- As execucoes devem ser registradas apos a conclusao real do workflow no GitHub Actions.
- Os dados deste arquivo devem ser comparados posteriormente com os artefatos e metricas coletadas automaticamente.
