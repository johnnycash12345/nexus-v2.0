# Use a imagem oficial do Python
FROM python:3.11-slim

# Define o diretório de trabalho dentro do contêiner
WORKDIR /app

# Copia o arquivo de requisitos primeiro, para otimizar o cache
COPY requirements.txt .

# Instala as dependências
RUN pip install --no-cache-dir -r requirements.txt

# Copia todo o código do backend para o contêiner
COPY . .

# Expõe a porta 8000 (onde o FastAPI roda)
EXPOSE 8000

# Comando para rodar a aplicação quando o contêiner iniciar
# O host 0.0.0.0 é necessário para que ele seja acessível de fora do contêiner
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
