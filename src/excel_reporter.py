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
    
    NUMBER_FORMAT_DECIMAL = '#,##0.00'
    PERIODS = ["12_months", "6_months", "3_months", "1_month"]
    PERIOD_DISPLAY = {
        "12_months": "12 Meses",
        "6_months": "6 Meses",
        "3_months": "3 Meses",
        "1_month": "1 Mês",
    }
    
    def __init__(self, filename: str = "reports/AnaliseCrypto.xlsx"):
        """
        Initialize the Excel reporter.
        
        Args:
            filename: Output Excel file path
        """
        self.filename = filename
        self.workbook = openpyxl.Workbook()
        self.workbook.remove(self.workbook.active)  # Remove default sheet
    
    def _setup_column_widths(self, ws):
        """Set up column widths for the summary sheet."""
        ws.column_dimensions['A'].width = 3.29  # Favorite column (23 pixels)
        ws.column_dimensions['B'].width = 8.29  # Symbol column (58 pixels)
        ws.column_dimensions['C'].width = 10  # Latest Quote column
        ws.column_dimensions['D'].width = 10  # Second Latest Quote column
        for i, period in enumerate(self.PERIODS):
            col_offset = i * 9  # 9 columns per period
            for j in range(9):
                col_letter = get_column_letter(5 + col_offset + j)
                ws.column_dimensions[col_letter].width = 10
    
    def _create_title_rows(self, ws):
        """Create title and date rows."""
        ws['A1'] = "Análise de Criptomoedas em EUR"
        ws['A1'].font = Font(bold=True, size=14)
        ws.merge_cells('A1:Z1')
        
        ws['A2'] = f"Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}"
        ws['A2'].font = Font(size=10, italic=True)
    
    def _create_period_headers(self, ws, row: int, col_idx: int, period: str, header_fill, header_font, border):
        """Create headers for a specific period."""
        period_display = self.PERIOD_DISPLAY[period]
        
        # Merge cells for period header
        start_col = get_column_letter(col_idx)
        end_col = get_column_letter(col_idx + 8)
        ws.merge_cells(f'{start_col}{row}:{end_col}{row}')
        
        cell = ws[f'{start_col}{row}']
        cell.value = period_display
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal='center')
        
        # Sub-headers
        sub_headers = ["Mínimo", "Máximo", "Média", "Desvio", "Média-Desvio", 
                      "Últ. Dif. Média %", "Últ. Dif. M-D %", 
                      "Penúlt. Dif. Média %", "Penúlt. Dif. M-D %"]
        for j, sub_header in enumerate(sub_headers):
            col_letter = get_column_letter(col_idx + j)
            cell = ws[f'{col_letter}{row + 1}']
            cell.value = sub_header
            cell.fill = PatternFill(start_color="D9E1F2", end_color="D9E1F2", fill_type="solid")
            cell.font = Font(bold=True, size=9)
            cell.alignment = Alignment(horizontal='center', wrap_text=True)
            cell.border = border
    
    def _write_symbol_row(self, ws, row: int, symbol: str, report: Dict, favorites: List[str], border):
        """Write data for a single cryptocurrency symbol."""
        # Favorite marker
        ws[f'A{row}'] = "X" if symbol in favorites else ""
        ws[f'A{row}'].font = Font(bold=True, size=12)
        ws[f'A{row}'].border = border
        ws[f'A{row}'].alignment = Alignment(horizontal='center')
        if symbol in favorites:
            ws[f'A{row}'].fill = PatternFill(start_color="FFD700", end_color="FFD700", fill_type="solid")
        
        # Symbol
        ws[f'B{row}'] = symbol
        ws[f'B{row}'].font = Font(bold=True)
        ws[f'B{row}'].border = border
        
        # Latest and second latest quotes
        latest_quote = report.get("periods", {}).get("12_months", {}).get("latest_quote")
        ws[f'C{row}'] = latest_quote
        ws[f'C{row}'].number_format = self.NUMBER_FORMAT_DECIMAL
        ws[f'C{row}'].border = border
        ws[f'C{row}'].alignment = Alignment(horizontal='right')
        ws[f'C{row}'].font = Font(bold=True)
        
        second_latest_quote = report.get("periods", {}).get("12_months", {}).get("second_latest_quote")
        ws[f'D{row}'] = second_latest_quote
        ws[f'D{row}'].number_format = self.NUMBER_FORMAT_DECIMAL
        ws[f'D{row}'].border = border
        ws[f'D{row}'].alignment = Alignment(horizontal='right')
        ws[f'D{row}'].font = Font(bold=True)
    
    def _write_period_stats(self, ws, row: int, col_idx: int, period_data: Dict, border):
        """Write statistics for a specific period."""
        stats = period_data.get("stats", {})
        
        # Minimum
        col_letter = get_column_letter(col_idx)
        ws[f'{col_letter}{row}'].value = stats.get("min")
        ws[f'{col_letter}{row}'].number_format = self.NUMBER_FORMAT_DECIMAL
        ws[f'{col_letter}{row}'].border = border
        ws[f'{col_letter}{row}'].alignment = Alignment(horizontal='right')
        
        # Maximum
        col_letter = get_column_letter(col_idx + 1)
        ws[f'{col_letter}{row}'].value = stats.get("max")
        ws[f'{col_letter}{row}'].number_format = self.NUMBER_FORMAT_DECIMAL
        ws[f'{col_letter}{row}'].border = border
        ws[f'{col_letter}{row}'].alignment = Alignment(horizontal='right')
        
        # Mean (use actual calculated value, not formula)
        mean_col = get_column_letter(col_idx + 2)
        ws[f'{mean_col}{row}'].value = stats.get("mean")
        ws[f'{mean_col}{row}'].number_format = self.NUMBER_FORMAT_DECIMAL
        ws[f'{mean_col}{row}'].border = border
        ws[f'{mean_col}{row}'].alignment = Alignment(horizontal='right')
        
        # Standard deviation
        col_letter = get_column_letter(col_idx + 3)
        ws[f'{col_letter}{row}'].value = stats.get("std")
        ws[f'{col_letter}{row}'].number_format = self.NUMBER_FORMAT_DECIMAL
        ws[f'{col_letter}{row}'].border = border
        ws[f'{col_letter}{row}'].alignment = Alignment(horizontal='right')
        
        # Mean - Std formula
        mean_std_col = get_column_letter(col_idx + 4)
        std_col = get_column_letter(col_idx + 3)
        ws[f'{mean_std_col}{row}'].value = f"={mean_col}{row}-{std_col}{row}"
        ws[f'{mean_std_col}{row}'].number_format = self.NUMBER_FORMAT_DECIMAL
        ws[f'{mean_std_col}{row}'].border = border
        ws[f'{mean_std_col}{row}'].alignment = Alignment(horizontal='right')
        
        # Deviation formulas with conditional formatting
        self._write_deviation_formulas(ws, row, col_idx, period_data, border)
    
    def _write_deviation_formulas(self, ws, row: int, col_idx: int, period_data: Dict, border):
        """Write deviation formulas with conditional formatting."""
        mean_col = get_column_letter(col_idx + 2)
        mean_std_col = get_column_letter(col_idx + 4)
        
        # Latest deviation from mean
        col_letter = get_column_letter(col_idx + 5)
        ws[f'{col_letter}{row}'].value = f"=(C{row}-{mean_col}{row})/{mean_col}{row}"
        ws[f'{col_letter}{row}'].number_format = '0.00%'
        ws[f'{col_letter}{row}'].border = border
        ws[f'{col_letter}{row}'].alignment = Alignment(horizontal='right')
        dev_mean_pct = period_data.get("latest_deviation_from_mean_pct")
        fill_color = "C6EFCE" if dev_mean_pct and dev_mean_pct >= 0 else "FFC7CE"
        ws[f'{col_letter}{row}'].fill = PatternFill(start_color=fill_color, end_color=fill_color, fill_type="solid")
        
        # Latest deviation from mean-std
        col_letter = get_column_letter(col_idx + 6)
        ws[f'{col_letter}{row}'].value = f"=(C{row}-{mean_std_col}{row})/{mean_std_col}{row}"
        ws[f'{col_letter}{row}'].number_format = '0.00%'
        ws[f'{col_letter}{row}'].border = border
        ws[f'{col_letter}{row}'].alignment = Alignment(horizontal='right')
        dev_mean_std_pct = period_data.get("latest_deviation_from_mean_minus_std_pct")
        fill_color = "C6EFCE" if dev_mean_std_pct and dev_mean_std_pct >= 0 else "FFC7CE"
        ws[f'{col_letter}{row}'].fill = PatternFill(start_color=fill_color, end_color=fill_color, fill_type="solid")
        
        # Second latest deviation from mean
        col_letter = get_column_letter(col_idx + 7)
        ws[f'{col_letter}{row}'].value = f"=(D{row}-{mean_col}{row})/{mean_col}{row}"
        ws[f'{col_letter}{row}'].number_format = '0.00%'
        ws[f'{col_letter}{row}'].border = border
        ws[f'{col_letter}{row}'].alignment = Alignment(horizontal='right')
        second_dev_mean_pct = period_data.get("second_deviation_from_mean_pct")
        fill_color = "C6EFCE" if second_dev_mean_pct and second_dev_mean_pct >= 0 else "FFC7CE"
        ws[f'{col_letter}{row}'].fill = PatternFill(start_color=fill_color, end_color=fill_color, fill_type="solid")
        
        # Second latest deviation from mean-std
        col_letter = get_column_letter(col_idx + 8)
        ws[f'{col_letter}{row}'].value = f"=(D{row}-{mean_std_col}{row})/{mean_std_col}{row}"
        ws[f'{col_letter}{row}'].number_format = '0.00%'
        ws[f'{col_letter}{row}'].border = border
        ws[f'{col_letter}{row}'].alignment = Alignment(horizontal='right')
        second_dev_mean_std_pct = period_data.get("second_deviation_from_mean_minus_std_pct")
        fill_color = "C6EFCE" if second_dev_mean_std_pct and second_dev_mean_std_pct >= 0 else "FFC7CE"
        ws[f'{col_letter}{row}'].fill = PatternFill(start_color=fill_color, end_color=fill_color, fill_type="solid")
    
    def create_summary_sheet(self, reports: Dict[str, Dict], market_caps: Dict[str, float] = None, favorites: List[str] = None):
        """
        Create a summary sheet with all cryptocurrencies and periods.
        
        Args:
            reports: Dictionary with analysis reports from StatisticalAnalyzer
            market_caps: Dictionary with market cap values for sorting
            favorites: List of favorite cryptocurrency symbols
        """
        ws = self.workbook.create_sheet(title="Resumo")
        
        # Setup basic structure
        self._setup_column_widths(ws)
        self._create_title_rows(ws)
        
        # Style definitions
        header_fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
        header_font = Font(color="FFFFFF", bold=True)
        border = Border(
            left=Side(style='thin'),
            right=Side(style='thin'),
            top=Side(style='thin'),
            bottom=Side(style='thin')
        )
        
        # Create column headers
        ws['A4'] = "Fav"
        ws['B4'] = "Símbolo"
        ws['C4'] = "Última Cotação"
        ws['D4'] = "Penúltima Cotação"
        
        for col in ['A4', 'B4', 'C4', 'D4']:
            ws[col].fill = header_fill
            ws[col].font = header_font
            ws[col].border = border
            ws[col].alignment = Alignment(horizontal='center', wrap_text=True)
        
        # Create period headers
        col_idx = 5
        for period in self.PERIODS:
            self._create_period_headers(ws, 4, col_idx, period, header_fill, header_font, border)
            col_idx += 9
        
        # Sort symbols by market cap
        symbols = list(reports.keys())
        if market_caps:
            symbols = sorted(symbols, key=lambda s: market_caps.get(s, 0), reverse=True)
        else:
            symbols.sort()
        
        # Write data rows
        row = 6
        favorites = favorites or []
        for symbol in symbols:
            report = reports[symbol]
            
            # Write symbol and quotes
            self._write_symbol_row(ws, row, symbol, report, favorites, border)
            
            # Write period statistics
            col_idx = 5
            for period in self.PERIODS:
                period_data = report.get("periods", {}).get(period, {})
                if period_data:
                    self._write_period_stats(ws, row, col_idx, period_data, border)
                col_idx += 9
            
            row += 1
        
        # Freeze panes
        ws.freeze_panes = ws['E6']
    
    def create_detail_sheet(self, symbol: str, report: Dict):
        """
        Create a detailed analysis sheet for a single cryptocurrency.
        
        Args:
            symbol: Cryptocurrency symbol
            report: Analysis report for the cryptocurrency
        """
        ws = self.workbook.create_sheet(symbol)
        
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
    
    def generate_report(self, reports: Dict[str, Dict], market_caps: Dict[str, float] = None, favorites: List[str] = None):
        """
        Generate complete Excel report.
        
        Args:
            reports: Dictionary with analysis reports from StatisticalAnalyzer
            market_caps: Dictionary with market cap values for sorting
            favorites: List of favorite cryptocurrency symbols
        """
        # Create summary sheet
        self.create_summary_sheet(reports, market_caps, favorites)
        
        # Create detailed sheets for each cryptocurrency
        for symbol, report in sorted(reports.items()):
            if "error" not in report:
                self.create_detail_sheet(symbol, report)
        
        # Save the workbook
        self.save()
