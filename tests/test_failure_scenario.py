def test_intentional_failure_for_ci_metrics_experiment():
    """
    Falha intencional utilizada para gerar uma execucao vermelha
    durante o experimento de metricas do GitHub Actions.
    """
    assert 1 == 2
