#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sauvegarde automatique RGPD pour Ollama WebUI
- Fonctionne entièrement en local
- Ne partage aucune donnée
- Compatible avec les exigences RGPD françaises
- Surveille le dossier de téléchargement pour les conversations Ollama
"""

import os
import time
import shutil
import re
import datetime
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class OllamaConversationHandler(FileSystemEventHandler):
    """Gestionnaire de sauvegarde RGPD pour conversations Ollama"""
    
    def __init__(self, source_dir, destination_dir="Txt-AI"):
        """Initialisation avec dossiers source et destination"""
        self.source_dir = Path(source_dir)
        self.destination_dir = Path(destination_dir)
        self.destination_dir.mkdir(parents=True, exist_ok=True)
        self.processed_files = set()
        print(f"🔒 Surveillance RGPD initialisée")
        print(f"📂 Dossier source: {self.source_dir}")
        print(f"📂 Dossier destination: {self.destination_dir}")
    
    def on_created(self, event):
        """Gère les nouveaux fichiers dans le dossier de téléchargement"""
        if event.is_directory:
            return
            
        file_path = Path(event.src_path)
        
        # Ignore les fichiers temporaires et déjà traités
        if file_path.name.startswith('.') or file_path in self.processed_files:
            return
            
        # Vérifier si c'est un fichier de conversation Ollama
        if self._is_ollama_conversation(file_path):
            self._process_conversation_file(file_path)
    
    def _is_ollama_conversation(self, file_path):
        """Vérifie si le fichier est une conversation Ollama"""
        if not file_path.suffix.lower() == '.txt':
            return False
            
        # Vérifier le nom ou le contenu du fichier
        if re.search(r'(chat-|GreenSEO|ollama|conversation)', file_path.name, re.IGNORECASE):
            return True
            
        # Vérifier le contenu si nécessaire
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read(500)  # Lire les premiers caractères
                if any(marker in content for marker in ['You:', 'Assistant:', 'User:', 'Vous:', 'GreenSEO']):
                    return True
        except:
            pass
            
        return False
    
    def _process_conversation_file(self, file_path):
        """Traite et sauvegarde une conversation au format souhaité"""
        try:
            # Marquer comme traité pour éviter les doublons
            self.processed_files.add(file_path)
            
            # Lire le contenu original
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Extraire un titre à partir du nom de fichier
            title_match = re.search(r'chat-(.*?)\.txt', file_path.name)
            if title_match:
                title = title_match.group(1).replace(' ', '_')
            else:
                title = file_path.stem.replace(' ', '_')
                
            # Formatter le nom de fichier
            now = datetime.datetime.now()
            date_str = now.strftime("%Y%m%d_%H%M")
            date_formatted = now.strftime("%d/%m/%Y %H:%M")
            new_filename = f"vie_privee_{date_str}_{title}.txt"
            
            # Formatter le contenu selon tes préférences
            formatted_content = self._format_content(content, date_formatted)
            
            # Créer le chemin de destination
            dest_path = self.destination_dir / new_filename
            
            # Écrire dans le nouveau fichier
            with open(dest_path, 'w', encoding='utf-8') as f:
                f.write(formatted_content)
                
            print(f"✅ Conversation sauvegardée: {new_filename}")
            
            # Option: supprimer le fichier original
            # os.remove(file_path)
            
        except Exception as e:
            print(f"❌ Erreur traitement fichier {file_path.name}: {str(e)}")
    
    def _format_content(self, content, date_formatted):
        """Formate le contenu d'une conversation"""
        # Analyse du contenu original pour le convertir au format souhaité
        formatted_content = f"🔐 SAUVEGARDE CONVERSATION\n"
        formatted_content += f"📅 DATE: {date_formatted}\n"
        formatted_content += f"==================================================\n"
        
        # Analyse ligne par ligne pour détecter les messages
        lines = content.split('\n')
        current_role = None
        current_content = []
        
        for line in lines:
            # Détecter les changements de locuteur
            user_markers = ['You:', 'User:', 'Vous:', 'Utilisateur:']
            assistant_markers = ['Assistant:', 'GreenSEO:', 'AI:']
            
            if any(marker in line for marker in user_markers):
                # Sauvegarder le message précédent s'il existe
                if current_role and current_content:
                    role_icon = "👤 VOUS" if current_role == "user" else "🤖 ASSISTANT"
                    formatted_content += f"{role_icon}:\n"
                    formatted_content += "\n".join(current_content).strip() + "\n"
                    formatted_content += "--------------------\n"
                    current_content = []
                
                # Commencer un nouveau message utilisateur
                current_role = "user"
                # Supprimer le marqueur du début de la ligne
                for marker in user_markers:
                    if marker in line:
                        line = line.replace(marker, '', 1).strip()
                        break
                        
                if line:  # Si la ligne n'est pas vide après suppression du marqueur
                    current_content.append(line)
                    
            elif any(marker in line for marker in assistant_markers):
                # Sauvegarder le message précédent s'il existe
                if current_role and current_content:
                    role_icon = "👤 VOUS" if current_role == "user" else "🤖 ASSISTANT"
                    formatted_content += f"{role_icon}:\n"
                    formatted_content += "\n".join(current_content).strip() + "\n"
                    formatted_content += "--------------------\n"
                    current_content = []
                
                # Commencer un nouveau message assistant
                current_role = "assistant"
                # Supprimer le marqueur du début de la ligne
                for marker in assistant_markers:
                    if marker in line:
                        line = line.replace(marker, '', 1).strip()
                        break
                        
                if line:  # Si la ligne n'est pas vide après suppression du marqueur
                    current_content.append(line)
            
            elif current_role:
                # Continuer le message en cours
                current_content.append(line)
                
        # Ajouter le dernier message s'il existe
        if current_role and current_content:
            role_icon = "👤 VOUS" if current_role == "user" else "🤖 ASSISTANT"
            formatted_content += f"{role_icon}:\n"
            formatted_content += "\n".join(current_content).strip() + "\n"
            formatted_content += "--------------------\n"
            
        formatted_content += f"🔒 FIN SAUVEGARDE\n"
        return formatted_content

def main():
    """Fonction principale de surveillance"""
    # Récupérer le chemin du dossier Téléchargements
    download_dir = Path.home() / "Downloads"
    if not download_dir.exists():
        download_dir = Path.home() / "Téléchargements"
    
    # Dossier de destination Txt-AI
    txt_ai_dir = Path.home() / "Local Sites" / "greenseo" / "app" / "public" / "wp-content" / "themes" / "geekmind-theme" / "Txt-AI"
    
    # Créer le gestionnaire et l'observateur
    event_handler = OllamaConversationHandler(download_dir, txt_ai_dir)
    observer = Observer()
    observer.schedule(event_handler, str(download_dir), recursive=False)
    
    # Démarrer la surveillance
    observer.start()
    
    print("🔐 Surveillance RGPD des conversations Ollama activée")
    print("👀 Utilise le bouton de téléchargement dans Ollama WebUI")
    print("📝 Les fichiers seront automatiquement convertis au format approprié")
    print("⌨️ Appuyez sur Ctrl+C pour arrêter")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        print("\n👋 Surveillance arrêtée")
    
    observer.join()

if __name__ == "__main__":
    main()
