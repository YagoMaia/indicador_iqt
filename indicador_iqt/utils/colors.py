from random import randint

class Colors:
    """
    Define um conjunto padrão de cores em formato hexadecimal para uso em visualizações.

    Esta classe fornece uma paleta de cores constante que pode ser utilizada de forma
    consistente em toda a aplicação. As cores são definidas em formato hexadecimal
    e seguem uma paleta similar à utilizada em várias bibliotecas de visualização
    de dados.

    Attributes:
        RED (str): Vermelho (#d62728)
        BLUE (str): Azul (#1f77b4)
        ORANGE (str): Laranja (#ff7f0e)
        GREEN (str): Verde (#2ca02c)
        PURPLE (str): Roxo (#9467bd)
        BROWN (str): Marrom (#8c564b)
        PINK (str): Rosa (#e377c2)
        GREY (str): Cinza (#7f7f7f)
        YELLOW (str): Amarelo (#bcbd22)
        CYAN (str): Ciano (#17becf)

    Example:
        >>> # Utilizando as cores em uma visualização
        >>> plt.plot(data, color=Colors.BLUE)
        >>> plt.scatter(x, y, color=Colors.RED)
    """
    RED = '#d62728'
    BLUE = '#1f77b4'
    ORANGE = '#ff7f0e'
    GREEN = '#2ca02c'
    PURPLE = '#9467bd'
    BROWN = '#8c564b'
    PINK = '#e377c2'
    GREY = '#7f7f7f'
    YELLOW = '#bcbd22'
    CYAN = '#17becf'

def color_iqt(iqt: float) -> str:
    """
    Determina a cor apropriada com base no valor do IQT (Índice de Qualidade do Transporte).

    Esta função mapeia diferentes faixas de valores IQT para cores específicas,
    permitindo uma representação visual da qualidade do transporte:
    - Verde: Qualidade Alta (IQT >= 3.0)
    - Azul: Qualidade Média (2.0 <= IQT < 3.0)
    - Vermelho: Qualidade Baixa (1.0 <= IQT < 2.0)
    - Rosa: Qualidade Muito Baixa (IQT < 1.0)

    Args:
        iqt (float): Valor do Índice de Qualidade do Transporte.

    Returns:
        str: Código hexadecimal da cor correspondente ao valor IQT,
             utilizando as cores definidas na classe Colors.

    Examples:
        >>> color_iqt(3.5)
        '#2ca02c'  # Verde para qualidade alta
        >>> color_iqt(2.5)
        '#1f77b4'  # Azul para qualidade média
        >>> color_iqt(1.5)
        '#d62728'  # Vermelho para qualidade baixa
        >>> color_iqt(0.5)
        '#e377c2'  # Rosa para qualidade muito baixa
    """
    if iqt >= 3.0:
        return Colors.GREEN
    elif 2 <= iqt < 3.0:
        return Colors.BLUE
    elif 1.0 <= iqt < 2:
        return Colors.RED
    else:
        return Colors.PINK
    
def randon_color() -> str:
    cor = "#{:06x}".format(randint(0, 0xFFFFFF))
    return cor