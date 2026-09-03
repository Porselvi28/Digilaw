from sqlalchemy import text

from app.database.connection import engine


try:

    with engine.connect() as connection:

        result = connection.execute(
            text("SELECT version();")
        )

        print("PostgreSQL connection successful!")

        print(
            result.fetchone()[0]
        )

except Exception as error:

    print("PostgreSQL connection failed!")

    print(error)