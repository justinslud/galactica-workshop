from django.core.management.base import BaseCommand

from core import search
from core.models import Article, SearchDocument


class Command(BaseCommand):
    help = 'Rebuild the FTS5 search index from published articles.'

    def handle(self, *args, **options):
        SearchDocument.objects.all().delete()
        count = 0
        for article in Article.objects.filter(published__isnull=False).select_related('published'):
            if search.index_article(article) is not None:
                count += 1
        self.stdout.write(self.style.SUCCESS(f'Rebuilt search for {count} published article(s).'))
