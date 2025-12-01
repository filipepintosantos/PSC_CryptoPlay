"""
Module for generating Excel reports with cryptocurrency analysis.
Creates formatted spreadsheets with statistical data for different time periods.
"""

import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from datetime import datetime
from typing import Dict, List, Optional

class ExcelReporter:
    """Generates Excel reports from statistical analysis data."""
    
    PERIODS = ["12_months", "6_months", "3_months", "1_month"]
    PERIOD_DISPLAY = {
        "12_months": "12 Meses",
        "6_months": "6 Meses",
        "3_months": "3 Meses",
        "1_month": "1 Mês",
    }
    
    def __init__(self, filename: str = "reports/crypto_analysis.xlsx"):
        """
        Initialize the Excel reporter.
        
        Args:
            filename: Output Excel file path
        """
        self.filename = filename
        self.workbook = openpyxl.Workbook()
        self.workbook.remove(self.workbook.active)  # Remove default sheet
    
    def create_summary_sheet(self, reports: Dict[str, Dict]):
        """
        Create a summary sheet with all cryptocurrencies and periods.
        
        Args:
            reports: Dictionary with analysis reports from StatisticalAnalyzer
        """
        ws = self.workbook.create_sheet("Resumo", 0)
        
        # Header styling
        header_fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
        header_font = Font(bold=True, color="FFFFFF", size=11)
        border = Border(
            left=Side(style='thin'),
            right=Side(style='thin'),
            top=Side(style='thin'),
            bottom=Side(style='thin')
        )
        
        # Set column widths
        ws.column_dimensions['A'].width = 12
        for i, period in enumerate(self.PERIODS):
            col_offset = i * 7
            for j in range(7):
                col_letter = get_column_letter(2 + col_offset + j)
                ws.column_dimensions[col_letter].width = 14
        
        # Title row
        ws['A1'] = "Análise de Criptomoedas em EUR"
        ws['A1'].font = Font(bold=True, size=14)
        ws.merge_cells('A1:Z1')
        
        # Date row
        ws['A2'] = f"Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}"
        ws['A2'].font = Font(size=10, italic=True)
        
        # Column headers
        row = 4
        ws[f'A{row}'] = "Símbolo"
        ws[f'A{row}'].fill = header_fill
        ws[f'A{row}'].font = header_font
        
        col_idx = 2
        for period in self.PERIODS:
            period_display = self.PERIOD_DISPLAY[period]
            
            # Merge cells for period header
            start_col = get_column_letter(col_idx)
            end_col = get_column_letter(col_idx + 6)
            ws.merge_cells(f'{start_col}{row}:{end_col}{row}')
            
            cell = ws[f'{start_col}{row}']
            cell.value = period_display
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = Alignment(horizontal='center')
            
            # Sub-headers
            sub_headers = ["Mínimo", "Máximo", "Média", "Desvio", "Média-Desvio", "Última Quot.", "Desvio Média"]
            for j, sub_header in enumerate(sub_headers):
                col_letter = get_column_letter(col_idx + j)
                cell = ws[f'{col_letter}{row + 1}']
                cell.value = sub_header
                cell.fill = PatternFill(start_color="D9E1F2", end_color="D9E1F2", fill_type="solid")
                cell.font = Font(bold=True, size=9)
                cell.alignment = Alignment(horizontal='center', wrap_text=True)
                cell.border = border
            
            col_idx += 7
        
        # Data rows
        row = 6
        for symbol, report in sorted(reports.items()):
            if "error" in report:
                continue
            
            ws[f'A{row}'] = symbol
            ws[f'A{row}'].font = Font(bold=True)
            ws[f'A{row}'].border = border
            
            col_idx = 2
            for period in self.PERIODS:
                period_data = report.get("periods", {}).get(period, {})
                stats = period_data.get("stats", {})
                
                # Minimum
                col_letter = get_column_letter(col_idx)
                cell = ws[f'{col_letter}{row}']
                cell.value = stats.get("min")
                cell.number_format = '0.000'
                cell.border = border
                cell.alignment = Alignment(horizontal='right')
                
                # Maximum
                col_letter = get_column_letter(col_idx + 1)
                cell = ws[f'{col_letter}{row}']
                cell.value = stats.get("max")
                cell.number_format = '0.000'
                cell.border = border
                cell.alignment = Alignment(horizontal='right')
                
                # Mean
                col_letter = get_column_letter(col_idx + 2)
                cell = ws[f'{col_letter}{row}']
                cell.value = stats.get("mean")
                cell.number_format = '0.000'
                cell.border = border
                cell.alignment = Alignment(horizontal='right')
                
                # Standard Deviation
                col_letter = get_column_letter(col_idx + 3)
                cell = ws[f'{col_letter}{row}']
                cell.value = stats.get("std")
                cell.number_format = '0.000'
                cell.border = border
                cell.alignment = Alignment(horizontal='right')
                
                # Mean - Std
                col_letter = get_column_letter(col_idx + 4)
                cell = ws[f'{col_letter}{row}']
                cell.value = stats.get("mean_minus_std")
                cell.number_format = '0.000'
                cell.border = border
                cell.alignment = Alignment(horizontal='right')
                
                # Latest Quote
                col_letter = get_column_letter(col_idx + 5)
                cell = ws[f'{col_letter}{row}']
                cell.value = period_data.get("latest_quote")
                cell.number_format = '0.000'
                cell.border = border
                cell.alignment = Alignment(horizontal='right')
                fill_color = "C6EFCE" if period_data.get("latest_deviation_from_mean", 0) >= 0 else "FFC7CE"
                cell.fill = PatternFill(start_color=fill_color, end_color=fill_color, fill_type="solid")
                
                # Deviation from Mean
                col_letter = get_column_letter(col_idx + 6)
                cell = ws[f'{col_letter}{row}']
                cell.value = period_data.get("latest_deviation_from_mean")
                cell.number_format = '0.000'
                cell.border = border
                cell.alignment = Alignment(horizontal='right')
                
                col_idx += 7
            
            row += 1
        
        # Add AutoFilter to the summary sheet
        last_col = get_column_letter(1 + len(self.PERIODS) * 7)
        ws.auto_filter.ref = f"A4:{last_col}{row - 1}"
    
    def create_detailed_sheet(self, symbol: str, report: Dict):
        """
        Create a detailed analysis sheet for a single cryptocurrency.
        
        Args:
            symbol: Cryptocurrency symbol
            report: Analysis report for the cryptocurrency
        """
        ws = self.workbook.create_sheet(symbol)
        
        header_fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
        header_font = Font(bold=True, color="FFFFFF", size=11)
        border = Border(
            left=Side(style='thin'),
            right=Side(style='thin'),
            top=Side(style='thin'),
            bottom=Side(style='thin')
        )
        
        # Title
        ws['A1'] = f"Análise Detalhada: {symbol}"
        ws['A1'].font = Font(bold=True, size=14)
        ws.merge_cells('A1:D1')
        
        # Date range
        date_range = report.get("date_range", {})
        ws['A3'] = "Período de Dados:"
        ws['B3'] = f"{date_range.get('start', 'N/A')} até {date_range.get('end', 'N/A')}"
        ws['A4'] = "Total de Pontos de Dados:"
        ws['B4'] = report.get("data_points", 0)
        
        # Period analysis
        row = 6
        for period in self.PERIODS:
            period_display = self.PERIOD_DISPLAY[period]
            period_data = report.get("periods", {}).get(period, {})
            stats = period_data.get("stats", {})
            
            # Period header
            ws[f'A{row}'] = period_display
            ws[f'A{row}'].font = Font(bold=True, size=12, color="FFFFFF")
            ws[f'A{row}'].fill = PatternFill(start_color="70AD47", end_color="70AD47", fill_type="solid")
            ws.merge_cells(f'A{row}:B{row}')
            row += 1
            
            # Statistics
            metrics = [
                ("Mínimo", stats.get("min")),
                ("Máximo", stats.get("max")),
                ("Média", stats.get("mean")),
                ("Desvio Padrão", stats.get("std")),
                ("Média - Desvio Padrão", stats.get("mean_minus_std")),
                ("Última Cotação", period_data.get("latest_quote")),
                ("Desvio da Última Cotação à Média", period_data.get("latest_deviation_from_mean")),
                ("Desvio da Última Cotação à Média-Desvio", period_data.get("latest_deviation_from_mean_minus_std")),
                ("Total de Pontos", stats.get("count")),
            ]
            
            for metric_name, value in metrics:
                ws[f'A{row}'] = metric_name
                ws[f'A{row}'].font = Font(bold=True)
                ws[f'A{row}'].border = border
                
                ws[f'B{row}'] = value
                ws[f'B{row}'].number_format = '0.00000000'
                ws[f'B{row}'].border = border
                
                row += 1
            
            row += 1  # Space between periods
        
        # Set column widths
        ws.column_dimensions['A'].width = 35
        ws.column_dimensions['B'].width = 20
    
    def save(self):
        """Save the workbook to file."""
        import os
        os.makedirs(os.path.dirname(self.filename) or ".", exist_ok=True)
        self.workbook.save(self.filename)
        print(f"Excel report saved to: {self.filename}")
    
    def generate_report(self, reports: Dict[str, Dict]):
        """
        Generate complete Excel report.
        
        Args:
            reports: Dictionary with analysis reports from StatisticalAnalyzer
        """
        # Create summary sheet
        self.create_summary_sheet(reports)
        
        # Create detailed sheets for each cryptocurrency
        for symbol, report in sorted(reports.items()):
            if "error" not in report:
                self.create_detailed_sheet(symbol, report)
        
        # Save the workbook
        self.save()
