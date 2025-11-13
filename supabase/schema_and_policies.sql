-- Supabase schema and RLS policies (idempotent)
-- Run this in Supabase SQL editor.

-- Extensions
create extension if not exists "uuid-ossp";
create extension if not exists pgcrypto;

-- Lookup tables
create table if not exists public.device_type (
  code text primary key,
  name text not null unique
);

create table if not exists public.device_status (
  code text primary key,
  name text not null unique
);

create table if not exists public.sensor_type (
  id uuid primary key default gen_random_uuid(),
  name text not null unique,
  unit text not null,
  description text
);

comment on table public.sensor_type is 'Tipos de sensores (equiv. TipoSensor)';
comment on column public.sensor_type.unit is 'Unidade de medida';

insert into public.device_type (code, name) values
  ('sensor','Sensor'),
  ('atuador','Atuador'),
  ('controlador','Controlador'),
  ('gateway','Gateway'),
  ('outro','Outro')
on conflict (code) do nothing;

insert into public.device_status (code, name) values
  ('ativo','Ativo'),
  ('inativo','Inativo'),
  ('manutencao','Manutenção'),
  ('erro','Erro')
on conflict (code) do nothing;

-- Ambiente
create table if not exists public.ambiente (
  id uuid primary key default gen_random_uuid(),
  name text not null,
  description text,
  user_id uuid not null references auth.users(id) on delete cascade,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create index if not exists ambiente_user_idx on public.ambiente(user_id);
create index if not exists ambiente_name_idx on public.ambiente(lower(name));
comment on table public.ambiente is 'Ambientes (Sala, Cozinha...)';

-- Dispositivo
create table if not exists public.dispositivo (
  id uuid primary key default gen_random_uuid(),
  name text not null,
  type_code text not null references public.device_type(code),
  model text,
  manufacturer text,
  mac_address text not null unique,
  ip_address inet,
  status_code text not null default 'ativo' references public.device_status(code),
  ambiente_id uuid not null references public.ambiente(id) on delete cascade,
  user_id uuid not null references auth.users(id) on delete cascade,
  description text,
  firmware_version text,
  last_contact timestamptz,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create index if not exists dispositivo_ambiente_idx on public.dispositivo(ambiente_id);
create index if not exists dispositivo_user_idx on public.dispositivo(user_id);
create index if not exists dispositivo_status_idx on public.dispositivo(status_code);
create index if not exists dispositivo_last_contact_idx on public.dispositivo(last_contact);
comment on table public.dispositivo is 'Dispositivos IoT';
comment on column public.dispositivo.mac_address is 'Endereço MAC único';

-- Sensor
create table if not exists public.sensor (
  id uuid primary key default gen_random_uuid(),
  name text not null,
  sensor_type_id uuid not null references public.sensor_type(id),
  dispositivo_id uuid not null references public.dispositivo(id) on delete cascade,
  ambiente_id uuid not null references public.ambiente(id) on delete cascade,
  user_id uuid not null references auth.users(id) on delete cascade,
  min_value double precision,
  max_value double precision,
  precision_digits int not null default 2,
  active boolean not null default true,
  description text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  unique (dispositivo_id, sensor_type_id)
);

create index if not exists sensor_dispositivo_idx on public.sensor(dispositivo_id);
create index if not exists sensor_ambiente_idx on public.sensor(ambiente_id);
create index if not exists sensor_user_idx on public.sensor(user_id);
create index if not exists sensor_active_idx on public.sensor(active);
comment on table public.sensor is 'Sensores específicos ligados a dispositivos';
comment on column public.sensor.precision_digits is 'Casas decimais para formatação';

-- Leitura do Sensor
create table if not exists public.leitura_sensor (
  id uuid primary key default gen_random_uuid(),
  sensor_id uuid not null references public.sensor(id) on delete cascade,
  value double precision not null,
  timestamp timestamptz not null default now(),
  note text
);

create index if not exists leitura_sensor_sensor_time_idx on public.leitura_sensor(sensor_id, timestamp desc);
create index if not exists leitura_sensor_time_idx on public.leitura_sensor(timestamp desc);
comment on table public.leitura_sensor is 'Leituras capturadas dos sensores';

-- Ar Condicionado
create table if not exists public.ar_condicionado (
  id uuid primary key default gen_random_uuid(),
  ligado boolean not null default false,
  temperatura int not null default 24,
  modo text not null default 'Frio',
  velocidade text not null default 'Média',
  inicio_ligado timestamptz,
  ambiente_id uuid references public.ambiente(id) on delete set null,
  user_id uuid references auth.users(id) on delete cascade,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create index if not exists ar_condicionado_user_idx on public.ar_condicionado(user_id);
create index if not exists ar_condicionado_amb_idx on public.ar_condicionado(ambiente_id);
comment on table public.ar_condicionado is 'Estado de aparelhos de ar condicionado';

-- updated_at trigger
create or replace function public.set_updated_at()
returns trigger language plpgsql as $$
begin
  new.updated_at = now();
  return new;
end; $$;

drop trigger if exists set_updated_at_ambiente on public.ambiente;
create trigger set_updated_at_ambiente before update on public.ambiente
for each row execute procedure public.set_updated_at();

drop trigger if exists set_updated_at_dispositivo on public.dispositivo;
create trigger set_updated_at_dispositivo before update on public.dispositivo
for each row execute procedure public.set_updated_at();

drop trigger if exists set_updated_at_sensor on public.sensor;
create trigger set_updated_at_sensor before update on public.sensor
for each row execute procedure public.set_updated_at();

drop trigger if exists set_updated_at_ar_condicionado on public.ar_condicionado;
create trigger set_updated_at_ar_condicionado before update on public.ar_condicionado
for each row execute procedure public.set_updated_at();

-- Enable RLS
alter table public.ambiente enable row level security;
alter table public.dispositivo enable row level security;
alter table public.sensor enable row level security;
alter table public.leitura_sensor enable row level security;
alter table public.ar_condicionado enable row level security;
alter table public.sensor_type enable row level security;
alter table public.device_type enable row level security;
alter table public.device_status enable row level security;

-- Policies (drop if exists then create for idempotency)
do $$ begin
  -- Lookup selects
  execute 'drop policy if exists "Select lookup tables" on public.device_type';
  execute 'create policy "Select lookup tables" on public.device_type for select using (true)';

  execute 'drop policy if exists "Select lookup tables status" on public.device_status';
  execute 'create policy "Select lookup tables status" on public.device_status for select using (true)';

  execute 'drop policy if exists "Select sensor types" on public.sensor_type';
  execute 'create policy "Select sensor types" on public.sensor_type for select using (true)';

  -- Ambiente
  execute 'drop policy if exists "Select own ambientes" on public.ambiente';
  execute 'create policy "Select own ambientes" on public.ambiente for select using (auth.uid() = user_id)';

  execute 'drop policy if exists "Insert own ambientes" on public.ambiente';
  execute 'create policy "Insert own ambientes" on public.ambiente for insert with check (auth.uid() = user_id)';

  execute 'drop policy if exists "Update own ambientes" on public.ambiente';
  execute 'create policy "Update own ambientes" on public.ambiente for update using (auth.uid() = user_id) with check (auth.uid() = user_id)';

  execute 'drop policy if exists "Delete own ambientes" on public.ambiente';
  execute 'create policy "Delete own ambientes" on public.ambiente for delete using (auth.uid() = user_id)';

  -- Dispositivo
  execute 'drop policy if exists "Select own dispositivos" on public.dispositivo';
  execute 'create policy "Select own dispositivos" on public.dispositivo for select using (auth.uid() = user_id)';

  execute 'drop policy if exists "Modify own dispositivos" on public.dispositivo';
  execute 'create policy "Modify own dispositivos" on public.dispositivo for all using (auth.uid() = user_id) with check (auth.uid() = user_id)';

  -- Sensor
  execute 'drop policy if exists "Select own sensores" on public.sensor';
  execute 'create policy "Select own sensores" on public.sensor for select using (auth.uid() = user_id)';

  execute 'drop policy if exists "Modify own sensores" on public.sensor';
  execute 'create policy "Modify own sensores" on public.sensor for all using (auth.uid() = user_id) with check (auth.uid() = user_id)';

  -- Leitura sensor
  execute 'drop policy if exists "Select leituras by owner" on public.leitura_sensor';
  execute $pol$create policy "Select leituras by owner" on public.leitura_sensor
           for select using (
             exists (
               select 1 from public.sensor s
               where s.id = leitura_sensor.sensor_id and s.user_id = auth.uid()
             )
           )$pol$;

  execute 'drop policy if exists "Insert leituras by owner" on public.leitura_sensor';
  execute $pol$create policy "Insert leituras by owner" on public.leitura_sensor
           for insert with check (
             exists (
               select 1 from public.sensor s
               where s.id = leitura_sensor.sensor_id and s.user_id = auth.uid()
             )
           )$pol$;

  -- Ar Condicionado
  execute 'drop policy if exists "Select own ar_condicionado" on public.ar_condicionado';
  execute 'create policy "Select own ar_condicionado" on public.ar_condicionado for select using (user_id is not null and auth.uid() = user_id)';

  execute 'drop policy if exists "Modify own ar_condicionado" on public.ar_condicionado';
  execute 'create policy "Modify own ar_condicionado" on public.ar_condicionado for all using (auth.uid() = user_id) with check (auth.uid() = user_id)';
end $$;

-- End of schema and policies
