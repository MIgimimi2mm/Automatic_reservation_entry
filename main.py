from services.mail_reader import process_reservation_emails
import sys
import traceback
import datetime

# ログファイルに出力する設定
log_file = "log.txt"
sys.stdout = open(log_file, "a", encoding="utf-8")
sys.stderr = sys.stdout  # エラー出力も同じログに記録

print(f"\n[{datetime.datetime.now()}] スクリプト開始")

# エラーを補足してログ出力
def log_exception(exc_type, exc_value, exc_traceback):
    print("例外が発生しました:")
    traceback.print_exception(exc_type, exc_value, exc_traceback)

sys.excepthook = log_exception

# メール処理からスプレッドシート保存までの一連の処理を実行
process_reservation_emails()
