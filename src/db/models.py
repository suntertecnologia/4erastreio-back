# models.py

from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    DateTime,
    Date,
    Text,
    ForeignKey,
    Boolean,
)
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime

# Base para todos os nossos modelos declarativos
Base = declarative_base()

# --- DEFINIÇÃO DOS MODELOS (CLASSES) ---


class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True)
    nome = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    senha_hash = Column(String(255), nullable=False)
    cargo = Column(String(50), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

    # Timestamps com valor padrão
    criado_em = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    atualizado_em = Column(DateTime(timezone=True), onupdate=datetime.utcnow)

    # Auto-relacionamento para auditoria (opcional, mas uma boa prática)
    criado_por_id = Column(Integer, ForeignKey("usuarios.id"))
    atualizado_por_id = Column(Integer, ForeignKey("usuarios.id"))


class Entrega(Base):
    __tablename__ = "entregas"

    id = Column(Integer, primary_key=True)
    transportadora = Column(String(100), nullable=False)
    codigo_rastreio = Column(String(100), nullable=False, index=True)
    numero_nf = Column(String(50), index=True)
    cliente = Column(String(255))
    cnpj_destinatario = Column(String(18))
    status = Column(String(100))
    previsao_entrega_inicial = Column(Date)
    previsao_entrega = Column(Date)

    criado_em = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    atualizado_em = Column(DateTime(timezone=True), onupdate=datetime.utcnow)

    criado_por_id = Column(Integer, ForeignKey("usuarios.id"))
    atualizado_por_id = Column(Integer, ForeignKey("usuarios.id"))

    # Relação: Uma Entrega tem muitas Movimentações
    movimentacoes = relationship(
        "EntregaMovimentacao", back_populates="entrega", cascade="all, delete-orphan"
    )


class NotificacaoLog(Base):
    __tablename__ = "notificacoes_log"

    id = Column(Integer, primary_key=True)
    detalhes = Column(Text, nullable=False)
    status = Column(String(50), nullable=False)
    criado_em = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    criado_por_id = Column(Integer, ForeignKey("usuarios.id"))
    entrega_id = Column(Integer, ForeignKey("entregas.id"))


class MovimentacaoNotificacao(Base):
    __tablename__ = "movimentacao_notificacao"

    id = Column(Integer, primary_key=True)
    entrega_id = Column(Integer, ForeignKey("entregas.id"), nullable=False)
    notificacao_id = Column(Integer, ForeignKey("notificacoes_log.id"))
    status = Column(String(50), nullable=False, default="nao notificado")
    criado_em = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)


class EntregaMovimentacao(Base):
    __tablename__ = "entrega_movimentacoes"

    id = Column(Integer, primary_key=True)
    movimento = Column(String(255), nullable=False)
    tipo = Column(String(50))
    dt_movimento = Column(DateTime(timezone=True))
    localizacao = Column(String(255))
    detalhes = Column(Text)

    # Chave estrangeira para a tabela de entregas
    entrega_id = Column(Integer, ForeignKey("entregas.id"), nullable=False)

    # Relação de volta para a Entrega
    entrega = relationship("Entrega", back_populates="movimentacoes")

    criado_em = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    atualizado_em = Column(DateTime(timezone=True), onupdate=datetime.utcnow)

    criado_por_id = Column(Integer, ForeignKey("usuarios.id"))
    atualizado_por_id = Column(Integer, ForeignKey("usuarios.id"))


class ScrapingTask(Base):
    __tablename__ = "scraping_tasks"

    id = Column(Integer, primary_key=True)
    task_id = Column(String(255), unique=True, nullable=False, index=True)
    status = Column(
        String(50), nullable=False, default="PENDING"
    )  # PENDING, SUCCESS, FAILED
    entrega_id = Column(Integer, ForeignKey("entregas.id"), nullable=True)
    error_message = Column(Text, nullable=True)
    created_at = Column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False
    )
    updated_at = Column(DateTime(timezone=True), onupdate=datetime.utcnow)


# As tabelas de notificação podem ser adicionadas de forma similar se necessário...

# --- COMO USAR (Exemplo) ---

# 1. Configurar a conexão com o banco de dados
#    (Isso geralmente fica em um arquivo de configuração)
# DATABASE_URL = "postgresql://seu_usuario:sua_senha@localhost/seu_banco"
# engine = create_engine(DATABASE_URL)


# 2. Criar todas as tabelas no banco de dados
#    (Você só executa isso uma vez na configuração inicial)
def criar_tabelas(engine):
    Base.metadata.create_all(engine)
    print("Tabelas criadas com sucesso!")


if __name__ == "__main__":
    # Este bloco permite que você execute `python models.py` para criar o banco
    # Usando SQLite para o exemplo de criação de tabelas
    sqlite_engine = create_engine("sqlite:///./test.db")
    criar_tabelas(sqlite_engine)
