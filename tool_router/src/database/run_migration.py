"""
🔧 Exécuter la migration pour ajouter satisfaction_score
"""

import psycopg2
from pathlib import Path
import os
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

def run_migration():
    """Exécute la migration SQL"""
    
    # Chemin du fichier de migration
    migration_file = Path(__file__).parent / "migrations" / "001_add_satisfaction_score.sql"
    
    if not migration_file.exists():
        print(f"❌ Fichier de migration introuvable: {migration_file}")
        return False
    
    # Lire le contenu SQL
    with open(migration_file, 'r', encoding='utf-8') as f:
        sql_content = f.read()
    
    # Connexion à la base de données (utiliser le superuser postgres)
    connection_string = os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:1598@localhost:5432/callbot_db"
    )
    
    # Si erreur de permissions, essayer avec postgres
    alt_connection_string = "postgresql://postgres:1598@localhost:5432/callbot_db"
    
    print("\n" + "="*80)
    print("🔧 EXÉCUTION DE LA MIGRATION: Ajout de satisfaction_score")
    print("="*80)
    print(f"📁 Fichier: {migration_file.name}")
    print(f"🗄️  Base: {connection_string.split('@')[1]}")
    print("="*80 + "\n")
    
    try:
        # Essayer d'abord avec la connexion standard
        try:
            conn = psycopg2.connect(connection_string)
        except psycopg2.OperationalError:
            print("⚠️  Tentative avec utilisateur postgres...")
            conn = psycopg2.connect(alt_connection_string)
        
        cursor = conn.cursor()
        
        # Exécuter la migration
        cursor.execute(sql_content)
        conn.commit()
        
        print("✅ Migration exécutée avec succès !")
        
        # Vérifier que la colonne existe
        cursor.execute("""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns
            WHERE table_name = 'callbot_interactions'
              AND column_name = 'satisfaction_score'
        """)
        
        result = cursor.fetchone()
        if result:
            print(f"\n📊 Colonne créée:")
            print(f"   Nom: {result[0]}")
            print(f"   Type: {result[1]}")
            print(f"   Nullable: {result[2]}")
        
        # Lister les vues créées
        cursor.execute("""
            SELECT viewname
            FROM pg_views
            WHERE viewname LIKE 'v_satisfaction%'
            ORDER BY viewname
        """)
        
        views = cursor.fetchall()
        if views:
            print(f"\n📈 Vues créées ({len(views)}):")
            for view in views:
                print(f"   • {view[0]}")
        
        cursor.close()
        conn.close()
        
        print("\n" + "="*80)
        print("🎉 MIGRATION TERMINÉE AVEC SUCCÈS")
        print("="*80 + "\n")
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERREUR lors de la migration:")
        print(f"   {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_migration()
    exit(0 if success else 1)