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
    PERIODS = ["1_month", "3_months", "6_months", "12_months"]
    PERIOD_DISPLAY = {
        "12_months": "12M",
        "6_months": "6M",
        "3_months": "3M",
        "1_month": "1M",
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
        ws.column_dimensions['C'].width = 5  # Period column
        ws.column_dimensions['D'].width = 10  # Latest Quote column
        ws.column_dimensions['E'].width = 10  # Second Latest Quote column
        # Statistics columns
        for i in range(9):
            col_letter = get_column_letter(6 + i)
            ws.column_dimensions[col_letter].width = 10
    
    def _create_title_rows(self, ws):
        """Create title and date rows."""
        ws['A1'] = "Análise de Criptomoedas em EUR"
        ws['A1'].font = Font(bold=True, size=14)
        ws.merge_cells('A1:O1')
        
        ws['A2'] = f"Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}"
        ws['A2'].font = Font(size=10, italic=True)
    
    def _create_headers(self, ws, row: int, header_fill, header_font, border):
        """Create column headers for the new row-based layout."""
        headers = ["Fav", "Símbolo", "Período", "Última Cotação", "Penúltima Cotação",
                  "Mínimo", "Máximo", "Média", "Desvio", "Média-Desvio",
                  "Últ. Dif. Média %", "Últ. Dif. M-D %",
                  "Penúlt. Dif. Média %", "Penúlt. Dif. M-D %"]
        
        for i, header in enumerate(headers):
            col_letter = get_column_letter(i + 1)
            cell = ws[f'{col_letter}{row}']
            cell.value = header
            cell.fill = header_fill
            cell.font = header_font
            cell.border = border
            cell.alignment = Alignment(horizontal='center', wrap_text=True)
    
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
    def _write_symbol_period_row(self, ws, row: int, symbol: str, period: str, report: Dict, 
                                  favorites: List[str], border, is_first_period: bool):
        """Write data for a single cryptocurrency symbol and period combination."""
        period_data = report.get("periods", {}).get(period, {})
        
        # Favorite marker (only on first period row)
        if is_first_period:
            ws[f'A{row}'] = "X" if symbol in favorites else ""
            ws[f'A{row}'].font = Font(bold=True, size=12)
            if symbol in favorites:
                ws[f'A{row}'].fill = PatternFill(start_color="FFD700", end_color="FFD700", fill_type="solid")
        ws[f'A{row}'].border = border
        ws[f'A{row}'].alignment = Alignment(horizontal='center')
        
        # Symbol (only on first period row)
        if is_first_period:
            ws[f'B{row}'] = symbol
            ws[f'B{row}'].font = Font(bold=True)
        ws[f'B{row}'].border = border
        
        # Period
        ws[f'C{row}'] = self.PERIOD_DISPLAY[period]
        ws[f'C{row}'].font = Font(bold=True, size=9)
        ws[f'C{row}'].border = border
        ws[f'C{row}'].alignment = Alignment(horizontal='center')
        
        # Latest quote
        latest_quote = period_data.get("latest_quote")
        ws[f'D{row}'] = latest_quote
        ws[f'D{row}'].number_format = self.NUMBER_FORMAT_DECIMAL
    def _write_period_stats(self, ws, row: int, period_data: Dict, border):
        """Write statistics for a specific period in the new row layout."""
        stats = period_data.get("stats", {})
        
        # Minimum (column F)
        ws[f'F{row}'].value = stats.get("min")
        ws[f'F{row}'].number_format = self.NUMBER_FORMAT_DECIMAL
        ws[f'F{row}'].border = border
        ws[f'F{row}'].alignment = Alignment(horizontal='right')
        
        # Maximum (column G)
        ws[f'G{row}'].value = stats.get("max")
        ws[f'G{row}'].number_format = self.NUMBER_FORMAT_DECIMAL
        ws[f'G{row}'].border = border
        ws[f'G{row}'].alignment = Alignment(horizontal='right')
        
        # Mean (column H)
        ws[f'H{row}'].value = stats.get("mean")
        ws[f'H{row}'].number_format = self.NUMBER_FORMAT_DECIMAL
        ws[f'H{row}'].border = border
        ws[f'H{row}'].alignment = Alignment(horizontal='right')
        
        # Standard deviation (column I)
        ws[f'I{row}'].value = stats.get("std")
        ws[f'I{row}'].number_format = self.NUMBER_FORMAT_DECIMAL
        ws[f'I{row}'].border = border
        ws[f'I{row}'].alignment = Alignment(horizontal='right')
        
        # Mean - Std formula (column J)
        ws[f'J{row}'].value = f"=H{row}-I{row}"
    def _write_deviation_formulas(self, ws, row: int, period_data: Dict, border):
        """Write deviation formulas with conditional formatting in the new row layout."""
        # Latest deviation from mean (column K)
        ws[f'K{row}'].value = f"=(D{row}-H{row})/H{row}"
        ws[f'K{row}'].number_format = '0.00%'
        ws[f'K{row}'].border = border
        ws[f'K{row}'].alignment = Alignment(horizontal='right')
        dev_mean_pct = period_data.get("latest_deviation_from_mean_pct")
        fill_color = "C6EFCE" if dev_mean_pct and dev_mean_pct >= 0 else "FFC7CE"
        ws[f'K{row}'].fill = PatternFill(start_color=fill_color, end_color=fill_color, fill_type="solid")
        
        # Latest deviation from mean-std (column L)
        ws[f'L{row}'].value = f"=(D{row}-J{row})/J{row}"
        ws[f'L{row}'].number_format = '0.00%'
        ws[f'L{row}'].border = border
        ws[f'L{row}'].alignment = Alignment(horizontal='right')
        dev_mean_std_pct = period_data.get("latest_deviation_from_mean_minus_std_pct")
        fill_color = "C6EFCE" if dev_mean_std_pct and dev_mean_std_pct >= 0 else "FFC7CE"
        ws[f'L{row}'].fill = PatternFill(start_color=fill_color, end_color=fill_color, fill_type="solid")
        
        # Second latest deviation from mean (column M)
        ws[f'M{row}'].value = f"=(E{row}-H{row})/H{row}"
        ws[f'M{row}'].number_format = '0.00%'
        ws[f'M{row}'].border = border
        ws[f'M{row}'].alignment = Alignment(horizontal='right')
        second_dev_mean_pct = period_data.get("second_deviation_from_mean_pct")
        fill_color = "C6EFCE" if second_dev_mean_pct and second_dev_mean_pct >= 0 else "FFC7CE"
        ws[f'M{row}'].fill = PatternFill(start_color=fill_color, end_color=fill_color, fill_type="solid")
        
        # Second latest deviation from mean-std (column N)
        ws[f'N{row}'].value = f"=(E{row}-J{row})/J{row}"
        ws[f'N{row}'].number_format = '0.00%'
        ws[f'N{row}'].border = border
        ws[f'N{row}'].alignment = Alignment(horizontal='right')
        second_dev_mean_std_pct = period_data.get("second_deviation_from_mean_minus_std_pct")
        fill_color = "C6EFCE" if second_dev_mean_std_pct and second_dev_mean_std_pct >= 0 else "FFC7CE"
        ws[f'N{row}'].fill = PatternFill(start_color=fill_color, end_color=fill_color, fill_type="solid")
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
    def create_summary_sheet(self, reports: Dict[str, Dict], market_caps: Dict[str, float] = None, favorites: List[str] = None):
        """
        Create a summary sheet with all cryptocurrencies and periods.
        Each cryptocurrency has 4 rows (one per period).
        
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
        header_font = Font(color="FFFFFF", bold=True, size=9)
        border = Border(
            left=Side(style='thin'),
            right=Side(style='thin'),
            top=Side(style='thin'),
            bottom=Side(style='thin')
        )
        
        # Create column headers (row 4)
        self._create_headers(ws, 4, header_fill, header_font, border)
        
        # Sort symbols by market cap
        symbols = list(reports.keys())
        if market_caps:
            symbols = sorted(symbols, key=lambda s: market_caps.get(s, 0), reverse=True)
        else:
            symbols.sort()
        
        # Write data rows - 4 rows per symbol (one for each period)
        row = 5
        favorites = favorites or []
        for symbol in symbols:
            report = reports[symbol]
            
            # Write 4 rows for this symbol (one per period)
            for period_idx, period in enumerate(self.PERIODS):
                is_first_period = (period_idx == 0)
                
                # Write symbol, period, and quotes
                self._write_symbol_period_row(ws, row, symbol, period, report, favorites, border, is_first_period)
                
                # Write period statistics
                period_data = report.get("periods", {}).get(period, {})
                if period_data:
                    self._write_period_stats(ws, row, period_data, border)
                
                row += 1
        
        # Add auto filter to the table
        ws.auto_filter.ref = f"A4:N{row - 1}"
        
        # Freeze panes (freeze first 3 columns and header row)
        ws.freeze_panes = ws['D5']
    
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
