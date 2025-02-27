import pandas as pd
from prisma import Prisma
from datetime import datetime

# Initialize Prisma Client
db = Prisma()

async def seed_database():
    await db.connect()
    file_path = "HINDALCO_1D.xlsx"

    try:
        # Load Excel File
        df = pd.read_excel(file_path, engine="openpyxl")

        # Convert datetime column
        df["datetime"] = pd.to_datetime(df["datetime"], errors="coerce")

        # Drop rows with invalid datetime
        df = df.dropna(subset=["datetime"])

        # Insert each row
        for _, row in df.iterrows():
            datetime_value = row["datetime"].to_pydatetime()

            # Check if record already exists
            existing_record = await db.stockdata.find_first(where={"datetime": datetime_value})

            if not existing_record:
                await db.stockdata.create(
                    data={
                        "datetime": datetime_value,
                        "open": float(row["open"]),
                        "high": float(row["high"]),
                        "low": float(row["low"]),
                        "close": float(row["close"]),
                        "volume": int(row["volume"]),
                        "instrument": row.get("instrument", "HINDALCO"),
                    }
                )
            else:
                print(f"Skipping duplicate datetime: {datetime_value}")

        print("✅ Data successfully seeded into PostgreSQL!")

    except Exception as e:
        print(f"❌ Error seeding data: {e}")

    finally:
        await db.disconnect()

# Run the function
import asyncio
asyncio.run(seed_database())
