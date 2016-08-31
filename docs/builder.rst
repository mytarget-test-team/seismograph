Builder
=======


About extension
---------------

Builder provides comfortable support for preparing data in database.
You can declare schema for data creation and configure preparing from any runnable object who has instance of builder.
Factories is an integral part of builder but can be usable separated of.
Main task of the factory is product of object and its relations.
Create method always gives rise to general object.
Any factory method must has property as storage.
If you don't set specific storage name that storage name will as method name without "create_" prefix.

Builder is not related to specific ORM and can be used with any ORM and simple sql.

Important!
Builder extension is not pluggable.
You should to create instance inside runnable object for using.


Example
-------

.. code-block:: python

    import seismograph

    from seismograph.ext.builder import BaseBuilder
    from seismograph.ext.builder import AliasToMethod
    from seismograph.ext.builder.factory import BaseFactory
    from seismograph.ext.builder.factory import factory_method


    class UserFactory(BaseFactory):

        def __init__(self, **user_data):
            self.user = None
            self.account = None
            self.permissions = []

            self._user_data = {}  # values by default

            self.build_data(**user_data)

        @property
        def data(self):  # must be implemented
            return self._user_data

        def build_data(self, **user_data):  # must be implemented
            self._user_data.update(user_data)

        @factory_method(required=['user'], only_one_creation=True)
        def create_account(self, **account_data):
            account_data.update(user_id=self.user.id)
            self.account = AccountModel.create(**account_data)
            return self._account

        @factory_method(required=['user'], storage='permissions')
        def create_permission(self, perm):
            created_perm = UserPermissionModel.create(
                perm=perm, user_id=self.user.id,
            )
            self.permissions.append(created_perm)
            return created_perm

        @factory_method(only_one_creation=True, storage='user')
        def create(self):  # must be implemented
            self.user = UserModel.create(**self._user_data)
            return self.user


    class UserBlogFactory(BaseFactory):

        def __init__(self, user, **blog_data):
            self.user = user

            self.blog = None
            self.posts = []

            self._blog_data = {}

            self.build_data(**blog_data)

        @property
        def data(self):  # must be implemented
            return self._blog_data

        def build_data(self, **blog_data):  # must be implemented
            self._blog_data.update(blog_data)
            self._blog_data.update(user_id=self.user.id)

        @factory_method(required=['blog'], storage='posts')
        def create_post(self, **post_data):
            post_data.update(blog_id=self.blog.id)
            post = PostModel.create(**post_data)
            self.posts.append(post)
            return post

        @factory_method(only_one_creation=True, storage='blog')
        def create(self):  # must be implemented
            self.blog = BlogModel.create(**self._blog_data)
            return self.blog


    def init_blog_factory(builder, cls, sig):  # for example
        return cls(builder.schema.user, *sig.args, **sig.kwargs)


    def create_user(factory, schema):  # for example
        user = factory.create()
        factory.create_account()
        return user


    class Builder(BaseBuilder):

        __build_schema__ = {
            'user': {
                'storage': 'users',
                'factory_class':  UserFactory,
                'staging': {
                    'pre': tuple(),  # for example only
                    'creator': create_user,
                    'post': (
                        AliasToMethod('account', 'create_account'),
                        AliasToMethod('permission', 'create_permission'),
                    ),
                },
                'embedded': {
                    'blog': {
                        'storage': 'blogs',
                        'factory_class': UserBlogFactory,
                        'initializer': init_blog_factory,
                        'staging': {
                            'pre': tuple(),  # for example only
                            'post': (
                                AliasToMethod('post', 'create_post'),
                            ),
                        },
                    },
                },
                # require = ['any key from this level can be here']
            },
        }


    suite = seismograph.Suite(__name__)


    @suite.register
    def simple_test(case):
        builder = Builder(case)
        builder.configure(
            user={
                'permission': {'perm': 'permission name'},
                'blog': (
                    {
                        'post': {'title': 'hello', 'text': 'Hello world!'},
                    },
                    {
                        'post': {'title': 'hello 2', 'text': 'Hello world!'},
                    },
                ),
            },
        )

        builder.schema.user  # last created user is here
        builder.schema.users  # user list is here, we set it by storage key

        builder.schema.user.blog  # this is last created blog
        builder.schema.user.blogs  # all created blogs here

        builder.schema.user.blog.posts  # this is list from factory
