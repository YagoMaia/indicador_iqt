from typing import Optional

import geopandas as gpd
import numpy as np
import pandas as pd
from shapely.geometry import LineString, Point
from shapely.wkt import loads

from ..utils import Associador, modelos
from ..utils.cores import cor_iqt
from .classificar_indicadores import ClassificarIndicadores


class CalcularIndicadores:
	"""
	Classe para cálculo e avaliação de indicadores de qualidade do transporte público.

	Esta classe contém métodos para calcular o Índice de Qualidade do Transporte (IQT)
	e avaliar diferentes aspectos do serviço de transporte público, como pontualidade,
	infraestrutura e atendimento.
	"""

	def __init__(self):
		"""
		Inicializa a classe com os valores predefinidos dos indicadores e suas prioridades.
		"""
		self.indicadores_prioridades = {
			"nomeclatura": ["I1", "I2", "I3", "I4", "I5", "I6", "I7", "I8", "I9", "I10"],
			"prioridade": [0.1526, 0.1121, 0.0997, 0.2269, 0.0992, 0.0831, 0.0954, 0.0756, 0.0277, 0.0277],
			"indicador": [
				"Porcentagem das vias pavimentadas",
				"Distância entre pontos",
				"Integração municipal do sistema de transporte",
				"Pontualidade – cumprir horários",
				"Frequência de atendimento",
				"Cumprimento dos itinerários",
				"Abrangência da rede – atender a cidade",
				"Treinamento e capacitação dos motoristas",
				"Existência Sistema de informação pela internet",
				"Valor da Tarifa ",
			],
		}

	def carregar_dados(self, df_linhas: pd.DataFrame, df_frequencia: pd.DataFrame, df_pontualidade: pd.DataFrame, df_cumprimento: pd.DataFrame):
		"""Carrega todos os dados necessários para o cálculo dos indicadores.

		Args:
			df_linhas (pd.DataFrame): DataFrame contendo os dados das linhas de transporte.
			df_frequencia (pd.DataFrame): DataFrame contendo os dados de frequência de atendimento.
			df_pontualidade (pd.DataFrame): DataFrame contendo os dados de pontualidade.
			df_cumprimento (pd.DataFrame): DataFrame contendo os dados de cumprimento de itinerário.
		"""
		self.dados_linhas = self.carregar_dados_linha(df_linhas)
		self.frequencia = self.carregar_frequencia_atendimento_pontuacao(df_frequencia)
		self.pontualidade = self.carregar_pontualidade(df_pontualidade)
		self.cumprimento = self.carregar_cumprimento(df_cumprimento)

	def carregar_dados_geometrias(self, df_pontos_onibus: pd.DataFrame, df_residencias: pd.DataFrame):
		"""Carrega os dados geométricos de pontos de ônibus e residências.

		Args:
			df_pontos_onibus (pd.DataFrame): DataFrame contendo os dados dos pontos de ônibus.
			df_residencias (pd.DataFrame): DataFrame contendo os dados das residências.
		"""
		self.associador = Associador(df_pontos_onibus, self.dados_linhas.copy(), df_residencias)
		self.dados_geograficos = self.associador.consolidar_associacoes()

	def carregar_dados_linha(self, df_line: pd.DataFrame) -> gpd.GeoDataFrame:
		"""
		Carrega os dados de frequência de atendimento a partir de um DataFrame.

		Args:
			df_line (pd.DataFrame): DataFrame contendo os dados de frequência de atendimento.

		Returns:
			gpd.GeoDataFrame: GeoDataFrame com a coluna geometry convertida para LineString 2D.
		"""
		try:
			if not modelos.validar_df_dados_linhas(df_line):
				raise

			df_copy = df_line.copy()

			dados_linhas = gpd.GeoDataFrame(df_copy)
			if not self._validar_geometry_wkt(dados_linhas).all():
				raise

			return self._converter_geometry_para_linestring(dados_linhas)
		except Exception as error:
			print("Erro ao carregar dados de linha: ", error)
			return gpd.GeoDataFrame()

	def _validar_geometry_wkt(self, df, coluna="geometry"):
		"""
		Valida se os valores da coluna geometry são strings WKT.

		Args:
			df (pd.DataFrame): DataFrame contendo a coluna geometry.
			coluna (str): Nome da coluna geometry.

		Returns:
			bool: True se todos os valores forem strings WKT, False caso contrário.
		"""
		return df[coluna].apply(lambda x: isinstance(x, str) and x.startswith("LINESTRING"))

	def _converter_geometry_para_linestring(self, df: pd.DataFrame, coluna: str = "geometry", crs: Optional[str] = "EPSG:4326") -> gpd.GeoDataFrame:
		"""
		Converte strings WKT em objetos LineString 2D e retorna um GeoDataFrame.

		Args:
			df (pd.DataFrame): DataFrame contendo a coluna geometry.
			coluna (str): Nome da coluna que contém as geometrias.
			crs (Optional[str]): Sistema de coordenadas do GeoDataFrame. Default é WGS84.

		Returns:
			gpd.GeoDataFrame: GeoDataFrame com a coluna geometry convertida para LineString 2D.

		Raises:
			ValueError: Se a coluna especificada não existir no DataFrame.
		"""
		if coluna not in df.columns:
			raise ValueError(f"Coluna '{coluna}' não encontrada no DataFrame")

		df_copy = df.copy()

		def converter_para_2d(geom):
			if geom is None:
				return None

			if isinstance(geom, str):
				geom = loads(geom)

			coords_2d = [(x, y) for x, y, *_ in geom.coords]

			return LineString(coords_2d)

		df_copy[coluna] = df_copy[coluna].apply(converter_para_2d)  # type: ignore

		gdf = gpd.GeoDataFrame(data=df_copy, geometry=coluna, crs=crs)  # type: ignore

		return gdf

	def _cria_geometry_pontos_rota(self, df: gpd.GeoDataFrame, coluna: str = "geometry") -> gpd.GeoDataFrame:
		"""
		Cria um geometry com os pontos da LineString e adiciona-os ao DataFrame.

		Args:
			df (gpd.GeoDataFrame): GeoDataFrame contendo a coluna 'geometry' que é um LineString.
			coluna (str): Nome da coluna que contém o LineString.

		Returns:
			gpd.GeoDataFrame: DataFrame com a coluna geometry contendo os pontos da LineString.
		"""
		try:
			if coluna not in df.columns:
				raise ValueError(f"Coluna '{coluna}' não encontrada no DataFrame.")

			novo_df_linhas = []

			for idx, row in df.iterrows():
				linha_geometry = row[coluna]

				if not isinstance(linha_geometry, LineString):
					print(f"Aviso: A geometria na linha {idx} não é um LineString. Pulando...")
					continue

				coords = list(linha_geometry.coords)

				for coord_idx, coord in enumerate(coords):
					nova_linha = {}
					nova_linha["linha"] = row.to_dict()["linha"]

					nova_linha["geometry"] = Point(coord[0], coord[1])

					nova_linha["ponto_ordem"] = coord_idx

					novo_df_linhas.append(nova_linha)

			gdf_pontos = gpd.GeoDataFrame(novo_df_linhas, crs=32723)  # type: ignore

			return gdf_pontos

		except Exception as error:
			print(f"Erro ao criar geometria dos pontos da rota: {error}")
			return gpd.GeoDataFrame()  # Retorna um GeoDataFrame vazio em caso de erro

	def carregar_cumprimento(self, df_cumprimento: pd.DataFrame) -> pd.DataFrame:
		"""
		Carrega os dados de cumprimento do itinerário a partir de um DataFrame.
		"""
		try:
			if not modelos.validar_df_cumprimento(df_cumprimento):
				raise
			return self.cumprimento_itinerario(df_cumprimento)
		except Exception as error:
			print("Erro ao carregar dados de cumprimento: ", error)
			return pd.DataFrame()

	def carregar_frequencia_atendimento_pontuacao(self, df_frequencia: pd.DataFrame) -> pd.DataFrame:
		"""
		Carrega os dados de frequência de atendimento a partir de um DataFrame.
		"""
		try:
			if not modelos.validar_df_frequencia(df_frequencia):
				raise
			return self.frequencia_atendimento_pontuacao(df_frequencia)
		except Exception as error:
			print("Erro ao carregar dados de frequência: ", error)
			return pd.DataFrame()

	def carregar_pontualidade(self, df_pontualidade: pd.DataFrame) -> pd.DataFrame:
		"""
		Carrega os dados de pontualidade a partir de um DataFrame.
		"""
		try:
			if not modelos.validar_df_pontualidade(df_pontualidade):
				raise
			return self.calcular_pontualidade(df_pontualidade)
		except Exception as error:
			print("Erro ao carregar dados de pontualidade: ", error)
			return pd.DataFrame()

	def cumprimento_itinerario(self, df_cumprimento: pd.DataFrame):
		"""_summary_.

		Args:
			df_cumprimento (pd.DataFrame): _description_

		Returns:
			_type_: _description_
		"""
		df_temp = df_cumprimento.copy()

		df_temp[["linha", "sentido"]] = df_temp["Trajeto"].str.extract(r"(\d+)\s*-\s*.*\((ida|volta)\)")
		df_temp.replace("-", pd.NA, inplace=True)
		df_temp.dropna(subset=["KM Executado"], inplace=True)
		df_temp["KM Executado"] = pd.to_numeric(df_temp["KM Executado"], errors="coerce")
		df_temp = df_temp.groupby(["linha"])["KM Executado"].mean().reset_index()

		return df_temp

	def calcular_pontualidade(self, df_pontualidade: pd.DataFrame) -> pd.DataFrame:
		"""
		Calcula a pontuação para o indicador de pontualidade.
		"""
		try:
			df_temp = df_pontualidade.copy()

			df_temp[["linha", "sentido"]] = df_temp["Trajeto"].str.extract(r"(\d+)\s*-\s*.*\((ida|volta)\)")
			df_temp["sentido"] = df_temp["sentido"].replace({"ida": "IDA", "volta": "VOLTA"})
			df_temp = df_temp.drop("Trajeto", axis=1)
			df_temp.replace("-", pd.NA, inplace=True)
			df_temp["com_horario"] = df_temp[["Chegada ao ponto", "Partida Real", "Chegada Real"]].notna().any(axis=1)
			df_temp = df_temp.groupby("linha")["com_horario"].value_counts(normalize=False).unstack(fill_value=0)

			# # Renomeia as colunas para maior clareza
			df_temp.columns = ["sem_horario", "com_horario"]

			# # Calcula a proporção de viagens sem horário sobre o total de viagens para cada grupo
			df_temp["pontualidade"] = df_temp["com_horario"] / (df_temp["sem_horario"] + df_temp["com_horario"])
			df_temp = df_temp.drop(["sem_horario", "com_horario"], axis=1)

			df_temp_reset = df_temp.reset_index()

			return df_temp_reset[["linha", "pontualidade"]]
		except Exception as error:
			print("Erro ao calcular pontualidade: ", error)
			return pd.DataFrame()

	def frequencia_atendimento_pontuacao(self, df_frequencia: pd.DataFrame) -> pd.DataFrame:
		"""Calcula o tempo médio de operação por rota (linha).

		Args:
			df_frequencia (pd.DataFrame): DataFrame contendo a coluna 'linha' para identificar a rota e colunas de tempo.

		Returns:
			pd.DataFrame: DataFrame com o tempo médio de operação por rota.
		"""
		df_temp = df_frequencia.copy()

		df_temp["hsstart"] = pd.to_datetime(df_temp["hsstart"], format="%H:%M:%S")
		df_temp["hsstop"] = pd.to_datetime(df_temp["hsstop"], format="%H:%M:%S")

		# Calcular a duração como a diferença entre hsstop e hsstart
		df_temp["frequencia_atendimento_pontuacao"] = df_temp["hsstop"] - df_temp["hsstart"]
		df_temp["frequencia_atendimento_pontuacao"] = df_temp["frequencia_atendimento_pontuacao"].apply(lambda x: int(x.total_seconds() / 60))

		df_temp["data"] = pd.to_datetime(df_temp["data"], format="%d/%m/%Y")
		df_temp["dataf"] = pd.to_datetime(df_temp["dataf"], format="%d/%m/%Y")

		# df_temp['sentido'] = df_temp['sentido'].replace({0: 'IDA', 1: 'VOLTA'})

		df_temp = df_temp.groupby(["linha"])["frequencia_atendimento_pontuacao"].mean().reset_index()

		return df_temp

	def merge_dados(self):
		"""Combina todos os dados carregados em um único DataFrame."""
		try:
			if not isinstance(self.dados_linhas, gpd.GeoDataFrame):
				raise
			crs_original = self.dados_linhas.crs

			self.dados_linhas = self.dados_linhas.to_crs(epsg=31983)

			if not isinstance(self.dados_linhas, gpd.GeoDataFrame):
				raise

			self.dados_linhas["distancia_km"] = self.dados_linhas.length / 1000

			self.dados_linhas = self.dados_linhas.to_crs(crs_original)

			if not isinstance(self.dados_linhas, gpd.GeoDataFrame):
				raise

			self.cumprimento["cumprimento_itinerario"] = self.cumprimento["KM Executado"].astype(float) / self.dados_linhas["distancia_km"].astype(
				float
			)  # type: ignore

			self.dados_completos = pd.merge(self.dados_linhas, self.cumprimento, on=["linha"])
			self.dados_completos = pd.merge(self.dados_completos, self.frequencia, on=["linha"])
			self.dados_completos = pd.merge(self.dados_completos, self.pontualidade, on=["linha"])
			self.dados_completos = pd.merge(self.dados_completos, self.dados_geograficos, on=["linha"])

			self.dados_completos = gpd.GeoDataFrame(self.dados_completos)

		except Exception as e:
			print(f"Erro ao mesclar os dados: {e}")

	def classificar_linha(self):
		"""Classifica as linhas de acordo com os indicadores calculados."""
		classificador = ClassificarIndicadores()
		self.merge_dados()
		self.classificao_linhas = classificador.classificar_linhas(self.dados_completos)

	def calcular_iqt(self, linha: list) -> float:
		"""Calcula o Índice de Qualidade do Transporte (IQT) para uma linha específica.

		Args:
			linha (list): Lista contendo os valores dos indicadores para uma linha específica. O primeiro elemento é ignorado, e os demais devem corresponder aos indicadores na ordem definida em indicadores_prioridades.

		Returns:
			float: Valor do IQT calculado.
		"""
		try:
			prioridades = self.indicadores_prioridades["prioridade"]
			soma_ponderada = np.dot(linha, prioridades)

			desvio_padrao_prioridades = np.std(prioridades)

			iqt = soma_ponderada / (desvio_padrao_prioridades * len(prioridades))
			return iqt
		except Exception as e:
			print(f"Erro ao calcular IQT: {e}")
			return 0.0

	def processar_iqt(self):
		"""Processa o cálculo do IQT para todas as linhas classificadas."""
		valores_iqt, cores = [], []
		for _, row in self.classificao_linhas.iterrows():
			# Excluir as colunas 'linha' e 'sentido' e converter para lista
			valores_indicadores = row.iloc[1:].tolist()  # Pegando valores de 'I1', 'I3', 'I4', etc.

			# Chamar a função de cálculo do IQT passando os valores da linha
			iqt = self.calcular_iqt(valores_indicadores)
			cor = cor_iqt(iqt)
			valores_iqt.append(iqt)
			cores.append(cor)
		self.dados_completos["iqt"] = valores_iqt
		self.dados_completos["cor"] = cores
