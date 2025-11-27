import os
from pathlib import Path
from thefuzz import process, fuzz

class MusicFinder:
    def __init__(self, root_directory):
        """
        Inicializa o buscador com o diretório raiz onde as músicas estão.
        """
        self.root = Path(root_directory)
        if not self.root.exists():
            raise FileNotFoundError(f"O diretório '{root_directory}' não existe.")

    def _fuzzy_match(self, query, choices, threshold=70):
        """
        Método auxiliar para encontrar a melhor correspondência em uma lista.
        Retorna (melhor_match, score) ou None se não atingir o limiar.
        """
        if not choices:
            return None
        
        # token_set_ratio é ótimo para ignorar palavras extras (ex: "The", "Deluxe Edition")
        # e ignorar a ordem das palavras.
        best_match, score = process.extractOne(query, choices, scorer=fuzz.token_set_ratio)
        
        if score >= threshold:
            return best_match
        return None

    def find_music(self, artist_query, album_query=None, track_query=None):
        """
        Busca músicas baseada na hierarquia Artista -> Album -> Faixa.
        Retorna uma lista de caminhos absolutos (Path objects).
        """
        found_files = []

        # --- 1. Encontrar o Artista ---
        # Lista apenas diretórios na raiz
        artists = [d.name for d in self.root.iterdir() if d.is_dir()]
        best_artist = self._fuzzy_match(artist_query, artists)

        if not best_artist:
            print(f"❌ Artista '{artist_query}' não encontrado (ou similaridade muito baixa).")
            return []
        
        artist_path = self.root / best_artist
        print(f"✅ Artista encontrado: {best_artist}")

        # --- 2. Encontrar o(s) Álbum(ns) ---
        target_albums_paths = []
        available_albums = [d.name for d in artist_path.iterdir() if d.is_dir()]

        if album_query:
            # Se o usuário pediu um álbum específico, tentamos achar
            best_album = self._fuzzy_match(album_query, available_albums)
            if best_album:
                print(f"✅ Álbum encontrado: {best_album}")
                target_albums_paths.append(artist_path / best_album)
            else:
                print(f"⚠️ Álbum '{album_query}' não encontrado. Buscando em todos os álbuns do artista...")
                # Fallback: Se não achar o álbum, procura a música em todos os álbuns do artista
                target_albums_paths = [artist_path / alg for alg in available_albums]
        else:
            # Se não especificou álbum, pega todos
            target_albums_paths = [artist_path / alg for alg in available_albums]

        # --- 3. Encontrar a(s) Faixa(s) ---
        for album_path in target_albums_paths:
            # Lista arquivos de áudio (filtros básicos)
            audio_files = [
                f.name for f in album_path.iterdir() 
                if f.is_file() and f.suffix.lower() in ['.mp3', '.flac', '.wav', '.m4a']
            ]

            if track_query:
                # Se pediu uma faixa específica, busca a melhor correspondência dentro deste álbum
                best_track = self._fuzzy_match(track_query, audio_files, threshold=60) # Limiar menor para faixas
                if best_track:
                    found_files.append(str(album_path / best_track))
            else:
                # Se não pediu faixa (só artista ou artista+album), adiciona TODAS as faixas
                for track in audio_files:
                    found_files.append(str(album_path / track))

        return found_files

# --- Exemplo de Uso ---
if __name__ == "__main__":
    # 1. DEFINA O CAMINHO DA SUA PASTA DE MÚSICAS AQUI
    # Exemplo Windows: r"C:\Users\SeuNome\Music"
    # Exemplo Linux/Mac: "/home/seunome/Music"
    CAMINHO_MUSICAS = r"F:\\Midioteca\\Musica" 


    finder = MusicFinder(CAMINHO_MUSICAS)

    print("--- Teste 1: Busca exata de faixa ---")
    playlist = finder.find_music("Pink Floid", "Dark Side", "Time") # Note os erros de digitação propositais
    print("Arquivos para tocar:", playlist)
    
    print("\n--- Teste 2: Apenas Artista e Album (Tocar álbum todo) ---")
    playlist = finder.find_music("Miles Davis", "Kind of Blue")
    print("Arquivos para tocar:", playlist)

    print("\n--- Teste 3: Apenas Artista (Discografia completa) ---")
    playlist = finder.find_music("Pink Floyd")
    print(f"Total encontradas: {len(playlist)}")