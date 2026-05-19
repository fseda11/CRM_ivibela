# ⚡ ivibe CRM — ATD 2026

App Streamlit com os 98 leads do evento ATD 2026, priorização por score e geração de emails personalizados com IA.

---

## Como rodar localmente

### 1. Instalar dependências
```bash
pip install -r requirements.txt
```

### 2. Rodar o app
```bash
streamlit run app.py
```

O app abre automaticamente em `http://localhost:8501`

---

## Como usar

1. **API Key**: cole sua chave Anthropic (`sk-ant-...`) na barra lateral
2. **Filtre** os leads por prioridade (HOT / Morno / Frio), país ou busca livre
3. **Clique em um lead** para expandir o perfil completo
4. **Gere o email** — o Claude lê o perfil e escreve um email personalizado
5. **Copie ou baixe** o email gerado

---

## Deploy grátis no Streamlit Cloud

1. Faça push deste repositório para o GitHub
2. Acesse [share.streamlit.io](https://share.streamlit.io)
3. Conecte o repositório e selecione `app.py`
4. Na aba **Secrets**, adicione:
   ```toml
   ANTHROPIC_API_KEY = "sk-ant-..."
   ```
5. Clique em **Deploy** — em ~2 minutos o app estará no ar com uma URL pública

---

## Estrutura dos arquivos

```
crm_ivibe/
├── app.py            ← app principal
├── leads_data.json   ← dados dos 98 leads enriquecidos
├── requirements.txt  ← dependências Python
└── README.md         ← este arquivo
```

---

## Score de prioridade

| Score | Classificação | Ação |
|-------|--------------|------|
| 7-10  | 🔥 HOT       | Abordar hoje |
| 4-6   | ⚡ Morno     | Esta semana |
| 0-3   | ❄️ Frio      | Nutrir com conteúdo |

**Critérios de pontuação:**
- Marcado como "Hot" na conversa: +4
- Pediu reunião ou follow-up: +3
- Interesse em ivibe: +3
- Quer parceria: +3
- Buscando LMS: +3
- Cargo sênior (CEO, Director, VP, Head): +3
- Manager / Gerente: +2
- Perfil LinkedIn rico: +1
- Empresa de destaque: +1
