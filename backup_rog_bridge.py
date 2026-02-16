#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ROG Dashboard Backup Tool v1.0
Script de sauvegarde automatique pour ROG Bridge
"""

import os
import shutil
import sys
from datetime import datetime
import json

# =============================================================================
# CONFIGURATION
# =============================================================================

# Liste des fichiers à sauvegarder (modifie si nécessaire)
FILES_TO_BACKUP = [
    "rog_bridge.py",
    "dashboard.js",
    "format.css",
    "start.html",
    "rog_password.txt"
]

# Dossier de sauvegarde (même emplacement que le script)
BACKUP_FOLDER_NAME = "ROG_Backup"

# =============================================================================
# FONCTIONS DE SAUVEGARDE
# =============================================================================

def get_script_directory():
    """Retourne le dossier où se trouve ce script"""
    return os.path.dirname(os.path.abspath(__file__))

def create_backup():
    """
    Crée une sauvegarde complète du ROG Dashboard.
    Si une sauvegarde existe déjà, elle est remplacée.
    """

    script_dir = get_script_directory()
    backup_dir = os.path.join(script_dir, BACKUP_FOLDER_NAME)

    print("=" * 70)
    print("🔧 ROG BRIDGE BACKUP TOOL v1.0")
    print("=" * 70)
    print(f"📁 Dossier source: {script_dir}")
    print(f"📂 Dossier sauvegarde: {backup_dir}")
    print()

    # Vérifier si les fichiers source existent
    existing_files = []
    missing_files = []

    for filename in FILES_TO_BACKUP:
        filepath = os.path.join(script_dir, filename)
        if os.path.exists(filepath):
            existing_files.append(filename)
        else:
            missing_files.append(filename)

    if not existing_files:
        print("❌ ERREUR: Aucun fichier à sauvegarder trouvé!")
        print("   Vérifie que ce script est dans le même dossier que tes fichiers ROG.")
        input("\nAppuie sur Entrée pour fermer...")
        return False

    # Si une ancienne sauvegarde existe, la supprimer
    if os.path.exists(backup_dir):
        print("🗑️  Ancienne sauvegarde détectée, suppression en cours...")
        try:
            shutil.rmtree(backup_dir)
            print("✅ Ancienne sauvegarde supprimée")
        except Exception as e:
            print(f"❌ Erreur lors de la suppression: {e}")
            input("\nAppuie sur Entrée pour fermer...")
            return False

    # Créer le nouveau dossier de sauvegarde
    try:
        os.makedirs(backup_dir, exist_ok=True)
        print(f"📂 Dossier de sauvegarde créé")
    except Exception as e:
        print(f"❌ Erreur création dossier: {e}")
        input("\nAppuie sur Entrée pour fermer...")
        return False

    print()
    print("📋 Copie des fichiers:")
    print("-" * 70)

    # Copier chaque fichier
    copied_files = []
    for filename in existing_files:
        source_path = os.path.join(script_dir, filename)
        dest_path = os.path.join(backup_dir, filename)

        try:
            shutil.copy2(source_path, dest_path)
            size = os.path.getsize(source_path)
            copied_files.append({"name": filename, "size": size})
            print(f"   ✅ {filename:<25} ({size:>7,} bytes)")
        except Exception as e:
            print(f"   ❌ {filename:<25} [ERREUR: {e}]")

    # Créer le fichier d'information
    backup_info = {
        "date_creation": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "version_dashboard": "6.0",
        "nombre_fichiers": len(copied_files),
        "fichiers": copied_files,
        "fichiers_manquants": missing_files
    }

    info_path = os.path.join(backup_dir, "_backup_info.json")
    with open(info_path, 'w', encoding='utf-8') as f:
        json.dump(backup_info, f, indent=2, ensure_ascii=False)

    print("-" * 70)
    print()

    # Résumé
    print("=" * 70)
    print("📊 RÉSULTAT")
    print("=" * 70)
    print(f"✅ Fichiers sauvegardés: {len(copied_files)}/{len(FILES_TO_BACKUP)}")

    if missing_files:
        print(f"⚠️  Fichiers manquants: {len(missing_files)}")
        for f in missing_files:
            print(f"      - {f}")

    total_size = sum(f["size"] for f in copied_files)
    print(f"💾 Taille totale: {total_size:,} bytes ({total_size/1024:.1f} KB)")
    print(f"🕐 Date: {backup_info['date_creation']}")
    print()
    print(f"📁 Emplacement: {backup_dir}")
    print()
    print("🚀 Sauvegarde terminée avec succès!")
    print("=" * 70)

    return True

def restore_backup():
    """
    Restaure les fichiers depuis la sauvegarde.
    ATTENTION: Écrase les fichiers existants!
    """

    script_dir = get_script_directory()
    backup_dir = os.path.join(script_dir, BACKUP_FOLDER_NAME)

    print("=" * 70)
    print("🔄 RESTAURATION DES FICHIERS")
    print("=" * 70)

    if not os.path.exists(backup_dir):
        print("❌ ERREUR: Aucune sauvegarde trouvée!")
        print(f"   Dossier attendu: {backup_dir}")
        input("\nAppuie sur Entrée pour fermer...")
        return False

    # Lire les infos
    info_path = os.path.join(backup_dir, "_backup_info.json")
    if os.path.exists(info_path):
        with open(info_path, 'r', encoding='utf-8') as f:
            info = json.load(f)
        print(f"📅 Sauvegarde du: {info.get('date_creation', 'Inconnue')}")
        print(f"📊 {info.get('nombre_fichiers', 0)} fichiers disponibles")

    print()
    print("⚠️  ATTENTION: Cela va ÉCRASER tes fichiers actuels!")
    confirm = input("Es-tu sûr? (tape OUI pour continuer): ")

    if confirm != "OUI":
        print("❌ Restauration annulée.")
        return False

    print()
    print("📋 Restauration en cours:")
    print("-" * 70)

    restored = 0
    for filename in FILES_TO_BACKUP:
        backup_path = os.path.join(backup_dir, filename)
        dest_path = os.path.join(script_dir, filename)

        if os.path.exists(backup_path):
            try:
                shutil.copy2(backup_path, dest_path)
                print(f"   ✅ {filename}")
                restored += 1
            except Exception as e:
                print(f"   ❌ {filename} [ERREUR: {e}]")
        else:
            print(f"   ⚠️  {filename} [non trouvé dans backup]")

    print("-" * 70)
    print(f"\n✅ {restored} fichier(s) restauré(s)!")
    print("=" * 70)

    return True

# =============================================================================
# MENU PRINCIPAL
# =============================================================================

def main():
    """Menu principal du programme de sauvegarde"""

    while True:
        print("\n" + "=" * 70)
        print("🔧 ROG BRIDGE BACKUP TOOL v1.0")
        print("=" * 70)
        print("1. 📦 Créer une sauvegarde (remplace l'ancienne)")
        print("2. 🔄 Restaurer depuis la sauvegarde")
        print("3. ℹ️  Voir les informations de sauvegarde")
        print("4. ❌ Quitter")
        print("=" * 70)

        choice = input("\nChoix (1-4): ").strip()

        if choice == "1":
            create_backup()
            input("\nAppuie sur Entrée pour continuer...")

        elif choice == "2":
            restore_backup()
            input("\nAppuie sur Entrée pour continuer...")

        elif choice == "3":
            show_backup_info()
            input("\nAppuie sur Entrée pour continuer...")

        elif choice == "4":
            print("\n👋 Au revoir!")
            break
        else:
            print("❌ Choix invalide!")

def show_backup_info():
    """Affiche les informations de la sauvegarde existante"""

    script_dir = get_script_directory()
    backup_dir = os.path.join(script_dir, BACKUP_FOLDER_NAME)
    info_path = os.path.join(backup_dir, "_backup_info.json")

    print("\n" + "=" * 70)
    print("ℹ️  INFORMATIONS DE SAUVEGARDE")
    print("=" * 70)

    if not os.path.exists(backup_dir):
        print("❌ Aucune sauvegarde trouvée!")
        return

    if os.path.exists(info_path):
        with open(info_path, 'r', encoding='utf-8') as f:
            info = json.load(f)

        print(f"📅 Date de création: {info.get('date_creation', 'Inconnue')}")
        print(f"🔢 Version Dashboard: {info.get('version_dashboard', 'Inconnue')}")
        print(f"📊 Nombre de fichiers: {info.get('nombre_fichiers', 0)}")
        print()
        print("📁 Fichiers sauvegardés:")
        for f in info.get('fichiers', []):
            print(f"   • {f['name']} ({f['size']:,} bytes)")

        if info.get('fichiers_manquants'):
            print()
            print("⚠️  Fichiers manquants lors de la sauvegarde:")
            for f in info['fichiers_manquants']:
                print(f"   • {f}")
    else:
        print("ℹ️  Info: Sauvegarde existante mais sans métadonnées")
        files = os.listdir(backup_dir)
        print(f"📁 Fichiers trouvés: {len(files)}")
        for f in files:
            print(f"   • {f}")

# =============================================================================
# POINT D'ENTRÉE
# =============================================================================

if __name__ == "__main__":
    try:
        # Si argument en ligne de commande
        if len(sys.argv) > 1:
            if sys.argv[1] == "--backup" or sys.argv[1] == "-b":
                create_backup()
            elif sys.argv[1] == "--restore" or sys.argv[1] == "-r":
                restore_backup()
            elif sys.argv[1] == "--info" or sys.argv[1] == "-i":
                show_backup_info()
            else:
                print("Usage: python backup_rog_bridge.py [option]")
                print("Options:")
                print("  --backup, -b    Créer une sauvegarde")
                print("  --restore, -r   Restaurer depuis la sauvegarde")
                print("  --info, -i      Voir les informations")
                print("  (sans option)   Menu interactif")
        else:
            # Mode interactif
            main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrompu par l'utilisateur")
    except Exception as e:
        print(f"\n❌ ERREUR: {e}")
        input("\nAppuie sur Entrée pour fermer...")
