"""
Sistema seguro de gerenciamento de credenciais para APIs.
Implementa criptografia, validação e proteção contra vazamentos.
"""
import os
import json
import base64
from pathlib import Path
from typing import Dict, Optional, Any
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import getpass
import logging

logger = logging.getLogger(__name__)

class SecureCredentialManager:
    """Gerenciador seguro de credenciais com criptografia."""
    
    def __init__(self, credentials_file: str = "config/credentials.enc"):
        """
        Inicializa o gerenciador de credenciais.
        
        Args:
            credentials_file: Caminho para arquivo de credenciais criptografadas
        """
        self.credentials_file = Path(credentials_file)
        self.key_file = Path("config/.key")
        self._cipher = None
        self._ensure_config_dir()
    
    def _ensure_config_dir(self):
        """Garante que o diretório de configuração existe."""
        self.credentials_file.parent.mkdir(exist_ok=True)
    
    def _get_master_key(self) -> bytes:
        """Obtém ou cria a chave mestra para criptografia."""
        if self.key_file.exists():
            return self.key_file.read_bytes()
        
        # Gerar nova chave mestra
        password = getpass.getpass("Digite uma senha mestra para proteger as credenciais: ").encode()
        salt = os.urandom(16)
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password))
        
        # Salvar salt + key
        key_data = salt + base64.urlsafe_b64decode(key)
        self.key_file.write_bytes(key_data)
        
        # Proteger arquivo
        if os.name != 'nt':  # Unix/Linux
            os.chmod(self.key_file, 0o600)
        
        return key_data[16:]  # Retorna apenas a chave
    
    def _get_cipher(self) -> Fernet:
        """Obtém o objeto de criptografia."""
        if self._cipher is None:
            key_data = self._get_master_key()
            if len(key_data) > 32:
                # Arquivo contém salt + key
                salt = key_data[:16]
                key = key_data[16:]
            else:
                # Arquivo contém apenas key
                key = key_data
            
            # Se precisar regenerar a partir da senha
            if len(key) != 32:
                password = getpass.getpass("Digite a senha mestra: ").encode()
                salt = self.key_file.read_bytes()[:16]
                
                kdf = PBKDF2HMAC(
                    algorithm=hashes.SHA256(),
                    length=32,
                    salt=salt,
                    iterations=100000,
                )
                key = kdf.derive(password)
            
            encoded_key = base64.urlsafe_b64encode(key)
            self._cipher = Fernet(encoded_key)
        
        return self._cipher
    
    def save_credentials(self, credentials: Dict[str, str]) -> bool:
        """
        Salva credenciais de forma criptografada.
        
        Args:
            credentials: Dicionário com as credenciais
            
        Returns:
            True se salvou com sucesso
        """
        try:
            # Validar credenciais
            validated_creds = self._validate_credentials(credentials)
            
            # Criptografar
            cipher = self._get_cipher()
            encrypted_data = cipher.encrypt(json.dumps(validated_creds).encode())
            
            # Salvar
            self.credentials_file.write_bytes(encrypted_data)
            
            # Proteger arquivo
            if os.name != 'nt':  # Unix/Linux
                os.chmod(self.credentials_file, 0o600)
            
            logger.info("Credenciais salvas com segurança")
            return True
        
        except Exception as e:
            logger.error(f"Erro ao salvar credenciais: {e}")
            return False
    
    def load_credentials(self) -> Optional[Dict[str, str]]:
        """
        Carrega credenciais descriptografadas.
        
        Returns:
            Dicionário com credenciais ou None se erro
        """
        try:
            if not self.credentials_file.exists():
                return None
            
            # Descriptografar
            cipher = self._get_cipher()
            encrypted_data = self.credentials_file.read_bytes()
            decrypted_data = cipher.decrypt(encrypted_data)
            
            credentials = json.loads(decrypted_data.decode())
            return credentials
        
        except Exception as e:
            logger.error(f"Erro ao carregar credenciais: {e}")
            return None
    
    def _validate_credentials(self, credentials: Dict[str, str]) -> Dict[str, str]:
        """Valida formato das credenciais."""
        validated = {}
        
        # OpenWeatherMap
        if 'OPENWEATHER_API_KEY' in credentials:
            key = credentials['OPENWEATHER_API_KEY'].strip()
            if len(key) >= 32:  # Chaves OpenWeather têm ~32 caracteres
                validated['OPENWEATHER_API_KEY'] = key
            else:
                raise ValueError("Chave OpenWeatherMap inválida (muito curta)")
        
        # AirVisual
        if 'AIRVISUAL_API_KEY' in credentials:
            key = credentials['AIRVISUAL_API_KEY'].strip()
            if len(key) >= 20:  # Chaves AirVisual típicas
                validated['AIRVISUAL_API_KEY'] = key
            else:
                raise ValueError("Chave AirVisual inválida (muito curta)")
        
        # NASA (opcional)
        if 'NASA_API_KEY' in credentials:
            key = credentials['NASA_API_KEY'].strip()
            if key and key != 'DEMO_KEY':
                validated['NASA_API_KEY'] = key
        
        return validated
    
    def update_env_file(self):
        """Atualiza arquivo .env com credenciais carregadas."""
        credentials = self.load_credentials()
        if not credentials:
            logger.warning("Nenhuma credencial encontrada para atualizar .env")
            return False
        
        env_file = Path(".env")
        
        # Ler .env existente
        env_content = {}
        if env_file.exists():
            for line in env_file.read_text().splitlines():
                if '=' in line and not line.startswith('#'):
                    key, value = line.split('=', 1)
                    env_content[key.strip()] = value.strip()
        
        # Atualizar com credenciais
        env_content.update(credentials)
        
        # Salvar .env atualizado
        with open(env_file, 'w') as f:
            f.write("# Configuração de ambiente - Climate Analytics\n")
            f.write("# ⚠️  NUNCA commite este arquivo no Git!\n\n")
            
            for key, value in env_content.items():
                f.write(f"{key}={value}\n")
        
        logger.info("Arquivo .env atualizado com credenciais")
        return True

def setup_credentials_interactive():
    """Configuração interativa de credenciais."""
    print("🔐 CONFIGURAÇÃO SEGURA DE CREDENCIAIS")
    print("=" * 50)
    
    manager = SecureCredentialManager()
    credentials = {}
    
    # OpenWeatherMap
    print("\n🌤️  OPENWEATHERMAP")
    print("Site: https://openweathermap.org/api")
    openweather_key = input("Cole sua chave OpenWeatherMap: ").strip()
    if openweather_key:
        credentials['OPENWEATHER_API_KEY'] = openweather_key
    
    # AirVisual
    print("\n💨 AIRVISUAL")
    print("Site: https://www.iqair.com/air-pollution-data-api")
    airvisual_key = input("Cole sua chave AirVisual (Enter para pular): ").strip()
    if airvisual_key:
        credentials['AIRVISUAL_API_KEY'] = airvisual_key
    
    # NASA (opcional)
    print("\n🛰️  NASA (Opcional)")
    print("Site: https://api.nasa.gov/")
    nasa_key = input("Cole sua chave NASA (Enter para usar DEMO_KEY): ").strip()
    if nasa_key:
        credentials['NASA_API_KEY'] = nasa_key
    else:
        credentials['NASA_API_KEY'] = 'DEMO_KEY'
    
    # Salvar credenciais
    if credentials:
        print("\n🔐 Salvando credenciais de forma segura...")
        if manager.save_credentials(credentials):
            print("✅ Credenciais salvas com criptografia!")
            
            # Atualizar .env
            if manager.update_env_file():
                print("✅ Arquivo .env atualizado!")
            
            return True
        else:
            print("❌ Erro ao salvar credenciais")
            return False
    else:
        print("⚠️ Nenhuma credencial fornecida")
        return False

if __name__ == "__main__":
    setup_credentials_interactive()
