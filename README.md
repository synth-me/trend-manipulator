# Tutorial de uso do aplicativo 

## Motivacao 

Este aplicativo tem como objetivo facilitar a modificacao das trends que ja existem dentro de algum projeto. 
Possibilidades de aplicaco: 

1. manutencao de equipamento que distorce as medicoes em um dado periodo de tempo
2. adicao de offset que distorceu em um momento especifico 
3. equiapmento teve falha e foram registrados diversos valores incongruentes 

## Por onde comecar ? 

## 1. Como extrair uma trend em XML 

A base deste aplicativo esta nos arquivos em XML extraido das trends. Para extrair esses valores basta navegar 
na trend desejada, adicionar a mesma quantidade de valores totais da trend (Ex: se o tamanho da trend esta em 8 mil, coloque a visualizacao em 8 mil valores para que todos possam ser extraidos). 

![alt text](./tutorial/size.png)
> aqui podemos ver uma trend com tamanho 5 mil 

![alt text](./tutorial/view.png)
> basta entao ir ate a visualizacao indicada na imagem 

![alt text](./tutorial/export.png)
> entao, basta visualizar toda a trend e exportar como XML

O formato do arquivo de saida deve ser algo parecido com: 

```xml
<?xml version="1.0" encoding="utf-8"?>
<LogRecords Log="storage" LogDescription="" LogPath="/Server 1/example/storage" Unit="NoUnit" Signal="/Server 1/example/Value" Locale="ja-JP" Max="NaN" Min="NaN" Average="NaN" Count="1" StartTime="2026/02/12 19:49:21" EndTime="2026/02/12 19:49:21" Description="">
  <TrendLogEventRecord Timestamp="2026/02/12 19:49:21" Value="1001" Events="" Comment="" User="" />
</LogRecords>
```

## 2. Possibilidade de acoes 

Utilizaremos a seguinte trend como base dos seguintes tutoriais:

![alt text](./tutorial/example.png)

### 2.1 Deletar dados 

Suponha que queremos deletar os valores de: 

12/02/2026 23:10:00 ate 12/02/2026 23:13:00

Primeiro basta acessar o botao "deletar intervalo de dados" 

![alt text](./tutorial/delete_button.png)

Apos isso, clique no botao para procurar o XML que foi extraido da sua trend e escolha o periodo de inicio e de fim da exclusao dos dados: 

![alt text](./tutorial/usage-delete.png)

Caso queira, tambem e possivel mudar o nome do arquivo de saida. 
Basta entao clicar em "Remover Dados". Isso ira gerar um novo arquivo 
que e uma copia do anterior sem as informacoes escolhidas. 

Para retornar para o EBO voce deve entao ir ate a trend e
exclui-la para que os valores nao fiquem duplicados: 

![alt text](./tutorial/clean-trend.png)

e entao para importar os novos valores na trend basta seguir o seguinte

![alt text](./tutorial/import-log.png)
> Utilize o botao "import log data" 

e entao navegue ate o XML que foi gerado, na pasta "outputs". 

![alt text](./tutorial/escolha-arquivo.png)
> o nome ira depender do nome escolhido pelo usuario 

O resultado deve ser algo parecido como:
![alt text](./tutorial/resultado-deletar.png)
> valores escolhidos foram excluidos


### 2.2 Modificar dados 

Assim como na situacao anterior, voce devera deletar os valores anteriores 
para poder modificar os existentes. Portanto caso queira saber como adicionar os valores
na trend, siga os passos anteriores relativos a isso (exportar, deletar e importar)

Utilizando o terceiro botao "Modificar Trend Existente" o usuario pode ao inves de 
deletar valores, modifica-los: 

![alt text](./tutorial/modificar-trend.png)
> Botao de modificacao de trend 

Neste caso iremos modificar os valores de 12/02/2026 23:10:00 ate 12/02/2026 23:13:00 para 1001 

![alt text](./tutorial/tela-modificacao.png)
> modificacao 

E entao basta clicar para gerar o novo arquivo. Apos isso importamos no EBO: 

![alt text](./tutorial/trend-modificada.png)
> trend apos a modificacao 

### 2.3 Gerar uma trend de exemplo 

Para gerar um trend e utilizar, por exemplo, para testar graficos e telas e possivel utilizar a primeira opcao do app: 

![alt text](./tutorial/gerar-button.png)
> botao para ir ate a tela de geracao de trend 

Basta escolher o periodo, o passo (quantidade de pontos naquele periodo) e o tipo de distribuicao (linear, cosseno, quadrado etc ...). 

![alt text](./tutorial/tela-geracao.png)
> exemplo de geracao de trend 

E entao utilizar o XML de saida para alguma trend que esteja em branco no EBO 

### 2.4 Gerar a partir de excel 

Parar gerar um XML a partir de um excel o usuario devera clicar no segundo botao "Converter Excel XML". 

![alt text](./tutorial/converstion-button.png)
> botao que dever ser clicado 

Apos isso basta selecionar o arquivo excel desejado. O arquivo em questao deve ter a seguinte estrutura para funcionar: 

![alt text](./tutorial/excel-example.png)
> exemplo de arquivo

![alt text](./tutorial/tela-conversion.png)
> selecao do arquivo 

Este arquivo, por exemplo ira gerar: 

![alt text](./tutorial/excel-to-xml.png)
> trend gerada no EBO
