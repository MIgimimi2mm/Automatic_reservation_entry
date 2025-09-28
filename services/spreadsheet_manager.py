import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os
from datetime import datetime

class SpreadsheetManager:
    def __init__(self, credentials_path, spreadsheet_name):
        scope = ['https://spreadsheets.google.com/feeds',
                 'https://www.googleapis.com/auth/drive']
        credentials = ServiceAccountCredentials.from_json_keyfile_name(credentials_path, scope)
        self.client = gspread.authorize(credentials)
        self.spreadsheet = self.client.open(spreadsheet_name)
        
        # 予約元ごとのシート名を設定
        self.sheet_names = {
            'jalan': 'じゃらん',
            'tabirai': 'たびらい',
            'koushiki': '公式'
        }

    def append_reservation(self, reservation_data):
        """予約データをスプレッドシートに追加"""
        # 予約元に基づいてシートを選択
        source = reservation_data.get('予約元', '').lower()
        if source not in self.sheet_names:
            print(f"警告: 未知の予約元 '{source}' が検出されました")
            return
            
        worksheet = self.spreadsheet.worksheet(self.sheet_names[source])
        
        # 現在の日時を取得
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # 既存のヘッダー行を取得
        headers = worksheet.row_values(1)
        
        # データを整形（ヘッダーの順序に合わせる）
        row_data = []
        for header in headers:
            if header == '記録日時':
                row_data.append(current_time)
            elif header in reservation_data:
                row_data.append(reservation_data[header])
            else:
                row_data.append('')
        
        # スプレッドシートに追加
        worksheet.append_row(row_data, value_input_option='USER_ENTERED')
        print(f"{self.sheet_names[source]}シートに予約情報を追加しました。") 