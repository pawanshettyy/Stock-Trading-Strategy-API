-- CreateTable
CREATE TABLE "StockData" (
    "id" SERIAL NOT NULL,
    "datetime" TIMESTAMP(3) NOT NULL,
    "open" DECIMAL(65,30) NOT NULL,
    "high" DECIMAL(65,30) NOT NULL,
    "low" DECIMAL(65,30) NOT NULL,
    "close" DECIMAL(65,30) NOT NULL,
    "volume" INTEGER NOT NULL,
    "instrument" TEXT NOT NULL,

    CONSTRAINT "StockData_pkey" PRIMARY KEY ("id")
);

-- CreateIndex
CREATE UNIQUE INDEX "StockData_datetime_key" ON "StockData"("datetime");
