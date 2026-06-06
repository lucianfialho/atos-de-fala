-- db/schema.sql — contrato compartilhado (web app aplica via migration; Python lê/escreve).
create table if not exists participant (
  id           uuid primary key,   -- gerado pelo cliente (anônimo, crypto.randomUUID); sem default no servidor
  age_band     text not null,
  gender       text not null,
  region       text not null,          -- UF
  education    text not null,
  created_at   timestamptz not null default now()
);

create table if not exists item (
  id           bigserial primary key,
  text         text not null,
  source       text not null default 'synthetic',   -- 'synthetic' | 'news'
  is_honeypot  boolean not null default false,
  created_at   timestamptz not null default now()
);

create table if not exists item_span (
  id            bigserial primary key,
  item_id       bigint not null references item(id) on delete cascade,
  char_start    int not null,
  char_end      int not null,
  ai_act        text not null,
  display_order int not null
);

create table if not exists span_gold (
  item_span_id  bigint primary key references item_span(id) on delete cascade,
  gold_act      text not null
);

create table if not exists vote (
  id             bigserial primary key,
  participant_id uuid not null references participant(id) on delete cascade,
  item_span_id   bigint not null references item_span(id) on delete cascade,
  verdict        text not null,         -- 'agree' | 'disagree'
  corrected_act  text,
  created_at     timestamptz not null default now(),
  unique (participant_id, item_span_id)
);

create table if not exists suggestion (
  id             bigserial primary key,
  participant_id uuid not null references participant(id) on delete cascade,
  item_span_id   bigint not null references item_span(id) on delete cascade,
  text           text not null,
  status         text not null default 'pending',   -- 'pending'|'confirmed'|'rejected'
  created_at     timestamptz not null default now()
);

create table if not exists participant_stats (
  participant_id uuid primary key references participant(id) on delete cascade,
  points         int not null default 0,
  streak         int not null default 0,
  reliability    double precision not null default 0.5,
  items_done     int not null default 0
);

-- spans a human selected-and-marked inside a real transcript (e.g. Roda Viva / FAPESP).
-- The local model proposes spans→acts; the human confirms/corrects (distillation-in-the-loop).
-- Dedicated table: this is already human gold, it doesn't go through the voting pool.
create table if not exists span_annotation (
  id             bigserial primary key,
  participant_id uuid not null references participant(id) on delete cascade,
  source         text not null,              -- corpus, e.g. 'rodaviva'
  source_ref     text not null,              -- interview url/id (provenance)
  speaker        text,                       -- who said it (from the transcript)
  context        text not null,              -- the full turn the span came from
  text           text not null,              -- the span text (the training unit)
  char_start     int not null,               -- offset of span within context
  char_end       int not null,
  act            text not null,              -- human's final label (one of the 13 acts)
  model_act      text,                       -- what the local model proposed (null = human-added span)
  verdict        text not null default 'confirmed', -- 'confirmed' | 'corrected' | 'added'
  created_at     timestamptz not null default now()
);

-- sliding-window rate limiting (one row per allowed mutating request; bucket = "ip:route")
create table if not exists rate_hit (
  id          bigserial primary key,
  bucket      text not null,
  created_at  timestamptz not null default now()
);

create index if not exists idx_vote_span on vote(item_span_id);
create index if not exists idx_span_item on item_span(item_id);
create index if not exists idx_suggestion_status on suggestion(status);
create index if not exists idx_rate_hit_bucket_time on rate_hit(bucket, created_at);
create index if not exists idx_span_annotation_participant on span_annotation(participant_id);
create index if not exists idx_span_annotation_source on span_annotation(source, source_ref);
