from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import os
from passlib.context import CryptContext

Base = declarative_base()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto", bcrypt__rounds=12)


class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    username = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    sessions = relationship("ChatSession", back_populates="user", cascade="all, delete-orphan")
    exploit_attempts = relationship("ExploitAttempt", back_populates="user", cascade="all, delete-orphan")


class ChatSession(Base):
    __tablename__ = 'chat_sessions'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    title = Column(String(255), default='New Chat')
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = relationship("User", back_populates="sessions")
    messages = relationship("ChatMessage", back_populates="session", cascade="all, delete-orphan")


class ChatMessage(Base):
    __tablename__ = 'chat_messages'
    
    id = Column(Integer, primary_key=True)
    session_id = Column(Integer, ForeignKey('chat_sessions.id', ondelete='CASCADE'), nullable=False)
    role = Column(String(50), nullable=False)  # 'user' or 'assistant'
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    session = relationship("ChatSession", back_populates="messages")


class ExploitAttempt(Base):
    """Log of exploit attempts for tracking student progress"""
    __tablename__ = 'exploit_attempts'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    session_id = Column(Integer, ForeignKey('chat_sessions.id', ondelete='SET NULL'), nullable=True)
    vulnerability_type = Column(String(100), nullable=False)
    challenge_id = Column(String(10), nullable=True)
    payload = Column(Text)
    success = Column(Boolean, default=False)
    response = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="exploit_attempts")


class Database:
    def __init__(self):
        self.database_url = os.getenv('DATABASE_URL', 'postgresql://labuser:labpass123@postgres:5432/donk_ai_lab')
        self.engine = create_engine(self.database_url)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        self._test_connection()
        self._initialize_database()
    
    def _test_connection(self):
        try:
            with self.engine.connect():
                print("✅ Database connected successfully")
        except Exception as e:
            print(f"❌ Database connection failed: {e}")
            raise
    
    def _initialize_database(self):
        try:
            Base.metadata.create_all(bind=self.engine)

            with self.engine.connect() as conn:
                from sqlalchemy import text
                conn.execute(text(
                    "ALTER TABLE exploit_attempts ADD COLUMN IF NOT EXISTS challenge_id VARCHAR(10)"
                ))
                conn.commit()

            with self.SessionLocal() as session:
                user_count = session.query(User).count()
                
                if user_count == 0:
                    print("📝 Creating demo users...")
                    self._create_demo_users(session)
                    print("✅ Demo users created successfully")
                else:
                    print(f"✅ Database already initialized ({user_count} users exist)")
        
        except Exception as e:
            print(f"❌ Database initialization error: {e}")
            import traceback
            traceback.print_exc()
    
    def _create_demo_users(self, session):
        demo_users = [
            {
                "username": "alice",
                "password": "password123",
                "is_admin": False
            },
            {
                "username": "bob",
                "password": "password123",
                "is_admin": False
            },
            {
                "username": "admin",
                "password": "admin123",
                "is_admin": True
            }
        ]
        
        for user_data in demo_users:
            password_hash = pwd_context.hash(user_data["password"])
            user = User(
                username=user_data["username"],
                password_hash=password_hash,
                is_admin=user_data["is_admin"]
            )
            session.add(user)
        
        session.commit()
        
        print("\n" + "="*60)
        print("DEMO USER CREDENTIALS")
        print("="*60)
        for user_data in demo_users:
            print(f"  Username: {user_data['username']:<10} Password: {user_data['password']}")
        print("="*60 + "\n")
    
    def authenticate_user(self, username: str, password: str):
        with self.SessionLocal() as session:
            print(f"🔍 Login attempt - Username: {username}")
            user = session.query(User).filter(User.username == username).first()
            
            if user:
                print(f"✅ User found: {user.username}, ID: {user.id}")
                password_match = pwd_context.verify(password, user.password_hash)
                
                if password_match:
                    print(f"✅ Authentication successful for {user.username}")
                    return user
                else:
                    print(f"❌ Password mismatch for {user.username}")
            else:
                print(f"❌ User not found: {username}")
            
            return None
    
    def create_session(self, user_id: int, title: str = "New Chat"):
        with self.SessionLocal() as session:
            chat_session = ChatSession(
                user_id=user_id,
                title=title
            )
            session.add(chat_session)
            session.commit()
            session.refresh(chat_session)
            return chat_session
    
    def get_session(self, session_id: int):
        with self.SessionLocal() as session:
            return session.query(ChatSession).filter(ChatSession.id == session_id).first()
    
    def get_user_sessions(self, user_id: int):
        with self.SessionLocal() as session:
            return session.query(ChatSession).filter(ChatSession.user_id == user_id).all()
    
    def delete_session(self, session_id: int):
        with self.SessionLocal() as session:
            session.query(ChatMessage).filter(ChatMessage.session_id == session_id).delete()
            chat_session = session.query(ChatSession).filter(ChatSession.id == session_id).first()
            if chat_session:
                session.delete(chat_session)
                session.commit()
                return True
            return False
    
    def save_message(self, session_id: int, role: str, content: str):
        with self.SessionLocal() as session:
            message = ChatMessage(
                session_id=session_id,
                role=role,
                content=content
            )
            session.add(message)
            session.commit()
            return message
    
    def get_session_messages(self, session_id: int):
        with self.SessionLocal() as session:
            messages = session.query(ChatMessage).filter(
                ChatMessage.session_id == session_id
            ).order_by(ChatMessage.created_at).all()
            
            return [
                {
                    "id": msg.id,
                    "role": msg.role,
                    "content": msg.content,
                    "created_at": msg.created_at.isoformat()
                }
                for msg in messages
            ]
    
    def log_exploit_attempt(self, user_id: int, vulnerability_type: str,
                           payload: str, success: bool, response: str = "",
                           session_id: int = None, challenge_id: str = None):
        with self.SessionLocal() as session:
            attempt = ExploitAttempt(
                user_id=user_id,
                session_id=session_id,
                vulnerability_type=vulnerability_type,
                challenge_id=challenge_id,
                payload=payload,
                success=success,
                response=response
            )
            session.add(attempt)
            session.commit()
            return attempt

    def get_attempts_for_challenge(self, user_id: int, vulnerability_type: str, challenge_id: str):
        with self.SessionLocal() as session:
            attempts = session.query(ExploitAttempt).filter(
                ExploitAttempt.user_id == user_id,
                ExploitAttempt.vulnerability_type == vulnerability_type,
                ExploitAttempt.challenge_id == challenge_id,
            ).order_by(ExploitAttempt.created_at.desc()).all()

            return [
                {
                    "id": a.id,
                    "payload": a.payload,
                    "success": a.success,
                    "response": a.response,
                    "created_at": a.created_at.isoformat(),
                }
                for a in attempts
            ]
    
    def get_exploit_attempts(self, user_id: int = None):
        with self.SessionLocal() as session:
            query = session.query(ExploitAttempt)
            
            if user_id:
                query = query.filter(ExploitAttempt.user_id == user_id)
            
            attempts = query.order_by(ExploitAttempt.created_at.desc()).all()
            
            return [
                {
                    "id": attempt.id,
                    "user_id": attempt.user_id,
                    "vulnerability_type": attempt.vulnerability_type,
                    "payload": attempt.payload,
                    "success": attempt.success,
                    "response": attempt.response,
                    "created_at": attempt.created_at.isoformat()
                }
                for attempt in attempts
            ]
    
    def get_all_exploit_attempts(self):
        with self.SessionLocal() as session:
            attempts = session.query(ExploitAttempt).order_by(ExploitAttempt.created_at.desc()).all()
            return attempts
    
    def create_user(self, username: str, password: str):
        with self.SessionLocal() as session:
            existing = session.query(User).filter(User.username == username).first()
            if existing:
                raise ValueError(f"Username '{username}' already taken")
            
            from passlib.context import CryptContext
            pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")
            user = User(
                username=username,
                password_hash=pwd_ctx.hash(password)
            )
            session.add(user)
            session.commit()
            session.refresh(user)
            print(f"✅ Created new user: {user.username}, ID: {user.id}")
            return user

    def get_all_users(self):
        with self.SessionLocal() as session:
            return session.query(User).all()
    
    def delete_user(self, user_id: int):
        with self.SessionLocal() as session:
            user = session.query(User).filter(User.id == user_id).first()
            if user:
                session.delete(user)
                session.commit()
                return True
            return False
    
    def execute_raw_query(self, query: str):
        with self.SessionLocal() as session:
            try:
                from sqlalchemy import text
                session.execute(text(query))
                session.commit()
                return {"status": "executed", "query": query}
            except Exception as e:
                session.rollback()
                raise Exception(f"Query execution failed: {str(e)}")


if __name__ == "__main__":
    print("Testing database connection...")
    db = Database()
    print("✅ Database test successful!")
