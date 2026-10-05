# Faceless YouTube Studio

Repositório oficial do projeto de criação e operação do canal **The Impossible Files**, com foco em alcance global, viralização, consistência de marca e monetização sustentável.

## Objetivo
Construir um ativo digital de mídia que use Shorts para descoberta e vídeos longos para retenção, autoridade e monetização, priorizando conteúdo original, narrativo e visualmente forte.

## Fonte oficial da verdade
Este repositório é a referência principal para regras, decisões, personagens, prompts, processos, aprendizados e histórico do canal.

Conversas com ChatGPT, Claude ou Codex só passam a ser canônicas quando a decisão relevante é registrada aqui.

## Onboarding de agentes
Ao clonar o repositório:

- **Codex / coding agents:** ler `AGENTS.md` primeiro.
- **Claude / Claude Code:** ler `CLAUDE.md` primeiro.
- Todos devem ler `AGENTS.md`, `CLAUDE.md` e `MASTER_RULES.md`, depois os documentos e arquivos de episódio referenciados.
- Handoffs do FILE #001: `docs/file-001-handoff.md`; contrato atualizado: manifest v3.

## Arquitetura híbrida
O estúdio foi desenhado para funcionar com:

- ChatGPT: estratégia, criatividade, roteiros, visual e analytics;
- Claude/Claude Code: revisão de contexto longo, lore, documentação e implementação assistida;
- Codex: engenharia, CLI, APIs, FFmpeg, testes e automação;
- Runway (ou provider equivalente): geração de vídeo;
- ElevenLabs (ou provider equivalente): voz e áudio;
- FFmpeg: composição;
- YouTube Data API: upload privado e metadados;
- GitHub: memória e coordenação central.

Veja `docs/automation-architecture.md`.

## Estrutura
- `MASTER_RULES.md` — regras máximas do projeto
- `AGENTS.md` — instruções compartilhadas para Codex e outros agentes
- `CLAUDE.md` — instruções específicas para Claude/Claude Code
- `docs/` — estratégia, marca, visual, história, segurança, automação e decisões
- `characters/` — bíblias de personagens
- `content/` — backlog, ideias, séries e roteiros
- `episodes/` — manifests de estado de cada episódio
- `prompts/` — prompts aprovados
- `analytics/` — experimentos, vencedores e aprendizados
- `production/` — SOPs, storyboards e checklists
- `schemas/` — contratos de dados
- `pipeline/` — automação e integrações
- `output/` — mídia gerada localmente; não versionada por padrão

## Segurança
Nunca commitar chaves ou tokens. Use `.env` localmente com base em `.env.example`.

Uploads automáticos devem ser privados por padrão. Publicação pública exige aprovação humana explícita.

## Princípio de versionamento
Mudanças relevantes devem ser registradas via commits claros. Regras antigas não devem ser apagadas sem contexto: mudanças estratégicas devem ser registradas também em `docs/decision-log.md`.

## Status
Fase atual: estruturação do estúdio híbrido e produção do **FILE #001 — Everyone Received the Same Message at 3:17 AM**.
