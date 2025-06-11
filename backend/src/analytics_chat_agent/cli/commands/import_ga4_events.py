"""
GA4イベントデータのインポートコマンド
"""

import logging
import click
from datetime import datetime
from ...config import get_settings
from ...core.database import BigQueryConnection, PostgresConnection
from ...core.importer import EventsImporter
import psycopg2

logger = logging.getLogger(__name__)

def import_ga4_events(mode: str, target_date: str):
    """
    GA4のイベントデータをBigQueryからPostgreSQLにインポートする

    MODE:
        full: PostgreSQLの全データを削除し、BigQueryから全期間のデータを取得して流し込む
        date: 指定された日付のデータのみPostgreSQLから削除し、その日のデータだけ再インポートする
    """
    try:
        # 日付モードの場合、日付の検証
        if mode == 'date':
            if not target_date:
                raise click.BadParameter('dateモードでは--target-dateが必須です')
            try:
                datetime.strptime(target_date, '%Y-%m-%d')
            except ValueError:
                raise click.BadParameter('target-dateはYYYY-MM-DD形式で指定してください')

        # 設定を取得
        settings = get_settings()
        
        # データベース接続を確立
        with BigQueryConnection(settings["bigquery"]) as bq_conn, \
             PostgresConnection(settings["postgres"]) as pg_conn:
            
            # インポーターを初期化
            importer = EventsImporter(bq_conn, pg_conn)
            
            # モードに応じてインポートを実行
            if mode == 'full':
                click.echo("フルインポートモードで実行します...")
                count = importer.import_all_events()
                click.echo(f"{count}件のイベントデータをインポートしました。")
            else:
                click.echo(f"日付指定モードで実行します（対象日: {target_date}）...")
                count = importer.import_events_by_date(target_date)
                click.echo(f"{count}件のイベントデータをインポートしました。")

    except psycopg2.Error as e:
        logger.error(f"PostgreSQLエラー: {str(e)}")
        logger.error(f"エラーコード: {e.pgcode}")
        logger.error(f"エラーメッセージ: {e.pgerror}")
        click.echo(f"エラー: {str(e)}")
        raise click.Abort()
    except Exception as e:
        logger.error(f"イベントデータインポートエラー: {e}")
        click.echo(f"エラー: {str(e)}")
        raise click.Abort()

# コマンドの定義
cmd = click.command()(
    click.option('--mode', type=click.Choice(['full', 'date']), required=True, help='インポートモード')(
        click.option('--target-date', help='対象日付 (YYYY-MM-DD形式、dateモード時必須)')(
            import_ga4_events
        )
    )
) 