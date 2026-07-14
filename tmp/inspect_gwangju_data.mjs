import fs from "node:fs/promises";
import path from "node:path";

const dir = "C:/Users/SSAFY/Desktop/나의_SSAFY_이야기/AI_온보딩_[팀_프로젝트]/데이터들/data/광주_전라권";
const names = (await fs.readdir(dir)).filter((name) => name.endsWith(".json")).sort();

for (const name of names) {
  const raw = await fs.readFile(path.join(dir, name), "utf8");
  const data = JSON.parse(raw);
  const items = Array.isArray(data) ? data : (data.items ?? []);
  const fieldCounts = {};
  const areaCounts = {};
  let imageCount = 0;
  let coordCount = 0;
  for (const item of items) {
    for (const key of Object.keys(item)) fieldCounts[key] = (fieldCounts[key] ?? 0) + 1;
    if (item.firstimage) imageCount++;
    if (item.mapx && item.mapy) coordCount++;
    const addr = item.addr1 ?? "";
    const area = ["광주광역시", "전라남도", "전북특별자치도", "전라북도"].find((x) => addr.startsWith(x)) ?? addr.split(" ")[0] ?? "미상";
    areaCounts[area || "미상"] = (areaCounts[area || "미상"] ?? 0) + 1;
  }
  console.log(JSON.stringify({
    file: name,
    region: data.region,
    contentType: data.contentType,
    declaredTotal: data.total,
    actualItems: items.length,
    withImage: imageCount,
    withCoords: coordCount,
    areas: areaCounts,
    fields: Object.keys(fieldCounts),
    samples: items.slice(0, 3).map(({title, addr1, mapx, mapy, eventstartdate, eventenddate, firstimage}) => ({title, addr1, mapx, mapy, eventstartdate, eventenddate, hasImage: Boolean(firstimage)})),
  }, null, 2));
}
