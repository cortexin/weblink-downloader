import databases
import sqlalchemy as sql

from link_downloader.config import DATABASE_URL


database = databases.Database(DATABASE_URL)

metadata = sql.MetaData()


links = sql.Table(
    'links',
    metadata,
    sql.Column('id', sql.Integer, primary_key=True),
    sql.Column('url', sql.String, nullable=False),
    sql.Column(
        'user_id',
        sql.Integer,
        sql.ForeignKey('app_users.id', ondelete='CASCADE'),
        nullable=False,
    ),
)

users = sql.Table(
    'app_users',
    metadata,
    sql.Column('id', sql.Integer, primary_key=True),
    sql.Column('username', sql.String(20), nullable=False, unique=True),
    sql.Column('password', sql.String, nullable=False),
)


engine = sql.create_engine(DATABASE_URL)

metadata.create_all(bind=engine)
