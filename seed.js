const { PrismaClient } = require("@prisma/client");
const xlsx = require("xlsx");
const prisma = new PrismaClient();

// Load Excel file
const workbook = xlsx.readFile("HINDALCO_1D.xlsx");
const sheetName = workbook.SheetNames[0];
const sheetData = xlsx.utils.sheet_to_json(workbook.Sheets[sheetName]);

async function seedDatabase() {
  try {
    for (const row of sheetData) {
      await prisma.stockData.create({
        data: {
          datetime: new Date(row.datetime),
          open: parseFloat(row.open),
          high: parseFloat(row.high),
          low: parseFloat(row.low),
          close: parseFloat(row.close),
          volume: parseInt(row.volume, 10),
          instrument: row.instrument || "HINDALCO",
        },
      });
    }
    console.log("✅ Data successfully seeded into PostgreSQL!");
  } catch (error) {
    console.error("❌ Error seeding data:", error);
  } finally {
    await prisma.$disconnect();
  }
}

seedDatabase();
