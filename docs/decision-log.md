# Decision Log

Registro cronológico das decisões estratégicas do projeto.

## 2026-10-03 — Repositório oficial
**Decisão:** usar `wellingtonblack/faceless-youtube-studio` como fonte oficial da verdade do projeto.
**Motivo:** centralizar documentação, regras, histórico, prompts, personagens e aprendizados com versionamento.

## 2026-10-03 — Modelo faceless
**Decisão:** o canal será criado sem depender da imagem pessoal do fundador.
**Motivo:** aumentar escalabilidade, permitir operação internacional e transformar o projeto em ativo de mídia.

## 2026-10-03 — Estratégia editorial inicial
**Decisão:** iniciar com Shorts em inglês simples e testar três pilares: What If/ciência impossível, mistério/suspense e micro-histórias cinematográficas.
**Motivo:** maximizar potencial de descoberta, retenção e expansão global.

## 2026-10-03 — Estratégia de monetização
**Decisão:** usar Shorts para aquisição de audiência e desenvolver vídeos longos a partir dos temas vencedores.
**Motivo:** combinar alcance com uma estrutura de monetização mais robusta.

## 2026-10-03 — Uso de IA
**Decisão:** IA será ferramenta de produção, não substituta de originalidade.
**Motivo:** preservar diferenciação e reduzir risco de conteúdo repetitivo ou genérico.

## 2026-10-03 — Universo principal escolhido
**Decisão:** adotar `The Impossible Files` como conceito principal do canal.
**Premissa:** cada vídeo documenta algo que não deveria ser possível.
**Motivo:** unir mistério, ficção científica, suspense, What If e storytelling sob uma identidade reconhecível e escalável.

## 2026-10-03 — Lore inicial
**Decisão:** usar `03:17` como primeiro motivo recorrente e introduzir a organização `The Archive` apenas gradualmente.
**Motivo:** incentivar teorias e continuidade sem criar barreira para novos espectadores.

## 2026-10-03 — Personagem conector
**Decisão:** desenvolver `The Archivist` como personagem recorrente, inicialmente sem rosto revelado.
**Motivo:** criar uma presença proprietária que conecte arquivos e permita expansão para vídeos longos e temporadas.

## 2026-10-03 — Primeiro episódio
**Decisão:** FILE #001 será `Everyone Received the Same Message at 3:17 AM`.
**Motivo:** premissa global, facilmente compreensível, visualmente forte e adequada para introduzir o motivo 03:17.

## 2026-10-03 — Continuidade do FILE #001 (D1–D6)
**Decisão:** aprovadas as decisões D1–D6 de `docs/proposals/2026-10-03-file-001-continuity.md`:
- D1: 03:17 em evento global = 03:17 UTC, um único instante.
- D2: quem olha para a Lua recebe `WE SAW YOU TOO.`, sem explicação.
- D3: o sting final é `FILE #001 — ARCHIVED`; remetentes dentro do universo nunca citam a numeração `FILE #`.
- D4: The Archivist não aparece no FILE #001; a voz fica neutra.
- D5: FILE #006 e #008 sinalizados para reescrita/substituição, sem exclusão.
- D6: interface de mensagem fictícia própria; nunca imitar alertas de emergência reais.

**Motivo:** a revisão de continuidade encontrou um furo lógico de fuso horário, um payoff sem consequência para quem olha, um sting que revelava conhecimento do remetente sobre a numeração editorial, um personagem recorrente introduzido sem aprovação, excesso de arquivos sobre a Lua e risco de confusão com alertas reais.

## 2026-10-03 — Manifest de episódio v2 e gate de publicação
**Decisão:** schema de manifest v2 (`docs/migrations/2026-10-03-episode-manifest-v2.md`):
- `schema_version`;
- gates de aprovação humana explícitos (`approvals`), com quem aprovou, quando e onde está documentado;
- `approvals.public_publish` como fonte única de aprovação de publicação;
- metadados YouTube `selfDeclaredMadeForKids` e `containsSyntheticMedia`;
- contagem de cenas derivada do storyboard;
- registro de assets versionado em `episodes/<id>/assets.json`.

A publicação pública passa a exigir **ambos**: aprovação no manifest **e** a flag explícita `--confirm-public` na execução. `AUTO_PUBLISH` deixa de ser um mecanismo de publicação: qualquer valor diferente de `false`/vazio é erro de configuração.

**Motivo:** o v1 não conseguia registrar os gates exigidos pela arquitetura, tinha duas fontes de aprovação de publicação que podiam divergir, e uma variável de ambiente sozinha poderia, em tese, habilitar publicação pública.

## 2026-10-03 — Slots da temporada 1 e FILE #001 v1.0
**Decisão:**
- Slot 6 `The Moon Moved` substituído (sobreposição com o FILE #001).
- Slot 8 `Something Was Detected Behind the Moon` adiado para lore futura, fora dos 10 primeiros lançamentos; possível consequência do FILE #001.
- Substitutos provisórios (aguardando confirmação do owner): slot 6 `The Rain Fell Upward for One Minute`, slot 8 `The Entire World Forgot His Name`.
- FILE #001: aprovada a frase de abertura "At the same second, every phone on Earth received the same message."
- FILE #001: aprovado o beat `WE SAW YOU TOO.` com som de notificação distinto e inquietante.
- FILE #001: The Archivist continua ausente.
- Interface fictícia de mensagem em preto/branco/vermelho (spec em `docs/visual/anomaly-message-interface.md`, aguardando aprovação). A paleta geral da marca continua formalmente em exploração.

**Motivo:** diversificar os primeiros arquivos (excesso de Lua) e fechar o roteiro do FILE #001 para produção.

**Pendente do owner:** aprovar o roteiro final, o storyboard e a spec da interface; confirmar os substitutos dos slots 6 e 8.
