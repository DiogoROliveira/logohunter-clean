from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
import os
import datetime
from PIL import Image as PILImage
import numpy as np
import matplotlib.pyplot as plt
import io
import tempfile
import shutil

class LogoDetectionReport:
    def __init__(self, output_dir):
        """
        Inicializa o gerador de relatórios.
        
        Args:
            output_dir (str): Diretório onde o relatório será salvo
        """
        self.output_dir = os.path.abspath(output_dir)
        os.makedirs(output_dir, exist_ok=True)
        
        # Criar diretório temporário para arquivos do relatório
        self.temp_dir = tempfile.mkdtemp()
        
        # Configurar estilos
        self.styles = getSampleStyleSheet()
        self.setup_custom_styles()
        
        # Lista para armazenar resultados
        self.results = []
        
    def setup_custom_styles(self):
        """Configura estilos personalizados para o relatório"""
        # Verificar se os estilos já existem antes de adicionar
        if 'ReportTitle' not in self.styles:
            self.styles.add(ParagraphStyle(
                name='ReportTitle',
                fontSize=24,
                spaceAfter=30,
                alignment=1  # Centralizado
            ))
        
        if 'ReportHeading1' not in self.styles:
            self.styles.add(ParagraphStyle(
                name='ReportHeading1',
                fontSize=18,
                spaceAfter=20,
                spaceBefore=20
            ))
        
        if 'ReportHeading2' not in self.styles:
            self.styles.add(ParagraphStyle(
                name='ReportHeading2',
                fontSize=14,
                spaceAfter=10,
                spaceBefore=10
            ))
        
        if 'ReportNormal' not in self.styles:
            self.styles.add(ParagraphStyle(
                name='ReportNormal',
                fontSize=11,
                spaceAfter=8
            ))

    def add_detection_result(self, image_path, predictions, confidence_scores, matched_logos):
        """
        Adiciona um resultado de detecção ao relatório.
        
        Args:
            image_path (str): Caminho da imagem analisada
            predictions (list/ndarray): Lista ou array de bounding boxes preditas
            confidence_scores (list): Scores de confiança para cada detecção
            matched_logos (dict): Dicionário com logos correspondentes e suas similaridades
        """
        # Converter arrays NumPy para listas Python se necessário
        if isinstance(predictions, np.ndarray):
            predictions = predictions.tolist()
        
        self.results.append({
            'image_path': image_path,
            'predictions': predictions,
            'confidence_scores': confidence_scores,
            'matched_logos': matched_logos
        })

    def create_confidence_plot(self, result, index):
        """Cria gráfico de confiança para uma detecção"""
        plt.figure(figsize=(4, 3))  # Tamanho reduzido
        if result['confidence_scores']:
            plt.bar(range(len(result['confidence_scores'])), result['confidence_scores'])
            plt.ylim(0, 1)
            plt.title('Scores de Confiança', fontsize=10)
            plt.xlabel('Detecção', fontsize=8)
            plt.ylabel('Confiança', fontsize=8)
            plt.xticks(fontsize=8)
            plt.yticks(fontsize=8)
            plt.tight_layout()
            
            # Salvar gráfico
            plot_path = os.path.join(self.temp_dir, f'confidence_plot_{index}.png')
            plt.savefig(plot_path, dpi=150, bbox_inches='tight')
            plt.close()
            return plot_path
        return None

    def create_matches_plot(self, result, index):
        """Cria gráfico de similaridade para matches"""
        if result['matched_logos']:
            plt.figure(figsize=(4, 3))  # Tamanho reduzido
            logos = list(result['matched_logos'].keys())
            similarities = [result['matched_logos'][logo] for logo in logos]
            
            plt.bar(range(len(similarities)), similarities)
            plt.ylim(0, 1)
            plt.title('Similaridade dos Matches', fontsize=10)
            plt.xticks(range(len(logos)), logos, rotation=45, ha='right', fontsize=8)
            plt.ylabel('Similaridade', fontsize=8)
            plt.yticks(fontsize=8)
            plt.tight_layout()
            
            # Salvar gráfico
            plot_path = os.path.join(self.temp_dir, f'matches_plot_{index}.png')
            plt.savefig(plot_path, dpi=150, bbox_inches='tight')
            plt.close()
            return plot_path
        return None

    def generate_report(self, output_filename='detection_report.pdf'):
        """Gera o relatório PDF com todos os resultados"""
        doc = SimpleDocTemplate(
            os.path.join(self.output_dir, output_filename),
            pagesize=A4,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=72
        )
        
        story = []
        
        # Título e cabeçalho
        title = Paragraph("Relatório de Detecção de Logos", self.styles['ReportTitle'])
        date = Paragraph(f"Gerado em: {datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')}", self.styles['ReportNormal'])
        story.extend([title, date, Spacer(1, 30)])
        
        # Sumário
        summary = Paragraph(f"Total de imagens analisadas: {len(self.results)}", self.styles['ReportHeading2'])
        story.extend([summary, Spacer(1, 20)])
        
        # Resultados por imagem
        for i, result in enumerate(self.results, 1):
            # Cabeçalho da seção
            section_title = Paragraph(f"Imagem {i}: {os.path.basename(result['image_path'])}", self.styles['ReportHeading1'])
            story.extend([section_title])
            
            # Estatísticas básicas
            stats = [
                [Paragraph("Detecções encontradas:", self.styles['ReportNormal']), str(len(result['predictions']))],
                [Paragraph("Matches realizados:", self.styles['ReportNormal']), str(len(result['matched_logos']))]
            ]
            
            stats_table = Table(stats, colWidths=[300, 200])
            stats_table.setStyle(TableStyle([
                ('GRID', (0, 0), (-1, -1), 1, colors.grey),
                ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
                ('PADDING', (0, 0), (-1, -1), 6)
            ]))
            story.extend([stats_table, Spacer(1, 20)])
            
            # Gráficos
            conf_plot = self.create_confidence_plot(result, i)
            matches_plot = self.create_matches_plot(result, i)
            
            if conf_plot or matches_plot:
                graphs = []
                if conf_plot:
                    graphs.append(Image(conf_plot, width=8*cm, height=6*cm))
                if matches_plot:
                    graphs.append(Image(matches_plot, width=8*cm, height=6*cm))
                
                if len(graphs) > 0:
                    table_data = [graphs]
                    graph_table = Table(table_data)
                    story.extend([graph_table, Spacer(1, 20)])
            
            # Detalhes dos matches
            if result['matched_logos']:
                matches_title = Paragraph("Detalhes dos Matches:", self.styles['ReportHeading2'])
                story.append(matches_title)
                
                matches_data = [[Paragraph("Logo", self.styles['ReportNormal']), 
                               Paragraph("Similaridade", self.styles['ReportNormal'])]]
                for logo, sim in result['matched_logos'].items():
                    matches_data.append([logo, f"{sim:.3f}"])
                
                matches_table = Table(matches_data, colWidths=[300, 200])
                matches_table.setStyle(TableStyle([
                    ('GRID', (0, 0), (-1, -1), 1, colors.grey),
                    ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
                    ('PADDING', (0, 0), (-1, -1), 6)
                ]))
                story.extend([matches_table, Spacer(1, 20)])
            
            # Adicionar quebra de página entre imagens
            if i < len(self.results):
                story.append(PageBreak())
        
        # Gerar PDF
        doc.build(story)
        
        # Limpar arquivos temporários
        shutil.rmtree(self.temp_dir)

    def __del__(self):
        """Limpar arquivos temporários se ainda existirem"""
        if hasattr(self, 'temp_dir') and os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

def create_report_from_detections(detections, output_dir="reports"):
    """
    Função auxiliar para criar um relatório a partir das detecções do modelo.
    
    Args:
        detections (list): Lista de tuplas (imagem, predições, scores, matches)
        output_dir (str): Diretório onde salvar o relatório
    """
    report = LogoDetectionReport(output_dir)
    
    for image_path, predictions, confidence_scores, matches in detections:
        report.add_detection_result(image_path, predictions, confidence_scores, matches)
    
    report.generate_report() 