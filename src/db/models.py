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
    Boolean
)
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

# Base para todos os nossos modelos declarativos
Base = declarative_base()

# --- DEFINIÇÃO DOS MODELOS (CLASSES) ---

class Usuario(Base):
    __tablename__ = 'usuarios'

    id = Column(Integer, primary_key=True)
    nome = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    senha_hash = Column(String(255), nullable=False)
    cargo = Column(String(50), nullable=False)
    is_active = Column(Boolean, default=True)
    
    # Timestamps com valor padrão
    criado_em = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    atualizado_em = Column(DateTime(timezone=True), onupdate=datetime.utcnow)
    
    # Auto-relacionamento para auditoria (opcional, mas uma boa prática)
    criado_por_id = Column(Integer, ForeignKey('usuarios.id'))
    atualizado_por_id = Column(Integer, ForeignKey('usuarios.id'))

class PasswordResetToken(Base):
    __tablename__ = 'password_reset_tokens'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('usuarios.id'), nullable=False)
    token = Column(String(255), unique=True, nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    is_used = Column(Boolean, default=False)
    criado_em = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

class Entrega(Base):
    __tablename__ = 'entregas'

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
    
    criado_por_id = Column(Integer, ForeignKey('usuarios.id'))
    atualizado_por_id = Column(Integer, ForeignKey('usuarios.id'))
    
    # Relação: Uma Entrega tem muitas Movimentações
    movimentacoes = relationship("EntregaMovimentacao", back_populates="entrega", cascade="all, delete-orphan")

class EntregaMovimentacao(Base):
    __tablename__ = 'entrega_movimentacoes'

    id = Column(Integer, primary_key=True)
    movimento = Column(String(255), nullable=False)
    tipo = Column(String(50))
    dt_movimento = Column(DateTime(timezone=True))
    localizacao = Column(String(255))
    detalhes = Column(Text)
    
    # Chave estrangeira para a tabela de entregas
    entrega_id = Column(Integer, ForeignKey('entregas.id'), nullable=False)
    
    # Relação de volta para a Entrega
    entrega = relationship("Entrega", back_populates="movimentacoes")
    
    criado_em = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    atualizado_em = Column(DateTime(timezone=True), onupdate=datetime.utcnow)
    
    criado_por_id = Column(Integer, ForeignKey('usuarios.id'))
    atualizado_por_id = Column(Integer, ForeignKey('usuarios.id'))

# As tabelas de notificação podem ser adicionadas de forma similar se necessário...

# --- COMO USAR (Exemplo) ---

# 1. Configurar a conexão com o banco de dados
#    (Isso geralmente fica em um arquivo de configuração)
DATABASE_URL = "postgresql://seu_usuario:sua_senha@localhost/seu_banco"
engine = create_engine(DATABASE_URL)

# 2. Criar todas as tabelas no banco de dados
#    (Você só executa isso uma vez na configuração inicial)
def criar_tabelas():
    Base.metadata.create_all(engine)
    print("Tabelas criadas com sucesso!")

if __name__ == "__main__":
    # Este bloco permite que você execute `python models.py` para criar o banco
    criar_tabelas()