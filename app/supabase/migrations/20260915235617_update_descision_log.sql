alter table "public"."decision_log" 
    alter column decision_value Type text,
    alter column decision_value drop not null,
    add column value_jsonb jsonb,
    alter column screen_id drop not null,
    add constraint unique_kid_decision
    unique(kid_session_id, decision_key);


alter table "public"."decision_log"
    rename column screen_id to source_screen;