const { PrismaClient } = require("@prisma/client");
const xlsx = require("xlsx");
const path = require("path");

const prisma = new PrismaClient();
const filePath = path.join(__dirname, "HINDALCO_1D.xlsx");

// Load Excel file
const workbook = xlsx.readFile(filePath);
const sheetName = workbook.SheetNames[0];
const sheetData = xlsx.utils.sheet_to_json(workbook.Sheets[sheetName]);

async function seedDatabase() {
  try {
    for (const row of sheetData) {
      const datetimeValue = new Date(row.datetime);

      if (isNaN(datetimeValue.getTime())) {
        console.error("Skipping invalid datetime:", row.datetime);
        continue;
      }

      // Check if the record already exists
      const existingRecord = await prisma.stockData.findUnique({
        where: { datetime: datetimeValue },
      });

      if (!existingRecord) {
        await prisma.stockData.create({
          data: {
            datetime: datetimeValue,
            open: parseFloat(row.open),
            high: parseFloat(row.high),
            low: parseFloat(row.low),
            close: parseFloat(row.close),
            volume: parseInt(row.volume, 10),
            instrument: row.instrument || "HINDALCO",
          },
        });
      } else {
        console.log(`Skipping duplicate datetime: ${datetimeValue}`);
      }
    }
    console.log("✅ Data successfully seeded into PostgreSQL!");
  } catch (error) {
    console.error("❌ Error seeding data:", error);
  } finally {
    await prisma.$disconnect();
  }
}

seedDatabase();
