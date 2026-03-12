#!/usr/bin/env python3
"""
Script de validación de seguridad para Digital Twin Dashboard
Verifica que las claves API no estén expuestas en el código
"""

import os
import re
import sys
from pathlib import Path

def check_security():
    """Realiza auditoría de seguridad del proyecto"""
    
    project_root = Path(__file__).parent
    issues = []
    
    print("🔒 Iniciando auditoría de seguridad...\n")
    
    # Patrones de claves a buscar
    patterns = [
        (r'sk-proj-[a-zA-Z0-9_-]{40,}', 'OpenAI API Key'),
        (r'sk-[a-zA-Z0-9_-]{40,}', 'Potential API Key'),
        (r'OPENAI_API_KEY\s*=\s*["\'][^"\']+["\']', 'Hardcoded OpenAI Key'),
    ]
    
    # Archivos a ignorar
    ignore_dirs = {'.venv', '.git', '__pycache__', '.env.example', 'node_modules'}
    ignore_files = {'.env', '.env.local'}
    
    # 1. Buscar claves hardcodeadas
    print("1️⃣  Buscando claves hardcodeadas en archivos Python...")
    for py_file in project_root.rglob('*.py'):
        # Ignorar directorios específicos
        if any(ignore_dir in py_file.parts for ignore_dir in ignore_dirs):
            continue
        
        try:
            content = py_file.read_text()
            for pattern, description in patterns:
                if re.search(pattern, content):
                    issues.append(f"⚠️  {py_file}: Encontrado patrón {description}")
        except:
            pass
    
    # 2. Verificar que .env esté en .gitignore
    print("2️⃣  Verificando .gitignore...")
    gitignore_path = project_root / '.gitignore'
    if gitignore_path.exists():
        gitignore_content = gitignore_path.read_text()
        if '.env' not in gitignore_content:
            issues.append("⚠️  .gitignore: '.env' no está incluido en .gitignore")
        else:
            print("   ✅ .env está protegido en .gitignore")
    else:
        issues.append("⚠️  .gitignore: archivo no encontrado")
    
    # 3. Verificar que config.py es seguro
    print("3️⃣  Verificando config.py...")
    config_path = project_root / 'config.py'
    if config_path.exists():
        config_content = config_path.read_text()
        if 'load_dotenv' in config_content and 'os.getenv' in config_content:
            print("   ✅ config.py usa variables de entorno correctamente")
        else:
            issues.append("⚠️  config.py: No parece usar os.getenv()")
    
    # 4. Verificar que .env existe (pero no lo listamos)
    print("4️⃣  Verificando presencia de .env...")
    env_path = project_root / '.env'
    if env_path.exists():
        print("   ✅ Archivo .env existe (contenido NOT mostrado por seguridad)")
    else:
        print("   ⚠️  Archivo .env no encontrado")
    
    # 5. Verificar permisos de archivo
    print("5️⃣  Verificando permisos de archivo...")
    for file in ['.env', '.env.example']:
        filepath = project_root / file
        if filepath.exists():
            # En macOS/Linux
            if hasattr(os, 'stat'):
                mode = oct(os.stat(filepath).st_mode)[-3:]
                if file == '.env' and mode == '600':
                    print(f"   ✅ {file} tiene permisos restrictivos (600)")
                elif file == '.env':
                    print(f"   ⚠️  {file} podría tener permisos inseguros: {mode}")
    
    # Resultados
    print("\n" + "="*50)
    if not issues:
        print("✅ ¡EXCELENTE! No se encontraron problemas de seguridad")
        return 0
    else:
        print(f"⚠️  Se encontraron {len(issues)} punto(s) de atención:\n")
        for issue in issues:
            print(f"   {issue}")
        return 1

if __name__ == '__main__':
    sys.exit(check_security())
