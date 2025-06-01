# Logos Originais

Coloque neste diretório os logos originais que você quer modificar. Os arquivos devem seguir o seguinte padrão de nomenclatura:

- adidas.png (ou .jpg/.jpeg)
- nike.png
- lexus.png
- golden_state_warriors.png
- duff_beer.png
- puma.png
- underarmour.png
- wellsfargo.png
- robin.png
- champion.png
- aldi.png

O script irá gerar variações destes logos que podem potencialmente confundir o modelo de detecção, mantendo-os ainda reconhecíveis para humanos.

## Tipos de Variações Geradas

Para cada logo, o script irá gerar as seguintes variações:

1. Rotações sutis (2°, -2°, 5°, -5°)
2. Modificações leves de cor (alteração de matiz)
3. Adição de ruído sutil
4. Suavização de bordas
5. Modificação de contraste
6. Esticamento leve
7. Realce de bordas
8. Combinação de várias modificações

Todas as variações serão salvas no diretório `data/modified_logos/[nome_do_logo]/` 