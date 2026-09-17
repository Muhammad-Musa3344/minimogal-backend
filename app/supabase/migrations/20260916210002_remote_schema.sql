SET local check_function_bodies = off;

CREATE TABLE "public"."dialogue_guidance" (
  "id"                 uuid                     NOT NULL DEFAULT gen_random_uuid(),
  "decision"           text                     NOT NULL,
  "level"              text,
  "audio_text"         text,
  "guidance"           text,
  "concept"            text,
  "tradeoff"           text,
  "recommended_action" text,
  "source_status"      text,
  "created_at"         timestamp with time zone,
  CONSTRAINT "dialogue_guidance_pkey" PRIMARY KEY (id)
);

ALTER TABLE "public"."dialogue_guidance"
  ENABLE ROW LEVEL SECURITY;

CREATE TABLE "public"."self_evaluations" (
  "id"                uuid                     NOT NULL,
  "guidance_id"       uuid                     NOT NULL,
  "question"          text,
  "choices"           jsonb,
  "model"             text,
  "generation_status" text,
  "qa_status"         text,
  "updated_at"        timestamp with time zone,
  "created_at"        timestamp with time zone NOT NULL DEFAULT now(),
  CONSTRAINT "self_evaluations_pkey" PRIMARY KEY (id, guidance_id)
);

ALTER TABLE "public"."self_evaluations"
  ENABLE ROW LEVEL SECURITY;

CREATE OR REPLACE FUNCTION public.handle_new_user_household()
  RETURNS TRIGGER
  LANGUAGE plpgsql
  SECURITY DEFINER
  SET search_path TO 'public'
  AS $function$
begin
  insert into public.households (id, email, auth_provider, email_verified, created_at)
  values (
    new.id,
    new.email,
    coalesce(new.raw_app_meta_data->>'provider', 'email'),
    coalesce((new.email_confirmed_at is not null), false),
    coalesce(new.created_at, now())
  )
  on conflict (id) do update set
    email = excluded.email,
    email_verified = excluded.email_verified;
  return new;
end;
$function$;

CREATE OR REPLACE FUNCTION public.update_vocabulary_tiers_timestamp()
  RETURNS TRIGGER
  LANGUAGE plpgsql
  AS $function$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$function$;

ALTER TABLE "public"."self_evaluations"
  ADD CONSTRAINT "self_evaluations_guidance_id_fkey" FOREIGN KEY (guidance_id) REFERENCES public.dialogue_guidance(id);

CREATE TRIGGER on_auth_user_created_household
  AFTER INSERT ON auth.users
  FOR EACH ROW
  EXECUTE FUNCTION public.handle_new_user_household();

COMMENT ON TABLE "public"."dialogue_guidance" IS 'This Table represents the dialogue of the child and guidance of the LLM';

GRANT EXECUTE ON FUNCTION "public"."handle_new_user_household"() TO PUBLIC, "anon", "authenticated", "postgres", "service_role";

GRANT DELETE, INSERT, MAINTAIN, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE ON TABLE "public"."dialogue_guidance" TO "anon", "authenticated", "postgres", "service_role";

GRANT DELETE, INSERT, MAINTAIN, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE ON TABLE "public"."self_evaluations" TO "anon", "authenticated", "postgres", "service_role";

