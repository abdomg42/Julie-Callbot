-- ============================================================================
-- MIGRATION 001: Ajout du feedback client (satisfaction_score)
-- Date: 2026-01-29
-- Description: Ajoute une colonne satisfaction_score à callbot_interactions
-- ============================================================================

-- 1. Ajouter la colonne satisfaction_score
ALTER TABLE callbot_interactions 
ADD COLUMN IF NOT EXISTS satisfaction_score INTEGER 
CHECK (satisfaction_score IS NULL OR satisfaction_score IN (1, 2));

-- Commentaire explicatif
COMMENT ON COLUMN callbot_interactions.satisfaction_score IS 
'Feedback client en fin d''appel: 1=Satisfait (Oui), 2=Insatisfait (Non), NULL=Pas de feedback collecté';

-- 2. Ajouter un index pour les requêtes statistiques rapides
CREATE INDEX IF NOT EXISTS idx_callbot_satisfaction 
ON callbot_interactions(satisfaction_score) 
WHERE satisfaction_score IS NOT NULL;

-- 3. Ajouter un index composite pour analyses avancées
CREATE INDEX IF NOT EXISTS idx_callbot_satisfaction_intent 
ON callbot_interactions(satisfaction_score, intent, created_at) 
WHERE satisfaction_score IS NOT NULL;

-- ============================================================================
-- VUES POUR STATISTIQUES
-- ============================================================================

-- Vue 1: Statistiques globales de satisfaction
CREATE OR REPLACE VIEW v_satisfaction_stats AS
SELECT 
    DATE(created_at) as date,
    COUNT(*) as total_interactions,
    COUNT(satisfaction_score) as feedbacks_collected,
    SUM(CASE WHEN satisfaction_score = 1 THEN 1 ELSE 0 END) as satisfied_count,
    SUM(CASE WHEN satisfaction_score = 2 THEN 1 ELSE 0 END) as unsatisfied_count,
    ROUND(
        100.0 * SUM(CASE WHEN satisfaction_score = 1 THEN 1 ELSE 0 END) 
        / NULLIF(COUNT(satisfaction_score), 0), 
        2
    ) as satisfaction_rate_pct,
    ROUND(
        100.0 * COUNT(satisfaction_score) / COUNT(*), 
        2
    ) as feedback_collection_rate_pct
FROM callbot_interactions
WHERE created_at >= CURRENT_DATE - INTERVAL '90 days'
GROUP BY DATE(created_at)
ORDER BY date DESC;

COMMENT ON VIEW v_satisfaction_stats IS 
'Statistiques quotidiennes de satisfaction client (90 derniers jours)';

-- Vue 2: Satisfaction par intention
CREATE OR REPLACE VIEW v_satisfaction_by_intent AS
SELECT 
    intent,
    COUNT(*) as total_with_feedback,
    SUM(CASE WHEN satisfaction_score = 1 THEN 1 ELSE 0 END) as satisfied,
    SUM(CASE WHEN satisfaction_score = 2 THEN 1 ELSE 0 END) as unsatisfied,
    ROUND(
        100.0 * SUM(CASE WHEN satisfaction_score = 1 THEN 1 ELSE 0 END) 
        / COUNT(*), 
        1
    ) as satisfaction_rate_pct,
    CASE 
        WHEN ROUND(100.0 * SUM(CASE WHEN satisfaction_score = 1 THEN 1 ELSE 0 END) / COUNT(*), 1) >= 80 THEN '✅ Excellent'
        WHEN ROUND(100.0 * SUM(CASE WHEN satisfaction_score = 1 THEN 1 ELSE 0 END) / COUNT(*), 1) >= 60 THEN '⚠️ Acceptable'
        ELSE '❌ Problématique'
    END as status
FROM callbot_interactions
WHERE satisfaction_score IS NOT NULL
  AND created_at >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY intent
ORDER BY satisfaction_rate_pct ASC, total_with_feedback DESC;

COMMENT ON VIEW v_satisfaction_by_intent IS 
'Performance de satisfaction par type d''intention (30 derniers jours)';

-- Vue 3: Interactions insatisfaites (pour analyse)
CREATE OR REPLACE VIEW v_unsatisfied_interactions AS
SELECT 
    interaction_id,
    customer_id,
    session_id,
    intent,
    urgency,
    emotion,
    confidence,
    action_taken,
    is_handoff,
    customer_message,
    bot_response,
    created_at,
    metadata
FROM callbot_interactions
WHERE satisfaction_score = 2
  AND created_at >= CURRENT_DATE - INTERVAL '30 days'
ORDER BY created_at DESC;

COMMENT ON VIEW v_unsatisfied_interactions IS 
'Liste des interactions insatisfaites pour amélioration du système';

-- Vue 4: Satisfaction par action (RAG vs Handoff)
CREATE OR REPLACE VIEW v_satisfaction_by_action AS
SELECT 
    action_taken,
    COUNT(*) as total,
    SUM(CASE WHEN satisfaction_score = 1 THEN 1 ELSE 0 END) as satisfied,
    SUM(CASE WHEN satisfaction_score = 2 THEN 1 ELSE 0 END) as unsatisfied,
    ROUND(
        100.0 * SUM(CASE WHEN satisfaction_score = 1 THEN 1 ELSE 0 END) 
        / COUNT(*), 
        1
    ) as satisfaction_rate_pct
FROM callbot_interactions
WHERE satisfaction_score IS NOT NULL
  AND created_at >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY action_taken
ORDER BY satisfaction_rate_pct DESC;

COMMENT ON VIEW v_satisfaction_by_action IS 
'Comparaison de satisfaction entre actions (RAG, handoff, etc.)';

-- ============================================================================
-- FONCTION UTILITAIRE: Obtenir les statistiques de satisfaction
-- ============================================================================

CREATE OR REPLACE FUNCTION get_satisfaction_statistics(days_back INTEGER DEFAULT 7)
RETURNS TABLE (
    total_interactions BIGINT,
    feedbacks_collected BIGINT,
    satisfied BIGINT,
    unsatisfied BIGINT,
    satisfaction_rate NUMERIC,
    feedback_rate NUMERIC
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        COUNT(*) as total_interactions,
        COUNT(satisfaction_score) as feedbacks_collected,
        SUM(CASE WHEN satisfaction_score = 1 THEN 1 ELSE 0 END) as satisfied,
        SUM(CASE WHEN satisfaction_score = 2 THEN 1 ELSE 0 END) as unsatisfied,
        ROUND(
            100.0 * SUM(CASE WHEN satisfaction_score = 1 THEN 1 ELSE 0 END) 
            / NULLIF(COUNT(satisfaction_score), 0), 
            2
        ) as satisfaction_rate,
        ROUND(
            100.0 * COUNT(satisfaction_score) / COUNT(*), 
            2
        ) as feedback_rate
    FROM callbot_interactions
    WHERE created_at >= CURRENT_DATE - (days_back || ' days')::INTERVAL;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION get_satisfaction_statistics IS 
'Fonction pour obtenir rapidement les stats de satisfaction: SELECT * FROM get_satisfaction_statistics(7);';

-- ============================================================================
-- VÉRIFICATION DE LA MIGRATION
-- ============================================================================

-- Vérifier que la colonne a été ajoutée
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 
        FROM information_schema.columns 
        WHERE table_name = 'callbot_interactions' 
          AND column_name = 'satisfaction_score'
    ) THEN
        RAISE NOTICE '✅ Migration réussie: colonne satisfaction_score ajoutée';
    ELSE
        RAISE EXCEPTION '❌ Migration échouée: colonne satisfaction_score non trouvée';
    END IF;
END $$;

-- Afficher les vues créées
SELECT 
    schemaname,
    viewname,
    viewowner
FROM pg_views
WHERE viewname LIKE 'v_satisfaction%'
ORDER BY viewname;

-- ============================================================================
-- FIN DE LA MIGRATION
-- ============================================================================