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
