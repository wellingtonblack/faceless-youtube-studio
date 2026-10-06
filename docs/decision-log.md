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

**Pendente do owner:** confirmar os substitutos dos slots 6 e 8.

## 2026-10-03 — Correções da auditoria de onboarding e handoffs
**Autorização:** owner solicitou “Ok corrija então” após a auditoria.
**Decisão operacional:** manifest v3 inclui gates de storyboard/interface, aprovações
operacionais vinculadas a hashes e registro de assets com IDs por plano/take.
Fluxo unificado: assets → voz/timing → clips → edição → QC. Responsáveis, entradas,
saídas e critérios estão em `docs/file-001-handoff.md`. Publicação manual no Studio
mantém os mesmos gates humanos; `--confirm-public` aplica-se à execução por API.
**Ajustes de clareza:** scene-01 usa painéis simultâneos; scene-07 mantém a não
observadora olhando para baixo. Narração e canon D1–D6 preservados.
**Limite:** esta autorização corrige contratos/documentação; não aprova roteiro final,
storyboard, interface, QC nem publicação. Essas aprovações continuam pendentes.

## 2026-10-03 — Storyboard do FILE #001 aprovado
**Decisão:** aprovar o storyboard v1.1 de `production/storyboards/file-001-storyboard.md` para `Everyone Received the Same Message at 3:17 AM`.
**Motivo:** as nove cenas preservam a continuidade de 03:17 UTC, tornam a consequência de olhar para a Lua legível e mantêm a linguagem visual cinematográfica prevista para o canal.

**Próximo gate:** a interface fictícia de mensagens e seu tom sonoro ainda exigem aprovação antes da geração de assets.

## 2026-10-03 — Interface de mensagens do FILE #001 aprovada
**Decisão:** aprovar a direção da interface fictícia v1.1 em `docs/visual/anomaly-message-interface.md`, incluindo a tela preta, texto branco monoespaçado e cursor vermelho, para as cenas 02, 07 e 08.
**Motivo:** a composição é legível em vertical, reforça a identidade de arquivo/anomalia e evita elementos que possam ser confundidos com alertas de emergência, interfaces de sistemas operacionais ou avisos governamentais.

**Antes de assets:** concluir a verificação visual privada contra alertas reais e auditar o tom final para garantir que ele não se assemelhe a um sinal de atenção de emergência.

## 2026-10-03 — Validação técnica da interface do FILE #001
**Decisão:** aprovar tecnicamente a interface v1.2 para geração de assets e avançar o FILE #001 para `assets`.
**Motivo:** o layout não contém chrome de sistema operacional, cartões de notificação, botões, rótulos de alerta, símbolos de aviso, identificação governamental ou paleta de risco. O tom da segunda mensagem foi fixado em 82 Hz + 392 Hz, sem o par 853 Hz/960 Hz nem a cadência/vibração de sinais de atenção de emergência.

**Referências de validação:** documentação de alertas da Apple, Android e FCC, consultada em 2026-10-03. Nenhuma captura de tela de terceiros foi armazenada no repositório.

## 2026-10-03 — Keyframe de revelação da Lua aprovada
**Decisão:** aprovar `scene-06-moon-reveal-keyframe-v1` como âncora visual para as cenas conectadas do FILE #001.
**Motivo:** a Lua domina o enquadramento vertical, a figura humana permanece anônima e a composição sustenta o payoff sem texto, marcas ou interface indevida.

## 2026-10-03 — Continuidade da Lua normal aprovada
**Decisão:** aprovar `scene-04-normal-moon-keyframe-v1` como contraponto visual da revelação da cena 06.
**Motivo:** a cena mantém o mesmo ambiente e enquadramento-base, mas deixa a Lua em escala natural antes da escalada da anomalia.

## 2026-10-04 — Primeiro clip do FILE #001 aprovado
**Decisão:** aprovar `scene-06-moon-reveal-clip-v1` como o clip de revelação da Lua.
**Motivo:** o movimento lento preserva a composição aprovada, mantém a Lua como foco dominante e entrega a escalada sem texto, marcas ou elementos de alerta.

## 2026-10-05 — Integração do main local com o PR #1 (manifest v3)
**Contexto:** o `main` local (aprovações registradas em 2026-10-03/04) e o PR #1 (v3, aprovações vinculadas a hashes) divergiram. A integração está no branch `claude/integrate-v3`, para revisão do owner.
**Estado após a integração:**
- Os gates operacionais da v3 ficam todos `false`. Nenhum hash foi atribuído por agente.
- O roteiro e o storyboard aprovados localmente foram alterados depois (roteiro: só a linha de versão; storyboard: cenas 01 e 07). Pela regra da v3, precisam de nova aprovação.
- A interface v1.2 é byte a byte a versão aprovada pelo owner. A vinculação do hash fica pendente por causa da divergência CRLF/LF entre Windows e CI.
- O registro de assets recebeu os 3 assets aprovados (keyframes das cenas 04 e 06 e clip da cena 06). 9 arquivos gerados continuam sem registro por falta de procedência.

**Detalhes e checklist de reaprovação:** `docs/handoffs/2026-10-05-integration-v3.md`.

## 2026-10-05 — Reaprovações e voz do FILE #001
**Decisão do owner:**
- reaprovar o roteiro v1.1;
- reaprovar o storyboard v1.2, incluindo três painéis simultâneos na cena 01 e a personagem da cena 07 mantendo o olhar baixo;
- vincular novamente a interface de mensagens v1.2;
- reconfirmar os assets selecionados das cenas 04 e 06;
- aprovar a voz ElevenLabs `JBFqnCBsd6RMkjVDRZzb` como narrador neutro exclusivo deste piloto.

**Autorização de produção:** seguir para composição, legendas e controle de qualidade, entregando um candidato final para revisão humana. Esta decisão não autoriza upload ou publicação no YouTube.

**Rastreabilidade:** as três aprovações de artefatos estão vinculadas aos hashes normalizados no manifest v3. A voz é identificada pelo ID do provedor e pelo preset `neutral-storyteller-v1`; não representa o personagem The Archivist.

## 2026-10-05 — QC final do FILE #001
**Decisão do owner:** aprovar o corte final v5 de FILE #001 após o reforço do gancho inicial, legendas maiores, trilha original de suspense e encerramento reduzido.

**Master aprovado:** `output/file-001/final/file-001-short.mp4` (31 s, 1080×1920, 30 fps, áudio AAC estéreo). O relatório técnico associado é `output/file-001/final/qc-report.json`.

**Limite:** esta é uma aprovação de QC. Nenhum upload foi feito e `approvals.public_publish` continua `false`.
