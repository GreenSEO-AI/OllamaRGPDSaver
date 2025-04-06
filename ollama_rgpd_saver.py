#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sauvegarde manuelle RGPD pour Ollama WebUI
- Fonctionne entièrement en local
- Ne partage aucune donnée
- Compatible avec les exigences RGPD françaises
"""

import os
import re
import datetime
import shutil
from pathlib import Path

class OllamaManualSaver:
    """Conversion manuelle des fichiers de conversation Ollama"""
    
    def __init__(self, destination_dir="C:\\Modelfile\\TXT-SEO"):
        """Initialisation avec dossier destination"""
        self.destination_dir = Path(destination_dir)
        self.destination_dir.mkdir(parents=True, exist_ok=True)
        print(f"🔒 Sauvegarde RGPD initialisée")
        print(f"📂 Dossier destination: {self.destination_dir}")
    
    def process_conversation_file(self, file_path):
        """Traite et sauvegarde une conversation au format souhaité"""
        try:
            file_path = Path(file_path)
            
            if not file_path.exists():
                print(f"❌ Fichier non trouvé: {file_path}")
                return False
                
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
            
            # Formatter le contenu selon les marqueurs spécifiques
            formatted_content = self._format_content(content, date_formatted)
            
            # Créer le chemin de destination
            dest_path = self.destination_dir / new_filename
            
            # Écrire dans le nouveau fichier
            with open(dest_path, 'w', encoding='utf-8') as f:
                f.write(formatted_content)
                
            print(f"✅ Conversation sauvegardée: {dest_path}")
            return True
            
        except Exception as e:
            print(f"❌ Erreur traitement fichier: {str(e)}")
            return False
    
    def _format_content(self, content, date_formatted):
        """Formate le contenu selon les marqueurs spécifiques"""
        formatted_content = f"🔐 SAUVEGARDE CONVERSATION\n"
        formatted_content += f"📅 DATE: {date_formatted}\n"
        formatted_content += f"==================================================\n"
        
        # Format spécifique avec "### USER" et "### ASSISTANT"
        parts = content.split("### ")
        
        for part in parts:
            if not part.strip():
                continue
            
            if part.startswith("USER"):
                lines = part[4:].strip().split('\n')
                formatted_content += f"👤 VOUS:\n"
                formatted_content += "\n".join(lines).strip() + "\n"
                formatted_content += "--------------------\n"
            
            elif part.startswith("ASSISTANT"):
                lines = part[9:].strip().split('\n')
                formatted_content += f"🤖 ASSISTANT:\n"
                formatted_content += "\n".join(lines).strip() + "\n"
                formatted_content += "--------------------\n"
        
        formatted_content += f"🔒 FIN SAUVEGARDE\n"
        return formatted_content

def main():
    """Fonction principale - sauvegarde manuelle"""
    # Dossier de destination
    txt_seo_dir = "C:\\Modelfile\\TXT-SEO"
    
    # Créer le convertisseur
    saver = OllamaManualSaver(txt_seo_dir)
    
    print("\n💬 Convertisseur de conversations GreenSEO-AI")
    print("🔒 Format compatible RGPD pour utilisation professionnelle")
    
    # Demander le chemin du fichier
    download_dir = Path.home() / "Downloads"
    print(f"\n📂 Dossier de téléchargements par défaut: {download_dir}")
    
    # Montrer les fichiers disponibles
    print("\nFichiers TXT disponibles dans téléchargements:")
    txt_files = list(download_dir.glob("*.txt"))
    
    if not txt_files:
        print("  Aucun fichier TXT trouvé dans téléchargements")
    else:
        for i, file in enumerate(txt_files):
            print(f"  {i+1}. {file.name}")
    
    # Demander le fichier à convertir
    file_input = input("\n📝 Chemin complet du fichier à convertir (ou numéro de la liste ci-dessus): ")
    
    # Traiter l'entrée
    file_to_process = None
    
    if file_input.isdigit():
        # L'utilisateur a entré un numéro de la liste
        index = int(file_input) - 1
        if 0 <= index < len(txt_files):
            file_to_process = txt_files[index]
        else:
            print("❌ Numéro de fichier invalide")
    else:
        # L'utilisateur a entré un chemin complet
        file_to_process = Path(file_input)
    
    # Traiter le fichier
    if file_to_process:
        success = saver.process_conversation_file(file_to_process)
        
        if success:
            print("\n✨ Conversion réussie!")
            print(f"📂 Le fichier converti se trouve dans: {txt_seo_dir}")
            print("🚀 Prêt pour ta présentation à l'incubateur!")
    else:
        print("❌ Aucun fichier à traiter")

if __name__ == "__main__":
    main()
