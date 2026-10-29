import os
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

# 1. Получаем URL из переменной окружения, которую вы задали в интерфейсе Render
DATABASE_URL = os.environ.get("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError("Переменная DATABASE_URL не найдена в окружении. Проверьте настройки на Render.")

# 2. Создаем асинхронный движок
# pool_pre_ping=True защищает от обрыва соединения, если БД "уснула" (важно для бесплатного плана Render)
engine = create_async_engine(DATABASE_URL, echo=True, pool_pre_ping=True)

# 3. Создаем фабрику сессий
AsyncSessionLocal = sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False
)

# 4. Зависимость (Dependency) для получения сессии в роутах
async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

app = FastAPI()

# 5. Тестовый маршрут для проверки подключения к БД
@app.get("/test-db")
async def read_test_db(db: AsyncSession = Depends(get_db)):
    try:
        # Выполняем простой запрос к системной таблице, чтобы проверить связь
        result = await db.execute(text("SELECT 1"))
        value = result.scalar_one_or_none()
        if value == 1:
            return {"status": "success", "db_check": "PostgreSQL connection OK"}
        else:
            raise HTTPException(status_code=500, detail="DB check failed")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database connection error: {str(e)}")

@app.get("/")
def read_root():
    return {"message": "Hello from Render!"}