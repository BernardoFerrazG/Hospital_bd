"""Test runner que cria as tabelas dos models ``managed = False``.

Em produção o schema vem de ``schema.sql``; nos testes, as tabelas são criadas
pelo próprio Django em um banco SQLite temporário.
"""

from django.apps import apps
from django.test.runner import DiscoverRunner


class ManagedModelTestRunner(DiscoverRunner):
    def setup_test_environment(self, *args, **kwargs):
        self._nao_gerenciados = [m for m in apps.get_models() if not m._meta.managed]
        for model in self._nao_gerenciados:
            model._meta.managed = True
        super().setup_test_environment(*args, **kwargs)

    def teardown_test_environment(self, *args, **kwargs):
        super().teardown_test_environment(*args, **kwargs)
        for model in self._nao_gerenciados:
            model._meta.managed = False
