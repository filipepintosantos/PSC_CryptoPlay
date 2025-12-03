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
    
    def create_summary_sheet(self, reports: Dict[str, Dict], market_caps: Dict[str, float] = None, favorites: List[str] = None):
        """
        Create a summary sheet with all cryptocurrencies and periods.
        
        Args:
            reports: Dictionary with analysis reports from StatisticalAnalyzer
            market_caps: Dictionary with market cap values for sorting
            favorites: List of favorite cryptocurrency symbols
        """
        ws = self.workbook.create_sheet("Resumo", 0)
        
        # Header styling
        header_fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
        header_font = Font(bold=True, color="FFFFFF", size=9)
        border = Border(
            left=Side(style='thin'),
            right=Side(style='thin'),
            top=Side(style='thin'),
            bottom=Side(style='thin')
        )
        
        # Set column widths (pixels converted to Excel width units)
        ws.column_dimensions['A'].width = 3.29  # Favorite column (23 pixels)
        ws.column_dimensions['B'].width = 8.29  # Symbol column (58 pixels)
        ws.column_dimensions['C'].width = 10  # Latest Quote column
        ws.column_dimensions['D'].width = 10  # Second Latest Quote column
        for i, period in enumerate(self.PERIODS):
            col_offset = i * 9  # 9 columns per period (5 stats + 4 deviations)
            for j in range(9):
                col_letter = get_column_letter(5 + col_offset + j)
                ws.column_dimensions[col_letter].width = 10
        
        # Title row
        ws['A1'] = "Análise de Criptomoedas em EUR"
        ws['A1'].font = Font(bold=True, size=14)
        ws.merge_cells('A1:Z1')
        
        # Date row
        ws['A2'] = f"Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}"
        ws['A2'].font = Font(size=10, italic=True)
        
        # Column headers
        row = 4
        ws[f'A{row}'] = "Fav"
        ws[f'A{row}'].fill = header_fill
        ws[f'A{row}'].font = header_font
        ws[f'A{row}'].alignment = Alignment(horizontal='center')
        
        ws[f'B{row}'] = "Símbolo"
        ws[f'B{row}'].fill = header_fill
        ws[f'B{row}'].font = header_font
        
        # Get dates from first report's 12_months period for headers
        latest_date = None
        second_latest_date = None
        if reports:
            first_report = next(iter(reports.values()))
            if "periods" in first_report and "12_months" in first_report["periods"]:
                latest_date = first_report["periods"]["12_months"].get("latest_date")
                second_latest_date = first_report["periods"]["12_months"].get("second_latest_date")
        
        ws[f'C{row}'] = f"Última Cotação\n{latest_date if latest_date else ''}"
        ws[f'C{row}'].fill = header_fill
        ws[f'C{row}'].font = header_font
        ws[f'C{row}'].alignment = Alignment(horizontal='center', wrap_text=True)
        ws[f'C{row+1}'] = "EUR"
        ws[f'C{row+1}'].fill = PatternFill(start_color="D9E1F2", end_color="D9E1F2", fill_type="solid")
        ws[f'C{row+1}'].font = Font(bold=True, size=9)
        ws[f'C{row+1}'].alignment = Alignment(horizontal='center')
        ws[f'C{row+1}'].border = border
        
        ws[f'D{row}'] = f"Penúltima Cotação\n{second_latest_date if second_latest_date else ''}"
        ws[f'D{row}'].fill = header_fill
        ws[f'D{row}'].font = header_font
        ws[f'D{row}'].alignment = Alignment(horizontal='center', wrap_text=True)
        ws[f'D{row+1}'] = "EUR"
        ws[f'D{row+1}'].fill = PatternFill(start_color="D9E1F2", end_color="D9E1F2", fill_type="solid")
        ws[f'D{row+1}'].font = Font(bold=True, size=9)
        ws[f'D{row+1}'].alignment = Alignment(horizontal='center')
        ws[f'D{row+1}'].border = border
        
        col_idx = 5
        for period in self.PERIODS:
            period_display = self.PERIOD_DISPLAY[period]
            
            # Merge cells for period header
            start_col = get_column_letter(col_idx)
            end_col = get_column_letter(col_idx + 8)  # 9 columns (5 stats + 4 deviations)
            ws.merge_cells(f'{start_col}{row}:{end_col}{row}')
            
            cell = ws[f'{start_col}{row}']
            cell.value = period_display
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = Alignment(horizontal='center')
            
            # Sub-headers with both latest and second-to-last deviations
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
            
            col_idx += 9
        
        # Sort by market cap (descending)
        if market_caps:
            sorted_symbols = sorted(reports.keys(), key=lambda s: market_caps.get(s, 0), reverse=True)
        else:
            sorted_symbols = sorted(reports.keys())
        
        # Data rows
        row = 6
        favorites = favorites or []
        for symbol in sorted_symbols:
            report = reports[symbol]
            if "error" in report:
                continue
            
            # Favorite marker in column A
            ws[f'A{row}'] = "X" if symbol in favorites else ""
            ws[f'A{row}'].font = Font(bold=True, size=12)
            ws[f'A{row}'].border = border
            ws[f'A{row}'].alignment = Alignment(horizontal='center')
            if symbol in favorites:
                ws[f'A{row}'].fill = PatternFill(start_color="FFD700", end_color="FFD700", fill_type="solid")
            
            # Symbol in column B
            ws[f'B{row}'] = symbol
            ws[f'B{row}'].font = Font(bold=True)
            ws[f'B{row}'].border = border
            
            # Latest Quote in column C (only once)
            latest_quote = report.get("periods", {}).get("12_months", {}).get("latest_quote")
            ws[f'C{row}'] = latest_quote
            ws[f'C{row}'].number_format = '#,##0.00'
            ws[f'C{row}'].border = border
            ws[f'C{row}'].alignment = Alignment(horizontal='right')
            ws[f'C{row}'].font = Font(bold=True)
            
            # Second Latest Quote in column D (only once) - keep as value for now
            second_latest_quote = report.get("periods", {}).get("12_months", {}).get("second_latest_quote")
            ws[f'D{row}'] = second_latest_quote
            ws[f'D{row}'].number_format = '#,##0.00'
            ws[f'D{row}'].border = border
            ws[f'D{row}'].alignment = Alignment(horizontal='right')
            ws[f'D{row}'].font = Font(bold=True)
            
            col_idx = 5
            for period in self.PERIODS:
                period_data = report.get("periods", {}).get(period, {})
                stats = period_data.get("stats", {})
                
                # Minimum
                col_letter = get_column_letter(col_idx)
                cell = ws[f'{col_letter}{row}']
                cell.value = stats.get("min")
                cell.number_format = '#,##0.00'
                cell.border = border
                cell.alignment = Alignment(horizontal='right')
                
                # Maximum
                col_letter = get_column_letter(col_idx + 1)
                cell = ws[f'{col_letter}{row}']
                cell.value = stats.get("max")
                cell.number_format = '#,##0.00'
                cell.border = border
                cell.alignment = Alignment(horizontal='right')
                
                # Mean - Formula: AVERAGE of min and max
                col_letter = get_column_letter(col_idx + 2)
                min_col = get_column_letter(col_idx)
                max_col = get_column_letter(col_idx + 1)
                cell = ws[f'{col_letter}{row}']
                cell.value = f"=({min_col}{row}+{max_col}{row})/2"
                cell.number_format = '#,##0.00'
                cell.border = border
                cell.alignment = Alignment(horizontal='right')
                
                # Standard Deviation - keep as value (needs historical data range)
                col_letter = get_column_letter(col_idx + 3)
                cell = ws[f'{col_letter}{row}']
                cell.value = stats.get("std")
                cell.number_format = '#,##0.00'
                cell.border = border
                cell.alignment = Alignment(horizontal='right')
                
                # Mean - Std - Formula
                col_letter = get_column_letter(col_idx + 4)
                mean_col = get_column_letter(col_idx + 2)
                std_col = get_column_letter(col_idx + 3)
                cell = ws[f'{col_letter}{row}']
                cell.value = f"={mean_col}{row}-{std_col}{row}"
                cell.number_format = '#,##0.00'
                cell.border = border
                cell.alignment = Alignment(horizontal='right')
                
                # Latest Deviation from Mean (%) - Formula
                col_letter = get_column_letter(col_idx + 5)
                mean_col = get_column_letter(col_idx + 2)
                cell = ws[f'{col_letter}{row}']
                cell.value = f"=(C{row}-{mean_col}{row})/{mean_col}{row}"
                cell.number_format = '0.00%'
                cell.border = border
                cell.alignment = Alignment(horizontal='right')
                # Conditional formatting will be applied based on formula result
                dev_mean_pct = period_data.get("latest_deviation_from_mean_pct")
                fill_color = "C6EFCE" if dev_mean_pct and dev_mean_pct >= 0 else "FFC7CE"
                cell.fill = PatternFill(start_color=fill_color, end_color=fill_color, fill_type="solid")
                
                # Latest Deviation from Mean-StdDev (%) - Formula
                col_letter = get_column_letter(col_idx + 6)
                mean_std_col = get_column_letter(col_idx + 4)
                cell = ws[f'{col_letter}{row}']
                cell.value = f"=(C{row}-{mean_std_col}{row})/{mean_std_col}{row}"
                cell.number_format = '0.00%'
                cell.border = border
                cell.alignment = Alignment(horizontal='right')
                dev_mean_std_pct = period_data.get("latest_deviation_from_mean_minus_std_pct")
                fill_color = "C6EFCE" if dev_mean_std_pct and dev_mean_std_pct >= 0 else "FFC7CE"
                cell.fill = PatternFill(start_color=fill_color, end_color=fill_color, fill_type="solid")
                
                # Second Latest Deviation from Mean (%) - Formula
                col_letter = get_column_letter(col_idx + 7)
                mean_col = get_column_letter(col_idx + 2)
                cell = ws[f'{col_letter}{row}']
                cell.value = f"=(D{row}-{mean_col}{row})/{mean_col}{row}"
                cell.number_format = '0.00%'
                cell.border = border
                cell.alignment = Alignment(horizontal='right')
                second_dev_mean_pct = period_data.get("second_deviation_from_mean_pct")
                fill_color = "C6EFCE" if second_dev_mean_pct and second_dev_mean_pct >= 0 else "FFC7CE"
                cell.fill = PatternFill(start_color=fill_color, end_color=fill_color, fill_type="solid")
                
                # Second Latest Deviation from Mean-StdDev (%) - Formula
                col_letter = get_column_letter(col_idx + 8)
                mean_std_col = get_column_letter(col_idx + 4)
                cell = ws[f'{col_letter}{row}']
                cell.value = f"=(D{row}-{mean_std_col}{row})/{mean_std_col}{row}"
                cell.number_format = '0.00%'
                cell.border = border
                cell.alignment = Alignment(horizontal='right')
                second_dev_mean_std_pct = period_data.get("second_deviation_from_mean_minus_std_pct")
                fill_color = "C6EFCE" if second_dev_mean_std_pct and second_dev_mean_std_pct >= 0 else "FFC7CE"
                cell.fill = PatternFill(start_color=fill_color, end_color=fill_color, fill_type="solid")
                
                col_idx += 9
            
            row += 1
        
        # Freeze panes at row 6 (after headers), column E (after Fav, Symbol, Latest Quote, and Second Latest Quote)
        ws.freeze_panes = 'E6'
        
        # Add AutoFilter to the summary sheet
        last_col = get_column_letter(4 + len(self.PERIODS) * 9)
        ws.auto_filter.ref = f"A5:{last_col}{row - 1}"
    
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
                self.create_detailed_sheet(symbol, report)
        
        # Save the workbook
        self.save()
