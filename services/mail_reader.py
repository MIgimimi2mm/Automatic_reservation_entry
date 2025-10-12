import os
import imaplib
import email
import codecs
from email.header import decode_header
from dotenv import load_dotenv
from datetime import datetime, timedelta
# パーサーとユーティリティをインポート（必要に応じて修正）
from parsers.jalan_parser import parse_jalan_email
from parsers.tabirai_parser import parse_tabirai_email
from parsers.koushiki_parser import parse_koushiki_email
from services.spreadsheet_manager import SpreadsheetManager

load_dotenv()

IMAP_SERVER = os.getenv("IMAP_SERVER")
EMAIL_ACCOUNT = os.getenv("EMAIL_ACCOUNT")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
DEBUG_MESSAGE_ID = os.getenv("DEBUG_TARGET_MESSAGE_ID", "").strip()



def detect_reservation_info(subject: str):
    """件名から予約元と予約/キャンセルの種別を判定"""
    if subject == "じゃらんnetレンタカー 予約通知":
        return ("jalan", "予約")
    elif subject == "じゃらんnetレンタカー キャンセル通知":
        return ("jalan", "キャンセル")
    elif subject.startswith("たびらい") and "様予約" in subject:
        return ("tabirai", "予約")
    elif subject.startswith("たびらい") and "より予約キャンセルの通知" in subject:
        return ("tabirai", "キャンセル")
    elif "《公式予約》ジェイトリップカーレンタルズ" in subject and "ご予約ありがとうございます" in subject:
        return ("koushiki", "予約")
    return None


def decode_mime_words(s):
    if s is None:
        return ""
    decoded_fragments = decode_header(s)
    return ''.join([
        fragment.decode(encoding or 'utf-8') if isinstance(fragment, bytes) else fragment
        for fragment, encoding in decoded_fragments
    ])

    
def process_reservation_emails():
    """メール処理からスプレッドシート保存までの一連の処理"""
    try:
        # スプレッドシートマネージャーの初期化
        spreadsheet_manager = SpreadsheetManager(
            credentials_path=os.getenv('GOOGLE_CREDENTIALS_PATH'),
            spreadsheet_name=os.getenv('SPREADSHEET_NAME')
        )
        
        print(f"IMAPサーバー {IMAP_SERVER} に接続中...")
        mail = imaplib.IMAP4_SSL(IMAP_SERVER)
        print("ログイン中...")
        mail.login(EMAIL_ACCOUNT, EMAIL_PASSWORD)
        print("受信トレイを選択中...")
        mail.select("inbox")


        
                # --- ここから検索条件の分岐 ---
        if DEBUG_MESSAGE_ID:
            escaped_message_id = DEBUG_MESSAGE_ID.replace('"', '\\"')
            print(f"Message-IDフィルターで検索: {DEBUG_MESSAGE_ID}")
            status, data = mail.search(None, f'(HEADER Message-ID "{escaped_message_id}")')

 

        else:
            # 指定日数前の日付を計算
            bfd = 151
            six_months_ago = datetime.now() - timedelta(days=bfd)
            date_str = six_months_ago.strftime("%d-%b-%Y")
            print(f"{bfd}日前の日付: {date_str}")
            print("6ヶ月以内の未読メールを検索中...")
            status, data = mail.search(None, f'UNSEEN SINCE "{date_str}"')
        # --- ここまで ---

        if status != 'OK':
            print("メールの検索に失敗しました。")
            return
        # 未読メールの数を表示
        email_nums = data[0].split()
        print(f"6ヶ月以内の未読メール数: {len(email_nums)}件")
        success_count = 0
        
        for i, num in enumerate(email_nums):
            print(f"メール処理中... ({i+1}/{len(email_nums)})")
            
            try:
                status, msg_data = mail.fetch(num, '(RFC822)')
                if status != 'OK':
                    print(f"メール {num} の取得に失敗しました。")
                    continue
                raw_email = msg_data[0][1]
                msg = email.message_from_bytes(raw_email)
                subject = decode_mime_words(msg["Subject"])
                sender = msg.get("From", "")
                info = detect_reservation_info(subject)
                if info:
                    source, status = info
                    print(f"[{source} / {status}] 該当メール: {subject}")
                    # 本文抽出（text/plain優先）
                    body = ""
                    if msg.is_multipart():
                        for part in msg.walk():
                            content_type = part.get_content_type()
                            if content_type == "text/plain":
                                # 文字エンコーディングを取得
                                charset = part.get_content_charset() or 'utf-8'
                                
                                try:
                                    body = part.get_payload(decode=True).decode(charset)
                                except UnicodeDecodeError:
                                    # エンコーディングエラーの場合は代替エンコーディングを試行
                                    for fallback_encoding in ['iso-2022-jp', 'shift_jis', 'euc-jp', 'utf-8']:
                                        try:
                                            if fallback_encoding == 'iso-2022-jp':
                                                # iso-2022-jpの場合は特別な処理
                                                body = part.get_payload(decode=True).decode('iso-2022-jp', errors='replace')
                                            else:
                                                body = part.get_payload(decode=True).decode(fallback_encoding)
                                            break
                                        except UnicodeDecodeError:
                                            continue
                                    else:
                                        # すべてのエンコーディングが失敗した場合
                                        body = part.get_payload(decode=True).decode('utf-8', errors='replace')
                                break
                    else:
                        # シンプルなメールの場合
                        charset = msg.get_content_charset() or 'utf-8'
                        
                        try:
                            body = msg.get_payload(decode=True).decode(charset)
                        except UnicodeDecodeError:
                            # エンコーディングエラーの場合は代替エンコーディングを試行
                            for fallback_encoding in ['iso-2022-jp', 'shift_jis', 'euc-jp', 'utf-8']:
                                try:
                                    if fallback_encoding == 'iso-2022-jp':
                                        # iso-2022-jpの場合は特別な処理
                                        body = msg.get_payload(decode=True).decode('iso-2022-jp', errors='replace')
                                    else:
                                        body = msg.get_payload(decode=True).decode(fallback_encoding)
                                    break
                                except UnicodeDecodeError:
                                    continue
                            else:
                                # すべてのエンコーディングが失敗した場合
                                body = msg.get_payload(decode=True).decode('utf-8', errors='replace')
                    # パーサー呼び出し
                    if source == "jalan":
                        result = parse_jalan_email(body)
                    elif source == "tabirai":
                        result = parse_tabirai_email(body)
                    elif source == "koushiki":
                        result = parse_koushiki_email(body)
                    else:
                        continue
                    # パーサーが予約状況を設定していない場合のみ設定
                    if "予約状況" not in result:
                        result["予約状況"] = status
                    # 予約情報を表示
                    print(f"\n=== 予約情報 {success_count + 1} ===")
                    for key, value in result.items():
                        print(f"{key}: {value}")
                    # スプレッドシートに保存
                    try:
                        spreadsheet_manager.append_reservation(result)
                        print("スプレッドシートに保存しました。\n\n")
                        success_count += 1
                    except Exception as e:
                        print(f"スプレッドシートへの保存に失敗しました\n\n: {e}")
                        print("メールを未読に戻します。")
                        mail.store(num, '-FLAGS', '\\Seen')
                        print("処理を停止します。")
                        mail.logout()
                        return
                else:
                    # 予約メールでない場合は未読に戻す
                    print(f"予約メールではありません: {subject}")
                    mail.store(num, '-FLAGS', '\\Seen')
                    print("メールを未読に戻しました。")
            except Exception as e:
                print(f"メール {num} の処理中にエラーが発生しました: {e}")
                # エラーが発生した場合も未読に戻す
                mail.store(num, '-FLAGS', '\\Seen')
                continue
        print(f"\n{success_count}件の予約情報をスプレッドシートに保存しました。")
        mail.logout()
    except imaplib.IMAP4.error as e:
        print(f"[IMAPエラー] {e}")
    except Exception as e:
        print(f"[予期せぬエラー] {e}")
# 後方互換性のため残しておく関数
def fetch_latest_unseen_emails():
    """後方互換性のための関数（使用しない）"""
    print("この関数は非推奨です。process_reservation_emails()を使用してください。")
    return [], []

# import imaplib
# import os
# from dotenv import load_dotenv
# load_dotenv()
# IMAP_SERVER = os.getenv("IMAP_SERVER")
# EMAIL_ACCOUNT = os.getenv("EMAIL_ACCOUNT")
# EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
# mail = imaplib.IMAP4_SSL(IMAP_SERVER)
# mail.login(EMAIL_ACCOUNT, EMAIL_PASSWORD)
# mail.select("inbox")
# # すべてのメールのUIDを取得
# status, data = mail.search(None, "ALL")
# if status == "OK":
#     for num in data[0].split():
#         mail.store(num, '-FLAGS', '\\Seen')
#     print("すべてのメールを未読にしました。")
# else:
#     print("メールの検索に失敗しました。")
# mail.logout()