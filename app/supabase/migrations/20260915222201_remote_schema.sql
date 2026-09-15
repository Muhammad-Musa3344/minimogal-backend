SET local check_function_bodies = off;

CREATE SEQUENCE "public"."age_level_mapping_mapping_id_seq" AS bigint INCREMENT BY 1 MINVALUE 1 MAXVALUE 9223372036854775807 START WITH 1 CACHE 1 NO CYCLE;

CREATE SEQUENCE "public"."badge_requirements_id_seq" AS integer INCREMENT BY 1 MINVALUE 1 MAXVALUE 2147483647 START WITH 1 CACHE 1 NO CYCLE;

CREATE SEQUENCE "public"."customer_responses_response_id_seq" AS bigint INCREMENT BY 1 MINVALUE 1 MAXVALUE 9223372036854775807 START WITH 1 CACHE 1 NO CYCLE;

CREATE SEQUENCE "public"."customer_types_type_id_seq" AS bigint INCREMENT BY 1 MINVALUE 1 MAXVALUE 9223372036854775807 START WITH 1 CACHE 1 NO CYCLE;

CREATE SEQUENCE "public"."decisions_decision_id_seq" AS bigint INCREMENT BY 1 MINVALUE 1 MAXVALUE 9223372036854775807 START WITH 1 CACHE 1 NO CYCLE;

CREATE SEQUENCE "public"."dialogue_golden_eval_dataset_eval_id_seq" AS bigint INCREMENT BY 1 MINVALUE 1 MAXVALUE 9223372036854775807 START WITH 1 CACHE 1 NO CYCLE;

CREATE SEQUENCE "public"."dialogue_r1_avatar_r1_avatar_id_seq" AS bigint INCREMENT BY 1 MINVALUE 1 MAXVALUE 9223372036854775807 START WITH 1 CACHE 1 NO CYCLE;

CREATE SEQUENCE "public"."dialogue_r1_kid_r1_kid_id_seq" AS bigint INCREMENT BY 1 MINVALUE 1 MAXVALUE 9223372036854775807 START WITH 1 CACHE 1 NO CYCLE;

CREATE SEQUENCE "public"."dialogue_r2_avatar_r2_avatar_id_seq" AS bigint INCREMENT BY 1 MINVALUE 1 MAXVALUE 9223372036854775807 START WITH 1 CACHE 1 NO CYCLE;

CREATE SEQUENCE "public"."dialogue_r2_kid_r2_kid_id_seq" AS bigint INCREMENT BY 1 MINVALUE 1 MAXVALUE 9223372036854775807 START WITH 1 CACHE 1 NO CYCLE;

CREATE SEQUENCE "public"."difficulty_event_options_option_id_seq" AS bigint INCREMENT BY 1 MINVALUE 1 MAXVALUE 9223372036854775807 START WITH 1 CACHE 1 NO CYCLE;

CREATE SEQUENCE "public"."difficulty_events_event_id_seq" AS bigint INCREMENT BY 1 MINVALUE 1 MAXVALUE 9223372036854775807 START WITH 1 CACHE 1 NO CYCLE;

CREATE SEQUENCE "public"."nudge_content_nudge_id_seq" AS bigint INCREMENT BY 1 MINVALUE 1 MAXVALUE 9223372036854775807 START WITH 1 CACHE 1 NO CYCLE;

CREATE SEQUENCE "public"."options_option_id_seq" AS bigint INCREMENT BY 1 MINVALUE 1 MAXVALUE 9223372036854775807 START WITH 1 CACHE 1 NO CYCLE;

CREATE SEQUENCE "public"."session_decision_logs_log_id_seq" AS bigint INCREMENT BY 1 MINVALUE 1 MAXVALUE 9223372036854775807 START WITH 1 CACHE 1 NO CYCLE;

CREATE SEQUENCE "public"."user_badges_id_seq" AS integer INCREMENT BY 1 MINVALUE 1 MAXVALUE 2147483647 START WITH 1 CACHE 1 NO CYCLE;

CREATE TABLE "public"."age_level_mapping" (
  "mapping_id" bigint   NOT NULL DEFAULT nextval('public.age_level_mapping_mapping_id_seq'::regclass),
  "min_age"    smallint NOT NULL,
  "max_age"    smallint NOT NULL,
  "level"      smallint NOT NULL,
  CONSTRAINT "age_level_mapping_level_key" UNIQUE (level),
  CONSTRAINT "age_level_mapping_pkey" PRIMARY KEY (mapping_id),
  CONSTRAINT "valid_age_range" CHECK ((min_age <= max_age))
);

ALTER TABLE "public"."age_level_mapping"
  ENABLE ROW LEVEL SECURITY;

CREATE TABLE "public"."badge_requirements" (
  "id"                  integer               NOT NULL DEFAULT nextval('public.badge_requirements_id_seq'::regclass),
  "badge_id"            character varying(50),
  "metric_type"         character varying(50) NOT NULL,
  "threshold_value"     character varying(50) NOT NULL,
  "comparison_operator" character varying(10) DEFAULT '>='::character varying,
  CONSTRAINT "badge_requirements_pkey" PRIMARY KEY (id)
);

ALTER TABLE "public"."badge_requirements"
  ENABLE ROW LEVEL SECURITY;

CREATE TABLE "public"."badges" (
  "id"          character varying(50)    NOT NULL,
  "title"       character varying(100)   NOT NULL,
  "description" text                     NOT NULL,
  "icon_url"    text,
  "category"    character varying(50)    NOT NULL,
  "is_active"   boolean                  DEFAULT true,
  "created_at"  timestamp with time zone DEFAULT now(),
  CONSTRAINT "badges_pkey" PRIMARY KEY (id)
);

ALTER TABLE "public"."badges"
  ENABLE ROW LEVEL SECURITY;

CREATE TABLE "public"."child_difficulty_progress" (
  "child_profile_id" uuid                     NOT NULL,
  "level"            smallint                 NOT NULL,
  "seen_event_ids"   bigint[]                 NOT NULL DEFAULT '{}'::bigint[],
  "updated_at"       timestamp with time zone NOT NULL DEFAULT now(),
  CONSTRAINT "child_difficulty_progress_level_check" CHECK ((level = ANY (ARRAY[1, 2, 3]))),
  CONSTRAINT "child_difficulty_progress_pkey" PRIMARY KEY (child_profile_id, level)
);

ALTER TABLE "public"."child_difficulty_progress"
  ENABLE ROW LEVEL SECURITY;

CREATE TABLE "public"."child_modifiers" (
  "child_profile_id"             uuid          NOT NULL,
  "level"                        smallint      NOT NULL,
  "current_conversion_threshold" smallint,
  "current_event_cost"           numeric(10,2),
  CONSTRAINT "child_modifiers_current_conversion_threshold_check" CHECK (((current_conversion_threshold >= 0) AND (current_conversion_threshold <= 100))),
  CONSTRAINT "child_modifiers_level_check" CHECK ((level = ANY (ARRAY[1, 2, 3]))),
  CONSTRAINT "child_modifiers_pkey" PRIMARY KEY (child_profile_id, level)
);

ALTER TABLE "public"."child_modifiers"
  ENABLE ROW LEVEL SECURITY;

CREATE TABLE "public"."child_reputation_stats" (
  "child_profile_id"      uuid     NOT NULL,
  "level"                 smallint NOT NULL,
  "customers_encountered" integer  NOT NULL DEFAULT 0,
  "customers_converted"   integer  NOT NULL DEFAULT 0,
  CONSTRAINT "child_reputation_stats_level_check" CHECK ((level = ANY (ARRAY[1, 2, 3]))),
  CONSTRAINT "child_reputation_stats_pkey" PRIMARY KEY (child_profile_id, level)
);

ALTER TABLE "public"."child_reputation_stats"
  ENABLE ROW LEVEL SECURITY;

CREATE TABLE "public"."concepts" (
  "concept_code" character varying(50)    NOT NULL,
  "display_name" character varying(100)   NOT NULL,
  "description"  text                     NOT NULL,
  "created_at"   timestamp with time zone NOT NULL DEFAULT now(),
  CONSTRAINT "concepts_pkey" PRIMARY KEY (concept_code)
);

ALTER TABLE "public"."concepts"
  ENABLE ROW LEVEL SECURITY;

CREATE TABLE "public"."customer_responses" (
  "response_id"      bigint   NOT NULL DEFAULT nextval('public.customer_responses_response_id_seq'::regclass),
  "decision_context" text     NOT NULL,
  "option_code"      text     NOT NULL,
  "generosity_score" smallint NOT NULL,
  "is_llm_generated" boolean  NOT NULL DEFAULT false,
  CONSTRAINT "customer_responses_decision_context_option_code_key" UNIQUE (decision_context, option_code),
  CONSTRAINT "customer_responses_generosity_score_check" CHECK (((generosity_score >= 0) AND (generosity_score <= 100))),
  CONSTRAINT "customer_responses_pkey" PRIMARY KEY (response_id)
);

ALTER TABLE "public"."customer_responses"
  ENABLE ROW LEVEL SECURITY;

CREATE TABLE "public"."customer_types" (
  "type_id"                   bigint   NOT NULL DEFAULT nextval('public.customer_types_type_id_seq'::regclass),
  "level"                     smallint NOT NULL,
  "type_code"                 text     NOT NULL,
  "display_label"             text     NOT NULL,
  "distribution_pct"          smallint NOT NULL,
  "base_conversion_threshold" smallint,
  CONSTRAINT "customer_types_base_conversion_threshold_check" CHECK (((base_conversion_threshold >= 0) AND (base_conversion_threshold <= 100))),
  CONSTRAINT "customer_types_distribution_pct_check" CHECK (((distribution_pct >= 0) AND (distribution_pct <= 100))),
  CONSTRAINT "customer_types_level_check" CHECK ((level = ANY (ARRAY[1, 2, 3]))),
  CONSTRAINT "customer_types_level_type_code_key" UNIQUE (level, type_code),
  CONSTRAINT "customer_types_pkey" PRIMARY KEY (type_id),
  CONSTRAINT "customer_types_type_code_check" CHECK ((type_code = ANY (ARRAY['NICE'::text, 'MODERATE'::text, 'STRICT'::text])))
);

ALTER TABLE "public"."customer_types"
  ENABLE ROW LEVEL SECURITY;

CREATE TABLE "public"."decision_concept_mapping" (
  "level"        smallint              NOT NULL,
  "decision_id"  bigint                NOT NULL,
  "concept_code" character varying(50) NOT NULL,
  CONSTRAINT "decision_concept_mapping_level_check" CHECK ((level = ANY (ARRAY[1, 2, 3]))),
  CONSTRAINT "decision_concept_mapping_pkey" PRIMARY KEY (decision_id, concept_code)
);

ALTER TABLE "public"."decision_concept_mapping"
  ENABLE ROW LEVEL SECURITY;

CREATE TABLE "public"."decision_log" (
  "id"             uuid                     NOT NULL DEFAULT gen_random_uuid(),
  "kid_session_id" uuid                     NOT NULL,
  "screen_id"      text                     NOT NULL,
  "decision_key"   text                     NOT NULL,
  "decision_value" jsonb                    NOT NULL,
  "created_at"     timestamp with time zone NOT NULL DEFAULT now(),
  CONSTRAINT "decision_log_pkey" PRIMARY KEY (id)
);

ALTER TABLE "public"."decision_log"
  ENABLE ROW LEVEL SECURITY;

CREATE TABLE "public"."decisions" (
  "decision_id"        bigint                   NOT NULL DEFAULT nextval('public.decisions_decision_id_seq'::regclass),
  "level"              smallint                 NOT NULL,
  "decision_code"      text                     NOT NULL,
  "decision_name"      text                     NOT NULL,
  "decision_order"     smallint                 NOT NULL,
  "ranking_applicable" boolean                  NOT NULL DEFAULT true,
  "created_at"         timestamp with time zone NOT NULL DEFAULT now(),
  "business_type"      text                     NOT NULL DEFAULT 'LOLLIPOP_STAND'::text,
  CONSTRAINT "decisions_business_level_code_key" UNIQUE (business_type, level, decision_code),
  CONSTRAINT "decisions_level_check" CHECK ((level = ANY (ARRAY[1, 2, 3]))),
  CONSTRAINT "decisions_pkey" PRIMARY KEY (decision_id)
);

ALTER TABLE "public"."decisions"
  ENABLE ROW LEVEL SECURITY;

CREATE TABLE "public"."dialogue_golden_eval_dataset" (
  "eval_id"                bigint                   NOT NULL DEFAULT nextval('public.dialogue_golden_eval_dataset_eval_id_seq'::regclass),
  "dialogue_stage"         text                     NOT NULL,
  "level"                  smallint                 NOT NULL,
  "customer_type_code"     text                     NOT NULL,
  "difficulty_event_code"  text,
  "difficulty_option_code" text,
  "dialogue_text"          text                     NOT NULL,
  "eval_label"             text                     NOT NULL,
  "failure_category"       text,
  "reviewer_notes"         text,
  "suggested_fix"          text,
  "created_at"             timestamp with time zone NOT NULL DEFAULT now(),
  CONSTRAINT "dialogue_golden_eval_dataset_customer_type_code_check" CHECK ((customer_type_code = ANY (ARRAY['NICE'::text, 'MODERATE'::text, 'STRICT'::text]))),
  CONSTRAINT "dialogue_golden_eval_dataset_dialogue_stage_check" CHECK ((dialogue_stage = ANY (ARRAY['R1_AVATAR'::text, 'R1_KID'::text, 'R2_AVATAR'::text, 'R2_KID'::text]))),
  CONSTRAINT "dialogue_golden_eval_dataset_eval_label_check" CHECK ((eval_label = ANY (ARRAY['PASS'::text, 'FAIL'::text]))),
  CONSTRAINT "dialogue_golden_eval_dataset_failure_category_check"
    CHECK ((failure_category = ANY (ARRAY['VOCABULARY_LEAK'::text, 'PHYSICAL_CONTRADICTION'::text, 'UNEARNED_DAMAGE'::text, 'NONE'::text]))),
  CONSTRAINT "dialogue_golden_eval_dataset_level_check" CHECK ((level = ANY (ARRAY[1, 2, 3]))),
  CONSTRAINT "dialogue_golden_eval_dataset_pkey" PRIMARY KEY (eval_id)
);

ALTER TABLE "public"."dialogue_golden_eval_dataset"
  ENABLE ROW LEVEL SECURITY;

CREATE TABLE "public"."dialogue_r1_avatar" (
  "r1_avatar_id"           bigint                   NOT NULL DEFAULT nextval('public.dialogue_r1_avatar_r1_avatar_id_seq'::regclass),
  "level"                  smallint                 NOT NULL,
  "customer_type_code"     text                     NOT NULL,
  "difficulty_event_code"  text,
  "difficulty_option_code" text,
  "variation_index"        smallint                 NOT NULL,
  "dialogue_text"          text                     NOT NULL,
  "pending_review"         boolean                  NOT NULL DEFAULT true,
  "approved_at"            timestamp with time zone,
  "model_used"             text                     NOT NULL,
  "created_at"             timestamp with time zone NOT NULL DEFAULT now(),
  "passed_readability"     boolean                  NOT NULL DEFAULT false,
  CONSTRAINT "dialogue_r1_avatar_customer_type_code_check" CHECK ((customer_type_code = ANY (ARRAY['NICE'::text, 'MODERATE'::text, 'STRICT'::text]))),
  CONSTRAINT "dialogue_r1_avatar_level_check" CHECK ((level = ANY (ARRAY[1, 2, 3]))),
  CONSTRAINT "dialogue_r1_avatar_pkey" PRIMARY KEY (r1_avatar_id),
  CONSTRAINT "dialogue_r1_avatar_variation_index_check" CHECK (((variation_index >= 1) AND (variation_index <= 5)))
);

ALTER TABLE "public"."dialogue_r1_avatar"
  ENABLE ROW LEVEL SECURITY;

CREATE TABLE "public"."dialogue_r1_kid" (
  "r1_kid_id"          bigint                   NOT NULL DEFAULT nextval('public.dialogue_r1_kid_r1_kid_id_seq'::regclass),
  "r1_avatar_id"       bigint                   NOT NULL,
  "avatar_prompt_text" text                     NOT NULL,
  "option_type"        text                     NOT NULL,
  "response_text"      text                     NOT NULL,
  "pending_review"     boolean                  NOT NULL DEFAULT true,
  "approved_at"        timestamp with time zone,
  "model_used"         text                     NOT NULL,
  "created_at"         timestamp with time zone NOT NULL DEFAULT now(),
  "passed_readability" boolean                  NOT NULL DEFAULT false,
  CONSTRAINT "dialogue_r1_kid_option_type_check" CHECK ((option_type = ANY (ARRAY['GOOD'::text, 'MODERATE'::text, 'BAD'::text]))),
  CONSTRAINT "dialogue_r1_kid_pkey" PRIMARY KEY (r1_kid_id)
);

ALTER TABLE "public"."dialogue_r1_kid"
  ENABLE ROW LEVEL SECURITY;

CREATE TABLE "public"."dialogue_r2_avatar" (
  "r2_avatar_id"       bigint                   NOT NULL DEFAULT nextval('public.dialogue_r2_avatar_r2_avatar_id_seq'::regclass),
  "r1_kid_moderate_id" bigint                   NOT NULL,
  "avatar_prompt_text" text                     NOT NULL,
  "objection_axis"     text                     NOT NULL,
  "dialogue_text"      text                     NOT NULL,
  "pending_review"     boolean                  NOT NULL DEFAULT true,
  "approved_at"        timestamp with time zone,
  "model_used"         text                     NOT NULL,
  "created_at"         timestamp with time zone NOT NULL DEFAULT now(),
  "passed_readability" boolean                  NOT NULL DEFAULT false,
  CONSTRAINT "dialogue_r2_avatar_objection_axis_check" CHECK ((objection_axis = ANY (ARRAY['PRICE'::text, 'SIZE'::text, 'CONVENIENCE'::text]))),
  CONSTRAINT "dialogue_r2_avatar_pkey" PRIMARY KEY (r2_avatar_id)
);

ALTER TABLE "public"."dialogue_r2_avatar"
  ENABLE ROW LEVEL SECURITY;

CREATE TABLE "public"."dialogue_r2_kid" (
  "r2_kid_id"          bigint                   NOT NULL DEFAULT nextval('public.dialogue_r2_kid_r2_kid_id_seq'::regclass),
  "r2_avatar_id"       bigint                   NOT NULL,
  "avatar_prompt_text" text                     NOT NULL,
  "option_type"        text                     NOT NULL,
  "response_text"      text                     NOT NULL,
  "pending_review"     boolean                  NOT NULL DEFAULT true,
  "approved_at"        timestamp with time zone,
  "model_used"         text                     NOT NULL,
  "created_at"         timestamp with time zone NOT NULL DEFAULT now(),
  "passed_readability" boolean                  NOT NULL DEFAULT false,
  CONSTRAINT "dialogue_r2_kid_option_type_check" CHECK ((option_type = ANY (ARRAY['GOOD'::text, 'BAD'::text]))),
  CONSTRAINT "dialogue_r2_kid_pkey" PRIMARY KEY (r2_kid_id)
);

ALTER TABLE "public"."dialogue_r2_kid"
  ENABLE ROW LEVEL SECURITY;

CREATE TABLE "public"."difficulty_event_options" (
  "option_id"         bigint        NOT NULL DEFAULT nextval('public.difficulty_event_options_option_id_seq'::regclass),
  "event_id"          bigint        NOT NULL,
  "option_code"       text          NOT NULL,
  "display_label"     text          NOT NULL,
  "damaged"           boolean       NOT NULL,
  "threshold_penalty" numeric(5,2)  NOT NULL DEFAULT 0,
  "base_cost"         numeric(10,2),
  CONSTRAINT "difficulty_event_options_event_id_option_code_key" UNIQUE (event_id, option_code),
  CONSTRAINT "difficulty_event_options_pkey" PRIMARY KEY (option_id)
);

ALTER TABLE "public"."difficulty_event_options"
  ENABLE ROW LEVEL SECURITY;

CREATE TABLE "public"."difficulty_events" (
  "event_id"         bigint                   NOT NULL DEFAULT nextval('public.difficulty_events_event_id_seq'::regclass),
  "level"            smallint                 NOT NULL,
  "event_code"       text                     NOT NULL,
  "event_name"       text                     NOT NULL,
  "source_tag"       text                     NOT NULL,
  "founder_source"   text,
  "scenario_text"    text                     NOT NULL,
  "trigger_index"    integer,
  "created_at"       timestamp with time zone NOT NULL DEFAULT now(),
  "timing_condition" text[],
  CONSTRAINT "difficulty_events_event_code_key" UNIQUE (event_code),
  CONSTRAINT "difficulty_events_level_check" CHECK ((level = ANY (ARRAY[1, 2, 3]))),
  CONSTRAINT "difficulty_events_pkey" PRIMARY KEY (event_id),
  CONSTRAINT "difficulty_events_source_tag_check" CHECK ((source_tag = ANY (ARRAY['grounded'::text, 'generic'::text])))
);

ALTER TABLE "public"."difficulty_events"
  ENABLE ROW LEVEL SECURITY;

CREATE TABLE "public"."households" (
  "id"             uuid                     NOT NULL DEFAULT gen_random_uuid(),
  "email"          text                     NOT NULL,
  "auth_provider"  text                     NOT NULL,
  "email_verified" boolean                  NOT NULL DEFAULT false,
  "created_at"     timestamp with time zone NOT NULL DEFAULT now(),
  CONSTRAINT "households_auth_provider_check" CHECK ((auth_provider = ANY (ARRAY['email'::text, 'google'::text]))),
  CONSTRAINT "households_email_key" UNIQUE (email),
  CONSTRAINT "households_pkey" PRIMARY KEY (id)
);

ALTER TABLE "public"."households"
  ENABLE ROW LEVEL SECURITY;

CREATE TABLE "public"."kid_session" (
  "id"            uuid                     NOT NULL DEFAULT gen_random_uuid(),
  "household_id"  uuid                     NOT NULL,
  "name"          text,
  "age"           integer,
  "age_tier"      text,
  "avatar_config" jsonb,
  "created_at"    timestamp with time zone NOT NULL DEFAULT now(),
  CONSTRAINT "kid_session_age_check" CHECK (((age >= 7) AND (age <= 14))),
  CONSTRAINT "kid_session_age_tier_check" CHECK ((age_tier = ANY (ARRAY['7-8'::text, '9-10'::text, '11-12'::text]))),
  CONSTRAINT "kid_session_pkey" PRIMARY KEY (id)
);

ALTER TABLE "public"."kid_session"
  ENABLE ROW LEVEL SECURITY;

CREATE TABLE "public"."level_flavor_settings" (
  "level"                  smallint NOT NULL,
  "flavors_shown"          smallint NOT NULL,
  "max_flavors_selectable" smallint NOT NULL,
  CONSTRAINT "level_flavor_settings_pkey" PRIMARY KEY (level)
);

ALTER TABLE "public"."level_flavor_settings"
  ENABLE ROW LEVEL SECURITY;

CREATE TABLE "public"."location_timing_traffic" (
  "location_code"      text         NOT NULL,
  "timing_code"        text         NOT NULL,
  "traffic_multiplier" numeric(5,2) NOT NULL,
  CONSTRAINT "location_timing_traffic_pkey" PRIMARY KEY (location_code, timing_code)
);

ALTER TABLE "public"."location_timing_traffic"
  ENABLE ROW LEVEL SECURITY;

CREATE TABLE "public"."nudge_content" (
  "nudge_id"           bigint                   NOT NULL DEFAULT nextval('public.nudge_content_nudge_id_seq'::regclass),
  "business_type"      text                     NOT NULL,
  "level"              smallint                 NOT NULL,
  "decision_code"      text                     NOT NULL,
  "source_hash"        text                     NOT NULL,
  "generated_at"       timestamp with time zone NOT NULL DEFAULT now(),
  "reviewed_by"        text,
  "reviewed_at"        timestamp with time zone,
  "status"             text                     NOT NULL DEFAULT 'pending_review'::text,
  "review_notes"       text,
  "tip_index"          smallint                 NOT NULL,
  "tip_text"           text                     NOT NULL,
  "passed_readability" boolean                  NOT NULL DEFAULT false,
  "model_used"         text,
  "Comments"           text,
  CONSTRAINT "nudge_content_level_check" CHECK ((level = ANY (ARRAY[1, 2, 3]))),
  CONSTRAINT "nudge_content_pkey" PRIMARY KEY (nudge_id),
  CONSTRAINT "nudge_content_status_check" CHECK ((status = ANY (ARRAY['pending_review'::text, 'approved'::text, 'stale'::text, 'removed'::text]))),
  CONSTRAINT "nudge_content_tip_index_check" CHECK (((tip_index >= 1) AND (tip_index <= 5))),
  CONSTRAINT "nudge_content_unique_tip" UNIQUE (business_type, level, decision_code, tip_index)
);

ALTER TABLE "public"."nudge_content"
  ENABLE ROW LEVEL SECURITY;

CREATE TABLE "public"."options" (
  "option_id"          bigint        NOT NULL DEFAULT nextval('public.options_option_id_seq'::regclass),
  "decision_id"        bigint        NOT NULL,
  "option_code"        text          NOT NULL,
  "display_label"      text          NOT NULL,
  "rank"               smallint,
  "confidence"         text,
  "base_cost"          numeric(10,2) DEFAULT 0,
  "traffic_multiplier" numeric(6,3),
  "notes"              text,
  "margin_pct"         numeric(5,2),
  "margin_boost"       numeric(5,2)  DEFAULT 0.00,
  "threshold_penalty"  numeric(5,2)  DEFAULT 0.00,
  "serving_capacity"   smallint      DEFAULT 1,
  CONSTRAINT "options_confidence_check" CHECK ((confidence = ANY (ARRAY['D'::text, 'F'::text]))),
  CONSTRAINT "options_decision_id_option_code_key" UNIQUE (decision_id, option_code),
  CONSTRAINT "options_pkey" PRIMARY KEY (option_id)
);

ALTER TABLE "public"."options"
  ENABLE ROW LEVEL SECURITY;

CREATE TABLE "public"."session_decision_logs" (
  "log_id"            bigint                   NOT NULL DEFAULT nextval('public.session_decision_logs_log_id_seq'::regclass),
  "child_profile_id"  uuid                     NOT NULL,
  "playthrough_index" integer                  NOT NULL,
  "level"             smallint                 NOT NULL,
  "step_code"         text                     NOT NULL,
  "decision_id"       bigint,
  "option_code"       text,
  "vocabulary_tags"   text[]                   NOT NULL DEFAULT '{}'::text[],
  "payload"           jsonb                    DEFAULT '{}'::jsonb,
  "created_at"        timestamp with time zone NOT NULL DEFAULT now(),
  CONSTRAINT "session_decision_logs_level_check" CHECK ((level = ANY (ARRAY[1, 2, 3]))),
  CONSTRAINT "session_decision_logs_pkey" PRIMARY KEY (log_id),
  CONSTRAINT "unique_child_playthrough_step" UNIQUE (child_profile_id, playthrough_index, step_code)
);

ALTER TABLE "public"."session_decision_logs"
  ENABLE ROW LEVEL SECURITY;

CREATE TABLE "public"."simulation_runs" (
  "id"                 uuid                     NOT NULL DEFAULT gen_random_uuid(),
  "kid_session_id"     uuid                     NOT NULL,
  "status"             text                     NOT NULL DEFAULT 'in_progress'::text,
  "final_profit_cents" integer,
  "started_at"         timestamp with time zone NOT NULL DEFAULT now(),
  "completed_at"       timestamp with time zone,
  CONSTRAINT "simulation_runs_pkey" PRIMARY KEY (id),
  CONSTRAINT "simulation_runs_status_check" CHECK ((status = ANY (ARRAY['in_progress'::text, 'complete_profit'::text, 'complete_loss'::text])))
);

ALTER TABLE "public"."simulation_runs"
  ENABLE ROW LEVEL SECURITY;

CREATE TABLE "public"."user_badges" (
  "id"         integer                  NOT NULL DEFAULT nextval('public.user_badges_id_seq'::regclass),
  "user_id"    uuid                     NOT NULL,
  "badge_id"   character varying(50),
  "awarded_at" timestamp with time zone DEFAULT now(),
  CONSTRAINT "user_badges_pkey" PRIMARY KEY (id),
  CONSTRAINT "user_badges_user_id_badge_id_key" UNIQUE (user_id, badge_id)
);

ALTER TABLE "public"."user_badges"
  ENABLE ROW LEVEL SECURITY;

CREATE TABLE "public"."vocabulary_tiers" (
  "id"                   bigint                   GENERATED ALWAYS AS IDENTITY NOT NULL,
  "term"                 text                     NOT NULL,
  "concept_category"     text,
  "tier"                 integer                  NOT NULL DEFAULT 0,
  "l1_status"            text                     NOT NULL DEFAULT 'blocked'::text,
  "l2_status"            text                     NOT NULL DEFAULT 'blocked'::text,
  "l3_status"            text                     NOT NULL DEFAULT 'blocked'::text,
  "decision_context"     text,
  "l1_preferred_wording" text                     DEFAULT ''::text,
  "l2_preferred_wording" text                     DEFAULT ''::text,
  "teach_through_audio"  boolean                  DEFAULT false,
  "policy_status"        text,
  "created_at"           timestamp with time zone DEFAULT now(),
  CONSTRAINT "vocabulary_tiers_pkey" PRIMARY KEY (id),
  CONSTRAINT "vocabulary_tiers_term_key" UNIQUE (term)
);

ALTER TABLE "public"."vocabulary_tiers"
  ENABLE ROW LEVEL SECURITY;

CREATE TABLE "public"."wallet_ledger" (
  "id"             uuid                     NOT NULL DEFAULT gen_random_uuid(),
  "kid_session_id" uuid                     NOT NULL,
  "amount_cents"   integer                  NOT NULL,
  "reason"         text                     NOT NULL,
  "screen_id"      text,
  "created_at"     timestamp with time zone NOT NULL DEFAULT now(),
  CONSTRAINT "wallet_ledger_pkey" PRIMARY KEY (id)
);

ALTER TABLE "public"."wallet_ledger"
  ENABLE ROW LEVEL SECURITY;

ALTER SEQUENCE "public"."age_level_mapping_mapping_id_seq" OWNED BY "public"."age_level_mapping"."mapping_id";

ALTER SEQUENCE "public"."badge_requirements_id_seq" OWNED BY "public"."badge_requirements"."id";

ALTER SEQUENCE "public"."customer_responses_response_id_seq" OWNED BY "public"."customer_responses"."response_id";

ALTER SEQUENCE "public"."customer_types_type_id_seq" OWNED BY "public"."customer_types"."type_id";

ALTER SEQUENCE "public"."decisions_decision_id_seq" OWNED BY "public"."decisions"."decision_id";

ALTER SEQUENCE "public"."dialogue_golden_eval_dataset_eval_id_seq" OWNED BY "public"."dialogue_golden_eval_dataset"."eval_id";

ALTER SEQUENCE "public"."dialogue_r1_avatar_r1_avatar_id_seq" OWNED BY "public"."dialogue_r1_avatar"."r1_avatar_id";

ALTER SEQUENCE "public"."dialogue_r1_kid_r1_kid_id_seq" OWNED BY "public"."dialogue_r1_kid"."r1_kid_id";

ALTER SEQUENCE "public"."dialogue_r2_avatar_r2_avatar_id_seq" OWNED BY "public"."dialogue_r2_avatar"."r2_avatar_id";

ALTER SEQUENCE "public"."dialogue_r2_kid_r2_kid_id_seq" OWNED BY "public"."dialogue_r2_kid"."r2_kid_id";

ALTER SEQUENCE "public"."difficulty_event_options_option_id_seq" OWNED BY "public"."difficulty_event_options"."option_id";

ALTER SEQUENCE "public"."difficulty_events_event_id_seq" OWNED BY "public"."difficulty_events"."event_id";

ALTER SEQUENCE "public"."nudge_content_nudge_id_seq" OWNED BY "public"."nudge_content"."nudge_id";

ALTER SEQUENCE "public"."options_option_id_seq" OWNED BY "public"."options"."option_id";

ALTER SEQUENCE "public"."session_decision_logs_log_id_seq" OWNED BY "public"."session_decision_logs"."log_id";

ALTER SEQUENCE "public"."user_badges_id_seq" OWNED BY "public"."user_badges"."id";

CREATE OR REPLACE FUNCTION public.update_vocabulary_tiers_timestamp()
  RETURNS TRIGGER
  LANGUAGE plpgsql
  AS $function$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$function$;

ALTER TABLE "public"."badge_requirements"
  ADD CONSTRAINT "badge_requirements_badge_id_fkey" FOREIGN KEY (badge_id) REFERENCES public.badges(id) ON DELETE CASCADE;

ALTER TABLE "public"."decision_concept_mapping"
  ADD CONSTRAINT "decision_concept_mapping_concept_code_fkey" FOREIGN KEY (concept_code) REFERENCES public.concepts(concept_code) ON DELETE CASCADE;

ALTER TABLE "public"."decision_concept_mapping"
  ADD CONSTRAINT "decision_concept_mapping_decision_id_fkey" FOREIGN KEY (decision_id) REFERENCES public.decisions(decision_id) ON DELETE CASCADE;

ALTER TABLE "public"."dialogue_r1_kid"
  ADD CONSTRAINT "dialogue_r1_kid_r1_avatar_id_fkey" FOREIGN KEY (r1_avatar_id) REFERENCES public.dialogue_r1_avatar(r1_avatar_id) ON DELETE CASCADE;

ALTER TABLE "public"."dialogue_r2_avatar"
  ADD CONSTRAINT "dialogue_r2_avatar_r1_kid_moderate_id_fkey" FOREIGN KEY (r1_kid_moderate_id) REFERENCES public.dialogue_r1_kid(r1_kid_id) ON DELETE CASCADE;

ALTER TABLE "public"."dialogue_r2_kid"
  ADD CONSTRAINT "dialogue_r2_kid_r2_avatar_id_fkey" FOREIGN KEY (r2_avatar_id) REFERENCES public.dialogue_r2_avatar(r2_avatar_id) ON DELETE CASCADE;

ALTER TABLE "public"."dialogue_r1_avatar"
  ADD CONSTRAINT "dialogue_r1_avatar_difficulty_event_code_fkey" FOREIGN KEY (difficulty_event_code) REFERENCES public.difficulty_events(event_code) ON DELETE SET NULL;

ALTER TABLE "public"."difficulty_event_options"
  ADD CONSTRAINT "difficulty_event_options_event_id_fkey" FOREIGN KEY (event_id) REFERENCES public.difficulty_events(event_id) ON DELETE CASCADE;

ALTER TABLE "public"."kid_session"
  ADD CONSTRAINT "kid_session_household_id_fkey" FOREIGN KEY (household_id) REFERENCES public.households(id) ON DELETE CASCADE;

ALTER TABLE "public"."decision_log"
  ADD CONSTRAINT "decision_log_kid_session_id_fkey" FOREIGN KEY (kid_session_id) REFERENCES public.kid_session(id) ON DELETE CASCADE;

ALTER TABLE "public"."options"
  ADD CONSTRAINT "options_decision_id_fkey" FOREIGN KEY (decision_id) REFERENCES public.decisions(decision_id) ON DELETE CASCADE;

ALTER TABLE "public"."session_decision_logs"
  ADD CONSTRAINT "session_decision_logs_decision_id_fkey" FOREIGN KEY (decision_id) REFERENCES public.decisions(decision_id) ON DELETE SET NULL;

ALTER TABLE "public"."simulation_runs"
  ADD CONSTRAINT "simulation_runs_kid_session_id_fkey" FOREIGN KEY (kid_session_id) REFERENCES public.kid_session(id) ON DELETE CASCADE;

ALTER TABLE "public"."user_badges"
  ADD CONSTRAINT "user_badges_badge_id_fkey" FOREIGN KEY (badge_id) REFERENCES public.badges(id) ON DELETE CASCADE;

ALTER TABLE "public"."wallet_ledger"
  ADD CONSTRAINT "wallet_ledger_kid_session_id_fkey" FOREIGN KEY (kid_session_id) REFERENCES public.kid_session(id) ON DELETE CASCADE;

CREATE VIEW "public"."child_reputation_pct" WITH (security_invoker=true) AS  SELECT child_profile_id,
    level,
    customers_encountered,
    customers_converted,
        CASE
            WHEN (customers_encountered = 0) THEN NULL::numeric
            ELSE round(((100.0 * (customers_converted)::numeric) / (customers_encountered)::numeric), 1)
        END AS reputation_pct
   FROM public.child_reputation_stats;

CREATE INDEX idx_decision_concept_decision ON public.decision_concept_mapping USING btree (decision_id);

CREATE INDEX idx_decision_log_kid ON public.decision_log USING btree (kid_session_id);

CREATE INDEX idx_kid_session_household ON public.kid_session USING btree (household_id);

CREATE INDEX idx_nudge_lookup ON public.nudge_content USING btree (business_type, level, decision_code, status, passed_readability);

CREATE INDEX idx_options_decision ON public.options USING btree (decision_id);

CREATE INDEX idx_r1_avatar_approved ON public.dialogue_r1_avatar USING btree (level, customer_type_code, difficulty_event_code, difficulty_option_code)
  WHERE (pending_review = false);

CREATE INDEX idx_r1_avatar_pending ON public.dialogue_r1_avatar USING btree (level, created_at)
  WHERE (pending_review = true);

CREATE UNIQUE INDEX idx_r1_avatar_scenario ON public.dialogue_r1_avatar
  USING btree (level, customer_type_code, difficulty_event_code, difficulty_option_code, variation_index) NULLS NOT DISTINCT;

CREATE INDEX idx_r1_kid_moderate ON public.dialogue_r1_kid USING btree (r1_avatar_id)
  WHERE (option_type = 'MODERATE'::text);

CREATE INDEX idx_r1_kid_pending ON public.dialogue_r1_kid USING btree (r1_avatar_id, created_at)
  WHERE (pending_review = true);

CREATE UNIQUE INDEX idx_r1_kid_scenario ON public.dialogue_r1_kid USING btree (r1_avatar_id, option_type);

CREATE INDEX idx_r2_avatar_pending ON public.dialogue_r2_avatar USING btree (r1_kid_moderate_id, created_at)
  WHERE (pending_review = true);

CREATE UNIQUE INDEX idx_r2_avatar_scenario ON public.dialogue_r2_avatar USING btree (r1_kid_moderate_id, objection_axis);

CREATE INDEX idx_r2_kid_pending ON public.dialogue_r2_kid USING btree (r2_avatar_id, created_at)
  WHERE (pending_review = true);

CREATE UNIQUE INDEX idx_r2_kid_scenario ON public.dialogue_r2_kid USING btree (r2_avatar_id, option_type);

CREATE INDEX idx_session_logs_lookup ON public.session_decision_logs USING btree (child_profile_id, playthrough_index, level);

CREATE INDEX idx_simulation_runs_kid ON public.simulation_runs USING btree (kid_session_id);

CREATE INDEX idx_vocabulary_tiers_l1_status ON public.vocabulary_tiers USING btree (l1_status, tier);

CREATE INDEX idx_vocabulary_tiers_l2_status ON public.vocabulary_tiers USING btree (l2_status, tier);

CREATE INDEX idx_vocabulary_tiers_l3_status ON public.vocabulary_tiers USING btree (l3_status, tier);

CREATE INDEX idx_vocabulary_tiers_term ON public.vocabulary_tiers USING btree (term);

CREATE INDEX idx_wallet_ledger_kid ON public.wallet_ledger USING btree (kid_session_id);

CREATE TRIGGER trigger_update_vocabulary_tiers_timestamp
  BEFORE UPDATE ON public.vocabulary_tiers
  FOR EACH ROW
  EXECUTE FUNCTION public.update_vocabulary_tiers_timestamp();

CREATE POLICY "Allow public read access to age_level_mapping" ON "public"."age_level_mapping"
  FOR SELECT
  TO PUBLIC
  USING (true);

CREATE POLICY "Allow authenticated read access to badge requirements" ON "public"."badge_requirements"
  FOR SELECT
  TO "authenticated"
  USING (true);

CREATE POLICY "Allow public read access to active badges" ON "public"."badges"
  FOR SELECT
  TO PUBLIC
  USING ((is_active = true));

CREATE POLICY "concepts_public_read" ON "public"."concepts"
  FOR SELECT
  TO PUBLIC
  USING (true);

CREATE POLICY "customer_responses_public_read" ON "public"."customer_responses"
  FOR SELECT
  TO PUBLIC
  USING (true);

CREATE POLICY "customer_types_public_read" ON "public"."customer_types"
  FOR SELECT
  TO PUBLIC
  USING (true);

CREATE POLICY "decision_concept_mapping_public_read" ON "public"."decision_concept_mapping"
  FOR SELECT
  TO PUBLIC
  USING (true);

CREATE POLICY "household_owns_decision_log" ON "public"."decision_log"
  FOR ALL
  TO PUBLIC
  USING ((kid_session_id IN ( SELECT kid_session.id
   FROM public.kid_session
  WHERE (kid_session.household_id = auth.uid()))));

CREATE POLICY "decisions_public_read" ON "public"."decisions"
  FOR SELECT
  TO PUBLIC
  USING (true);

CREATE POLICY "dialogue_golden_eval_dataset_service_role" ON "public"."dialogue_golden_eval_dataset"
  FOR ALL
  TO "service_role"
  USING (true)
  WITH CHECK (true);

CREATE POLICY "dialogue_r1_avatar_public_read" ON "public"."dialogue_r1_avatar"
  FOR SELECT
  TO PUBLIC
  USING (true);

CREATE POLICY "dialogue_r1_kid_public_read" ON "public"."dialogue_r1_kid"
  FOR SELECT
  TO PUBLIC
  USING (true);

CREATE POLICY "dialogue_r2_avatar_public_read" ON "public"."dialogue_r2_avatar"
  FOR SELECT
  TO PUBLIC
  USING (true);

CREATE POLICY "dialogue_r2_kid_public_read" ON "public"."dialogue_r2_kid"
  FOR SELECT
  TO PUBLIC
  USING (true);

CREATE POLICY "difficulty_event_options_public_read" ON "public"."difficulty_event_options"
  FOR SELECT
  TO PUBLIC
  USING (true);

CREATE POLICY "difficulty_events_public_read" ON "public"."difficulty_events"
  FOR SELECT
  TO PUBLIC
  USING (true);

CREATE POLICY "household_owns_self" ON "public"."households"
  FOR SELECT
  TO PUBLIC
  USING ((auth.uid() = id));

CREATE POLICY "household_owns_kid_session" ON "public"."kid_session"
  FOR ALL
  TO PUBLIC
  USING ((household_id = auth.uid()));

CREATE POLICY "level_flavor_settings_public_read" ON "public"."level_flavor_settings"
  FOR SELECT
  TO PUBLIC
  USING (true);

CREATE POLICY "location_timing_traffic_public_read" ON "public"."location_timing_traffic"
  FOR SELECT
  TO PUBLIC
  USING (true);

CREATE POLICY "nudge_content_public_read_approved_only" ON "public"."nudge_content"
  FOR SELECT
  TO PUBLIC
  USING ((status = 'approved'::text));

CREATE POLICY "options_public_read" ON "public"."options"
  FOR SELECT
  TO PUBLIC
  USING (true);

CREATE POLICY "session_logs_insert_policy" ON "public"."session_decision_logs"
  FOR INSERT
  TO PUBLIC
  WITH CHECK ((auth.uid() IS NOT NULL));

CREATE POLICY "session_logs_select_policy" ON "public"."session_decision_logs"
  FOR SELECT
  TO PUBLIC
  USING ((auth.uid() IS NOT NULL));

CREATE POLICY "session_logs_update_policy" ON "public"."session_decision_logs"
  FOR UPDATE
  TO PUBLIC
  USING ((auth.uid() IS NOT NULL));

CREATE POLICY "household_owns_simulation_runs" ON "public"."simulation_runs"
  FOR ALL
  TO PUBLIC
  USING ((kid_session_id IN ( SELECT kid_session.id
   FROM public.kid_session
  WHERE (kid_session.household_id = auth.uid()))));

CREATE POLICY "Allow users to view their own badges" ON "public"."user_badges"
  FOR SELECT
  TO "authenticated"
  USING ((auth.uid() = user_id));

CREATE POLICY "Allow public read access to vocabulary tiers" ON "public"."vocabulary_tiers"
  FOR SELECT
  TO PUBLIC
  USING (true);

CREATE POLICY "Allow read access for all users" ON "public"."vocabulary_tiers"
  FOR SELECT
  TO PUBLIC
  USING (true);

CREATE POLICY "Allow service role full access" ON "public"."vocabulary_tiers"
  FOR ALL
  TO PUBLIC
  USING ((auth.role() = 'service_role'::text));

CREATE POLICY "household_owns_wallet_ledger" ON "public"."wallet_ledger"
  FOR ALL
  TO PUBLIC
  USING ((kid_session_id IN ( SELECT kid_session.id
   FROM public.kid_session
  WHERE (kid_session.household_id = auth.uid()))));

COMMENT ON COLUMN "public"."vocabulary_tiers"."teach_through_audio" IS 'Flag indicating whether term should be taught via audio prompts.';

COMMENT ON COLUMN "public"."vocabulary_tiers"."term" IS 'Target business or vocabulary word (lowercase).';

COMMENT ON TABLE "public"."vocabulary_tiers" IS 'Vocabulary tier levels, statuses, and replacement mappings for readability engine.';

GRANT EXECUTE ON FUNCTION "public"."update_vocabulary_tiers_timestamp"() TO PUBLIC, "anon", "authenticated", "postgres", "service_role";

GRANT SELECT, UPDATE, USAGE ON SEQUENCE "public"."age_level_mapping_mapping_id_seq" TO "anon", "authenticated", "postgres", "service_role";

GRANT SELECT, UPDATE, USAGE ON SEQUENCE "public"."badge_requirements_id_seq" TO "anon", "authenticated", "postgres", "service_role";

GRANT SELECT, UPDATE, USAGE ON SEQUENCE "public"."customer_responses_response_id_seq" TO "anon", "authenticated", "postgres", "service_role";

GRANT SELECT, UPDATE, USAGE ON SEQUENCE "public"."customer_types_type_id_seq" TO "anon", "authenticated", "postgres", "service_role";

GRANT SELECT, UPDATE, USAGE ON SEQUENCE "public"."decisions_decision_id_seq" TO "anon", "authenticated", "postgres", "service_role";

GRANT SELECT, UPDATE, USAGE ON SEQUENCE "public"."dialogue_golden_eval_dataset_eval_id_seq" TO "anon", "authenticated", "postgres", "service_role";

GRANT SELECT, UPDATE, USAGE ON SEQUENCE "public"."dialogue_r1_avatar_r1_avatar_id_seq" TO "anon", "authenticated", "postgres", "service_role";

GRANT SELECT, UPDATE, USAGE ON SEQUENCE "public"."dialogue_r1_kid_r1_kid_id_seq" TO "anon", "authenticated", "postgres", "service_role";

GRANT SELECT, UPDATE, USAGE ON SEQUENCE "public"."dialogue_r2_avatar_r2_avatar_id_seq" TO "anon", "authenticated", "postgres", "service_role";

GRANT SELECT, UPDATE, USAGE ON SEQUENCE "public"."dialogue_r2_kid_r2_kid_id_seq" TO "anon", "authenticated", "postgres", "service_role";

GRANT SELECT, UPDATE, USAGE ON SEQUENCE "public"."difficulty_event_options_option_id_seq" TO "anon", "authenticated", "postgres", "service_role";

GRANT SELECT, UPDATE, USAGE ON SEQUENCE "public"."difficulty_events_event_id_seq" TO "anon", "authenticated", "postgres", "service_role";

GRANT SELECT, UPDATE, USAGE ON SEQUENCE "public"."nudge_content_nudge_id_seq" TO "anon", "authenticated", "postgres", "service_role";

GRANT SELECT, UPDATE, USAGE ON SEQUENCE "public"."options_option_id_seq" TO "anon", "authenticated", "postgres", "service_role";

GRANT SELECT, UPDATE, USAGE ON SEQUENCE "public"."session_decision_logs_log_id_seq" TO "anon", "authenticated", "postgres", "service_role";

GRANT SELECT, UPDATE, USAGE ON SEQUENCE "public"."user_badges_id_seq" TO "anon", "authenticated", "postgres", "service_role";

GRANT DELETE, INSERT, MAINTAIN, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE ON TABLE "public"."age_level_mapping" TO "anon", "authenticated", "postgres", "service_role";

GRANT DELETE, INSERT, MAINTAIN, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE ON TABLE "public"."badge_requirements" TO "anon", "authenticated", "postgres", "service_role";

GRANT DELETE, INSERT, MAINTAIN, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE ON TABLE "public"."badges" TO "anon", "authenticated", "postgres", "service_role";

GRANT DELETE, INSERT, MAINTAIN, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE ON TABLE "public"."child_difficulty_progress" TO "anon", "authenticated", "postgres", "service_role";

GRANT DELETE, INSERT, MAINTAIN, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE ON TABLE "public"."child_modifiers" TO "anon", "authenticated", "postgres", "service_role";

GRANT DELETE, INSERT, MAINTAIN, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE ON TABLE "public"."child_reputation_stats" TO "anon", "authenticated", "postgres", "service_role";

GRANT DELETE, INSERT, MAINTAIN, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE ON TABLE "public"."concepts" TO "anon", "authenticated", "postgres", "service_role";

GRANT DELETE, INSERT, MAINTAIN, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE ON TABLE "public"."customer_responses" TO "anon", "authenticated", "postgres", "service_role";

GRANT DELETE, INSERT, MAINTAIN, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE ON TABLE "public"."customer_types" TO "anon", "authenticated", "postgres", "service_role";

GRANT DELETE, INSERT, MAINTAIN, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE ON TABLE "public"."decision_concept_mapping" TO "anon", "authenticated", "postgres", "service_role";

GRANT DELETE, INSERT, MAINTAIN, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE ON TABLE "public"."decision_log" TO "anon", "authenticated", "postgres", "service_role";

GRANT DELETE, INSERT, MAINTAIN, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE ON TABLE "public"."decisions" TO "anon", "authenticated", "postgres", "service_role";

GRANT DELETE, INSERT, MAINTAIN, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE
  ON TABLE "public"."dialogue_golden_eval_dataset"
  TO "anon", "authenticated", "postgres", "service_role";

GRANT DELETE, INSERT, MAINTAIN, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE ON TABLE "public"."dialogue_r1_avatar" TO "anon", "authenticated", "postgres", "service_role";

GRANT DELETE, INSERT, MAINTAIN, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE ON TABLE "public"."dialogue_r1_kid" TO "anon", "authenticated", "postgres", "service_role";

GRANT DELETE, INSERT, MAINTAIN, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE ON TABLE "public"."dialogue_r2_avatar" TO "anon", "authenticated", "postgres", "service_role";

GRANT DELETE, INSERT, MAINTAIN, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE ON TABLE "public"."dialogue_r2_kid" TO "anon", "authenticated", "postgres", "service_role";

GRANT DELETE, INSERT, MAINTAIN, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE ON TABLE "public"."difficulty_event_options" TO "anon", "authenticated", "postgres", "service_role";

GRANT DELETE, INSERT, MAINTAIN, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE ON TABLE "public"."difficulty_events" TO "anon", "authenticated", "postgres", "service_role";

GRANT DELETE, INSERT, MAINTAIN, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE ON TABLE "public"."households" TO "anon", "authenticated", "postgres", "service_role";

GRANT DELETE, INSERT, MAINTAIN, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE ON TABLE "public"."kid_session" TO "anon", "authenticated", "postgres", "service_role";

GRANT DELETE, INSERT, MAINTAIN, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE ON TABLE "public"."level_flavor_settings" TO "anon", "authenticated", "postgres", "service_role";

GRANT DELETE, INSERT, MAINTAIN, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE ON TABLE "public"."location_timing_traffic" TO "anon", "authenticated", "postgres", "service_role";

GRANT DELETE, INSERT, MAINTAIN, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE ON TABLE "public"."nudge_content" TO "anon", "authenticated", "postgres", "service_role";

GRANT DELETE, INSERT, MAINTAIN, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE ON TABLE "public"."options" TO "anon", "authenticated", "postgres", "service_role";

GRANT DELETE, INSERT, MAINTAIN, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE ON TABLE "public"."session_decision_logs" TO "anon", "authenticated", "postgres", "service_role";

GRANT DELETE, INSERT, MAINTAIN, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE ON TABLE "public"."simulation_runs" TO "anon", "authenticated", "postgres", "service_role";

GRANT DELETE, INSERT, MAINTAIN, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE ON TABLE "public"."user_badges" TO "anon", "authenticated", "postgres", "service_role";

GRANT DELETE, INSERT, MAINTAIN, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE ON TABLE "public"."vocabulary_tiers" TO "anon", "authenticated", "postgres", "service_role";

GRANT DELETE, INSERT, MAINTAIN, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE ON TABLE "public"."wallet_ledger" TO "anon", "authenticated", "postgres", "service_role";

GRANT DELETE, INSERT, MAINTAIN, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE ON TABLE "public"."child_reputation_pct" TO "anon", "authenticated", "postgres", "service_role";

