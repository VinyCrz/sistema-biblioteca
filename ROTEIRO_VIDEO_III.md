# Roteiro do vídeo — Desk App III (até 6 minutos)

*Antes de gravar, abra o terminal na pasta do projeto e apague o banco antigo para começar do zero: `rm -f biblioteca.db`. Deixe o terminal e o editor de código abertos. Não abra o app ainda: ele vai ser aberto durante o vídeo.*

---

Oi, eu sou o Vinicius e este é o Sistema de Biblioteca, agora na etapa Desk App III. Nas etapas anteriores o sistema já tinha todas as funcionalidades e um menu completo, mas os dados ficavam só na memória, e quando o programa fechava tudo se perdia. Nesta etapa eu coloquei um banco de dados, e é isso que eu vou mostrar funcionando aqui na minha máquina.

O banco que eu usei é o SQLite, que já vem junto com o Python, então não precisa instalar nada. Aqui no terminal eu abro o sistema com `python3 app.py`. Como é a primeira vez, o programa cria o arquivo `biblioteca.db` e já grava alguns dados de exemplo. Repara aqui embaixo na barra de status: ela mostra que os dados estão vindo do banco de dados.

Agora vou usar o sistema normalmente. Em Cadastros, Acervo, Novo Livro, eu cadastro O Cortiço, do Aluísio Azevedo, de 1890, com o código L3. Depois, em Cadastros, Membros, Novo Aluno, eu cadastro o Bruno Alves, CPF 111.222.333-44, matrícula A002, do curso de ADS. O sistema gera a carteirinha dele na hora.

Em seguida faço alguns empréstimos. Em Movimentação, Emprestar item, eu empresto o DVD Cidade de Deus para a Ana com a data de primeiro de novembro, e empresto O Cortiço para o Bruno com a data de hoje. Depois, em Devolver item, eu devolvo o DVD com a data de seis de novembro. O prazo do DVD é de três dias e ela atrasou dois, então o sistema calcula uma multa de quatro reais. As regras continuam funcionando como antes: se eu tento emprestar O Cortiço de novo, o sistema avisa que o item já está emprestado.

Também vou editar um cadastro. Em Cadastros, Membros, Editar membro, eu escolho o professor Carlos e troco o departamento para Matemática. E em Cadastros, Acervo, Remover item, eu removo o livro Clean Code.

Agora vem a parte mais importante desta etapa. Eu vou fechar o programa pelo menu Arquivo, Sair. Pronto, fechou. Abrindo de novo com `python3 app.py`, dá para ver que tudo continua aqui: O Cortiço está no acervo e aparece como emprestado, o Bruno está cadastrado com a mesma carteirinha, o Carlos agora é de Matemática, o Clean Code não aparece mais, e na aba Empréstimos está o histórico com a multa de quatro reais. Nada se perdeu, porque cada operação foi gravada no banco na hora em que foi feita.

Dá para ver o banco por dentro de dois jeitos. No próprio sistema, em Arquivo, Ver banco de dados, aparecem as três tabelas: itens, membros e empréstimos. E pelo terminal, com o comando `python3 ver_banco.py`, o conteúdo das tabelas é impresso direto na tela. Repara que o Clean Code continua na tabela de itens, mas com `ativo` igual a zero. Eu fiz assim de propósito: o item removido some do sistema, mas o histórico de empréstimos e as multas não se perdem.

Rapidamente no código: o banco ficou em duas classes novas. O `RepositorioSQLite`, no arquivo `repositorio.py`, é a única classe que conhece SQL. Ele cria as tabelas, faz os inserts e updates e transforma as linhas do banco de volta em objetos, como Livro, Aluno e Empréstimo. Livro, Revista e DVD ficam na mesma tabela, separados pela coluna tipo, e os empréstimos usam chaves estrangeiras para ligar o item ao membro. A outra classe é a `BibliotecaPersistente`, no arquivo `persistente.py`, que herda da Biblioteca. Cada método dela chama o método da classe mãe com `super()`, onde estão as regras de negócio, e só se deu tudo certo é que grava no banco. Se a regra falhar, nada é gravado.

Para terminar, os testes. Rodando `python3 -m pytest -q`, são 128 testes, todos passando. Os testes novos do banco gravam os dados, fecham o banco, abrem de novo e conferem se tudo voltou igual.

Então é isso: o Sistema de Biblioteca agora funciona completo, com os dados salvos de verdade num banco de dados. O código e a documentação estão no GitHub. Obrigado!
