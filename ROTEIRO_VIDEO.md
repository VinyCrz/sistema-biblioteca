# 🎬 Roteiro do vídeo — Desk App I (máx. 3:00)

| Tempo | O que mostrar | O que falar |
|---|---|---|
| **0:00 – 0:15** | README aberto no GitHub | "Olá, eu sou o Vinicius e este é o Sistema de Biblioteca, projeto de POO da disciplina Desk App I, feito em Python com Tkinter. O repositório é público e tem diagrama UML e testes automatizados." |
| **0:15 – 0:30** | `docs/uml_simples.png` — apontar Livro/Revista/DVD → ItemAcervo, Aluno/Professor → Membro, exportadores → Exportador | "Este é o diagrama de classes. **Herança:** Livro, Revista e DVD herdam de ItemAcervo; Aluno e Professor herdam de Membro; e os dois exportadores herdam de Exportador. **Polimorfismo:** cada filho responde do seu jeito — o DVD tem prazo de 3 dias, o livro de 14; o professor tem limite maior e desconto na multa." |
| **0:30 – 0:45** | Losangos cheios: Biblioteca–Emprestimo e Membro–Carteirinha | "**Composição**, o losango cheio: a carteirinha é criada dentro do membro, e o empréstimo é criado pela biblioteca. Um não existe sem o outro." |
| **0:45 – 0:55** | Losangos vazios: Biblioteca–ItemAcervo e Biblioteca–Membro | "**Agregação**, o losango vazio: itens e membros são criados fora e só adicionados à biblioteca — se eu removo um livro, ele continua existindo." |
| **0:55 – 1:05** | Setas cheias saindo de Emprestimo | "**Associação**: o empréstimo liga um membro a um item, guardando a referência dos dois." |
| **1:05 – 1:15** | Linhas pontilhadas: → CalculadoraMulta e → Exportador | "**Dependência**, a linha pontilhada: o empréstimo só usa a calculadora de multa na hora de devolver, e a biblioteca recebe o exportador como parâmetro para gerar o relatório." |
| **1:15 – 1:35** | `pessoas.py` (`# COMPOSIÇÃO` no `Membro.__init__`), `emprestimo.py` (`devolver`), `biblioteca.py` (`emprestar`) | "No código, cada relação está marcada com um comentário. Aqui o membro cria a carteirinha; aqui o devolver usa a calculadora; e aqui o emprestar verifica o limite de forma polimórfica." |
| **1:35 – 1:50** | `python3 app.py` → aba **Acervo**: cadastrar Livro (L3, "O Cortiço", 1890, Aluísio Azevedo) e digitar "machado" na pesquisa | "Na aba Acervo eu cadastro um livro — repare que o campo extra muda conforme o tipo — e a pesquisa filtra enquanto eu digito." |
| **1:50 – 2:00** | Aba **Membros**: cadastrar Aluno (Bruno, 111.222.333-44, A002, ADS) | "Cadastro um aluno e a carteirinha é gerada automaticamente com validade de um ano." |
| **2:00 – 2:15** | Aba **Empréstimos**: D1 + A001, data 01/11/2026 → Emprestar; depois data 06/11/2026 → Devolver item | "Empresto o DVD Cidade de Deus para a Ana em 01/11. O prazo do DVD é 3 dias. Devolvendo em 06/11, são 2 dias de atraso a R$ 2,00: multa de **R$ 4,00**." |
| **2:15 – 2:20** | Emprestar D1 para A001 e tentar emprestar D1 de novo para P001 | "Se eu tento emprestar um item que já está emprestado, o sistema mostra o erro." |
| **2:20 – 2:30** | Aba **Relatório**: Gerar em Texto, depois em CSV | "E aqui gero o relatório em texto ou em CSV — o mesmo botão, exportadores diferentes: polimorfismo de novo." |
| **2:30 – 2:55** | Terminal: `python3 -m pytest -v` | "Todas as funcionalidades estão testadas: são 79 testes com pytest, separados em herança e polimorfismo, relações, funcionalidades e interface — todos passando." |
| **2:55 – 3:00** | README no GitHub | "O código e o UML estão no GitHub. Obrigado!" |

**Dicas:** deixe o app, o editor e o terminal já abertos antes de gravar; os dados de exemplo (L1, L2, R1, D1, A001, P001) já carregam ao abrir o app.
