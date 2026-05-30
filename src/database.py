import databases
import sqlalchemy

from src.config import config

# db schema
metadata = sqlalchemy.MetaData()
post_table = sqlalchemy.Table(
    "post",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("body", sqlalchemy.String),
    sqlalchemy.Column("user_id", sqlalchemy.ForeignKey("user.id"), nullable=False),
    sqlalchemy.Column("image_url", sqlalchemy.String),
)
user_table = sqlalchemy.Table(
    "user",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("email", sqlalchemy.String, unique=True),
    sqlalchemy.Column("password", sqlalchemy.String),
    sqlalchemy.Column("confirmed", sqlalchemy.Boolean, default=False),
)
comment_table = sqlalchemy.Table(
    "comment",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("body", sqlalchemy.String),
    sqlalchemy.Column("post_id", sqlalchemy.ForeignKey("post.id"), nullable=False),
    sqlalchemy.Column("user_id", sqlalchemy.ForeignKey("user.id"), nullable=False),
    # nullable=False to avoid comments without posts
)

like_table = sqlalchemy.Table(
    "like",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("post_id", sqlalchemy.ForeignKey("post.id"), nullable=False),
    sqlalchemy.Column("user_id", sqlalchemy.ForeignKey("user.id"), nullable=False),
)

# connect to a specific db
connect_args = {"check_same_thread": False} if "sqlite" in config.DATABASE_URL else {}
engine = sqlalchemy.create_engine(
    config.DATABASE_URL,
    connect_args=connect_args,  # {"check_same_thread": False},  # for sqlite
)

# db creation
metadata.create_all(engine)
database = databases.Database(config.DATABASE_URL, force_rollback=config.DB_FORCE_ROLL_BACK)
