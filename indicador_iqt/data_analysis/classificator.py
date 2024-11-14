import numpy as np
import pandas as pd

class IndicadoresClassificator:
    """
    Classe para classificar os indicadores de qualidade do transporte público.
    
    Esta classe contém métodos para calcular o Índice de Qualidade do Transporte (IQT)
    e avaliar diferentes aspectos do serviço de transporte público, como pontualidade,
    infraestrutura e atendimento.

    Attributes
    ----------
    indicadores_prioridades : dict
        Dicionário contendo as informações dos indicadores com as seguintes chaves:
        - 'nomeclatura': Lista de códigos dos indicadores (I1, I2, etc.)
        - 'prioridade': Lista de pesos para cada indicador
        - 'indicador': Lista com descrições dos indicadores
    """


    def pontualidade_pontuacao(self, pontualidade: float) -> int:
        """
        Calcula a pontuação para o indicador de pontualidade.

        Parameters
        ----------
        pontualidade : float
            Valor entre 0 e 1 representando a taxa de pontualidade.

        Returns
        -------
        int
            Pontuação atribuída:
            - 3: pontualidade >= 0.95
            - 2: 0.90 <= pontualidade < 0.95
            - 1: 0.80 <= pontualidade < 0.90
            - 0: pontualidade < 0.80
        """
        if 0.95 <= pontualidade:
            return 3
        elif 0.90 <= pontualidade < 0.95:
            return 2
        elif 0.80 <= pontualidade < 0.90:
            return 1
        else:
            return 0

    def porcentagem_vias_pavimentadas(self, porcentagem: float) -> int:
        """
        Calcula a pontuação para o indicador de vias pavimentadas.

        Parameters
        ----------
        porcentagem : float
            Valor entre 0 e 1 representando a porcentagem de vias pavimentadas.

        Returns
        -------
        int
            Pontuação atribuída:
            - 3: porcentagem >= 1
            - 2: 0.95 <= porcentagem < 0.99
            - 1: 0.85 <= porcentagem < 0.95
            - 0: porcentagem < 0.85
        """
        if 1 <= porcentagem:
            return 3
        elif 0.95 <= porcentagem < 0.99:
            return 2
        elif 0.85 <= porcentagem < 0.95:
            return 1
        else:
            return 0

    def distancia_pontos(self, distancia: float) -> int:
        """
        Calcula a pontuação para o indicador de distância entre pontos.

        Parameters
        ----------
        distancia : float
            Distância em metros entre os pontos de parada.

        Returns
        -------
        int
            Pontuação atribuída:
            - 3: distancia >= 250
            - 2: 250 <= distancia < 400
            - 1: 400 <= distancia < 500
            - 0: distancia >= 500 ou distancia < 250
        """
        if 250 <= distancia:
            return 3
        elif 250 <= distancia < 400:
            return 2
        elif 400 <= distancia < 500:
            return 1
        else:
            return 0

    def integracao_municipal(self, integracao: str) -> int:
        """
        Calcula a pontuação para o indicador de integração municipal.

        Parameters
        ----------
        integracao : float
            Valor entre 0 e 1 representando o nível de integração municipal.

        Returns
        -------
        int
            Pontuação atribuída:
            - 3: integracao >= 1
            - 2: 0.95 <= integracao < 1
            - 1: 0.85 <= integracao < 0.95
            - 0: integracao < 0.85
        """
        match integracao.strip():
            case 'Sistema de transporte público totalmente integrado com terminais com o uso de bilhete eletrônico para integração intra e intermodal':
                return 3
            case 'Sistema de transporte público totalmente integrado com terminais com o uso de bilhete eletrônico para integração intramodal somente':
                return 2
            case 'Integração tarifária temporal ocorre em determinados pontos, apenas com transferências intramodais':
                return 1
            case _:
                return 0

    def frequencia_atendimento(self, frequencia: float) -> int:
        """
        Calcula a pontuação para o indicador de frequência de atendimento.

        Parameters
        ----------
        frequencia : float
            Tempo em minutos entre atendimentos.

        Returns
        -------
        int
            Pontuação atribuída:
            - 3: frequencia <= 10
            - 2: 10 < frequencia <= 15
            - 1: 15 < frequencia <= 30
            - 0: frequencia > 30
        """
        if frequencia <= 10:
            return 3
        elif frequencia <= 15:
            return 2
        elif 15 < frequencia <= 30:
            return 1
        else:
            return 0

    def cumprimento_etinerarios(self, etinerario: float) -> int:
        """
        Calcula a pontuação para o indicador de cumprimento de itinerários.

        Parameters
        ----------
        etinerario : float
            Valor entre 0 e 1 representando a taxa de cumprimento dos itinerários.

        Returns
        -------
        int
            Pontuação atribuída:
            - 3: etinerario >= 1
            - 2: 0.8 <= etinerario <= 0.9
            - 1: 0.5 <= etinerario <= 0.7
            - 0: etinerario < 0.5
        """
        if 1 <= etinerario:
            return 3
        elif 0.9 <= etinerario <= 0.8:
            return 2
        elif 0.7 <= etinerario <= 0.5:
            return 1
        else:
            return 0

    def treinamento_capacitacao(self, treinamento: float) -> int:
        """
        Calcula a pontuação para o indicador de treinamento e capacitação.

        Parameters
        ----------
        treinamento : float
            Valor entre 0 e 1 representando o nível de treinamento dos motoristas.

        Returns
        -------
        int
            Pontuação atribuída:
            - 3: treinamento >= 1
            - 2: 0.95 <= treinamento <= 0.98
            - 1: 0.90 <= treinamento <= 0.95
            - 0: treinamento < 0.90
        """
        if 1 <= treinamento:
            return 3
        elif 0.98 <= treinamento <= 0.95:
            return 2
        elif 0.90 <= treinamento <= 0.95:
            return 1
        else:
            return 0
        
    def informacao_internet(self, informacao : str) -> int:
        match informacao:
            case 'Possuir informações em site e aplicativo atualizados':
                return 3
            case 'Possuir informações em site parcialmente atualizado':
                return 2
            case 'Possuir informação em site desatualizado':
                return 1
            case _:
                return 0
            
    def valor_tarrifa(self, informacao_tarifa : str) -> int:
        match informacao_tarifa:
            case 'Não houve aumento da tarifa ':
                return 3
            case 'Aumento inferior ao índice':
                return 2
            case 'Aumento equivalente ao índice':
                return 1
            case _:
                return 0

    def classificacao_iqt(self, iqt: float) -> str:
        """
        Classifica o IQT em categorias qualitativas.

        Parameters
        ----------
        iqt : float
            Valor do Índice de Qualidade do Transporte (IQT).

        Returns
        -------
        str
            Classificação do IQT:
            - 'Excelente': iqt >= 3.0
            - 'Bom': 2.0 <= iqt < 3.0
            - 'Suficiente': 1.0 <= iqt < 2.0
            - 'Insuficiente': iqt < 1.0
        """
        if iqt >= 3.0:
            return 'Excelente'
        elif 2 <= iqt < 3.0:
            return 'Bom'
        elif 1.0 <= iqt < 2:
            return 'Suficiente'
        else:
            return 'Insuficiente'
    def classificar_linhas(self, dados_linhas: pd.DataFrame) -> pd.DataFrame:
        classificacao = {
            'linha': [],
            'sentido': [],
            'I1': [],
            'I2': [],
            'I3': [],
            'I4': [],
            'I5': [],
            'I6': [],
            'I7': [],
            'I8': [],
            'I9': [],
            'I10': [],
        }

        # Itera pelas linhas do DataFrame e calcula as pontuações
        for _, linha in dados_linhas.iterrows():
            classificacao['linha'].append(linha['linha'])
            classificacao['sentido'].append(linha['sentido'])
            classificacao['I1'].append(self.porcentagem_vias_pavimentadas(linha['via_pavimentada']))
            classificacao['I2'].append(0)
            classificacao['I3'].append(self.integracao_municipal(linha['integracao']))
            classificacao['I4'].append(self.pontualidade_pontuacao(linha['pontualidade']))
            classificacao['I5'].append(self.frequencia_atendimento(linha['frequencia_atendimento']))
            classificacao['I6'].append(0)
            classificacao['I7'].append(0)
            classificacao['I8'].append(self.treinamento_capacitacao(linha['treinamento_motorista']))
            classificacao['I9'].append(self.informacao_internet(linha['informacao_internet']))
            classificacao['I10'].append(0)

        # Converte o dicionário em DataFrame
        return pd.DataFrame(classificacao)