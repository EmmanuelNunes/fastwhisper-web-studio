# 🎙️ FastWhisper Web Studio

Aplicativo local de alta performance para transcrição automática de áudio a partir de múltiplas fontes (URLs de vídeos/sites, arquivos locais e microfone ao vivo) com exportação estruturada em **.docx (Microsoft Word)**, **.md (Markdown)** e **.txt (Texto puro)**.

Desenvolvido com base no motor **`faster-whisper` (CTranslate2)**, que é até **4x a 8x mais rápido** que o repositório original `openai/whisper`, com quantização `int8` (CPU) e `float16` (GPU CUDA), e filtragem inteligente de silêncios via **Silero VAD**.

---

## 🚀 Como Iniciar em 1 Clique (Windows)

Basta dar dois cliques no arquivo:
```cmd
iniciar.bat
```
O script cuidará de:
1. Criar o ambiente virtual (`.venv`) automaticamente caso não exista.
2. Instalar todas as bibliotecas necessárias.
3. Iniciar o servidor local e abrir seu navegador em `http://127.0.0.1:7860`.

---

## 🛠️ Inicialização Manual via Terminal

Caso prefira rodar via PowerShell ou Prompt de Comando:

```bash
# 1. Acesse a pasta do projeto
cd transcritor-whisper

# 2. Ative o ambiente virtual
.\.venv\Scripts\activate

# 3. Inicie o aplicativo
python app.py
```
Em seguida, abra o navegador no endereço: **http://127.0.0.1:7860**

---

## 🌟 Principais Recursos

1. 🌐 **Extração Direta de Sites e Redes Sociais:**
   - Cole o link de vídeos do YouTube, podcasts, Twitter/X, SoundCloud, Instagram, etc.
   - O áudio é baixado diretamente em alta velocidade via `yt-dlp` sem precisar baixar o arquivo de vídeo completo.

2. 📁 **Upload e Suporte Universal de Arquivos:**
   - Suporte a `.mp3`, `.wav`, `.m4a`, `.mp4`, `.mkv`, `.ogg`, `.flac`, `.aac`, `.webm`, etc.

3. 🎙️ **Gravação ao Vivo:**
   - Grave áudio do microfone ou de conferências diretamente pelo navegador.

4. ⚡ **Velocidade Extrema com `faster-whisper`:**
   - Utiliza CTranslate2 com quantização int8 no processador (CPU) ou float16 na placa de vídeo (GPU NVIDIA).
   - Suporte ao modelo **`large-v3-turbo`** (qualidade máxima com velocidade ultra-rápida).
   - Silero VAD para ignorar silêncios e ruídos de fundo automaticamente.

5. 📑 **Leitura e Narração de PDF em pt-BR (IA):**
   - Extrai o texto de documentos `.pdf` página por página mantendo a estrutura de parágrafos.
   - Narra em voz alta natural com vozes neurais brasileiras de alta qualidade (Francisca, Antonio, Thalita).
   - Permite ouvir e baixar o áudio gerado (`.mp3`) além de exportar o texto formatado para `.docx`, `.md` e `.txt`.

6. 📥 **Exportação Imediata Multi-Formato:**
   - **📄 Word (.docx):** Documento formatado com cabeçalho corporativo, tabela de metadados (data, duração, idioma detectado com probabilidade e modelo), marcas de tempo e parágrafos estruturados.
   - **📝 Markdown (.md):** Estrutura limpa com metadados em frontmatter YAML.
   - **📃 Texto (.txt):** Texto corrido pronto para leitura ou ingestão em LLMs.

---

## 📂 Estrutura de Arquivos

```
transcritor-whisper/
├── app.py                  # Interface Web Gradio
├── iniciar.bat             # Launcher em 1 clique para Windows
├── requirements.txt        # Dependências do projeto
├── README.md               # Documentação de uso
├── core/
│   ├── transcriber.py      # Motor de IA faster-whisper + Silero VAD
│   ├── downloader.py       # Extração de URLs via yt-dlp
│   ├── exporter.py         # Exportação em .docx, .md e .txt
│   └── utils.py            # Utilitários de tempo e detecção de hardware
├── tests/                  # Testes automatizados (pytest)
├── outputs/                # Destino dos arquivos transcritos (.docx, .md, .txt)
└── temp_audio/             # Áudios temporários baixados de links
```

---

## 🧪 Executando os Testes

Para rodar a suíte de testes unitários:
```bash
.\.venv\Scripts\python -m pytest tests/
```
