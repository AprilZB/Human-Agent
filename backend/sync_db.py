from app.core.database import engine, Base
import app.models.master_data
import app.models.production
import app.models.system

Base.metadata.create_all(bind=engine)
print("Database synced successfully!")
