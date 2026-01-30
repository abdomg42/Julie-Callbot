"""
📊 DASHBOARD DE SATISFACTION CLIENT
====================================

Affiche les statistiques de feedback client en temps réel.
"""

import sys
from pathlib import Path

# Add project to path
BASE_DIR = Path(__file__).parent.parent.resolve()
sys.path.insert(0, str(BASE_DIR))

from tool_router.src.database.db_service import db_service


def display_dashboard():
    """Affiche le tableau de bord de satisfaction client"""
    
    print("\n" + "="*80)
    print("📊 DASHBOARD DE SATISFACTION CLIENT - CALLBOT JULIE V2")
    print("="*80)
    
    # =========================================================================
    # 1. STATISTIQUES GLOBALES
    # =========================================================================
    
    # 7 derniers jours
    stats_7d = db_service.get_satisfaction_statistics(days=7)
    
    # 30 derniers jours
    stats_30d = db_service.get_satisfaction_statistics(days=30)
    
    print(f"\n📅 7 DERNIERS JOURS:")
    print(f"   ├── Total interactions: {stats_7d['total_interactions']}")
    print(f"   ├── Feedbacks collectés: {stats_7d['feedbacks_collected']} ({stats_7d['feedback_rate']:.1f}%)")
    print(f"   ├── ✅ Satisfaits: {stats_7d['satisfied']}")
    print(f"   ├── ❌ Insatisfaits: {stats_7d['unsatisfied']}")
    print(f"   └── 📈 TAUX DE SATISFACTION: {stats_7d['satisfaction_rate']:.1f}%")
    
    # Graphique simple ASCII
    if stats_7d['satisfaction_rate'] > 0:
        bar_length = int(stats_7d['satisfaction_rate'] / 5)  # 20 chars = 100%
        bar = "█" * bar_length + "░" * (20 - bar_length)
        print(f"\n       [{bar}] {stats_7d['satisfaction_rate']:.1f}%")
    
    print(f"\n📅 30 DERNIERS JOURS:")
    print(f"   ├── Total interactions: {stats_30d['total_interactions']}")
    print(f"   ├── Feedbacks collectés: {stats_30d['feedbacks_collected']} ({stats_30d['feedback_rate']:.1f}%)")
    print(f"   └── 📈 TAUX DE SATISFACTION: {stats_30d['satisfaction_rate']:.1f}%")
    
    # =========================================================================
    # 2. PERFORMANCE PAR INTENTION
    # =========================================================================
    
    print("\n" + "-"*80)
    print("\n📋 PERFORMANCE PAR INTENTION (30 derniers jours):")
    print("-"*80)
    
    by_intent = db_service.get_satisfaction_by_intent()
    
    if by_intent:
        print(f"\n   {'Intention':<25} {'Total':<8} {'Satisfait':<10} {'Taux':<10} {'Status'}")
        print(f"   {'-'*65}")
        
        for item in by_intent:
            intent = item['intent'][:24] if item['intent'] else 'N/A'
            total = item['total']
            satisfied = item['satisfied']
            rate = item['satisfaction_rate']
            status = item['status']
            
            print(f"   {intent:<25} {total:<8} {satisfied:<10} {rate:>5.1f}%      {status}")
    else:
        print("   (Aucune donnée disponible)")
    
    # =========================================================================
    # 3. PERFORMANCE PAR ACTION (RAG vs HANDOFF)
    # =========================================================================
    
    print("\n" + "-"*80)
    print("\n🎯 PERFORMANCE PAR ACTION (RAG vs Handoff):")
    print("-"*80)
    
    by_action = db_service.get_satisfaction_by_action()
    
    if by_action:
        print(f"\n   {'Action':<25} {'Total':<8} {'Satisfait':<10} {'Insatisfait':<12} {'Taux'}")
        print(f"   {'-'*65}")
        
        for item in by_action:
            action = item['action_taken'][:24] if item['action_taken'] else 'N/A'
            total = item['total']
            satisfied = item['satisfied']
            unsatisfied = item['unsatisfied']
            rate = item['satisfaction_rate']
            
            # Emoji basé sur le taux
            emoji = "✅" if rate >= 80 else "⚠️" if rate >= 60 else "❌"
            
            print(f"   {emoji} {action:<23} {total:<8} {satisfied:<10} {unsatisfied:<12} {rate:>5.1f}%")
    else:
        print("   (Aucune donnée disponible)")
    
    # =========================================================================
    # 4. ANALYSE ET RECOMMANDATIONS
    # =========================================================================
    
    print("\n" + "-"*80)
    print("\n💡 RECOMMANDATIONS:")
    print("-"*80)
    
    recommendations = []
    
    # Analyser les données
    if stats_7d['satisfaction_rate'] < 70:
        recommendations.append("⚠️ Taux de satisfaction < 70% - Améliorer les templates de réponse")
    
    if stats_7d['feedback_rate'] < 50:
        recommendations.append("⚠️ Taux de collecte < 50% - Encourager davantage les feedbacks")
    
    if by_intent:
        low_performers = [i for i in by_intent if i['satisfaction_rate'] < 60]
        for lp in low_performers[:3]:
            recommendations.append(f"❌ Intent '{lp['intent']}' problématique ({lp['satisfaction_rate']:.1f}%) - Améliorer les réponses")
    
    if by_action:
        for action in by_action:
            if action['action_taken'] == 'rag_query' and action['satisfaction_rate'] < 75:
                recommendations.append(f"⚠️ RAG performance faible ({action['satisfaction_rate']:.1f}%) - Enrichir la base de connaissances")
    
    if not recommendations:
        recommendations.append("✅ Aucun problème majeur détecté - Continuez comme ça !")
    
    for i, rec in enumerate(recommendations, 1):
        print(f"   {i}. {rec}")
    
    # =========================================================================
    # FOOTER
    # =========================================================================
    
    print("\n" + "="*80)
    print("🕐 Dashboard généré le:", end=" ")
    import time
    print(time.strftime("%Y-%m-%d %H:%M:%S"))
    print("="*80 + "\n")


if __name__ == "__main__":
    display_dashboard()
