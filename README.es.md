[Português (Brasil)](README.md) · [English](README.en.md) · **Español**

<picture>
  <source media="(prefers-reduced-motion: reduce)" srcset="docs/assets/readme/hero-still.svg">
  <img src="docs/assets/readme/hero.svg" alt="FastWhisper Web Studio Banner" width="1600" height="680">
</picture>

# FastWhisper Web Studio

**Uma estação de trabalho local, visual e ultrarrápida para transformar áudio e documentos em inteligência textual formatada.**

Transcreva vídeos da Web (YouTube, podcasts, redes sociais), arquivos locais e microfone com motor **faster-whisper (CTranslate2)** até 8x mais rápido que o OpenAI Whisper padrão, exportando em **.docx**, **.md** e **.txt**, com narração neural de PDFs em pt-BR.

<p align="center"><a href="#start"><strong>COMEÇAR AGORA →</strong></a> &nbsp; · &nbsp; <a href="#performance"><strong>PERFORMANCE</strong></a> &nbsp; · &nbsp; <a href="#architecture"><strong>ARQUITETURA</strong></a> &nbsp; · &nbsp; <a href="#quality"><strong>TESTES (18 PASSANDO)</strong></a> &nbsp; · &nbsp; <a href="#structure"><strong>ESTRUTURA</strong></a></p>

---

<a id="start"></a>
## 00 / Escolha onde começar

| Seu objetivo | Caminho rápido | O que você obtém |
|---|---|---|
| **Iniciar em 1 Clique (Windows)** | Execute `iniciar.bat` | Cria o ambiente venv automaticamente, instala dependências e abre o navegador. |
| **Executar via Linha de Comando** | `python app.py` | Inicia o servidor Gradio local em `http://127.0.0.1:7860`. |
| **Rodar Testes Automatizados** | `pytest tests/ -v` | Executa os 18 testes unitários e de integração comprovando a estabilidade da aplicação. |
| **Transcrever Vídeo da Web** | Aba "Link da Web" | Cole a URL de YouTube, Twitter/X ou podcast e gere o Word/Markdown direto. |
| **Narrar PDF com Voz Humana** | Aba "Leitor de PDF" | Converte documentos acadêmicos em áudio MP3 cristalino com Edge-TTS pt-BR. |

---

<a id="setup"></a>
## 01 / Prepare e execute a base

### Pré-requisitos
- Python 3.10 ou superior
- FFmpeg instalado no sistema (necessário para manipulação de áudio)

### Inicialização Rápida

```bash
# 1. Clone o repositório
git clone https://github.com/EmmanuelNunes/fastwhisper-web-studio.git
cd fastwhisper-web-studio

# 2. Crie e ative o ambiente virtual
python -m venv venv
# No Windows:
.\venv\Scripts\activate
# No Linux/macOS:
source venv/bin/activate

# 3. Instale as dependências
pip install -r requirements.txt

# 4. Inicie o estúdio
python app.py
```

---

<a id="performance"></a>
## 02 / Arquitetura e fluxo de processamento

<picture>
  <source media="(prefers-reduced-motion: reduce)" srcset="docs/assets/readme/architecture-still.svg">
  <img src="docs/assets/readme/architecture.svg" alt="Arquitetura do FastWhisper Web Studio" width="1600" height="520">
</picture>

### Comparativo de Performance

| Funcionalidade / Métrica | OpenAI Whisper Padrão | FastWhisper Web Studio |
|---|:---:|:---:|
| **Motor de Inferência** | PyTorch puro (Python) | **CTranslate2 (C++ Otimizado)** |
| **Velocidade de Processamento** | 1x (Base de referência) | **4x a 8x mais rápido** ⚡ |
| **Consumo de Memória (VRAM / RAM)** | Alto (estouro frequente) | **Redução de até 70%** (quantização int8/float16) |
| **Filtro de Silêncio / Ruído** | Inexistente (alucina em pausas) | **Silero VAD Integrado** (ignora silêncio) |
| **Extração de Vídeos / Redes** | Requer scripts externos | **Nativo via yt-dlp (YouTube, Podcasts, X)** |
| **Entrada ao Vivo** | Não suportada nativamente | **Gravação direta de microfone no navegador** |
| **Leitura de PDF com IA** | Não suportada | **Vozes Neurais Humanas (Edge-TTS pt-BR)** |
| **Formatos de Saída** | .txt bruto | **.docx estilizado + .md + .txt com timestamps** |

---

<a id="features"></a>
## 03 / Recursos, capacidades e uso prático

1. **Transcrição de Mídias Locais e Gravação ao Vivo:** Suporte completo a `.mp3`, `.wav`, `.m4a`, `.mp4`, `.mkv`, `.ogg`, `.flac`, `.aac` e `.webm`.
2. **Seleção Flexível de Modelos:** Escolha de `tiny` a `large-v3`, equilibrando velocidade e acurácia.
3. **Download Rápido de Áudio:** O `yt-dlp` faz download exclusivamente da faixa sonora, economizando banda e tempo.
4. **Exportação Profissional:** Gera arquivos Microsoft Word estilizados com capa e metadados, além de Markdown pronto para documentação.

---

<a id="quality"></a>
## 04 / Qualidade, testes e verificação

A estabilidade do FastWhisper Web Studio é garantida por uma suíte completa de **18 testes automatizados** em Pytest cobrindo:
- Sanitização de caminhos de arquivos e segurança de uploads
- Extração de áudio via yt-dlp e tratamento de erros de rede
- Formatação de timestamps e diarização de segmentos
- Geração correta de documentos .docx, .md e .txt

```bash
# Executar a suíte de testes
pytest tests/ -v --tb=short
```

---

<a id="structure"></a>
## 05 / Estrutura do repositório

```text
fastwhisper-web-studio/
├── assets/
│   └── banner.svg
├── docs/
│   └── assets/
│       └── readme/
│           ├── hero.svg + hero-still.svg
│           └── architecture.svg + architecture-still.svg
├── tests/                   # 18 testes automatizados com Pytest
│   ├── test_transcriber.py
│   ├── test_exporter.py
│   └── test_tts.py
├── app.py                   # Ponto de entrada do Gradio Web Studio
├── requirements.txt         # Dependências canônicas do projeto
├── iniciar.bat              # Inicializador em 1 clique para Windows
├── AGENTS.md                # Instruções e contratos para agentes de IA
├── CLAUDE.md                # Ponte para Claude Code (@AGENTS.md)
├── README.md                # Documentação em Português (Brasil)
├── README.en.md             # Documentação em Inglês
└── README.es.md             # Documentação em Espanhol
```

---

<a id="credits"></a>
## 06 / Créditos, pesquisa e licença

Desenvolvido por **Emmanuel Nunes** como parte do ecossistema de ferramentas inteligentes e agênticas.
Conectado ao [EmmanuelNunes/vibe-coding-toolkit](https://github.com/EmmanuelNunes/vibe-coding-toolkit).

Licenciado sob a Licença MIT. Consulte [LICENSE](LICENSE) para mais detalhes.

<p align="center">
  <br>
  <strong>BUILD WITH INTENT. SHIP WITH FLOW.</strong>
  <br><br>
  <a href="#fastwhisper-web-studio">Voltar ao topo ↑</a>
</p>
