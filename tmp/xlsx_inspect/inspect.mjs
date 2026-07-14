import fs from "node:fs/promises";
import path from "node:path";
import { FileBlob, SpreadsheetFile } from "@oai/artifact-tool";

const base = "C:/Users/SSAFY/Desktop/나의_SSAFY_이야기/AI_온보딩_[팀_프로젝트]";
const files = [
  "데이터들/03_3일차_팀프로젝트_실습기획서_작성예제.xlsx",
  "데이터들/03_3일차_팀프로젝트_실습기획서_작성예제 (1).xlsx",
  "데이터들/04_3일차_팀프로젝트_실습기획서_템플렛.xlsx",
];

await fs.mkdir(path.join(base, "tmp/xlsx_inspect/previews"), { recursive: true });

for (const rel of files) {
  const full = path.join(base, rel);
  const workbook = await SpreadsheetFile.importXlsx(await FileBlob.load(full));
  console.log(`\n===== ${path.basename(full)} =====`);
  const sheetInfo = await workbook.inspect({ kind: "sheet", include: "id,name", maxChars: 12000 });
  console.log(sheetInfo.ndjson);
  for (const sheet of workbook.worksheets.items) {
    const used = sheet.getUsedRange();
    console.log(`--- SHEET: ${sheet.name}; USED: ${used?.address ?? "none"} ---`);
    if (used) {
      const region = await workbook.inspect({
        kind: "region",
        sheetId: sheet.name,
        range: used.address,
        maxChars: 30000,
        tableMaxRows: 100,
        tableMaxCols: 30,
        tableMaxCellChars: 400,
      });
      console.log(region.ndjson);
      const preview = await workbook.render({ sheetName: sheet.name, autoCrop: "all", scale: 1.2, format: "png" });
      const safe = `${path.basename(full, ".xlsx")}_${sheet.name}`.replace(/[\\/:*?"<>|]/g, "_");
      await fs.writeFile(path.join(base, `tmp/xlsx_inspect/previews/${safe}.png`), new Uint8Array(await preview.arrayBuffer()));
    }
  }
}
