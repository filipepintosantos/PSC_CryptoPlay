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
        ws.column_dimensions['A'].width = 3  # Favorite column
        ws.column_dimensions['B'].width = 7  # Symbol column
        ws.column_dimensions['C'].width = 9  # Latest Quote column
        ws.column_dimensions['D'].width = 9  # Second Latest Quote column
        ws.column_dimensions['E'].width = 5  # Period column
        # Statistics columns (F to U = 16 columns) - reduced width
        for i in range(16):
            col_letter = get_column_letter(6 + i)
            ws.column_dimensions[col_letter].width = 8.5
        # Volatility columns (V to Z = 5 columns)
        for i in range(5):
            col_letter = get_column_letter(22 + i)  # 22 = V
            ws.column_dimensions[col_letter].width = 7
    
    def _create_title_rows(self, ws):
        """Create title and date rows."""
        ws['A1'] = "Análise de Criptomoedas em EUR"
        ws['A1'].font = Font(bold=True, size=14)
        ws.merge_cells('A1:Z1')
        ws.row_dimensions[1].height = 25
        
        ws['A2'] = f"Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}"
        ws['A2'].font = Font(size=10, italic=True)
        ws.row_dimensions[2].height = 18
    
    def _create_headers(self, ws, row: int, header_fill, header_font, border):
        """Create column headers for the new row-based layout."""
        headers = ["Fav", "Symbol", "Last", "2nd Last", "Period",
                  "MIN", "MAX", "AVG", "STD", "AVG-STD",
                  "Last-AVG%", "Last-A-S%", "2nd-AVG%", "2nd-A-S%",
                  "MEDIAN", "MAD", "MED-MAD",
                  "Last-MED%", "Last-M-M%", "2nd-MED%", "2nd-M-M%",
                  "Vol+5%", "Vol+10%", "Vol-5%", "Vol-10%", "VolScore"]
        
        for i, header in enumerate(headers):
            col_letter = get_column_letter(i + 1)
            cell = ws[f'{col_letter}{row}']
            cell.value = header
            cell.fill = header_fill
            cell.font = header_font
            cell.border = border
            cell.alignment = Alignment(horizontal='center', vertical='top', wrap_text=True)
    
    def _write_symbol_period_row(self, ws, row: int, symbol: str, period: str, report: Dict, 
                                  favorites: List[str], border):
        """Write data for a single cryptocurrency symbol and period combination."""
        period_data = report.get("periods", {}).get(period, {})
        
        # Favorite marker (in all rows)
        ws[f'A{row}'] = "X" if symbol in favorites else ""
        ws[f'A{row}'].font = Font(bold=True, size=12)
        if symbol in favorites:
            ws[f'A{row}'].fill = PatternFill(start_color="FFD700", end_color="FFD700", fill_type="solid")
        ws[f'A{row}'].border = border
        ws[f'A{row}'].alignment = Alignment(horizontal='center')
        
        # Symbol (in all rows)
        ws[f'B{row}'] = symbol
        ws[f'B{row}'].font = Font(bold=True)
        ws[f'B{row}'].border = border
        
        # Latest quote (column C)
        latest_quote = period_data.get("latest_quote")
        ws[f'C{row}'] = latest_quote
        ws[f'C{row}'].number_format = self.NUMBER_FORMAT_DECIMAL
        ws[f'C{row}'].border = border
        ws[f'C{row}'].alignment = Alignment(horizontal='right')
        ws[f'C{row}'].font = Font(bold=True, size=9)
        
        # Second latest quote (column D)
        second_latest_quote = period_data.get("second_latest_quote")
        ws[f'D{row}'] = second_latest_quote
        ws[f'D{row}'].number_format = self.NUMBER_FORMAT_DECIMAL
        ws[f'D{row}'].border = border
        ws[f'D{row}'].alignment = Alignment(horizontal='right')
        ws[f'D{row}'].font = Font(bold=True, size=9)
        
        # Period (column E)
        ws[f'E{row}'] = self.PERIOD_DISPLAY[period]
        ws[f'E{row}'].font = Font(bold=True, size=9)
        ws[f'E{row}'].border = border
        ws[f'E{row}'].alignment = Alignment(horizontal='center')
    def _write_period_stats(self, ws, row: int, period_data: Dict, border):
        """Write statistics for a specific period in the new row layout."""
        stats = period_data.get("stats", {})
        small_font = Font(size=9)
        
        # Minimum (column F)
        ws[f'F{row}'].value = stats.get("min")
        ws[f'F{row}'].number_format = self.NUMBER_FORMAT_DECIMAL
        ws[f'F{row}'].border = border
        ws[f'F{row}'].alignment = Alignment(horizontal='right')
        ws[f'F{row}'].font = small_font
        
        # Maximum (column G)
        ws[f'G{row}'].value = stats.get("max")
        ws[f'G{row}'].number_format = self.NUMBER_FORMAT_DECIMAL
        ws[f'G{row}'].border = border
        ws[f'G{row}'].alignment = Alignment(horizontal='right')
        ws[f'G{row}'].font = small_font
        
        # Mean (column H)
        ws[f'H{row}'].value = stats.get("mean")
        ws[f'H{row}'].number_format = self.NUMBER_FORMAT_DECIMAL
        ws[f'H{row}'].border = border
        ws[f'H{row}'].alignment = Alignment(horizontal='right')
        ws[f'H{row}'].font = small_font
        
        # Standard deviation (column I)
        ws[f'I{row}'].value = stats.get("std")
        ws[f'I{row}'].number_format = self.NUMBER_FORMAT_DECIMAL
        ws[f'I{row}'].border = border
        ws[f'I{row}'].alignment = Alignment(horizontal='right')
        ws[f'I{row}'].font = small_font
        
        # Mean - Std formula (column J)
        ws[f'J{row}'].value = f"=H{row}-I{row}"
        ws[f'J{row}'].number_format = self.NUMBER_FORMAT_DECIMAL
        ws[f'J{row}'].border = border
        ws[f'J{row}'].alignment = Alignment(horizontal='right')
        ws[f'J{row}'].font = small_font
        
        # Median (column O)
        ws[f'O{row}'].value = stats.get("median")
        ws[f'O{row}'].number_format = self.NUMBER_FORMAT_DECIMAL
        ws[f'O{row}'].border = border
        ws[f'O{row}'].alignment = Alignment(horizontal='right')
        ws[f'O{row}'].font = small_font
        
        # MAD - Median Absolute Deviation (column P)
        ws[f'P{row}'].value = stats.get("mad")
        ws[f'P{row}'].number_format = self.NUMBER_FORMAT_DECIMAL
        ws[f'P{row}'].border = border
        ws[f'P{row}'].alignment = Alignment(horizontal='right')
        ws[f'P{row}'].font = small_font
        
        # Median - MAD formula (column Q)
        ws[f'Q{row}'].value = f"=O{row}-P{row}"
        ws[f'Q{row}'].number_format = self.NUMBER_FORMAT_DECIMAL
        ws[f'Q{row}'].border = border
        ws[f'Q{row}'].alignment = Alignment(horizontal='right')
        ws[f'Q{row}'].font = small_font
        
        # Deviation formulas with conditional formatting
        self._write_deviation_formulas(ws, row, period_data, border)
    
    def _write_deviation_formulas(self, ws, row: int, period_data: Dict, border):
        """Write deviation formulas with conditional formatting in the new row layout."""
        small_font = Font(size=9)
        
        # Column K: Última - Média % (uses C and H)
        ws[f'K{row}'].value = f"=(C{row}-H{row})/H{row}"
        ws[f'K{row}'].number_format = '0.00%'
        ws[f'K{row}'].border = border
        ws[f'K{row}'].alignment = Alignment(horizontal='right')
        ws[f'K{row}'].font = small_font
        dev_mean_pct = period_data.get("latest_deviation_from_mean_pct")
        fill_color = "C6EFCE" if dev_mean_pct and dev_mean_pct >= 0 else "FFC7CE"
        ws[f'K{row}'].fill = PatternFill(start_color=fill_color, end_color=fill_color, fill_type="solid")
        
        # Column L: Última - Méd-STD % (uses C and J)
        ws[f'L{row}'].value = f"=(C{row}-J{row})/J{row}"
        ws[f'L{row}'].number_format = '0.00%'
        ws[f'L{row}'].border = border
        ws[f'L{row}'].alignment = Alignment(horizontal='right')
        ws[f'L{row}'].font = small_font
        dev_mean_std_pct = period_data.get("latest_deviation_from_mean_minus_std_pct")
        fill_color = "C6EFCE" if dev_mean_std_pct and dev_mean_std_pct >= 0 else "FFC7CE"
        ws[f'L{row}'].fill = PatternFill(start_color=fill_color, end_color=fill_color, fill_type="solid")
        
        # Column M: Penúltima - Média % (uses D and H)
        ws[f'M{row}'].value = f"=(D{row}-H{row})/H{row}"
        ws[f'M{row}'].number_format = '0.00%'
        ws[f'M{row}'].border = border
        ws[f'M{row}'].alignment = Alignment(horizontal='right')
        ws[f'M{row}'].font = small_font
        second_dev_mean_pct = period_data.get("second_deviation_from_mean_pct")
        fill_color = "C6EFCE" if second_dev_mean_pct and second_dev_mean_pct >= 0 else "FFC7CE"
        ws[f'M{row}'].fill = PatternFill(start_color=fill_color, end_color=fill_color, fill_type="solid")
        
        # Column N: Penúltima - Méd-STD % (uses D and J)
        ws[f'N{row}'].value = f"=(D{row}-J{row})/J{row}"
        ws[f'N{row}'].number_format = '0.00%'
        ws[f'N{row}'].border = border
        ws[f'N{row}'].alignment = Alignment(horizontal='right')
        ws[f'N{row}'].font = small_font
        second_dev_mean_std_pct = period_data.get("second_deviation_from_mean_minus_std_pct")
        fill_color = "C6EFCE" if second_dev_mean_std_pct and second_dev_mean_std_pct >= 0 else "FFC7CE"
        ws[f'N{row}'].fill = PatternFill(start_color=fill_color, end_color=fill_color, fill_type="solid")
        
        # Column R: Última - Mediana % (uses C and O)
        ws[f'R{row}'].value = f"=(C{row}-O{row})/O{row}"
        ws[f'R{row}'].number_format = '0.00%'
        ws[f'R{row}'].border = border
        ws[f'R{row}'].alignment = Alignment(horizontal='right')
        ws[f'R{row}'].font = small_font
        fill_color = "C6EFCE" if dev_mean_pct and dev_mean_pct >= 0 else "FFC7CE"  # Using mean as proxy
        ws[f'R{row}'].fill = PatternFill(start_color=fill_color, end_color=fill_color, fill_type="solid")
        
        # Column S: Última - Med-MAD % (uses C and Q)
        ws[f'S{row}'].value = f"=(C{row}-Q{row})/Q{row}"
        ws[f'S{row}'].number_format = '0.00%'
        ws[f'S{row}'].border = border
        ws[f'S{row}'].alignment = Alignment(horizontal='right')
        ws[f'S{row}'].font = small_font
        fill_color = "C6EFCE" if dev_mean_std_pct and dev_mean_std_pct >= 0 else "FFC7CE"  # Using mean-std as proxy
        ws[f'S{row}'].fill = PatternFill(start_color=fill_color, end_color=fill_color, fill_type="solid")
        
        # Column T: Penúltima - Mediana % (uses D and O)
        ws[f'T{row}'].value = f"=(D{row}-O{row})/O{row}"
        ws[f'T{row}'].number_format = '0.00%'
        ws[f'T{row}'].border = border
        ws[f'T{row}'].alignment = Alignment(horizontal='right')
        ws[f'T{row}'].font = small_font
        fill_color = "C6EFCE" if second_dev_mean_pct and second_dev_mean_pct >= 0 else "FFC7CE"  # Using mean as proxy
        ws[f'T{row}'].fill = PatternFill(start_color=fill_color, end_color=fill_color, fill_type="solid")
        
        # Column U: Penúltima - Med-MAD % (uses D and Q)
        ws[f'U{row}'].value = f"=(D{row}-Q{row})/Q{row}"
        ws[f'U{row}'].number_format = '0.00%'
        ws[f'U{row}'].border = border
        ws[f'U{row}'].alignment = Alignment(horizontal='right')
        ws[f'U{row}'].font = small_font
        fill_color = "C6EFCE" if second_dev_mean_std_pct and second_dev_mean_std_pct >= 0 else "FFC7CE"  # Using mean-std as proxy
        ws[f'U{row}'].fill = PatternFill(start_color=fill_color, end_color=fill_color, fill_type="solid")
    
    def _write_volatility_stats(self, ws, row: int, volatility_data: Dict, border):
        """Write volatility statistics for each period row."""
        if not volatility_data:
            return
        
        small_font = Font(size=9)
        
        # Column V: Vol+5% (positive oscillations >= 5%)
        ws[f'V{row}'].value = volatility_data.get('volatility_positive_5', 0)
        ws[f'V{row}'].border = border
        ws[f'V{row}'].alignment = Alignment(horizontal='center')
        ws[f'V{row}'].font = small_font
        
        # Column W: Vol+10% (positive oscillations >= 10%)
        ws[f'W{row}'].value = volatility_data.get('volatility_positive_10', 0)
        ws[f'W{row}'].border = border
        ws[f'W{row}'].alignment = Alignment(horizontal='center')
        ws[f'W{row}'].font = small_font
        
        # Column X: Vol-5% (negative oscillations <= -5%)
        ws[f'X{row}'].value = volatility_data.get('volatility_negative_5', 0)
        ws[f'X{row}'].border = border
        ws[f'X{row}'].alignment = Alignment(horizontal='center')
        ws[f'X{row}'].font = small_font
        
        # Column Y: Vol-10% (negative oscillations <= -10%)
        ws[f'Y{row}'].value = volatility_data.get('volatility_negative_10', 0)
        ws[f'Y{row}'].border = border
        ws[f'Y{row}'].alignment = Alignment(horizontal='center')
        ws[f'Y{row}'].font = small_font
        
        # Column Z: VolScore (total volatility score)
        ws[f'Z{row}'].value = volatility_data.get('volatility_score', 0)
        ws[f'Z{row}'].border = border
        ws[f'Z{row}'].alignment = Alignment(horizontal='center')
        ws[f'Z{row}'].font = Font(bold=True, size=9)
        # Color code: higher score = more volatile (orange)
        score = volatility_data.get('volatility_score', 0)
        if score > 100:
            ws[f'Z{row}'].fill = PatternFill(start_color="FFA500", end_color="FFA500", fill_type="solid")
        elif score > 50:
            ws[f'Z{row}'].fill = PatternFill(start_color="FFD700", end_color="FFD700", fill_type="solid")
    
    def create_summary_sheet(self, reports: Dict[str, Dict], market_caps: Dict[str, float] = None, favorites: List[str] = None):
        """
        Create a summary sheet with all cryptocurrencies and periods.
        Each cryptocurrency has 4 rows (one per period).
        
        Args:
            reports: Dictionary with analysis reports from StatisticalAnalyzer
            market_caps: Dictionary with market cap values for sorting (used for sorting)
            favorites: List of favorite cryptocurrency symbols (used for highlighting)
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
        ws.row_dimensions[4].height = 30  # Compact header row with top alignment
        
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
            for i, period in enumerate(self.PERIODS):
                # Write symbol, period, and quotes
                self._write_symbol_period_row(ws, row, symbol, period, report, favorites, border)
                
                # Write period statistics
                period_data = report.get("periods", {}).get(period, {})
                if period_data:
                    self._write_period_stats(ws, row, period_data, border)
                    
                    # Write volatility stats for this period
                    volatility_data = period_data.get('volatility', {})
                    self._write_volatility_stats(ws, row, volatility_data, border)
                
                row += 1
        
        # Add auto filter to the table
        ws.auto_filter.ref = f"A4:Z{row - 1}"
        
        # Freeze panes (freeze columns A-D and header row)
        ws.freeze_panes = ws['E5']
    
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
    
    def create_volatility_detail_sheet(self, volatility_results: Dict[str, Dict]):
        """
        Create a detailed volatility analysis sheet with all windows and thresholds.
        
        Args:
            volatility_results: Dictionary with volatility analysis from VolatilityAnalyzer.analyze_all_symbols()
        """
        ws = self.workbook.create_sheet(title="Volatility Detail")
        
        # Define styles
        header_fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
        header_font = Font(bold=True, color="FFFFFF", size=10)
        border = Border(
            left=Side(style='thin'),
            right=Side(style='thin'),
            top=Side(style='thin'),
            bottom=Side(style='thin')
        )
        
        # Title
        ws['A1'] = "Análise Detalhada de Volatilidade"
        ws['A1'].font = Font(bold=True, size=14)
        ws.merge_cells('A1:J1')
        ws.row_dimensions[1].height = 25
        
        # Headers
        headers = ["Symbol", "Window", "+5%", "+10%", "+15%", "+20%", "-5%", "-10%", "-15%", "-20%"]
        for i, header in enumerate(headers, start=1):
            cell = ws.cell(row=3, column=i)
            cell.value = header
            cell.fill = header_fill
            cell.font = header_font
            cell.border = border
            cell.alignment = Alignment(horizontal='center', vertical='center')
        
        # Column widths
        ws.column_dimensions['A'].width = 10  # Symbol
        ws.column_dimensions['B'].width = 8   # Window
        for col in ['C', 'D', 'E', 'F', 'G', 'H', 'I', 'J']:
            ws.column_dimensions[col].width = 7
        
        # Write data
        row = 4
        for symbol in sorted(volatility_results.keys()):
            windows = volatility_results[symbol]
            
            # Write data for each window (only short windows: 24h, 72h, 7d)
            for window_name in ["24h", "72h", "7d"]:
                if window_name in windows:
                    events = windows[window_name]
                    
                    # Symbol
                    ws.cell(row=row, column=1).value = symbol
                    ws.cell(row=row, column=1).font = Font(bold=True)
                    ws.cell(row=row, column=1).border = border
                    ws.cell(row=row, column=1).alignment = Alignment(horizontal='center')
                    
                    # Window
                    ws.cell(row=row, column=2).value = window_name
                    ws.cell(row=row, column=2).border = border
                    ws.cell(row=row, column=2).alignment = Alignment(horizontal='center')
                    
                    # Positive thresholds
                    col = 3
                    for threshold in [5, 10, 15, 20]:
                        cell = ws.cell(row=row, column=col)
                        cell.value = events.get(f'positive_{threshold}', 0)
                        cell.border = border
                        cell.alignment = Alignment(horizontal='center')
                        col += 1
                    
                    # Negative thresholds
                    for threshold in [5, 10, 15, 20]:
                        cell = ws.cell(row=row, column=col)
                        cell.value = events.get(f'negative_{threshold}', 0)
                        cell.border = border
                        cell.alignment = Alignment(horizontal='center')
                        col += 1
                    
                    row += 1
        
        # Add auto filter
        ws.auto_filter.ref = f"A3:J{row-1}"
        
        # Freeze panes (freeze header)
        ws.freeze_panes = ws['A4']
    
    def generate_report(self, reports: Dict[str, Dict], market_caps: Dict[str, float] = None, 
                       favorites: List[str] = None, volatility_results: Dict[str, Dict] = None):
        """
        Generate complete Excel report.
        
        Args:
            reports: Dictionary with analysis reports from StatisticalAnalyzer
            market_caps: Dictionary with market cap values for sorting
            favorites: List of favorite cryptocurrency symbols
            volatility_results: Dictionary with detailed volatility analysis (optional)
        """
        # Create summary sheet
        self.create_summary_sheet(reports, market_caps, favorites)
        
        # Create volatility detail sheet if data available
        if volatility_results:
            self.create_volatility_detail_sheet(volatility_results)
        
        # Create detailed sheets for each cryptocurrency
        for symbol, report in sorted(reports.items()):
            if "error" not in report:
                self.create_detail_sheet(symbol, report)
        
        # Save the workbook
        self.save()
