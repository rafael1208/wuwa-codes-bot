# Robô de códigos do Wuthering Waves no Discord

Verifica a cada 30 minutos os códigos ativos (fonte: prydwen.gg) e posta no seu canal
apenas os que ainda não foram enviados. Na primeira execução, publica os ativos atuais
(ex.: WUTHERINGGIFT); depois, só os novos.

## Fase 1 — Webhook no Discord
1. No canal `#codigos-wuwa`: **Editar canal → Integrações → Webhooks → Novo webhook**.
2. Dê o nome "Códigos WuWa" e clique em **Copiar URL do webhook**.
3. Guarde essa URL só para você — quem tiver ela pode postar no canal.

(Opcional) Para mencionar um cargo: ative o **Modo Desenvolvedor** em Configurações → Avançado,
clique com o botão direito no cargo e em **Copiar ID do cargo**.

## Fase 2 — Repositório no GitHub
1. Crie uma conta em github.com (se não tiver) e um repositório novo, por exemplo `wuwa-codes-bot`.
2. Envie os arquivos desta pasta mantendo a estrutura:
   ```
   wuwa_codes.py
   requirements.txt
   sent_codes.json
   .github/workflows/wuwa-codes.yml
   ```
   Pelo site: **Add file → Upload files** e arraste tudo (inclusive a pasta `.github`).

## Fase 3 — Segredos
No repositório: **Settings → Secrets and variables → Actions → New repository secret**.
- `DISCORD_WEBHOOK_URL` = a URL copiada na Fase 1
- `DISCORD_ROLE_ID` = o ID do cargo (opcional)

## Fase 4 — Primeiro teste
1. Aba **Actions** → "Códigos WuWa no Discord" → **Run workflow**.
2. Em alguns segundos o WUTHERINGGIFT deve aparecer no canal.
3. Rode de novo: nada deve ser postado (já foi enviado).

## Fase 5 — Funcionamento contínuo
- Roda sozinho a cada 30 minutos. Códigos de live costumam durar ~2 dias, então chegam a tempo.
- Se a página mudar de formato e nenhum código for encontrado, a execução falha e o GitHub
  te avisa por e-mail.
- O GitHub pausa agendamentos em repositórios sem atividade por 60 dias. Se receber esse
  aviso por e-mail, basta clicar para reativar.
- Para reenviar um código, apague-o de `sent_codes.json`.
