# db.py
import pymysql
from typing import Dict, List, Optional

db_config = {
    "host": "localhost",
    "user": 'root',
    "db_port": "3306",
    "password": '',
    "database": 'MASTERARTICLE',
}

def connect_to_db():
    try:
        connection = pymysql.connect(
            host=db_config['host'],
            port=int(db_config['db_port']),
            user=db_config['user'],
            password=db_config['password'],
            database=db_config['database'],
        )
        return connection
    except Exception as e:
        print(f"Failed to connect to the database: {e}")
        return None

def get_article_by_id(article_id: int) -> Optional[Dict]:
    connection = connect_to_db()
    if not connection:
        return None
    
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT id, link, articlename, summary, credibility, tags, related, fullarticle
                FROM ARTICLES 
                WHERE id = %s
            """, (article_id,))
            result = cursor.fetchone()
            
            if result:
                return {
                    'id': result[0],
                    'link': result[1],
                    'articlename': result[2],
                    'summary': result[3],
                    'credibility': result[4],
                    'tags': result[5],
                    'related': result[6],
                    'fullarticle': result[7]
                }
            return None
    finally:
        connection.close()

def get_all_articles() -> List[Dict]:
    connection = connect_to_db()
    if not connection:
        return []
    
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT id, link, articlename, summary, credibility, tags, related
                FROM ARTICLES
            """)
            results = cursor.fetchall()
            
            return [{
                'id': row[0],
                'link': row[1],
                'articlename': row[2],
                'summary': row[3],
                'credibility': row[4],
                'tags': row[5],
                'related': row[6]
            } for row in results]
    finally:
        connection.close()