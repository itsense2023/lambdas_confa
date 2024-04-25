from connection.db_connection import connect_to_database
from utils.general_utils import build_records
from utils.general_utils import response_api
from utils.token_manage import verify_token_access
import models.responses as STATUS_CODE
from datetime import datetime
import pytz

def main(event, context):
    if 'Authorization' not in event['headers']:
        return STATUS_CODE.UNAUTHORIZED
    token_data, profiles, username = verify_token_access(event['headers']['Authorization'])
    data = event['body']
    time_zone = 'America/Bogota'
    current_time_with_zone = datetime.now(pytz.timezone(time_zone))
    current_date = current_time_with_zone.strftime('%Y-%m-%d')
    conn = connect_to_database()
    if conn is None:
        return STATUS_CODE.INTERNAL_ERROR_SERVER
    cur = conn.cursor()
    try:
        cur.execute("select * from dbo.sp_modify_notification(%s::bigint,%s::character varying,%s::character varying,%s::character varying[],%s::int,%s::int,%s::character varying,%s::date)", 
                (data["notification_id"],
                  data["notification_name"],
                  data["notification_message"],
                  data["notification_receiver"],
                  data['notification_receiver_id'],
                  data['action_id'],
                  username,
                  current_date))
        conn.commit()
        return response_api(STATUS_CODE.OK['code'], STATUS_CODE.OK['message'], "created")
    except Exception as e:
        conn.commit()
        conn.rollback()
        cur.close()
        conn.close()
        print("error --> ", str(e))
        return STATUS_CODE.INTERNAL_ERROR_SERVER