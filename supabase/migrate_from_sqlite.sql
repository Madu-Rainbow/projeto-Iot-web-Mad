-- Migration from existing Django SQLite dump to Supabase schema
-- Requires prior execution of schema_and_policies.sql
-- 1. Upload CSVs into staging tables, then run mapping inserts.

create schema if not exists staging;

-- Staging tables mirroring SQLite structure (simplified)
create table if not exists staging.auth_user (
  id integer primary key,
  username text,
  email text,
  date_joined timestamptz
);

create table if not exists staging.core_ambiente (
  id integer primary key,
  nome text,
  descricao text,
  usuario_id integer,
  criado_em timestamptz,
  atualizado_em timestamptz
);

create table if not exists staging.core_dispositivo (
  id integer primary key,
  nome text,
  tipo text,
  modelo text,
  fabricante text,
  mac_address text,
  ip_address text,
  status text,
  descricao text,
  firmware_versao text,
  criado_em timestamptz,
  atualizado_em timestamptz,
  ultimo_contato timestamptz,
  ambiente_id integer,
  usuario_id integer
);

create table if not exists staging.core_tiposensor (
  id integer primary key,
  nome text,
  unidade text,
  descricao text
);

create table if not exists staging.core_sensor (
  id integer primary key,
  nome text,
  tipo_id integer,
  dispositivo_id integer,
  ambiente_id integer,
  usuario_id integer,
  valor_minimo double precision,
  valor_maximo double precision,
  precisao int,
  ativo boolean,
  descricao text,
  criado_em timestamptz,
  atualizado_em timestamptz
);

create table if not exists staging.core_leiturasensor (
  id integer primary key,
  sensor_id integer,
  valor double precision,
  timestamp timestamptz,
  observacao text
);

create table if not exists staging.ar_condicionado (
  id integer primary key,
  ligado boolean,
  temperatura int,
  modo text,
  velocidade text,
  inicio_ligado timestamptz
);

-- Map tables
create table if not exists staging.user_map (
  old_user_id int primary key,
  new_user_id uuid not null
);

create table if not exists staging.sensor_type_map (
  old_id int primary key,
  new_id uuid not null
);

create table if not exists staging.ambiente_map (
  old_id int primary key,
  new_id uuid not null
);

create table if not exists staging.dispositivo_map (
  old_id int primary key,
  new_id uuid not null
);

create table if not exists staging.sensor_map (
  old_id int primary key,
  new_id uuid not null
);

-- USER MAP (match by email - ensure emails exist in auth.users beforehand)
insert into staging.user_map (old_user_id, new_user_id)
select au.id, u.id
from staging.auth_user au
join auth.users u on lower(u.email) = lower(au.email)
on conflict (old_user_id) do nothing;

-- SENSOR TYPES
insert into public.sensor_type (id, name, unit, description)
select gen_random_uuid(), t.nome, t.unidade, t.descricao
from staging.core_tiposensor t
on conflict (name) do nothing;

insert into staging.sensor_type_map (old_id, new_id)
select t.id, st.id
from staging.core_tiposensor t
join public.sensor_type st on st.name = t.nome
on conflict (old_id) do nothing;

-- AMBIENTE
insert into public.ambiente (id, name, description, user_id, created_at, updated_at)
select gen_random_uuid(), a.nome, a.descricao, um.new_user_id,
       coalesce(a.criado_em, now()), coalesce(a.atualizado_em, now())
from staging.core_ambiente a
join staging.user_map um on um.old_user_id = a.usuario_id
on conflict (name, user_id) do nothing;

insert into staging.ambiente_map (old_id, new_id)
select a.id, amb.id
from staging.core_ambiente a
join public.ambiente amb on amb.name = a.nome
join staging.user_map um on um.new_user_id = amb.user_id and um.old_user_id = a.usuario_id
on conflict (old_id) do nothing;

-- DISPOSITIVO
insert into public.dispositivo (
  id, name, type_code, model, manufacturer, mac_address, ip_address,
  status_code, ambiente_id, user_id, description, firmware_version,
  last_contact, created_at, updated_at)
select gen_random_uuid(), d.nome, d.tipo, d.modelo, d.fabricante, d.mac_address,
       nullif(d.ip_address,'')::inet, d.status, am.new_id, um.new_user_id,
       d.descricao, d.firmware_versao, d.ultimo_contato,
       coalesce(d.criado_em, now()), coalesce(d.atualizado_em, now())
from staging.core_dispositivo d
join staging.ambiente_map am on am.old_id = d.ambiente_id
join staging.user_map um on um.old_user_id = d.usuario_id
on conflict (mac_address) do nothing;

insert into staging.dispositivo_map (old_id, new_id)
select d.id, disp.id
from staging.core_dispositivo d
join public.dispositivo disp on disp.mac_address = d.mac_address
on conflict (old_id) do nothing;

-- SENSOR
insert into public.sensor (
  id, name, sensor_type_id, dispositivo_id, ambiente_id, user_id,
  min_value, max_value, precision_digits, active, description,
  created_at, updated_at)
select gen_random_uuid(), s.nome, stm.new_id, dm.new_id, am.new_id, um.new_user_id,
       s.valor_minimo, s.valor_maximo, coalesce(s.precisao,2), coalesce(s.ativo,true), s.descricao,
       coalesce(s.criado_em, now()), coalesce(s.atualizado_em, now())
from staging.core_sensor s
join staging.sensor_type_map stm on stm.old_id = s.tipo_id
join staging.dispositivo_map dm on dm.old_id = s.dispositivo_id
join staging.ambiente_map am on am.old_id = s.ambiente_id
join staging.user_map um on um.old_user_id = s.usuario_id
on conflict do nothing;

insert into staging.sensor_map (old_id, new_id)
select s.id, sens.id
from staging.core_sensor s
join public.sensor sens on sens.name = s.nome
join staging.dispositivo_map dm on dm.new_id = sens.dispositivo_id and dm.old_id = s.dispositivo_id
on conflict (old_id) do nothing;

-- LEITURA SENSOR
insert into public.leitura_sensor (id, sensor_id, value, timestamp, note)
select gen_random_uuid(), sm.new_id, l.valor, l.timestamp, l.observacao
from staging.core_leiturasensor l
join staging.sensor_map sm on sm.old_id = l.sensor_id
on conflict do nothing;

-- AR CONDICIONADO (no user mapping originally; can attach later manually)
insert into public.ar_condicionado (id, ligado, temperatura, modo, velocidade, inicio_ligado, created_at, updated_at)
select gen_random_uuid(), a.ligado, a.temperatura, a.modo, a.velocidade, a.inicio_ligado, now(), now()
from staging.ar_condicionado a
on conflict do nothing;

-- Verification queries (optional)
-- select count(*) from public.ambiente;
-- select count(*) from public.dispositivo;
-- select count(*) from public.sensor;
-- select count(*) from public.leitura_sensor;

-- Cleanup (uncomment after validation)
-- drop schema staging cascade;
