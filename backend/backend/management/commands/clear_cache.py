from django.core.management.base import BaseCommand
from django.core.cache import cache
from django.db import connection

class Command(BaseCommand):
    help = 'Clear Django cache selectively: all | products | search'

    def add_arguments(self, parser):
        parser.add_argument(
            'cache_type',
            nargs='?',
            default='all',
            type=str,
            help='Type of cache to clear: "all" (default), "products" (product cards), or "search" (home page)',
        )

    def handle(self, *args, **options):
        cache_type = options['cache_type'].lower()

        if cache_type == 'all':
            cache.clear()
            self.stdout.write(self.style.SUCCESS('✓ Cleared ALL cache (searches + product cards)'))

        elif cache_type == 'products':
            # Clear only product prices cache (product cards)
            with connection.cursor() as cursor:
                cursor.execute(
                    "DELETE FROM django_cache_table WHERE cache_key LIKE 'product_prices_%'"
                )
            self.stdout.write(self.style.SUCCESS('✓ Cleared PRODUCT CARDS cache only'))

        elif cache_type == 'search':
            # Clear only search cache (home page results)
            with connection.cursor() as cursor:
                cursor.execute(
                    "DELETE FROM django_cache_table WHERE cache_key LIKE 'search_user%' OR cache_key LIKE 'search_%'"
                )
            self.stdout.write(self.style.SUCCESS('✓ Cleared HOME PAGE search cache only'))

        else:
            self.stdout.write(
                self.style.ERROR(
                    f'Invalid cache_type "{cache_type}". Use: all, products, or search'
                )
            )