# Imagem base enxuta, alinhada à diretriz "Python 3.11+ obrigatório"
FROM python:3.11-slim

WORKDIR /app

# Instala dependências primeiro (aproveita cache de camadas do Docker)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia apenas o necessário para rodar o módulo e os testes
COPY src/ src/
COPY tests/ tests/
COPY specs/ specs/
COPY CONTEXT_RULES.md .

# Usuário não-root, por boas práticas de segurança
RUN useradd --create-home appuser
USER appuser

# Por padrão, o container valida o código executando a suíte de testes —
# reforça que nenhuma imagem é publicada sem homologação automatizada.
CMD ["python", "-m", "pytest", "tests/test_harness.py", "-v"]
