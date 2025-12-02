# Signet
**Signet** é uma ferramenta de comando de linha (CLI) open source licenciada sob AGPLv3 que permite você adicionar marcas d'àgua e metadados em PDFs antes de distribuí-los para usuários finais, garantindo que a licença de distribuição do arquivo esteja publicamente visível.

# How to use
```
$ pip install -r requirements.txt
$ chmod +x signet.sh
$ ./signet.sh --help
````

# Licensing
Recomenda-se que esta ferramenta CLI seja utilizada de forma independente através do CLI. A biblioteca PyMuPDF é utilizada e está licenciada com a Affero General Public License v3 (AGPLv3). Por consequência, esta biblioteca também é licenciada como AGPL para sua distribuição.

# Expected Improvements
* Suporte para arquivos EPUB
* Padronizar transferência de ```userdata``` através de modelos **Pydantic**
* Tornar respostas em JSON opcional.
* Introspecção de PDFs processados via Signet.
* Personalização da marca d'àgua via CLI
* Adicionar validação de dados de usuário
* Retornar mais informações sobre o PDF
    * Quantidade de páginas
    * Orientação da página
    * Dimensões da capa
    * Probes do arquivo (criptografia, metadados, etc)
