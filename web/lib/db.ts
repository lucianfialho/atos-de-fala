// Neon serverless client. `sql` is a tagged-template query fn (parametrized, safe).
// DATABASE_URL is set in Vercel + .env.local.
import { neon } from "@neondatabase/serverless";

export const sql = neon(process.env.DATABASE_URL!);
