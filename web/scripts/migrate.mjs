// Applies the repo-root db/schema.sql to DATABASE_URL. Same contract the Python pipeline reads.
// Neon's HTTP driver runs ONE statement per query(), so we strip SQL comments and split the
// DDL on ';' into individual statements. (Our schema has no ';' or '--' inside string literals.)
import { readFileSync } from "node:fs";
import { neon } from "@neondatabase/serverless";

const ddl = readFileSync(new URL("../../db/schema.sql", import.meta.url), "utf-8");
const statements = ddl
  .replace(/--[^\n]*/g, "")        // drop line comments (full-line and trailing)
  .split(";")
  .map((s) => s.trim())
  .filter(Boolean);

const sql = neon(process.env.DATABASE_URL);
for (const stmt of statements) {
  await sql.query(stmt);
}
console.log(`schema applied (${statements.length} statements)`);
