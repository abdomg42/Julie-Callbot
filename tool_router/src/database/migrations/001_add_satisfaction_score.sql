-- Migration: Add satisfaction_score column to callbot_interactions table
-- Date: January 29, 2026
-- Description: Adds customer satisfaction scoring functionality

-- Add satisfaction_score column
ALTER TABLE callbot_interactions
ADD COLUMN IF NOT EXISTS satisfaction_score DECIMAL(3,2) CHECK (satisfaction_score >= 0.0 AND satisfaction_score <= 5.0);

-- Add comment for documentation
COMMENT ON COLUMN callbot_interactions.satisfaction_score IS 'Customer satisfaction score (0.0 to 5.0 scale)';

-- Create index for performance
CREATE INDEX IF NOT EXISTS idx_callbot_interactions_satisfaction_score
ON callbot_interactions(satisfaction_score);

-- Create view for satisfaction analytics
CREATE OR REPLACE VIEW v_satisfaction_summary AS
SELECT
    DATE(created_at) as date,
    COUNT(*) as total_interactions,
    ROUND(AVG(satisfaction_score), 2) as avg_satisfaction,
    COUNT(CASE WHEN satisfaction_score >= 4.0 THEN 1 END) as satisfied_count,
    COUNT(CASE WHEN satisfaction_score < 3.0 THEN 1 END) as dissatisfied_count,
    ROUND(
        (COUNT(CASE WHEN satisfaction_score >= 4.0 THEN 1 END)::DECIMAL /
         NULLIF(COUNT(*), 0)) * 100, 1
    ) as satisfaction_rate_percent
FROM callbot_interactions
WHERE satisfaction_score IS NOT NULL
GROUP BY DATE(created_at)
ORDER BY date DESC;

-- Create view for detailed satisfaction analysis
CREATE OR REPLACE VIEW v_satisfaction_details AS
SELECT
    interaction_id,
    session_id,
    intent,
    urgency,
    emotion,
    action_taken,
    satisfaction_score,
    created_at,
    CASE
        WHEN satisfaction_score >= 4.5 THEN 'Excellent'
        WHEN satisfaction_score >= 4.0 THEN 'Very Good'
        WHEN satisfaction_score >= 3.5 THEN 'Good'
        WHEN satisfaction_score >= 3.0 THEN 'Fair'
        WHEN satisfaction_score >= 2.0 THEN 'Poor'
        ELSE 'Very Poor'
    END as satisfaction_category
FROM callbot_interactions
WHERE satisfaction_score IS NOT NULL
ORDER BY created_at DESC;

-- Grant permissions (adjust as needed for your setup)
-- GRANT SELECT ON v_satisfaction_summary TO your_readonly_user;
-- GRANT SELECT ON v_satisfaction_details TO your_readonly_user;
