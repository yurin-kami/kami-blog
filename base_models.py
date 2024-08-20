# 导入数据库相关的基类和字段类型
import json

from sqlalchemy import Column, Integer, String, DateTime, Text, create_engine, inspect,Table,MetaData
from sqlalchemy.exc import NoResultFound, IntegrityError
from sqlalchemy.orm import sessionmaker,declarative_base
from sqlalchemy.dialects.mysql import LONGTEXT
from datetime import datetime

# 创建基类，用于ORM映射
Base = declarative_base()

class BlogPost(Base):
    # 定义博客文章表的映射类
    __tablename__ = 'blog_post'  # 指定表名为blog_posts
    id = Column(Integer, primary_key=True)  # 主键
    title = Column(String(100), nullable=False)  # 标题，长度100，不能为空
    content = Column(LONGTEXT)  # 内容，长文本类型
    publish_date = Column(DateTime, default=datetime.utcnow)  # 发布日期，默认为当前时间
    tags = Column(String(200))  # 标签，长度200

    # 将博客文章信息转换为字典
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'publish_date': self.publish_date.isoformat(),
            'tags': self.tags,
        }

class BookshelfItem(Base):
    # 定义书架条目表的映射类
    __tablename__ = 'bookshelf_item'  # 指定表名为bookshelf_items
    id = Column(Integer, primary_key=True)  # 主键
    title = Column(String(100), nullable=False)  # 标题，长度100，不能为空
    author = Column(String(50), nullable=False)  # 作者，长度50，不能为空
    cover_image = Column(String(200))  # 封面图片，长度200
    book_id = Column(String(100))  # 外部链接，长度200
    book_url=Column(String(200))

    # 将书架条目信息转换为字典
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'author': self.author,
            'cover_image': self.cover_image,
            'book_id': self.book_id,
            'book_url': self.book_url
        }

class Music(Base):
    # 定义音乐表的映射类
    __tablename__ = 'music'  # 指定表名为musics
    id = Column(Integer, primary_key=True)  # 主键
    title = Column(String(100), nullable=False)  # 标题，长度100，不能为空
    artist = Column(String(50), nullable=False)  # 艺术家，长度50，不能为空
    external_id = Column(String(50))  # 外部ID，长度50
    img_url = Column(String(500))

    # 将音乐信息转换为字典
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'artist': self.artist,
            'external_id': self.external_id,
            'img_url': self.img_url,
        }

class User(Base):
    # 定义用户表的映射类
    __tablename__ = 'users'  # 指定表名为users
    id = Column(Integer, primary_key=True)  # 主键
    username = Column(String(50), unique=True, nullable=False)  # 用户名，长度50，唯一，不能为空
    password = Column(String(128), nullable=False)  # 密码哈希值，长度128，不能为空
    email = Column(String(120), unique=True)  # 邮箱，长度120，唯一，不能为空

    # 设置密码
    def set_password(self, password):
        """
        设置密码。
        :param password: 明文密码
        """
        self.password = password  # 将明文密码哈希后保存

    # 校验密码
    def check_password(self, password):
        """
        校验密码。
        :param password: 明文密码
        :return: 布尔值，密码是否正确
        """
        return self.password==password  # 检查传入的明文密码与哈希后的密码是否匹配

    # 将用户信息转换为字典
    def to_dict(self):
        """
        将用户信息转换为字典。
        :return: 包含用户信息的字典
        """
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'password': self.password,  # 密码明文，仅用于展示
        }
class Kami:
    def __init__(self):
        self.engine=create_engine('mysql+pymysql://root:kami@127.0.0.1/kami_blog', echo=True)
        self.session=sessionmaker(self.engine)()
        self.mata=MetaData()
    def insert_music(self, model, data: dict):
        new_instances = []  # 用于存储不重复数据的列表
        try:
            self.session.begin()  # 开始事务
            for title, external_id, img_url in zip(data['title'], data['external_id'], data['img_url']):
                # 检查是否存在具有相同 external_id 的记录
                existing_record = self.session.query(model).filter_by(external_id=external_id).first()
                if not existing_record:
                    # 如果不存在，则创建新的实例
                    new_instance = model(
                        title=title,
                        artist=data['artist'],  # 注意这里的 artist 是列表，需要按索引获取
                        external_id=external_id,
                        img_url=img_url
                    )
                    new_instances.append(new_instance)
            # 添加所有不重复的新实例
            self.session.add_all(new_instances)
            # 提交事务
            self.session.commit()
            return "ok"
        except Exception as e:
            # 如果出现任何错误，则回滚事务
            self.session.rollback()
            print(e)
            return False
        finally:
            self.session.close()

    def insert_book(self,model,data:dict):
        new_instances = []
        try:
            self.session.begin()  # 开始事务

            for title, book_id, author, cover_image, book_url in zip(
                    data['title'],
                    data['book_id'],
                    data['author'],
                    data['cover_image'],
                    data['book_url']
            ):
                # 检查是否存在具有相同 book_id 的记录
                try:
                    existing_record = self.session.query(model).filter_by(book_id=book_id).one()
                except NoResultFound:
                    existing_record = None

                if not existing_record:
                    # 如果不存在，则创建新的实例
                    new_instance = model(
                        title=title,
                        author=author,
                        book_id=book_id,
                        cover_image=cover_image,
                        book_url=book_url
                    )
                    new_instances.append(new_instance)

            # 添加所有不重复的新实例
            self.session.add_all(new_instances)
            # 提交事务
            self.session.commit()
            return "ok"
        except Exception as e:
            # 如果出现任何错误，则回滚事务
            self.session.rollback()
            print(e)
            return False
        finally:
            self.session.close()

    def insert_blog(self, data: dict):
        """
        插入博客数据到数据库。

        参数:
        - data: 包含博客数据的字典，应包含 title, content, 和 tags 键。
        """
        new_instances = []  # 用于存储不重复数据的列表
        try:
            self.session.begin()  # 开始事务

            # 确保 tags 是一个列表
            tags_list = data['tags']

            # 检查是否存在具有相同标题的记录
            existing_record = self.session.query(BlogPost).filter_by(title=data['title']).first()
            if not existing_record:
                # 如果不存在，则创建新的实例
                new_instance = BlogPost(
                    title=data['title'],
                    content=data['content'],
                    tags=str(tags_list),  # 直接使用列表形式的 tags
                    publish_date=datetime.utcnow()
                )
                new_instances.append(new_instance)

            # 添加所有不重复的新实例
            self.session.add_all(new_instances)
            # 提交事务
            self.session.commit()
            return "ok"
        except IntegrityError as e:
            # 如果出现完整性错误（例如主键重复），则回滚事务
            self.session.rollback()
            print(e)
            return False
        except Exception as e:
            # 如果出现任何其他错误，则回滚事务
            self.session.rollback()
            print(e)
            return False

    def query(self, table, **kwargs):
        try:
            if not kwargs:
                data = self.session.query(table).all()
                data = [i.to_dict() for i in data]
                return data
            else:
                query = self.session.query(table)
                for key, value in kwargs.items():
                    query = query.filter(getattr(table, key) == value)  # 使用 getattr 获取表对象的属性并设置过滤条件
                data = query.all()
                data = [i.to_dict() for i in data]
                return data
        except Exception as e:
            print(e)
            return False
        finally:
            self.session.close()
    def update(self,table,**kwargs):
        try:
            self.session.query(table).filter_by(**kwargs).update(kwargs)
            self.session.commit()
            return "ok"
        except Exception as e:
            print(e)
            return False
        finally:
            self.session.close()
    def delete(self,table,**kwargs):
        try:
            self.session.query(table).filter_by(**kwargs).delete()
            self.session.commit()
            return "ok"
        except Exception as e:
            print(e)
            return False
        finally:
            self.session.close()
if __name__ == '__main__':
    kami=Kami()
#     data={
#         'title':['1'],
#         'content':'anwdujdlnbuiasfbuiebdswlkfhyb',
#         'tags':['1','2']
#     }
#     kami.insert_blog(data)
    for i in kami.query(BlogPost):
        print(i['title'])