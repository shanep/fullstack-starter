from django.core.management.base import BaseCommand
from hello.models import GameVariant

class Command(BaseCommand):
    help = 'Initialize game variants in the database'

    def handle(self, *args, **options):
        variants = [
            {
                'name': 'Klondike',
                'description': 'Classic single-deck solitaire. Draw from stock pile, build sequences on tableau, and complete foundations.',
                'difficulty': 'easy',
                'deck_count': 1,
                'rules': 'Tableau: Descending rank, alternating color. Foundation: Ascending rank, same suit starting with Ace.'
            },
            {
                'name': 'Spider',
                'description': 'Two-deck variant with 10 tableau columns. More complex with larger tableau and multiple foundations.',
                'difficulty': 'hard',
                'deck_count': 2,
                'rules': 'Build sequences K-A within tableaus. Cards of any suit can be played on next lower rank.'
            },
            {
                'name': 'FreeCell',
                'description': 'All cards visible with 4 free cells for temporary storage. Strategic gameplay with visible information.',
                'difficulty': 'medium',
                'deck_count': 1,
                'rules': 'Use free cells to temporarily store cards. Build foundations by suit in ascending order.'
            },
        ]

        for variant_data in variants:
            variant, created = GameVariant.objects.get_or_create(
                name=variant_data['name'],
                defaults=variant_data
            )
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'Created variant: {variant.name}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'Variant already exists: {variant.name}')
                )
