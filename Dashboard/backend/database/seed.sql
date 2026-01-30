--
-- PostgreSQL database dump
--

\restrict ccTMzl8ymVMl6raf2weZ8MPkRkSkawRtwaoPJcxbe8RelOtSNg7C8tTYo5Fe7AX

-- Dumped from database version 18.1
-- Dumped by pg_dump version 18.1

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: uuid-ossp; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS "uuid-ossp" WITH SCHEMA public;


--
-- Name: EXTENSION "uuid-ossp"; Type: COMMENT; Schema: -; Owner: -
--

COMMENT ON EXTENSION "uuid-ossp" IS 'generate universally unique identifiers (UUIDs)';


--
-- Name: calculate_resolution_time(); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION public.calculate_resolution_time() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    IF NEW.resolved_at IS NOT NULL AND OLD.resolved_at IS NULL THEN
        NEW.resolution_time_seconds = EXTRACT(EPOCH FROM (NEW.resolved_at - NEW.created_at));
    END IF;
    RETURN NEW;
END;
$$;


--
-- Name: update_callbot_timestamp(); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION public.update_callbot_timestamp() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    
    -- Calculer le temps de résolution si l'interaction est résolue
    IF NEW.status IN ('completed', 'resolved') AND OLD.status != NEW.status THEN
        NEW.resolved_at = CURRENT_TIMESTAMP;
        NEW.resolution_time_seconds = EXTRACT(EPOCH FROM (CURRENT_TIMESTAMP - NEW.created_at))::INTEGER;
    END IF;
    
    RETURN NEW;
END;
$$;


SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: callbot_interactions; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.callbot_interactions (
    interaction_id character varying(50) DEFAULT ((('INT-'::text || EXTRACT(year FROM CURRENT_DATE)) || '-'::text) || "substring"((public.uuid_generate_v4())::text, 1, 8)) NOT NULL,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    customer_id character varying(50),
    customer_name character varying(200),
    customer_email character varying(150),
    customer_phone character varying(20),
    session_id character varying(100),
    channel character varying(20) DEFAULT 'phone'::character varying,
    intent character varying(50) NOT NULL,
    urgency character varying(20) DEFAULT 'medium'::character varying,
    emotion character varying(20) DEFAULT 'neutral'::character varying,
    confidence numeric(3,2),
    customer_message text,
    bot_response text,
    conversation_history jsonb DEFAULT '[]'::jsonb,
    action_taken character varying(50) NOT NULL,
    action_type character varying(50),
    action_result jsonb,
    success boolean DEFAULT true,
    crm_action_details jsonb,
    execution_time_ms integer,
    is_handoff boolean DEFAULT false,
    handoff_reason text,
    handoff_queue character varying(20),
    handoff_department character varying(50),
    assigned_agent character varying(50),
    ticket_status character varying(20),
    estimated_wait_seconds integer,
    status character varying(20) DEFAULT 'pending'::character varying,
    priority character varying(20) DEFAULT 'normal'::character varying,
    resolved_at timestamp without time zone,
    resolution_time_seconds integer,
    customer_satisfaction integer,
    feedback_comment text,
    metadata jsonb DEFAULT '{}'::jsonb
);


--
-- Name: TABLE callbot_interactions; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.callbot_interactions IS 'Table unique regroupant toutes les interactions du callbot';


--
-- Name: COLUMN callbot_interactions.conversation_history; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.callbot_interactions.conversation_history IS 'Historique complet en JSON [{turn: 1, speaker: "customer", text: "..."}]';


--
-- Name: COLUMN callbot_interactions.action_result; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.callbot_interactions.action_result IS 'Résultat de l''action en JSON';


--
-- Name: COLUMN callbot_interactions.crm_action_details; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.callbot_interactions.crm_action_details IS 'Détails spécifiques de l''action CRM en JSON';


--
-- Name: COLUMN callbot_interactions.metadata; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.callbot_interactions.metadata IS 'Données additionnelles flexibles en JSON';


--
-- Name: v_active_interactions; Type: VIEW; Schema: public; Owner: -
--

CREATE VIEW public.v_active_interactions AS
 SELECT interaction_id,
    customer_name,
    intent,
    urgency,
    action_taken,
    status,
    created_at,
    (EXTRACT(epoch FROM (CURRENT_TIMESTAMP - (created_at)::timestamp with time zone)))::integer AS duration_seconds
   FROM public.callbot_interactions
  WHERE ((status)::text = ANY (ARRAY[('pending'::character varying)::text, ('in_progress'::character varying)::text]));


--
-- Name: v_daily_stats; Type: VIEW; Schema: public; Owner: -
--

CREATE VIEW public.v_daily_stats AS
 SELECT date(created_at) AS date,
    count(*) AS total_interactions,
    count(*) FILTER (WHERE ((action_taken)::text = 'automated_response'::text)) AS automated,
    count(*) FILTER (WHERE ((action_taken)::text = 'crm_action'::text)) AS crm_actions,
    count(*) FILTER (WHERE (is_handoff = true)) AS handoffs,
    round(avg(confidence), 2) AS avg_confidence,
    avg(resolution_time_seconds) AS avg_resolution_time,
    count(DISTINCT customer_id) AS unique_customers,
    count(*) FILTER (WHERE ((status)::text = 'completed'::text)) AS completed,
    count(*) FILTER (WHERE ((status)::text = 'failed'::text)) AS failed
   FROM public.callbot_interactions
  GROUP BY (date(created_at))
  ORDER BY (date(created_at)) DESC;


--
-- Name: v_pending_handoffs; Type: VIEW; Schema: public; Owner: -
--

CREATE VIEW public.v_pending_handoffs AS
 SELECT interaction_id,
    customer_name,
    customer_phone,
    handoff_reason,
    handoff_queue,
    handoff_department,
    ticket_status,
    estimated_wait_seconds,
    created_at
   FROM public.callbot_interactions
  WHERE ((is_handoff = true) AND ((ticket_status)::text = ANY (ARRAY[('pending'::character varying)::text, ('assigned'::character varying)::text])));


--
-- Data for Name: callbot_interactions; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.callbot_interactions (interaction_id, created_at, updated_at, customer_id, customer_name, customer_email, customer_phone, session_id, channel, intent, urgency, emotion, confidence, customer_message, bot_response, conversation_history, action_taken, action_type, action_result, success, crm_action_details, execution_time_ms, is_handoff, handoff_reason, handoff_queue, handoff_department, assigned_agent, ticket_status, estimated_wait_seconds, status, priority, resolved_at, resolution_time_seconds, customer_satisfaction, feedback_comment, metadata) FROM stdin;
INT-2026-77df2a36	2026-01-24 17:53:10.819919	2026-01-24 17:53:10.819919	CUST-001	Jean Dupont	jean.dupont@example.com	+33612345678	SESSION-001	phone	update_address	low	neutral	0.95	Je veux mettre à jour mon adresse	Bien sûr, je peux vous aider à mettre à jour votre adresse.	[]	crm_action	update_address	\N	t	{"new_address": "456 Av Champs-Élysées", "old_address": "123 Rue Paris"}	\N	f	\N	\N	\N	\N	\N	\N	completed	normal	\N	\N	\N	\N	{}
INT-2026-5069e150	2026-01-24 17:53:10.819919	2026-01-24 17:53:10.819919	CUST-002	Marie Dubois	marie.dubois@example.com	+33687654321	SESSION-002	phone	declare_claim	high	stressed	0.88	Mon fils a eu un accident grave ! C'est urgent !	Je comprends votre situation. Je vous mets en relation avec un agent spécialisé.	[]	human_handoff	\N	\N	t	\N	\N	t	Cas urgent - accident grave	urgent	sinistres	\N	pending	120	in_progress	high	\N	\N	\N	\N	{}
INT-2026-21D3CD07	2026-01-24 18:09:08.241881	2026-01-24 18:09:08.365865	TEST-CUST-001	\N	\N	\N	TEST-SESSION-001	phone	test_connection	low	neutral	0.95	\N	\N	[]	automated_response	\N	\N	t	\N	\N	f	\N	\N	\N	\N	\N	\N	completed	normal	2026-01-24 18:09:08.365865	0	\N	\N	{}
INT-2026-3B705D7B	2026-01-24 18:09:34.143593	2026-01-24 18:09:34.475119	TEST-CUST-001	\N	\N	\N	TEST-SESSION-001	phone	test_connection	low	neutral	0.95	Test message de connexion à la base de données	\N	[{"speaker": "customer", "metadata": {}, "timestamp": "2026-01-24T18:09:34.312968", "confidence": 0.95, "message_id": "MSG-CB983E53", "turn_number": 1, "message_text": "Test message de connexion à la base de données", "detected_intent": "test_connection", "detected_emotion": "neutral"}]	automated_response	test_action	{"test": "output"}	t	{"error": null, "input": {"test": "input"}}	100	f	\N	\N	\N	\N	\N	\N	completed	normal	2026-01-24 18:09:34.255457	0	\N	\N	{}
INT-2026-FE146F69	2026-01-24 18:24:36.99076	2026-01-24 18:24:37.94793	TEST-CUST-001	\N	\N	\N	TEST-SESSION-001	phone	test_connection	low	neutral	0.95	Test message de connexion à la base de données	Test response	[{"speaker": "customer", "metadata": {}, "timestamp": "2026-01-24T18:24:37.188333", "confidence": 0.95, "message_id": "MSG-04A56E04", "turn_number": 1, "message_text": "Test message de connexion à la base de données", "detected_intent": "test_connection", "detected_emotion": "neutral"}]	automated_response	test_action	{"test": "output"}	t	{"error": null, "input": {"test": "input"}}	100	t	Test escalation pour vérification connexion DB	test_queue	test_department	\N	queued	300	completed	normal	2026-01-24 18:24:37.101007	0	\N	\N	{"tone": "professional", "language": "fr", "ticket_id": "TKT-2026-7C70A3", "key_information": {"test": true, "connection": "ok"}, "skills_required": [], "generation_method": "template", "generation_time_ms": 200}
INT-2026-684B7807	2026-01-24 18:09:59.081894	2026-01-24 18:09:59.755124	TEST-CUST-001	\N	\N	\N	TEST-SESSION-001	phone	test_connection	low	neutral	0.95	Test message de connexion à la base de données	Test response	[{"speaker": "customer", "metadata": {}, "timestamp": "2026-01-24T18:09:59.399332", "confidence": 0.95, "message_id": "MSG-6A0488B1", "turn_number": 1, "message_text": "Test message de connexion à la base de données", "detected_intent": "test_connection", "detected_emotion": "neutral"}]	automated_response	test_action	{"test": "output"}	t	{"error": null, "input": {"test": "input"}}	100	t	Test escalation pour vérification connexion DB	test_queue	test_department	\N	queued	300	completed	normal	2026-01-24 18:09:59.190604	0	\N	\N	{"tone": "professional", "language": "fr", "ticket_id": "TKT-2026-A7FB2F", "key_information": {"test": true, "connection": "ok"}, "skills_required": [], "generation_method": "template", "generation_time_ms": 200}
INT-2026-F70D71A7	2026-01-24 18:34:40.261139	2026-01-24 18:34:40.712518	DEMO-CUST-001	\N	\N	\N	SESSION-20260124-1F4D7638	phone	check_policy_status	low	neutral	0.92	Bonjour, je voudrais vérifier le statut de ma police d'assurance	Votre police d'assurance est active et valide jusqu'au 31 décembre 2025. Puis-je vous aider avec autre chose ?	[{"speaker": "customer", "metadata": {}, "timestamp": "2026-01-24T18:34:40.265890", "confidence": 0.92, "message_id": "MSG-7C5FD8F9", "turn_number": 1, "message_text": "Bonjour, je voudrais vérifier le statut de ma police d'assurance", "detected_intent": "check_policy_status", "detected_emotion": "neutral"}, {"speaker": "agent", "metadata": {}, "timestamp": "2026-01-24T18:34:40.413496", "confidence": null, "message_id": "MSG-B46092F1", "turn_number": 2, "message_text": "Votre police d'assurance est active et valide jusqu'au 31 décembre 2025. Puis-je vous aider avec autre chose ?", "detected_intent": null, "detected_emotion": null}]	crm_action	check_policy_status	{"status": "active", "expiry_date": "2025-12-31"}	t	{"error": null, "input": {"policy_id": "POL-12345"}}	150	f	\N	\N	\N	\N	\N	\N	completed	normal	2026-01-24 18:34:40.712518	0	\N	\N	{"tone": "professional", "language": "fr", "generation_method": "template", "generation_time_ms": 200}
INT-2026-8933AB5C	2026-01-24 18:34:45.568302	2026-01-24 18:34:46.154136	DEMO-CUST-002	\N	\N	\N	SESSION-20260124-7ED2A2B7	phone	declare_claim	high	stressed	0.88	Bonjour, mon fils a eu un accident grave ! Je dois déclarer un sinistre immédiatement !	Je comprends votre situation et je vous assure que nous allons vous aider. Je vous transfère immédiatement vers un conseiller spécialisé en sinistres graves.	[{"speaker": "customer", "metadata": {}, "timestamp": "2026-01-24T18:34:45.571645", "confidence": 0.88, "message_id": "MSG-1F9057C1", "turn_number": 1, "message_text": "Bonjour, mon fils a eu un accident grave ! Je dois déclarer un sinistre immédiatement !", "detected_intent": "declare_claim", "detected_emotion": "stressed"}, {"speaker": "agent", "metadata": {}, "timestamp": "2026-01-24T18:34:45.708280", "confidence": null, "message_id": "MSG-C595A755", "turn_number": 2, "message_text": "Je comprends votre situation et je vous assure que nous allons vous aider. Je vous transfère immédiatement vers un conseiller spécialisé en sinistres graves. Vous serez pris en charge dans les 3 prochaines minutes maximum.", "detected_intent": null, "detected_emotion": null}]	human_handoff	\N	\N	t	\N	\N	t	Client très stressé - fils victime d'accident grave - besoin intervention immédiate	urgent	sinistres_graves	\N	queued	180	in_progress	high	\N	\N	\N	\N	{"tone": "empathetic", "language": "fr", "ticket_id": "TKT-2026-0C4680", "key_information": {"victim": "fils du client", "emotion": "stressed", "urgency": "high", "accident_type": "grave"}, "skills_required": ["gestion_sinistres", "urgences", "empathie"], "generation_method": "template", "generation_time_ms": 180}
INT-2026-5C006D8C	2026-01-26 21:44:28.441844	2026-01-26 21:45:18.612851	CUST-001	\N	\N	\N	SESSION-20260126-9CD8C5FF	phone	check_policy_status	low	neutral	0.92	Je voudrais vérifier le statut de ma police d'assurance	None	[{"speaker": "customer", "metadata": {}, "timestamp": "2026-01-26T21:44:28.453582", "confidence": 0.92, "message_id": "MSG-5B499459", "turn_number": 1, "message_text": "Je voudrais vérifier le statut de ma police d'assurance", "detected_intent": "check_policy_status", "detected_emotion": "neutral"}, {"speaker": "agent", "metadata": {}, "timestamp": "2026-01-26T21:44:35.305507", "confidence": null, "message_id": "MSG-A5335C74", "turn_number": 2, "message_text": "None", "detected_intent": null, "detected_emotion": null}]	routing	\N	\N	t	\N	\N	f	\N	\N	\N	\N	\N	\N	pending	normal	\N	\N	\N	\N	{"tone": "professional", "language": "fr", "generation_method": "team", "generation_time_ms": 43142}
INT-2026-587DFC6E	2026-01-24 18:34:49.952117	2026-01-24 18:34:50.566514	DEMO-CUST-003	\N	\N	\N	SESSION-20260124-9D30482C	phone	update_payment_method	medium	neutral	0.85	Je veux changer ma carte bancaire pour les prélèvements	Je suis désolé, mais je ne peux pas enregistrer cette carte car elle est expirée. Pourriez-vous fournir une autre carte bancaire valide ?	[{"speaker": "customer", "metadata": {}, "timestamp": "2026-01-24T18:34:49.955090", "confidence": 0.85, "message_id": "MSG-E8F2374C", "turn_number": 1, "message_text": "Je veux changer ma carte bancaire pour les prélèvements", "detected_intent": "update_payment_method", "detected_emotion": "neutral"}, {"speaker": "agent", "metadata": {}, "timestamp": "2026-01-24T18:34:50.224377", "confidence": null, "message_id": "MSG-43B26FC1", "turn_number": 2, "message_text": "Je suis désolé, mais je ne peux pas enregistrer cette carte car elle est expirée. Pourriez-vous fournir une autre carte bancaire valide ?", "detected_intent": null, "detected_emotion": null}]	crm_action	update_payment_method	{}	f	{"error": "Erreur de validation - carte expirée", "input": {"new_card_number": "****1234"}}	120	f	\N	\N	\N	\N	\N	\N	failed	normal	2026-01-24 18:34:50.566514	1	\N	\N	{}
INT-2026-3514596D	2026-01-26 21:46:11.252709	2026-01-26 21:46:24.663719	CUST-002	\N	\N	\N	SESSION-20260126-1169C8D5	phone	declare_claim	high	stressed	0.88	Je dois déclarer un accident grave, c'est urgent!	None	[{"speaker": "customer", "metadata": {}, "timestamp": "2026-01-26T21:46:11.256848", "confidence": 0.88, "message_id": "MSG-EB2E10D9", "turn_number": 1, "message_text": "Je dois déclarer un accident grave, c'est urgent!", "detected_intent": "declare_claim", "detected_emotion": "stressed"}, {"speaker": "agent", "metadata": {}, "timestamp": "2026-01-26T21:46:14.332689", "confidence": null, "message_id": "MSG-A1B2E334", "turn_number": 2, "message_text": "None", "detected_intent": null, "detected_emotion": null}]	routing	\N	\N	t	\N	\N	f	\N	\N	\N	\N	\N	\N	pending	high	\N	\N	\N	\N	{"tone": "reassuring", "language": "fr", "generation_method": "team", "generation_time_ms": 10168}
\.


--
-- Name: callbot_interactions callbot_interactions_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.callbot_interactions
    ADD CONSTRAINT callbot_interactions_pkey PRIMARY KEY (interaction_id);


--
-- Name: idx_callbot_created; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_callbot_created ON public.callbot_interactions USING btree (created_at DESC);


--
-- Name: idx_callbot_customer; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_callbot_customer ON public.callbot_interactions USING btree (customer_id);


--
-- Name: idx_callbot_handoff; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_callbot_handoff ON public.callbot_interactions USING btree (is_handoff) WHERE (is_handoff = true);


--
-- Name: idx_callbot_intent; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_callbot_intent ON public.callbot_interactions USING btree (intent);


--
-- Name: idx_callbot_status; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_callbot_status ON public.callbot_interactions USING btree (status);


--
-- Name: callbot_interactions trigger_update_callbot_timestamp; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER trigger_update_callbot_timestamp BEFORE UPDATE ON public.callbot_interactions FOR EACH ROW EXECUTE FUNCTION public.update_callbot_timestamp();


--
-- PostgreSQL database dump complete
--

\unrestrict ccTMzl8ymVMl6raf2weZ8MPkRkSkawRtwaoPJcxbe8RelOtSNg7C8tTYo5Fe7AX

