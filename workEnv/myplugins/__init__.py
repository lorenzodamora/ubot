exec(open('../__init__.py', 'r', encoding='utf-8').read())
exec(open('../myClientParameter.py', 'r', encoding='utf-8').read())
__version__ = locals().get('__version__')
__date__ = locals().get('__date__')
GIST_TOKEN = locals().get('GIST_TOKEN')

__all__ = (
    "__version__",
    "__date__",
    "GIST_TOKEN"
)
