Boa! Ótima pergunta.

Os dois sistemas são independentes e rodam de formas diferentes. Você precisará de um terminal (prompt de comando) para cada processo.

Aqui está como rodar cada um deles:

🏥 Como Rodar (Sistema de Farmácia - Binário/TCP)
Este sistema simula um cliente enviando novos medicamentos para um servidor, e o servidor respondendo com a lista completa do estoque.

Pré-requisito: Todos os 6 arquivos farmacia_*.py devem estar na mesma pasta.

Passo a passo (Cliente/Servidor):

Abra o Terminal 1 (Servidor):

Digite python farmacia_tcp_server.py e pressione Enter.

Você verá: Servidor da Farmácia ouvindo em 127.0.0.1:65432

Ele ficará "travado", esperando clientes.

Abra- um NOVO Terminal 2 (Cliente):

Digite python farmacia_tcp_client.py e pressione Enter.

O cliente vai rodar instantaneamente: ele se conecta, envia 2 itens ("Rivotril" e "Shampoo"), recebe 3 itens de volta (os 2 dele + a "Dipirona" do servidor) e depois se fecha.

No Terminal 2 (Cliente), você verá a lista completa.

No Terminal 1 (Servidor), você verá o log de que um cliente se conectou e os itens que ele recebeu. O servidor continuará rodando, pronto para outro cliente.

Como Rodar (Testes de Streams - Item 2 e 3):

Para testar apenas a escrita e leitura em arquivos (sem rede):

No terminal, digite: python farmacia_teste_streams.py

Isso criará um arquivo itens_farmacia.bin e depois o lerá, verificando se os dados bateram.

🗳️ Como Rodar (Sistema de Votação - JSON/TCP/UDP)
Este sistema é mais complexo e precisa de três terminais rodando ao mesmo tempo para ver tudo funcionando.

Pré-requisito: Todos os 3 arquivos voting_*.py devem estar na mesma pasta.

Passo a passo:

Abra o Terminal 1 (Servidor):

Digite python voting_server.py e pressione Enter.

Você verá: Servidor TCP (Votação) ouvindo em 0.0.0.0:50007

Ele ficará rodando, esperando conexões.

Abra o Terminal 2 (Votante):

Digite python voting_client.py e pressione Enter.

O cliente se conectará e pedirá um login.

Usuário: votante1

Senha: 123

Este cliente agora também está ouvindo as notas (Multicast) em segundo plano.

Abra o Terminal 3 (Admin):

Digite python voting_admin.py e pressione Enter.

O admin se conectará e pedirá um login.

Usuário: admin

Senha: admin123

Para Testar a "Magia" (Multicast):

Com os 3 terminais abertos e logados...

No Terminal 3 (Admin), escolha a opção 2. Enviar nota informativa.

Digite uma mensagem, como: Teste de nota para todos! e pressione Enter.

Instantaneamente, no Terminal 2 (Votante), a mensagem aparecerá, "interrompendo" o menu, provando que o Multicast (UDP) funcionou!

Pronto! É assim que você executa e demonstra os dois sistemas.