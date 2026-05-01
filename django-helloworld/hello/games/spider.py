from .base import BaseSolitaire

class Spider(BaseSolitaire):
    """
    Spider Solitaire - Two deck variant with 10 tableau columns.
    Goal: Build complete sequences (K-A) within a tableau, then move to foundations.
    """
    
    def setup_board(self):
        self.stock = []
        self.waste = []
        self.foundations = [[] for _ in range(8)]  # 8 foundations (2 of each suit)
        self.tableaus = [[] for _ in range(10)]  # 10 columns for tableau

        self.generate_deck(decks=2)  # Spider uses 2 decks

        # Deal 6 cards to first 4 columns, 5 cards to remaining 6 columns
        tableau_index = 0
        for column_num in range(10):
            cards_to_deal = 6 if column_num < 4 else 5
            for card_index in range(cards_to_deal):
                if self.stock:
                    card = self.stock.pop()
                    # Only top card is face up
                    card.is_face_up = (card_index == cards_to_deal - 1)
                    self.tableaus[column_num].append(card)

    def is_valid_move(self, card, destination):
        """
        In Spider, sequences of the same suit can be moved together.
        King can start an empty column.
        Any card can go on a card of next higher rank.
        """
        # Cannot move face-down cards
        if not card.is_face_up:
            return False
        
        rank = card.rank
        
        # If destination is empty, only King can start
        if not destination:
            return rank == 13
        
        top_card = destination[-1] if destination else None
        if not top_card:
            return rank == 13
        
        # Can place on card of next higher rank (regardless of suit in Spider)
        return rank == top_card.rank - 1

    def draw_from_stock(self):
        """Deal 10 cards (one to each tableau) from stock"""
        if self.stock:
            for _ in range(10):
                if self.stock:
                    card = self.stock.pop()
                    card.is_face_up = True
                    self.tableaus[_].append(card)

    def check_win_condition(self):
        """Win if all 8 foundations are complete"""
        return all(len(f) == 13 for f in self.foundations)

    def to_dict(self):
        """Convert game state to dictionary for JSON serialization"""
        base_dict = super().to_dict()
        base_dict['variant'] = 'Spider'
        base_dict['num_tableaus'] = 10
        return base_dict
