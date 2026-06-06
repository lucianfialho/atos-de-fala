// Applies the repo-root db/schema.sql to DATABASE_URL. Same contract the Python pipeline reads.
import { readFileSync } from "node:fs";
import { neon } from "@neondatabase/serverless";

const ddl = readFileSync(new URL("../../db/schema.sql", import.meta.url), "utf-8");
const sql = neon(process.env.DATABASE_URL);
await sql.query(ddl);
console.log("schema applied");
