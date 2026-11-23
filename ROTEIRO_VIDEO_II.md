# 🎬 Roteiro do vídeo — Desk App II (máx. 6:00, YouTube)

**Objetivo do nível:** mostrar, rodando na minha máquina, o funcionamento parcial do projeto com um **menu totalmente funcional**, que dá acesso a **todos os modelos e funcionalidades**. Ainda **não há banco de dados**: os dados ficam em memória.

**Antes de gravar:** abra o terminal na pasta do projeto, rode `python3 app.py` e deixe a janela maximizada. Os dados de exemplo (L1, L2, R1, D1, A001, P001) já carregam ao abrir.

| Tempo | O que mostrar | O que falar |
|---|---|---|
| **0:00 – 0:25** | Terminal com `python3 app.py` → janela abre | "Olá, eu sou o Vinicius. Este é o Sistema de Biblioteca, agora na etapa Desk App II. Vou mostrar ele rodando na minha máquina, com o menu completo dando acesso a todos os modelos e funcionalidades. Nesta etapa os dados ainda ficam só em memória — o banco de dados entra na próxima." |
| **0:25 – 0:50** | Passar o mouse por cada menu da barra: Arquivo, Cadastros, Movimentação, Consultas, Relatórios, Exibir, Ajuda. Apontar a barra de status embaixo | "A barra de menu tem sete grupos. Cada modelo do sistema — Livro, Revista, DVD, Aluno, Professor, Carteirinha, Empréstimo e os Exportadores — tem acesso por aqui. Embaixo, a barra de status mostra os totais e lembra que os dados estão em memória." |
| **0:50 – 1:35** | **Cadastros ▸ Acervo ▸ Novo Livro** (L3, "O Cortiço", 1890, Aluísio Azevedo) → Cadastrar. Depois **Nova Revista** (R2, "Galileu", 2025, 380) e **Novo DVD** (D2, "Central do Brasil", 1998, 110) | "Começo pelos cadastros. Novo livro: código, título, ano e autor. Nova revista: no lugar do autor vem a edição. Novo DVD: a duração. Cada tipo tem seu próprio campo, isso é o polimorfismo aparecendo na tela." |
| **1:35 – 1:50** | Tentar **Novo Livro** com código L1 → erro; corrigir para L4 e cadastrar | "Se eu repito um código, o sistema avisa e a janela continua aberta para eu corrigir." |
| **1:50 – 2:20** | **Cadastros ▸ Membros ▸ Novo Aluno** (Bruno Alves, 111.222.333-44, A002, ADS) e **Novo Professor** (Maria Silva, 555.666.777-88, P002, Matemática). Mostrar a aba Membros com as carteirinhas | "Agora os membros: um aluno e uma professora. A carteirinha é criada automaticamente junto com o membro — é a composição — com validade de um ano." |
| **2:20 – 2:50** | **Cadastros ▸ Acervo ▸ Editar item** → trocar o combo para R1 (campo vira "Edição") e depois D1 (vira "Duração"); alterar o título de R1 → Salvar. Depois **Editar membro** P001 → trocar o departamento | "Também dá para editar. Ao trocar o item, o formulário muda o campo extra sozinho, de acordo com o tipo. O código e a matrícula não mudam. O mesmo para membros." |
| **2:50 – 3:05** | **Cadastros ▸ Membros ▸ Renovar carteirinha** → A001, data vazia → Renovar | "Aqui renovo a carteirinha: é a mesma carteirinha, só ganha validade nova." |
| **3:05 – 3:45** | **Movimentação ▸ Emprestar item** (`Ctrl+E`): D1 + A001, data 01/11/2026 → Emprestar. **Emprestar** de novo: mostrar que D1 não aparece mais na lista. **Devolver item** (`Ctrl+D`): D1, data 06/11/2026 → Devolver | "No menu Movimentação eu empresto o DVD para a Ana em primeiro de novembro. Repare que ele some da lista de itens disponíveis. Devolvendo dia seis, são dois dias de atraso a dois reais: multa de quatro reais." |
| **3:45 – 4:00** | **Emprestar**: L1, L2 e L3 para A001 (hoje) e tentar um quarto (R1) → erro de limite | "O aluno tem limite de três empréstimos; no quarto, o sistema bloqueia." |
| **4:00 – 4:45** | **Consultas**: Acervo completo → Itens disponíveis → Itens emprestados → **Pesquisar** "machado" (`Ctrl+F`) → Membros → Carteirinhas → Empréstimos ativos → Atrasados → Histórico → **Empréstimos de um membro** (A001) | "O menu Consultas abre cada listagem numa janela: acervo, disponíveis, emprestados, pesquisa, membros, carteirinhas com validade, empréstimos ativos, atrasados, o histórico completo e o histórico de um membro com as multas." |
| **4:45 – 5:15** | **Relatórios ▸ Relatório em Texto** (`Ctrl+R`), depois **em CSV**, **Salvar relatório** (salvar em `relatorio.csv`) e **Resumo geral** | "Em Relatórios gero em texto ou CSV — o mesmo comando com exportadores diferentes — salvo em arquivo e vejo o resumo geral com totais e multas." |
| **5:15 – 5:30** | **Exibir** → Acervo/Membros/Empréstimos/Relatório; **Ajuda** → Regras de negócio (`F1`), Atalhos, Sobre | "O menu Exibir troca as abas e o menu Ajuda traz as regras de negócio, os atalhos de teclado e o sobre." |
| **5:30 – 5:45** | **Arquivo ▸ Nova biblioteca (vazia)** → confirmar → tudo zera; **Carregar dados de exemplo** | "No Arquivo eu começo uma biblioteca vazia ou recarrego os exemplos. Como ainda não tem banco, ao fechar o programa os dados se perdem — isso fica para a próxima etapa." |
| **5:45 – 6:00** | Terminal: `python3 -m pytest -q` → 113 passed; **Arquivo ▸ Sair** | "Por fim, os testes: 113 testes automáticos, incluindo um que aciona todas as opções do menu. Todos passando. Obrigado!" |

**Dicas**
- Use os atalhos (`Ctrl+E`, `Ctrl+D`, `Ctrl+F`, `Ctrl+R`) para ganhar tempo; Enter confirma e Esc fecha as janelas.
- Se o tempo apertar, encurte as Consultas (mostre 4 ou 5) e pule a edição de membro.
- Grave em 1080p e confira se o texto dos menus está legível antes de subir no YouTube.
